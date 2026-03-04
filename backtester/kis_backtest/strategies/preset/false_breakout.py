"""추세 돌파 후 이탈 전략 (가짜 돌파).

Single Source of Truth:
- 진입: 전고점(N일 최고가) 돌파
- 청산: M일 내 종가가 다시 전고점 아래로 이탈 (가짜 돌파)

⚠️ 특수 로직 - 진입 후 일정 기간 내 이탈 감지
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
    "false_breakout",
    name="추세 돌파 후 이탈",
    category="trend",
    description="전고점 돌파 후 N일 내 다시 이탈하면 손절 (가짜 돌파 포착)",
    tags=["trend", "breakout", "false_breakout", "reversal"],
)
class FalseBreakoutStrategy(BaseStrategy):
    """가짜 돌파 포착 전략

    Parameters:
        lookback: 전고점 계산 기간 (default: 20)
        exit_days: 이탈 확인 일수 (default: 3)
        stop_loss: 손절 비율 % (default: 3.0)

    Entry Condition (매수):
        Price.close().crosses_above(Maximum(lookback))
        → 종가가 N일 최고가를 돌파할 때 매수

    Exit Condition (매도):
        진입 후 M일 내 Close < Maximum(lookback)
        → 가짜 돌파로 판단하여 손절

    Note:
        실제 "M일 내" 로직은 Lean 코드에서 별도 구현 필요.
        기본 청산 조건은 가격 < 전고점으로 설정.
    """

    # PARAM_DEFINITIONS - Single Source of Truth
    PARAM_DEFINITIONS = {
        "lookback": {"default": 20, "min": 10, "max": 60, "type": "int", "description": "전고점 계산 기간"},
        "exit_days": {"default": 3, "min": 1, "max": 10, "type": "int", "description": "이탈 확인 일수"},
        "stop_loss_pct": {"default": 3.0, "min": 1, "max": 10, "type": "float", "description": "손절 %"},
    }

    lookback: int = 20
    exit_days: int = 3
    stop_loss_pct: float = 3.0
    
    def __init__(
        self,
        lookback: int = 20,
        exit_days: int = 3,
        stop_loss_pct: float = 3.0,
    ):
        self.lookback = lookback
        self.exit_days = exit_days
        self.stop_loss_pct = stop_loss_pct
    
    @property
    def id(self) -> str:
        return "false_breakout"
    
    @property
    def name(self) -> str:
        return "추세 돌파 후 이탈"
    
    @property
    def category(self) -> str:
        return "trend"
    
    @property
    def description(self) -> str:
        return f"{self.lookback}일 고점 돌파 후 {self.exit_days}일 내 이탈 시 손절"
    
    def indicators(self) -> list:
        """사용하는 지표 목록"""
        return [Maximum(self.lookback, alias="prev_high")]
    
    def entry_condition(self) -> Condition:
        """진입 조건: 전고점 돌파"""
        price = Price.close()
        prev_high = Maximum(self.lookback, alias="prev_high")
        return price.crosses_above(prev_high)
    
    def exit_condition(self) -> Condition:
        """청산 조건: 가격 < 전고점 (이탈)"""
        price = Price.close()
        prev_high = Maximum(self.lookback, alias="prev_high")
        return price < prev_high
    
    def risk_management(self) -> RiskManagement:
        """리스크 관리"""
        return RiskManagement(
            stop_loss_pct=self.stop_loss_pct,
        )

    def get_custom_lean_code(self) -> str:
        """가짜 돌파 감지 로직

        진입 후 M일 내 전고점 아래로 이탈하면 청산합니다.
        """
        return f'''
            # 진입 고점 추적 초기화
            if symbol not in self.entry_high:
                self.entry_high[symbol] = None
                self.entry_day[symbol] = None

            # 진입 시 고점 기록
            if holdings > 0:
                if self.entry_high[symbol] is None:
                    self.entry_high[symbol] = prev_high
                    self.entry_day[symbol] = self.Time

                # M일 내 이탈 확인
                days_since_entry = (self.Time - self.entry_day[symbol]).days
                if days_since_entry <= {self.exit_days}:
                    if price < self.entry_high[symbol]:
                        exit_signal = True  # 가짜 돌파 - 손절

            # 청산 시 초기화
            if holdings == 0:
                self.entry_high[symbol] = None
                self.entry_day[symbol] = None'''

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
        """Lean 코드 생성용 파라미터"""
        return {
            "prev_high": {
                "lean_class": "Maximum",
                "init": f"Maximum({self.lookback})",
                "value": "prev_high.Current.Value",
                "warmup": self.lookback,
            },
            "custom_vars": {
                "entry_day": None,
                "entry_high": None,
            },
            "entry": {
                "type": "cross_above",
                "price": "close",
                "indicator": "prev_high",
                "lean_condition": "self.prev_close <= self.prev_prev_high and close > prev_high",
            },
            "exit": {
                "type": "false_breakout",
                "days": self.exit_days,
                "lean_condition": f"self.days_since_entry <= {self.exit_days} and close < self.entry_high",
            },
            "custom_logic": """
        # 진입 시 기록
        if not self.Portfolio.Invested:
            self.entry_day = None
            self.entry_high = None
        elif self.entry_day is None:
            self.entry_day = self.Time
            self.entry_high = prev_high
        
        # 진입 후 일수 계산
        if self.entry_day is not None:
            self.days_since_entry = (self.Time - self.entry_day).days
""",
        }
