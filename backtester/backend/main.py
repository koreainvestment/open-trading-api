"""P2 Backend - FastAPI Application.

백테스팅 라이브러리 REST API 서버.

실행 방법:
    cd backtester/
    uv run python -m uvicorn backend.main:app --reload --port 8002
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# .env 로드 (backtester/ 또는 backend/)
_env_paths = [
    Path(__file__).resolve().parent / ".env",      # backend/.env
    Path(__file__).resolve().parents[1] / ".env",  # backtester/.env
]
for _p in _env_paths:
    if _p.exists():
        load_dotenv(_p)
        break

# Lean 워크스페이스 설정 (backtester/.lean-workspace 사용)
_project_root = Path(__file__).resolve().parents[1]  # backtester/
_workspace_path = _project_root / ".lean-workspace"
from kis_backtest.lean.project_manager import LeanProjectManager
LeanProjectManager.set_workspace(str(_workspace_path))

from backend.routes import strategies, backtest, files, symbols, auth

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """애플리케이션 라이프사이클 관리"""
    logger.info("KIS2 Strategy API 서버 시작")
    yield
    logger.info("KIS2 Strategy API 서버 종료")


# FastAPI 앱 생성
app = FastAPI(
    title="KIS2 Strategy API",
    description="""
KIS2 독립형 전략 프레임워크 API

## 기능
- 전략 목록 조회 및 상세 정보
- 백테스트 실행 (Lean Docker)
- 전략 파일 Import/Export (.kis.yaml)

## 특징
- kis 폴더와 독립적으로 동작
- Single Source of Truth 기반 전략 정의
- 14종 기본 전략 + 커스텀 전략 지원
""",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


# ============================================
# CORS 설정
# ============================================

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page", "X-Per-Page"],
)


# ============================================
# 전역 예외 핸들러
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """전역 예외 핸들러"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "서버 내부 오류가 발생했습니다",
            },
        },
    )


# ============================================
# 라우터 등록
# ============================================

app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["auth"],
)

app.include_router(
    strategies.router,
    prefix="/api/strategies",
    tags=["strategies"],
)

app.include_router(
    backtest.router,
    prefix="/api/backtest",
    tags=["backtest"],
)

app.include_router(
    files.router,
    prefix="/api/files",
    tags=["files"],
)

app.include_router(
    symbols.router,
    prefix="/api/symbols",
    tags=["symbols"],
)


# ============================================
# 시스템 엔드포인트
# ============================================

@app.get("/api/health", tags=["system"])
async def health_check() -> dict:
    """헬스체크"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "kis_backtest",
    }


@app.get("/", tags=["system"])
async def root() -> dict:
    """루트"""
    return {
        "name": "KIS2 Strategy API",
        "version": "1.0.0",
        "docs": "/api/docs",
    }
