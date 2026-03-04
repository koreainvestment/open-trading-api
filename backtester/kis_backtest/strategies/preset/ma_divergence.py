"""이동평균 이격도 전략.

Single Source of Truth:
- 진입: 종가/이동평균 비율 < 0.9 (침체, 분할매수)
- 청산: 종가/이동평균 비율 > 1.1 (과열, 차익실현)

⚠️ 이격도(Divergence Ratio) = Close / SMA
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
    "ma_divergence",
    name="이동평균 이격도",
    category="mean_reversion",
    description="종가/N일선 비율로 과열(>1.1) 차익실현, 침체(<0.9) 분할매수",
    tags=["mean_reversion", "divergence", "sma", "ratio"],
)
class MADivergenceStrategy(BaseStrategy):
    """이동평균 이격도 전략

    Parameters:
        period: 이동평균 기간 (default: 20)
        buy_ratio: 매수 이격도 (default: 0.9)
        sell_ratio: 매도 이격도 (default: 1.1)

    Entry Condition (매수):
        Close / SMA(period) < buy_ratio
        → 이격도가 0.9 이하면 침체로 판단하여 분할매수

    Exit Condition (매도):
        Close / SMA(period) > sell_ratio
        → 이격도가 1.1 이상이면 과열로 판단하여 차익실현

    Note:
        Lean에서는 직접 비율 계산 필요.
    """

    # PARAM_DEFINITIONS - Single Source of Truth
    PARAM_DEFINITIONS = {
        "period": {"default": 20, "min": 10, "max": 60, "type": "int", "description": "이동평균 기간"},
        "buy_ratio": {"default": 0.9, "min": 0.8, "max": 0.95, "type": "float", "description": "매수 이격도"},
        "sell_ratio": {"default": 1.1, "min": 1.05, "max": 1.2, "type": "float", "description": "매도 이격도"},
    }

    period: int = 20
    buy_ratio: float = 0.9
    sell_ratio: float = 1.1
    
    def __init__(
        self,
        period: int = 20,
        buy_ratio: float = 0.9,
        sell_ratio: float = 1.1,
    ):
        self.period = period
        self.buy_ratio = buy_ratio
        self.sell_ratio = sell_ratio
    
    @property
    def id(self) -> str:
        return "ma_divergence"
    
    @property
    def name(self) -> str:
        return "이동평균 이격도"
    
    @property
    def category(self) -> str:
        return "mean_reversion"
    
    @property
    def description(self) -> str:
        return f"이격도 < {self.buy_ratio} 매수, > {self.sell_ratio} 매도"
    
    def indicators(self) -> list:
        """사용하는 지표 목록"""
        return [SMA(self.period, alias="ma")]
    
    def entry_condition(self) -> Condition:
        """진입 조건: 가격이 이동평균 대비 N% 이상 하락"""
        # 이격도 < buy_ratio → Close < SMA * buy_ratio
        price = Price.close()
        ma = SMA(self.period, alias="ma")
        # 가격이 MA의 buy_ratio배 미만일 때 (예: 0.9 * MA)
        return price < ma * self.buy_ratio
    
    def exit_condition(self) -> Condition:
        """청산 조건: 가격이 이동평균 대비 N% 이상 상승"""
        # 이격도 > sell_ratio → Close > SMA * sell_ratio
        price = Price.close()
        ma = SMA(self.period, alias="ma")
        return price > ma * self.sell_ratio
    
    def risk_management(self) -> RiskManagement:
        """리스크 관리"""
        return RiskManagement()  # 별도 손절/익절 없음
    
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
            "ma": {
                "lean_class": "SimpleMovingAverage",
                "init": f"SimpleMovingAverage({self.period})",
                "value": "ma.Current.Value",
                "warmup": self.period,
            },
            "entry": {
                "type": "ratio_below",
                "price": "close",
                "indicator": "ma",
                "ratio": self.buy_ratio,
                "lean_condition": f"close / ma < {self.buy_ratio}",
            },
            "exit": {
                "type": "ratio_above",
                "price": "close",
                "indicator": "ma",
                "ratio": self.sell_ratio,
                "lean_condition": f"close / ma > {self.sell_ratio}",
            },
        }
