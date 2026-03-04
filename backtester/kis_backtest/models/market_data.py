"""시장 데이터 모델
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Bar(BaseModel):
    """OHLCV 바 데이터"""
    
    time: datetime = Field(..., description="시간")
    open: float = Field(..., description="시가")
    high: float = Field(..., description="고가")
    low: float = Field(..., description="저가")
    close: float = Field(..., description="종가")
    volume: int = Field(..., description="거래량")
    
    @property
    def typical_price(self) -> float:
        """대표가 (HLC 평균)"""
        return (self.high + self.low + self.close) / 3
    
    @property
    def range(self) -> float:
        """고저 범위"""
        return self.high - self.low
    
    @property
    def body(self) -> float:
        """캔들 몸통 크기"""
        return abs(self.close - self.open)
    
    @property
    def is_bullish(self) -> bool:
        """양봉 여부"""
        return self.close > self.open


class Quote(BaseModel):
    """호가 데이터"""
    
    time: datetime = Field(..., description="시간")
    bid_price: float = Field(..., description="매수 1호가")
    bid_size: int = Field(..., description="매수 1호가 잔량")
    ask_price: float = Field(..., description="매도 1호가")
    ask_size: int = Field(..., description="매도 1호가 잔량")
    
    @property
    def spread(self) -> float:
        """스프레드 (매도-매수)"""
        return self.ask_price - self.bid_price
    
    @property
    def spread_percent(self) -> float:
        """스프레드 비율"""
        mid = (self.ask_price + self.bid_price) / 2
        return (self.spread / mid * 100) if mid > 0 else 0
    
    @property
    def mid_price(self) -> float:
        """중간가"""
        return (self.ask_price + self.bid_price) / 2

    @property
    def price(self) -> float:
        """현재가 (mid_price 별칭)"""
        return self.mid_price

    # 하위 호환성을 위한 별칭
    change: float = Field(default=0.0, description="전일대비")
    change_pct: float = Field(default=0.0, description="전일대비율")


class StockInfo(BaseModel):
    """종목 정보"""
    
    symbol: str = Field(..., description="종목코드")
    name: str = Field(..., description="종목명")
    market: str = Field(..., description="시장 (kospi, kosdaq, nasdaq 등)")
    sector: Optional[str] = Field(None, description="업종")
    
    # 기본 정보
    market_cap: Optional[float] = Field(None, description="시가총액")
    shares_outstanding: Optional[int] = Field(None, description="발행주식수")
    
    # 가격 정보
    prev_close: Optional[float] = Field(None, description="전일종가")
    price_limit_up: Optional[float] = Field(None, description="상한가")
    price_limit_down: Optional[float] = Field(None, description="하한가")


class IndexBar(BaseModel):
    """지수 OHLCV 바 데이터 (KOSPI, KOSDAQ 등)"""

    time: datetime = Field(..., description="시간")
    open: float = Field(..., description="시가")
    high: float = Field(..., description="고가")
    low: float = Field(..., description="저가")
    close: float = Field(..., description="종가")
    volume: int = Field(0, description="거래량")

    def to_lean_csv_line(self) -> str:
        """Lean CSV 형식으로 변환 (YYYYMMDD,open,high,low,close,volume)"""
        return (
            f"{self.time.strftime('%Y%m%d')},"
            f"{self.open},{self.high},{self.low},{self.close},{self.volume}"
        )


class FinancialData(BaseModel):
    """재무 데이터"""

    symbol: str = Field(..., description="종목코드")

    # 가치 지표
    per: Optional[float] = Field(None, description="PER")
    pbr: Optional[float] = Field(None, description="PBR")
    eps: Optional[float] = Field(None, description="EPS")
    bps: Optional[float] = Field(None, description="BPS")

    # 수익성
    roe: Optional[float] = Field(None, description="ROE (%)")
    roa: Optional[float] = Field(None, description="ROA (%)")

    # 배당
    dividend_yield: Optional[float] = Field(None, description="배당수익률 (%)")
