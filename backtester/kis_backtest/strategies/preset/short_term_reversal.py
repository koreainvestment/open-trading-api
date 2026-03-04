"""단기 반전 전략.

Single Source of Truth:
- 진입: 종가가 최근 N일 평균보다 M% 이상 낮음 (과매도)
- 청산: 종가가 최근 N일 평균보다 M% 이상 높음 (과매수)

⚠️ 평균 회귀 전략 - 단기 이격 활용
"""

from __future__ import annotations

from typing import Any, Dict

from kis_backtest.strategies.base import BaseStrategy
from kis_backtest.strategies.registry import register
from kis_backtest.core.strategy import StrategyDefinition
from kis_backtest.core.condition import Condition
from kis_backtest.core.risk import RiskManagement
from kis_backtest.dsl.helpers import SMA, Price


@register(
    "short_term_reversal",
    name="단기 반전",
    category="mean_reversion",
    description="종가가 N일 평균보다 M% 이상 낮으면 매수, M% 이상 높으면 매도",
    tags=["mean_reversion", "reversal", "short_term", "oversold"],
)
class ShortTermReversalStrategy(BaseStrategy):
    """단기 반전 전략

    Parameters:
        period: 평균 기간 (default: 5)
        threshold_pct: 이격 임계치 % (default: 3.0)
        stop_loss: 손절 비율 % (default: 5.0)

    Entry Condition (매수):
        Close < SMA(period) * (1 - threshold_pct/100)
        → 가격이 평균보다 M% 이상 낮으면 과매도로 판단

    Exit Condition (매도):
        Close > SMA(period) * (1 + threshold_pct/100)
        → 가격이 평균보다 M% 이상 높으면 과매수로 판단
    """

    # PARAM_DEFINITIONS - Single Source of Truth
    PARAM_DEFINITIONS = {
        "period": {"default": 5, "min": 3, "max": 20, "type": "int", "description": "평균 기간"},
        "threshold_pct": {"default": 3.0, "min": 1.0, "max": 10.0, "type": "float", "description": "이격 임계치 %"},
        "stop_loss_pct": {"default": 5.0, "min": 2, "max": 15, "type": "float", "description": "손절 %"},
    }

    period: int = 5
    threshold_pct: float = 3.0
    stop_loss_pct: float = 5.0
    
    def __init__(
        self,
        period: int = 5,
        threshold_pct: float = 3.0,
        stop_loss_pct: float = 5.0,
    ):
        self.period = period
        self.threshold_pct = threshold_pct
        self.stop_loss_pct = stop_loss_pct
    
    @property
    def id(self) -> str:
        return "short_term_reversal"
    
    @property
    def name(self) -> str:
        return "단기 반전"
    
    @property
    def category(self) -> str:
        return "mean_reversion"
    
    @property
    def description(self) -> str:
        return f"{self.period}일 평균 대비 {self.threshold_pct}% 이격 시 반전 매매"
    
    def indicators(self) -> list:
        """사용하는 지표 목록"""
        return [SMA(self.period, alias="ma")]
    
    def entry_condition(self) -> Condition:
        """진입 조건: 가격 < 평균 * (1 - threshold)"""
        price = Price.close()
        ma = SMA(self.period, alias="ma")
        # 가격이 MA의 (1 - threshold_pct/100)배 미만일 때
        multiplier = 1 - self.threshold_pct / 100
        return price < ma * multiplier
    
    def exit_condition(self) -> Condition:
        """청산 조건: 가격 > 평균 * (1 + threshold)"""
        price = Price.close()
        ma = SMA(self.period, alias="ma")
        # 가격이 MA의 (1 + threshold_pct/100)배 초과일 때
        multiplier = 1 + self.threshold_pct / 100
        return price > ma * multiplier
    
    def risk_management(self) -> RiskManagement:
        """리스크 관리"""
        return RiskManagement(
            stop_loss_pct=self.stop_loss_pct if self.stop_loss_pct > 0 else None,
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
        buy_mult = 1 - self.threshold_pct / 100
        sell_mult = 1 + self.threshold_pct / 100
        return {
            "ma": {
                "lean_class": "SimpleMovingAverage",
                "init": f"SimpleMovingAverage({self.period})",
                "value": "ma.Current.Value",
                "warmup": self.period,
            },
            "entry": {
                "type": "divergence_below",
                "price": "close",
                "indicator": "ma",
                "multiplier": buy_mult,
                "lean_condition": f"close < ma * {buy_mult}",
            },
            "exit": {
                "type": "divergence_above",
                "price": "close",
                "indicator": "ma",
                "multiplier": sell_mult,
                "lean_condition": f"close > ma * {sell_mult}",
            },
        }
