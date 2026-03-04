"""
UI Backend Package

TradingState를 통한 상태 관리:
- 인증 상태
- 모의/실전 모드
- 모드 전환 쿨다운
"""

from .state import trading_state


def authenticate(svr: str = "vps") -> bool:
    """KIS API 인증
    
    Args:
        svr: 트레이딩 모드 ("vps" 모의투자, "prod" 실전투자)
        
    Returns:
        인증 성공 여부
    """
    try:
        return trading_state.authenticate(mode=svr)
    except Exception as e:
        print(f"인증 실패: {e}")
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


# 편의를 위해 싱글톤 인스턴스 직접 노출
__all__ = [
    "trading_state",
    "authenticate",
    "is_authenticated",
    "get_current_mode",
    "get_status",
]
