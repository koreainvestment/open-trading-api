"""열거형 정의
"""

from enum import Enum


class Resolution(str, Enum):
    """데이터 해상도"""
    TICK = "tick"
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAILY = "daily"


class OrderSide(str, Enum):
    """주문 방향"""
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """주문 유형"""
    MARKET = "market"
    LIMIT = "limit"


class OrderStatus(str, Enum):
    """주문 상태"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class TimeInForce(str, Enum):
    """주문 유효 기간"""
    DAY = "day"  # 당일 유효
    GTC = "gtc"  # 취소될 때까지 유효 (Good Till Cancel)
    IOC = "ioc"  # 즉시 체결 또는 취소 (Immediate or Cancel)
    FOK = "fok"  # 전량 체결 또는 취소 (Fill or Kill)
