"""인증 관련 API Router

Mode Switching Feature:
- POST /login: 인증 (모드 지정)
- GET /status: 인증 상태 및 모드 정보
- POST /switch-mode: 모드 전환 (1분 쿨다운)
- POST /logout: 로그아웃
"""
import asyncio

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend import get_current_mode, get_status
from backend.state import trading_state

router = APIRouter()


class LoginRequest(BaseModel):
    mode: str = "vps"  # vps(모의) or prod(실전)


class SwitchModeRequest(BaseModel):
    mode: str  # vps(모의) or prod(실전)


class AuthStatusResponse(BaseModel):
    authenticated: bool
    mode: str
    mode_display: str
    can_switch_mode: bool
    cooldown_remaining: int


@router.post("/login")
async def login(request: LoginRequest):
    """KIS API 인증

    Args:
        mode: 트레이딩 모드 ("vps" 모의투자, "prod" 실전투자)
    """
    if request.mode not in ("vps", "prod"):
        raise HTTPException(
            status_code=400,
            detail="mode는 'vps' 또는 'prod'만 가능합니다.",
        )

    try:
        loop = asyncio.get_running_loop()
        await asyncio.wait_for(
            loop.run_in_executor(None, trading_state.authenticate, request.mode),
            timeout=60.0,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408,
            detail="인증 시간 초과 (60초). kis_devlp.yaml의 URL 및 appkey/appsecret을 확인하세요.",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    status = get_status()
    return {"status": "success", **status}


@router.get("/status", response_model=AuthStatusResponse)
async def get_auth_status():
    """인증 상태 확인"""
    status = get_status()
    return AuthStatusResponse(**status)


@router.post("/switch-mode")
async def switch_mode(request: SwitchModeRequest):
    """트레이딩 모드 전환 (모의투자 ↔ 실전투자, 1분 쿨다운)"""
    if request.mode not in ("vps", "prod"):
        raise HTTPException(
            status_code=400,
            detail="mode는 'vps' 또는 'prod'만 가능합니다.",
        )

    if request.mode == get_current_mode():
        raise HTTPException(
            status_code=400,
            detail=f"이미 {trading_state.mode_display} 모드입니다.",
        )

    try:
        loop = asyncio.get_running_loop()
        await asyncio.wait_for(
            loop.run_in_executor(None, trading_state.authenticate, request.mode),
            timeout=60.0,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408,
            detail="인증 시간 초과 (60초). kis_devlp.yaml 설정을 확인하세요.",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    status = get_status()
    return {
        "status": "success",
        "message": f"{trading_state.mode_display}로 전환되었습니다.",
        **status,
    }


@router.post("/logout")
async def logout():
    """로그아웃 (토큰 삭제 및 인증 상태 초기화)"""
    trading_state.logout()
    return {
        "status": "success",
        "message": "로그아웃되었습니다.",
        "authenticated": False,
    }
