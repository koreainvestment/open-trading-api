"""모멘텀 전략.

Single Source of Truth:
- 진입: N일 수익률이 양수이고 상위 10% (절대 + 상대 모멘텀)
- 청산: 수익률이 음수이거나 하위 10%

다중 종목 비교 전략 - 단일 종목에서는 절대 모멘텀만 적용
"""

from __future__ import annotations

from typing import Any, Dict

from kis_backtest.strategies.base import BaseStrategy
from kis_backtest.strategies.registry import register
from kis_backtest.core.strategy import StrategyDefinition
from kis_backtest.core.condition import Condition
from kis_backtest.core.risk import RiskManagement
from kis_backtest.dsl.helpers import ROC


@register(
    "momentum",
    name="모멘텀",
    category="momentum",
    description="N일 수익률 기준으로 상위 종목 매수, 하위 종목 매도",
    tags=["momentum", "ranking", "relative", "absolute"],
)
class MomentumStrategy(BaseStrategy):
    """모멘텀 전략

    Parameters:
        lookback: 수익률 계산 기간 (default: 60)
        threshold: 진입 수익률 임계치 % (default: 0, 양수면 매수)
        stop_loss: 손절 비율 % (default: 10.0)

    Entry Condition (매수):
        ROC(lookback) > threshold
        → N일 수익률이 임계치보다 높으면 매수

    Exit Condition (매도):
        ROC(lookback) < -threshold
        → N일 수익률이 음의 임계치보다 낮으면 매도

    Note:
        다중 종목 랭킹은 상위 레이어(Portfolio)에서 처리.
        단일 종목에서는 절대 모멘텀(수익률 > 0)만 적용.
    """

    # PARAM_DEFINITIONS - Single Source of Truth
    PARAM_DEFINITIONS = {
        "lookback": {"default": 60, "min": 20, "max": 252, "type": "int", "description": "수익률 계산 기간"},
        "threshold": {"default": 0.0, "min": -10, "max": 10, "type": "float", "description": "진입 임계치 %"},
        "stop_loss_pct": {"default": 10.0, "min": 2, "max": 20, "type": "float", "description": "손절 %"},
    }

    lookback: int = 60
    threshold: float = 0.0
    stop_loss_pct: float = 10.0

    def __init__(
        self,
        lookback: int = 60,
        threshold: float = 0.0,
        stop_loss_pct: float = 10.0,
    ):
        self.lookback = lookback
        self.threshold = threshold
        self.stop_loss_pct = stop_loss_pct

    @property
    def id(self) -> str:
        return "momentum"

    @property
    def name(self) -> str:
        return "모멘텀"

    @property
    def category(self) -> str:
        return "momentum"

    @property
    def description(self) -> str:
        return f"{self.lookback}일 수익률 > {self.threshold}% 시 매수"

    def indicators(self) -> list:
        """사용하는 지표 목록"""
        return [ROC(self.lookback, alias="momentum")]

    def entry_condition(self) -> Condition:
        """진입 조건: 모멘텀 > 임계치"""
        roc = ROC(self.lookback, alias="momentum")
        return roc > self.threshold

    def exit_condition(self) -> Condition:
        """청산 조건: 모멘텀 < 음의 임계치"""
        roc = ROC(self.lookback, alias="momentum")
        return roc < -self.threshold

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
            metadata={
                "rebalance": "monthly",
                "multi_asset": True,
            },
        )

    def to_lean_params(self) -> Dict[str, Any]:
        """Lean 코드 생성용 파라미터"""
        return {
            "momentum": {
                "lean_class": "RateOfChangePercent",
                "init": f"RateOfChangePercent({self.lookback})",
                "value": "momentum.Current.Value",
                "warmup": self.lookback + 1,
            },
            "entry": {
                "type": "greater_than",
                "indicator": "momentum",
                "threshold": self.threshold,
                "lean_condition": f"momentum > {self.threshold}",
            },
            "exit": {
                "type": "less_than",
                "indicator": "momentum",
                "threshold": -self.threshold,
                "lean_condition": f"momentum < {-self.threshold}",
            },
        }
