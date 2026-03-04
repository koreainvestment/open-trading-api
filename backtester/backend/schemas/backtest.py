"""Backtest API Schemas.

"""

from datetime import date
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class BacktestRequest(BaseModel):
    """백테스트 요청"""
    strategy_id: str = Field(..., description="전략 ID")
    symbols: List[str] = Field(..., description="종목 코드 리스트")
    start_date: Union[str, date] = Field(..., description="시작일 (YYYY-MM-DD)")
    end_date: Union[str, date] = Field(..., description="종료일 (YYYY-MM-DD)")
    initial_capital: float = Field(default=100_000_000, description="초기 자본")
    param_overrides: Optional[Dict[str, Any]] = Field(
        default=None,
        description="파라미터 오버라이드 (예: {'period': 21, 'oversold': 25})"
    )
    commission_rate: Optional[float] = Field(
        default=0.00015,
        description="수수료율 (기본 0.00015 = 0.015%)"
    )
    tax_rate: Optional[float] = Field(
        default=0.002,
        description="거래세율 (기본 0.002 = 0.2%, 매도 시)"
    )
    slippage: Optional[float] = Field(
        default=0.0,
        description="슬리피지 (기본 0 = 0%)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "strategy_id": "rsi_oversold",
                "symbols": ["005930", "000660"],
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "initial_capital": 100000000,
                "param_overrides": {"period": 21, "oversold": 25},
                "commission_rate": 0.00015,
                "tax_rate": 0.002,
                "slippage": 0.001,
            }
        }


class BacktestResponse(BaseModel):
    """백테스트 응답"""
    success: bool = True
    data: Dict[str, Any]
    message: Optional[str] = None
