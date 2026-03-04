"""SMA 골든/데드 크로스 전략.

Single Source of Truth:
- 진입: 단기 SMA가 장기 SMA를 상향 돌파 (골든크로스)
- 청산: 단기 SMA가 장기 SMA를 하향 돌파 (데드크로스)

⚠️ 교차(Cross) 조건 사용 - 단순 비교가 아님!
"""

from __future__ import annotations

from typing import Any, Dict

from kis_backtest.strategies.base import BaseStrategy
from kis_backtest.strategies.registry import register
from kis_backtest.core.strategy import StrategyDefinition
from kis_backtest.core.condition import Condition
from kis_backtest.core.risk import RiskManagement
from kis_backtest.dsl.helpers import SMA


@register(
    "sma_crossover",
    name="SMA 골든/데드 크로스",
    category="trend",
    description="단기 SMA가 장기 SMA를 상향 돌파하면 매수 (골든크로스), 하향 돌파하면 매도 (데드크로스)",
    tags=["sma", "trend", "crossover", "golden_cross", "death_cross"],
)
class SMACrossoverStrategy(BaseStrategy):
    """SMA 골든/데드 크로스 전략

    Parameters:
        fast_period: 단기 SMA 기간 (default: 5)
        slow_period: 장기 SMA 기간 (default: 20)
        stop_loss: 손절 비율 % (default: 5.0)
        take_profit: 익절 비율 % (default: 10.0)

    Entry Condition (매수):
        fast_sma.crosses_above(slow_sma)
        → 단기 SMA가 장기 SMA 아래에 있다가 위로 돌파

    Exit Condition (매도):
        fast_sma.crosses_below(slow_sma)
        → 단기 SMA가 장기 SMA 위에 있다가 아래로 돌파
    """

    # PARAM_DEFINITIONS - Single Source of Truth
    PARAM_DEFINITIONS = {
        "fast_period": {"default": 5, "min": 2, "max": 50, "type": "int", "description": "단기 SMA 기간"},
        "slow_period": {"default": 20, "min": 10, "max": 200, "type": "int", "description": "장기 SMA 기간"},
        "stop_loss_pct": {"default": 5.0, "min": 1, "max": 20, "type": "float", "description": "손절 %"},
        "take_profit_pct": {"default": 10.0, "min": 2, "max": 50, "type": "float", "description": "익절 %"},
    }

    fast_period: int = 5
    slow_period: int = 20
    stop_loss_pct: float = 5.0
    take_profit_pct: float = 10.0
    
    def __init__(
        self,
        fast_period: int = 5,
        slow_period: int = 20,
        stop_loss_pct: float = 5.0,
        take_profit_pct: float = 10.0,
    ):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
    
    @property
    def id(self) -> str:
        return "sma_crossover"
    
    @property
    def name(self) -> str:
        return "SMA 골든/데드 크로스"
    
    @property
    def category(self) -> str:
        return "trend"
    
    @property
    def description(self) -> str:
        return f"SMA({self.fast_period})가 SMA({self.slow_period})를 상향돌파 시 매수, 하향돌파 시 매도"
    
    def indicators(self) -> list:
        """사용하는 지표 목록"""
        return [
            SMA(self.fast_period, alias="sma_fast"),
            SMA(self.slow_period, alias="sma_slow"),
        ]
    
    def entry_condition(self) -> Condition:
        """진입 조건: 골든크로스 (단기 SMA > 장기 SMA 돌파)"""
        fast = SMA(self.fast_period, alias="sma_fast")
        slow = SMA(self.slow_period, alias="sma_slow")
        return fast.crosses_above(slow)
    
    def exit_condition(self) -> Condition:
        """청산 조건: 데드크로스 (단기 SMA < 장기 SMA 돌파)"""
        fast = SMA(self.fast_period, alias="sma_fast")
        slow = SMA(self.slow_period, alias="sma_slow")
        return fast.crosses_below(slow)
    
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
            "sma_fast": {
                "lean_class": "SimpleMovingAverage",
                "init": f"SimpleMovingAverage({self.fast_period})",
                "value": "sma_fast.Current.Value",
                "warmup": self.fast_period,
            },
            "sma_slow": {
                "lean_class": "SimpleMovingAverage",
                "init": f"SimpleMovingAverage({self.slow_period})",
                "value": "sma_slow.Current.Value",
                "warmup": self.slow_period,
            },
            "entry": {
                "type": "cross_above",
                "indicator1": "sma_fast",
                "indicator2": "sma_slow",
                # Lean 코드: prev_fast <= prev_slow and fast > slow
                "lean_condition": "self.prev_sma_fast <= self.prev_sma_slow and sma_fast > sma_slow",
            },
            "exit": {
                "type": "cross_below",
                "indicator1": "sma_fast",
                "indicator2": "sma_slow",
                # Lean 코드: prev_fast >= prev_slow and fast < slow
                "lean_condition": "self.prev_sma_fast >= self.prev_sma_slow and sma_fast < sma_slow",
            },
        }
