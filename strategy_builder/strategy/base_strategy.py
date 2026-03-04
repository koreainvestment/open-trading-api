"""
전략 베이스 클래스

Applied Skills: skills/investment-strategy-framework.md
- 모든 전략은 BaseStrategy를 상속
- 전략은 데이터 조회/지표 계산만 사용, 직접 주문 금지
"""

from abc import ABC, abstractmethod

from core.signal import Signal


class BaseStrategy(ABC):
    """
    모든 전략의 베이스 클래스

    skill:
        - 전략은 다른 전략을 참조하지 않는다
        - 전략 간 상태 공유 금지
        - 전략은 core.data_fetcher와 core.indicators만 사용
    """

    @abstractmethod
    def generate_signal(self, stock_code: str, stock_name: str) -> Signal:
        """
        단일 종목에 대한 시그널 생성

        Args:
            stock_code: 종목코드 (6자리)
            stock_name: 종목명

        Returns:
            Signal 객체
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """전략명"""
        pass

    @property
    @abstractmethod
    def required_days(self) -> int:
        """필요한 과거 데이터 일수"""
        pass

    def __str__(self) -> str:
        return f"{self.name} (required_days={self.required_days})"

