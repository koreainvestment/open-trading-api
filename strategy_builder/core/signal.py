"""
Signal 클래스 정의

Applied Skills: skills/investment-strategy-framework.md
- Signal 불변성 (frozen=True)
- 필수 속성 정의
- 시그널 강도 기준
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Action(Enum):
    """매매 행동 구분"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass(frozen=True)
class Signal:
    """
    투자 시그널 데이터 클래스

    skill: Signal 객체는 생성 후 변경 불가 (immutable)

    Attributes:
        stock_code: 종목코드 (6자리)
        stock_name: 종목명
        action: 매매 행동 (BUY/SELL/HOLD)
        strength: 시그널 강도 (0.0 ~ 1.0)
        reason: 시그널 발생 사유
        timestamp: 시그널 생성 시각
        target_price: 목표가격 (지정가 주문용, None이면 시장가)
        quantity: 주문 수량 (None이면 자동 계산)

    시그널 강도 기준 (skill):
        0.8 ~ 1.0: 강한 시그널 → 시장가 주문
        0.5 ~ 0.8: 일반 시그널 → 지정가 주문
        0.0 ~ 0.5: 약한 시그널 → 주문 보류 가능
    """
    stock_code: str
    stock_name: str
    action: Action
    strength: float
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)
    target_price: Optional[int] = None
    quantity: Optional[int] = None

    def __post_init__(self):
        """생성 시 유효성 검증"""
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(f"strength must be between 0.0 and 1.0, got {self.strength}")

        if len(self.stock_code) != 6:
            raise ValueError(f"stock_code must be 6 digits, got {self.stock_code}")

    def is_strong(self) -> bool:
        """강한 시그널 여부 (시장가 주문 대상)"""
        return self.strength >= 0.8

    def is_actionable(self) -> bool:
        """주문 실행 가능 여부"""
        return self.action != Action.HOLD and self.strength >= 0.5

    def __str__(self) -> str:
        return (
            f"Signal({self.stock_name}[{self.stock_code}] "
            f"{self.action.value.upper()} "
            f"strength={self.strength:.2f} "
            f"reason='{self.reason}')"
        )

