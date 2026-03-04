"""추세 필터 + 시그널 결합 전략.

Single Source of Truth:
- 진입: 가격 > N일선 (상승 추세) AND 전일 대비 상승
- 청산: 가격 < N일선 (하락 추세) AND 전일 대비 하락

⚠️ 추세 + 모멘텀 복합 전략
"""

from __future__ import annotations

from typing import Any, Dict

from kis_backtest.strategies.base import BaseStrategy
from kis_backtest.strategies.registry import register
from kis_backtest.core.strategy import StrategyDefinition
from kis_backtest.core.condition import Condition, CompositeCondition
from kis_backtest.core.risk import RiskManagement
from kis_backtest.dsl.helpers import SMA, ROC, Price


@register(
    "trend_filter_signal",
    name="추세 필터 + 시그널",
    category="composite",
    description="N일선 위에서 전일 대비 상승 시 매수, N일선 아래에서 하락 시 매도",
    tags=["trend", "momentum", "composite", "filter"],
)
class TrendFilterSignalStrategy(BaseStrategy):
    """추세 필터 + 시그널 전략

    Parameters:
        trend_period: 추세 MA 기간 (default: 60)
        stop_loss: 손절 비율 % (default: 5.0)
        take_profit: 익절 비율 % (default: 10.0)

    Entry Condition (매수):
        Close > SMA(trend_period) (상승 추세)
        AND ROC(1) > 0 (전일 대비 상승)

    Exit Condition (매도):
        Close < SMA(trend_period) (하락 추세)
        AND ROC(1) < 0 (전일 대비 하락)
    """

    # PARAM_DEFINITIONS - Single Source of Truth
    PARAM_DEFINITIONS = {
        "trend_period": {"default": 60, "min": 20, "max": 200, "type": "int", "description": "추세 MA 기간"},
        "stop_loss_pct": {"default": 5.0, "min": 2, "max": 15, "type": "float", "description": "손절 %"},
        "take_profit_pct": {"default": 10.0, "min": 5, "max": 30, "type": "float", "description": "익절 %"},
    }

    trend_period: int = 60
    stop_loss_pct: float = 5.0
    take_profit_pct: float = 10.0
    
    def __init__(
        self,
        trend_period: int = 60,
        stop_loss_pct: float = 5.0,
        take_profit_pct: float = 10.0,
    ):
        self.trend_period = trend_period
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
    
    @property
    def id(self) -> str:
        return "trend_filter_signal"
    
    @property
    def name(self) -> str:
        return "추세 필터 + 시그널"
    
    @property
    def category(self) -> str:
        return "composite"
    
    @property
    def description(self) -> str:
        return f"{self.trend_period}일선 위 + 상승 시 매수"
    
    def indicators(self) -> list:
        """사용하는 지표 목록"""
        return [
            SMA(self.trend_period, alias="trend"),
            ROC(1, alias="daily_return"),
        ]
    
    def entry_condition(self) -> Condition:
        """진입 조건: 추세 상승 + 당일 상승"""
        price = Price.close()
        trend = SMA(self.trend_period, alias="trend")
        roc = ROC(1, alias="daily_return")
        
        # 가격 > 추세선 AND 당일 상승
        trend_up = price > trend
        momentum_up = roc > 0
        return trend_up & momentum_up
    
    def exit_condition(self) -> Condition:
        """청산 조건: 추세 하락 + 당일 하락"""
        price = Price.close()
        trend = SMA(self.trend_period, alias="trend")
        roc = ROC(1, alias="daily_return")
        
        # 가격 < 추세선 AND 당일 하락
        trend_down = price < trend
        momentum_down = roc < 0
        return trend_down & momentum_down
    
    def risk_management(self) -> RiskManagement:
        """리스크 관리"""
        return RiskManagement(
            stop_loss_pct=self.stop_loss_pct if self.stop_loss_pct > 0 else None,
            take_profit_pct=self.take_profit_pct if self.take_profit_pct > 0 else None,
        )
    
    def build(self) -> StrategyDefinition:
        """StrategyDefinition 빌드"""
        return StrategyDefinition(
            id=self.id,
            name=self.name,
            category=self.category,
            description=self.description,
            indicators=[ind.to_dict() for ind in self.indicators()],
            entry=self.entry_condition().to_dict(),
            exit=self.exit_condition().to_dict(),
            risk_management=self.risk_management().to_dict(),
            params=self._build_params(),  # PARAM_DEFINITIONS 기반
        )
    
    def to_lean_params(self) -> Dict[str, Any]:
        """Lean 코드 생성용 파라미터"""
        return {
            "trend": {
                "lean_class": "SimpleMovingAverage",
                "init": f"SimpleMovingAverage({self.trend_period})",
                "value": "trend.Current.Value",
                "warmup": self.trend_period,
            },
            "daily_return": {
                "lean_class": "RateOfChangePercent",
                "init": "RateOfChangePercent(1)",
                "value": "daily_return.Current.Value",
                "warmup": 2,
            },
            "entry": {
                "type": "composite_and",
                "conditions": [
                    "close > trend",
                    "daily_return > 0",
                ],
                "lean_condition": "close > trend and daily_return > 0",
            },
            "exit": {
                "type": "composite_and",
                "conditions": [
                    "close < trend",
                    "daily_return < 0",
                ],
                "lean_condition": "close < trend and daily_return < 0",
            },
        }
