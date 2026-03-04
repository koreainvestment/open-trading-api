"""강한 종가 전략.

Single Source of Truth:
- 진입: IBS (Internal Bar Strength)가 임계치 이상
- 청산: IBS가 임계치 미만

IBS = (Close - Low) / (High - Low)
→ 비율이 0.8 이상이면 종가가 당일 고가에 가까움 (강세)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from kis_backtest.strategies.base import BaseStrategy
from kis_backtest.strategies.registry import register
from kis_backtest.core.strategy import StrategyDefinition
from kis_backtest.core.condition import Condition
from kis_backtest.core.risk import RiskManagement
from kis_backtest.dsl.helpers import IBS


@register(
    "strong_close",
    name="강한 종가",
    category="momentum",
    description="종가가 당일 범위의 상위 N% 이내에 위치할 때 매수 (IBS 지표 활용)",
    tags=["momentum", "strong_close", "ibs"],
)
class StrongCloseStrategy(BaseStrategy):
    """강한 종가 전략

    Parameters:
        min_close_ratio: 최소 종가 비율 (default: 0.8)
            - 0.8 = 종가가 당일 범위의 상위 20% 이내
            - 0.9 = 종가가 당일 범위의 상위 10% 이내
        stop_loss_pct: 손절 비율 % (default: 5.0)

    Entry Condition (매수):
        IBS >= min_close_ratio
        → 종가가 당일 범위의 상위 구간에 위치하면 매수

    Exit Condition (매도):
        IBS < (1 - min_close_ratio)
        → 종가가 당일 범위의 하위 구간에 위치하면 매도

    Note:
        장마감 후(15:30 이후) 실행 권장
        - 장중에는 고가/저가/종가가 확정되지 않아 신호가 부정확할 수 있음
        - 데일리 바 기준으로만 사용
    """

    # PARAM_DEFINITIONS - Single Source of Truth
    PARAM_DEFINITIONS = {
        "min_close_ratio": {
            "default": 0.8,
            "min": 0.5,
            "max": 0.99,
            "type": "float",
            "description": "최소 종가 비율 (0~1)",
        },
        "stop_loss_pct": {
            "default": 5.0,
            "min": 1.0,
            "max": 15.0,
            "type": "float",
            "description": "손절 %",
        },
    }

    min_close_ratio: float = 0.8
    stop_loss_pct: float = 5.0

    def __init__(
        self,
        min_close_ratio: float = 0.8,
        stop_loss_pct: float = 5.0,
    ):
        self.min_close_ratio = min_close_ratio
        self.stop_loss_pct = stop_loss_pct

    @property
    def id(self) -> str:
        return "strong_close"

    @property
    def name(self) -> str:
        return "강한 종가"

    @property
    def category(self) -> str:
        return "momentum"

    @property
    def description(self) -> str:
        pct = int((1 - self.min_close_ratio) * 100)
        return f"종가가 당일 범위의 상위 {pct}% 이내일 때 매수 (IBS >= {self.min_close_ratio})"

    def indicators(self) -> list:
        """사용하는 지표 목록"""
        return [IBS(alias="ibs")]

    def entry_condition(self) -> Condition:
        """진입 조건: IBS >= min_close_ratio"""
        ibs = IBS(alias="ibs")
        return ibs >= self.min_close_ratio

    def exit_condition(self) -> Condition:
        """청산 조건: IBS < (1 - min_close_ratio)
        
        종가가 당일 범위의 하위 구간에 위치하면 매도
        예: min_close_ratio=0.8이면 IBS < 0.2일 때 매도
        """
        ibs = IBS(alias="ibs")
        exit_threshold = 1 - self.min_close_ratio
        return ibs < exit_threshold

    def risk_management(self) -> RiskManagement:
        """리스크 관리"""
        return RiskManagement(
            stop_loss_pct=self.stop_loss_pct,
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
        exit_threshold = 1 - self.min_close_ratio
        return {
            "ibs": {
                "lean_class": "InternalBarStrength",
                "init": "InternalBarStrength()",
                "value": "ibs.Current.Value",
                "warmup": 1,
            },
            "entry": {
                "type": "greater_equal",
                "indicator": "ibs",
                "threshold": self.min_close_ratio,
                "lean_condition": f"ibs >= {self.min_close_ratio}",
            },
            "exit": {
                "type": "less_than",
                "indicator": "ibs",
                "threshold": exit_threshold,
                "lean_condition": f"ibs < {exit_threshold}",
            },
        }
