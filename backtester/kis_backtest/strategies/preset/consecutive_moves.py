"""N일 연속 상승/하락 전략.

Single Source of Truth:
- 진입: N일 연속 종가 상승
- 청산: N일 연속 종가 하락

⚠️ 특수 로직 - 연속 상승/하락 카운트 필요
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
    "consecutive_moves",
    name="연속 상승·하락",
    category="momentum",
    description="N일 연속 종가 상승 시 매수, N일 연속 하락 시 매도",
    tags=["momentum", "consecutive", "streak"],
)
class ConsecutiveMovesStrategy(BaseStrategy):
    """연속 상승/하락 전략

    Parameters:
        up_days: 연속 상승일 (default: 5)
        down_days: 연속 하락일 (default: 5)
        stop_loss: 손절 비율 % (default: 5.0)

    Entry Condition (매수):
        N일 연속 종가 상승 (close[t] > close[t-1] for N days)

    Exit Condition (매도):
        N일 연속 종가 하락 (close[t] < close[t-1] for N days)

    Note:
        Lean에서는 RollingWindow를 사용하여 연속 상승/하락 추적.
        간단히 구현을 위해 ROC > 0 (당일 상승)을 기본 조건으로 사용.
    """

    # PARAM_DEFINITIONS - Single Source of Truth
    PARAM_DEFINITIONS = {
        "up_days": {"default": 5, "min": 2, "max": 10, "type": "int", "description": "연속 상승일"},
        "down_days": {"default": 5, "min": 2, "max": 10, "type": "int", "description": "연속 하락일"},
        "stop_loss_pct": {"default": 5.0, "min": 1, "max": 15, "type": "float", "description": "손절 %"},
    }

    up_days: int = 5
    down_days: int = 5
    stop_loss_pct: float = 5.0
    
    def __init__(
        self,
        up_days: int = 5,
        down_days: int = 5,
        stop_loss_pct: float = 5.0,
    ):
        self.up_days = up_days
        self.down_days = down_days
        self.stop_loss_pct = stop_loss_pct
    
    @property
    def id(self) -> str:
        return "consecutive_moves"
    
    @property
    def name(self) -> str:
        return "연속 상승·하락"
    
    @property
    def category(self) -> str:
        return "momentum"
    
    @property
    def description(self) -> str:
        return f"{self.up_days}일 연속 상승 시 매수, {self.down_days}일 연속 하락 시 매도"
    
    def indicators(self) -> list:
        """사용하는 지표 목록"""
        # 1일 변화율 지표 사용 (당일 vs 전일)
        return [ROC(1, alias="daily_change")]
    
    def entry_condition(self) -> Condition:
        """진입 조건: 당일 상승 (단순화)
        
        Note: 실제 N일 연속 상승은 Lean 코드에서 구현
        """
        roc = ROC(1, alias="daily_change")
        return roc > 0
    
    def exit_condition(self) -> Condition:
        """청산 조건: 당일 하락 (단순화)"""
        roc = ROC(1, alias="daily_change")
        return roc < 0
    
    def risk_management(self) -> RiskManagement:
        """리스크 관리"""
        return RiskManagement(
            stop_loss_pct=self.stop_loss_pct if self.stop_loss_pct > 0 else None,
        )

    def get_custom_lean_code(self) -> str:
        """연속 상승/하락 카운터 로직

        Lean OnData에서 지표 업데이트 후 삽입됩니다.
        """
        return f'''
            # 연속 상승/하락 카운터 초기화
            if symbol not in self.consecutive_up:
                self.consecutive_up[symbol] = 0
                self.consecutive_down[symbol] = 0

            prev_price = self.prev_values[symbol].get('price', price)

            if price > prev_price:
                self.consecutive_up[symbol] += 1
                self.consecutive_down[symbol] = 0
            elif price < prev_price:
                self.consecutive_down[symbol] += 1
                self.consecutive_up[symbol] = 0
            else:
                # 보합 - 연속 상승/하락 초기화
                pass

            # 커스텀 진입/청산 조건 오버라이드
            entry_signal = self.consecutive_up[symbol] >= {self.up_days}
            exit_signal = self.consecutive_down[symbol] >= {self.down_days}'''

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
                "custom_logic": True,  # 특수 로직 필요
            },
        )
    
    def to_lean_params(self) -> Dict[str, Any]:
        """Lean 코드 생성용 파라미터
        
        Lean에서는 RollingWindow로 연속 상승/하락 추적
        """
        return {
            "daily_change": {
                "lean_class": "RateOfChangePercent",
                "init": "RateOfChangePercent(1)",
                "value": "daily_change.Current.Value",
                "warmup": 2,
            },
            "custom_vars": {
                "consecutive_up": 0,
                "consecutive_down": 0,
                "prev_close": None,
            },
            "entry": {
                "type": "consecutive",
                "direction": "up",
                "days": self.up_days,
                "lean_condition": f"self.consecutive_up >= {self.up_days}",
            },
            "exit": {
                "type": "consecutive",
                "direction": "down",
                "days": self.down_days,
                "lean_condition": f"self.consecutive_down >= {self.down_days}",
            },
            "custom_logic": """
        # 연속 상승/하락 카운트
        if self.prev_close is not None:
            if close > self.prev_close:
                self.consecutive_up += 1
                self.consecutive_down = 0
            elif close < self.prev_close:
                self.consecutive_down += 1
                self.consecutive_up = 0
            else:
                self.consecutive_up = 0
                self.consecutive_down = 0
        self.prev_close = close
""",
        }
