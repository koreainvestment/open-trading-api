"""52주 신고가 돌파 전략.

Single Source of Truth:
- 진입: 종가가 52주(252거래일) 최고가를 상향 돌파
- 청산: 손절 기준 도달

⚠️ 돌파 조건 사용 - Maximum 지표 활용
"""

from __future__ import annotations

from typing import Any, Dict

from kis_backtest.strategies.base import BaseStrategy
from kis_backtest.strategies.registry import register
from kis_backtest.core.strategy import StrategyDefinition
from kis_backtest.core.condition import Condition
from kis_backtest.core.risk import RiskManagement
from kis_backtest.dsl.helpers import Maximum, Price


@register(
    "week52_high",
    name="52주 신고가 돌파",
    category="trend",
    description="당일 종가가 52주 최고가를 갱신하면 매수",
    tags=["trend", "breakout", "52week", "high"],
)
class Week52HighStrategy(BaseStrategy):
    """52주 신고가 돌파 전략

    Parameters:
        lookback: 최고가 계산 기간 (default: 252, 52주)
        stop_loss: 손절 비율 % (default: 5.0)
        take_profit: 익절 비율 % (default: 15.0)

    Entry Condition (매수):
        Price.close().crosses_above(Maximum(252))
        → 종가가 52주 최고가를 돌파할 때 매수

    Exit Condition (매도):
        손절 또는 익절 조건 도달
    """

    # PARAM_DEFINITIONS - Single Source of Truth
    PARAM_DEFINITIONS = {
        "lookback": {"default": 252, "min": 60, "max": 504, "type": "int", "description": "최고가 계산 기간"},
        "stop_loss_pct": {"default": 5.0, "min": 2, "max": 15, "type": "float", "description": "손절 %"},
        "take_profit_pct": {"default": 15.0, "min": 5, "max": 30, "type": "float", "description": "익절 %"},
    }

    lookback: int = 252
    stop_loss_pct: float = 5.0
    take_profit_pct: float = 15.0
    
    def __init__(
        self,
        lookback: int = 252,
        stop_loss_pct: float = 5.0,
        take_profit_pct: float = 15.0,
    ):
        self.lookback = lookback
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
    
    @property
    def id(self) -> str:
        return "week52_high"
    
    @property
    def name(self) -> str:
        return "52주 신고가 돌파"
    
    @property
    def category(self) -> str:
        return "trend"
    
    @property
    def description(self) -> str:
        return f"종가가 {self.lookback}일 최고가 돌파 시 매수"
    
    def indicators(self) -> list:
        """사용하는 지표 목록"""
        return [Maximum(self.lookback, alias="high52")]
    
    def entry_condition(self) -> Condition:
        """진입 조건: 종가 > 52주 최고가"""
        price = Price.close()
        high52 = Maximum(self.lookback, alias="high52")
        return price.crosses_above(high52)
    
    def exit_condition(self) -> Condition:
        """청산 조건: 손절/익절 (리스크 관리로 처리)"""
        # 별도 청산 조건 없음 - 손절/익절로 관리
        # 형식상 항상 False인 조건 반환
        high52 = Maximum(self.lookback, alias="high52")
        return high52 < 0  # 항상 False (가격은 음수가 될 수 없음)
    
    def risk_management(self) -> RiskManagement:
        """리스크 관리"""
        return RiskManagement(
            stop_loss_pct=self.stop_loss_pct,
            take_profit_pct=self.take_profit_pct,
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
            "high52": {
                "lean_class": "Maximum",
                "init": f"Maximum({self.lookback})",
                "value": "high52.Current.Value",
                "warmup": self.lookback,
            },
            "entry": {
                "type": "cross_above",
                "price": "close",
                "indicator": "high52",
                "lean_condition": "self.prev_close <= self.prev_high52 and close > high52",
            },
            "exit": {
                "type": "risk_management",
                "stop_loss_pct": self.stop_loss_pct,
                "take_profit_pct": self.take_profit_pct,
            },
        }
