"""Provider Protocol 정의

데이터 및 브로커리지 제공자의 추상 인터페이스.
한국투자증권 등 다양한 제공자로 교체 가능.
"""

from abc import abstractmethod
from datetime import date
from typing import Callable, List, Optional, Protocol, runtime_checkable

from ..models import (
    Bar,
    Quote,
    Order,
    Position,
    OrderSide,
    OrderType,
    OrderStatus,
    Resolution,
)
from ..models.trading import AccountBalance, Subscription
from ..models.market_data import StockInfo, FinancialData


@runtime_checkable
class DataProvider(Protocol):
    """데이터 제공자 인터페이스
    
    과거 데이터 조회, 실시간 데이터 구독, 종목 정보 조회.
    """
    
    @abstractmethod
    def get_history(
        self,
        symbol: str,
        start: date,
        end: date,
        resolution: Resolution = Resolution.DAILY
    ) -> List[Bar]:
        """과거 데이터 조회
        
        Args:
            symbol: 종목코드 (예: "005930", "AAPL")
            start: 시작일
            end: 종료일
            resolution: 해상도 (DAILY, MINUTE 등)
        
        Returns:
            Bar 리스트 (시간순 정렬)
        """
        ...
    
    @abstractmethod
    def get_quote(self, symbol: str) -> Quote:
        """현재 호가 조회
        
        Args:
            symbol: 종목코드
        
        Returns:
            Quote 객체
        """
        ...
    
    @abstractmethod
    def subscribe_realtime(
        self,
        symbols: List[str],
        on_bar: Callable[[str, Bar], None]
    ) -> Subscription:
        """실시간 데이터 구독
        
        Args:
            symbols: 종목코드 리스트
            on_bar: 데이터 수신 시 콜백
        
        Returns:
            Subscription (cancel 메서드로 해제)
        """
        ...
    
    def get_stock_info(self, symbol: str) -> Optional[StockInfo]:
        """종목 정보 조회 (선택)"""
        return None
    
    def get_financial_data(self, symbol: str) -> Optional[FinancialData]:
        """재무 데이터 조회 (선택)"""
        return None


@runtime_checkable
class BrokerageProvider(Protocol):
    """브로커리지 제공자 인터페이스
    
    주문 제출/취소/정정, 잔고 조회, 체결 통보.
    """
    
    @abstractmethod
    def submit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: int,
        order_type: OrderType = OrderType.MARKET,
        price: Optional[float] = None
    ) -> Order:
        """주문 제출
        
        Args:
            symbol: 종목코드
            side: 매수/매도
            quantity: 수량
            order_type: 시장가/지정가
            price: 지정가 (order_type=LIMIT일 때 필수)
        
        Returns:
            Order 객체
        
        Raises:
            KISOrderError: 주문 실패
        """
        ...
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """주문 취소
        
        Args:
            order_id: 주문번호
        
        Returns:
            성공 여부
        """
        ...
    
    @abstractmethod
    def modify_order(
        self,
        order_id: str,
        quantity: Optional[int] = None,
        price: Optional[float] = None
    ) -> Order:
        """주문 정정
        
        Args:
            order_id: 주문번호
            quantity: 변경할 수량 (None이면 유지)
            price: 변경할 가격 (None이면 유지)
        
        Returns:
            수정된 Order 객체
        """
        ...
    
    @abstractmethod
    def get_positions(self) -> List[Position]:
        """포지션 조회
        
        Returns:
            Position 리스트
        """
        ...
    
    @abstractmethod
    def get_balance(self) -> AccountBalance:
        """계좌 잔고 조회
        
        Returns:
            AccountBalance 객체
        """
        ...
    
    @abstractmethod
    def get_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        """주문 목록 조회
        
        Args:
            status: 필터할 상태 (None이면 전체)
        
        Returns:
            Order 리스트
        """
        ...
    
    @abstractmethod
    def subscribe_fills(
        self,
        on_fill: Callable[[Order], None]
    ) -> Subscription:
        """체결 통보 구독
        
        Args:
            on_fill: 체결 시 콜백
        
        Returns:
            Subscription (cancel 메서드로 해제)
        """
        ...
