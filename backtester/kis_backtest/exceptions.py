"""예외 클래스
"""

from typing import Optional


class LeanError(Exception):
    """KIS Backtest 기본 예외"""
    pass


class ConfigurationError(LeanError):
    """설정 오류"""
    pass


class AlgorithmError(LeanError):
    """알고리즘 실행 오류"""
    
    def __init__(self, message: str, stacktrace: Optional[str] = None):
        self.message = message
        self.stacktrace = stacktrace
        super().__init__(message)


class DockerError(LeanError):
    """Docker 오류"""
    pass


# ============================================
# 한국투자증권 관련 예외
# ============================================

class KISError(LeanError):
    """한국투자증권 API 오류"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        self.error_code = error_code
        self.error_message = error_message
        super().__init__(message)


class KISAuthError(KISError):
    """인증 오류 (토큰 만료, 잘못된 키 등)"""
    pass


class KISOrderError(KISError):
    """주문 오류 (잔고 부족, 호가 오류 등)"""
    pass

