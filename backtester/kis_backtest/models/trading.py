"""거래 관련 모델
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from .enums import OrderSide, OrderType, OrderStatus


class Order(BaseModel):
    """주문 정보"""
    
    id: str = Field(..., description="주문번호")
    symbol: str = Field(..., description="종목코드")
    side: OrderSide = Field(..., description="매수/매도")
    order_type: OrderType = Field(..., description="주문유형")
    quantity: int = Field(..., description="주문수량")
    price: Optional[float] = Field(None, description="주문가격 (지정가)")
    
    filled_quantity: int = Field(0, description="체결수량")
    average_price: float = Field(0.0, description="평균체결가")
    
    status: OrderStatus = Field(..., description="주문상태")
    
    created_at: datetime = Field(..., description="주문시간")
    updated_at: datetime = Field(..., description="최종수정시간")
    
    # 추가 정보
    pnl: Optional[float] = Field(None, description="실현손익")
    commission: Optional[float] = Field(None, description="수수료")
    
    @property
    def unfilled_quantity(self) -> int:
        """미체결수량"""
        return self.quantity - self.filled_quantity
    
    @property
    def is_filled(self) -> bool:
        """완전체결 여부"""
        return self.status == OrderStatus.FILLED
    
    @property
    def is_pending(self) -> bool:
        """대기 중 여부"""
        return self.status in (OrderStatus.PENDING, OrderStatus.SUBMITTED)
    
    @property
    def fill_rate(self) -> float:
        """체결률"""
        return self.filled_quantity / self.quantity if self.quantity > 0 else 0


class Position(BaseModel):
    """포지션 정보"""
    
    symbol: str = Field(..., description="종목코드")
    quantity: int = Field(..., description="보유수량")
    average_price: float = Field(..., description="평균매입가")
    current_price: float = Field(..., description="현재가")
    
    unrealized_pnl: float = Field(..., description="평가손익")
    unrealized_pnl_percent: float = Field(..., description="평가손익률 (%)")
    
    # 선택적 필드
    name: Optional[str] = Field(None, description="종목명")
    
    @property
    def market_value(self) -> float:
        """평가금액"""
        return self.quantity * self.current_price
    
    @property
    def cost_basis(self) -> float:
        """매입금액"""
        return self.quantity * self.average_price
    


class AccountBalance(BaseModel):
    """계좌 잔고"""
    
    # 현금
    total_cash: float = Field(..., description="총 예수금")
    available_cash: float = Field(..., description="주문가능금액")
    
    # 평가
    total_equity: float = Field(..., description="총 평가금액")
    total_pnl: float = Field(..., description="총 평가손익")
    total_pnl_percent: float = Field(..., description="총 평가손익률 (%)")
    
    # 통화
    currency: str = Field("KRW", description="통화")


class Subscription(BaseModel):
    """실시간 구독"""
    
    id: str = Field(..., description="구독 ID")
    symbols: list[str] = Field(..., description="구독 종목")
    is_active: bool = Field(True, description="활성 여부")
    

