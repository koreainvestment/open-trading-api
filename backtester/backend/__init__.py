"""KIS2 Strategy API.

FastAPI 기반 REST API 서버.
"""

from .state import trading_state


def authenticate(svr: str = "vps") -> bool:
    """KIS API 인증

    Args:
        svr: 트레이딩 모드 ("vps" 모의투자, "prod" 실전투자)
    """
    try:
        return trading_state.authenticate(mode=svr)
    except Exception:
        return False


def is_authenticated() -> bool:
    """인증 상태 확인"""
    return trading_state.is_authenticated


def get_current_mode() -> str:
    """현재 트레이딩 모드 반환"""
    return trading_state.current_mode


def get_status() -> dict:
    """전체 상태 정보 반환"""
    return trading_state.get_status()


# app은 마지막에 임포트 (순환 참조 방지)
from .main import app  # noqa: E402

__all__ = [
    "app",
    "trading_state",
    "authenticate",
    "is_authenticated",
    "get_current_mode",
    "get_status",
]
