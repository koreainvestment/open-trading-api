"""변동성 축소 후 확장 전략.

Single Source of Truth:
- 진입: ATR이 최근 N일 평균 대비 축소 후, 가격이 전일 대비 M% 이상 상승 (돌파)
- 청산: 손절 또는 ATR 급등 시

⚠️ 변동성 수축 → 확장 패턴 감지
"""

from __future__ import annotations

from typing import Any, Dict

from kis_backtest.strategies.base import BaseStrategy
from kis_backtest.strategies.registry import register
from kis_backtest.core.strategy import StrategyDefinition
from kis_backtest.core.condition import Condition
from kis_backtest.core.risk import RiskManagement
from kis_backtest.dsl.helpers import ATR, ROC, SMA


@register(
    "volatility_breakout",
    name="변동성 축소 후 확장",
    category="volatility",
    description="변동성이 축소된 후 급등 시 매수, 급락 시 매도",
    tags=["volatility", "atr", "breakout", "squeeze"],
)
class VolatilityBreakoutStrategy(BaseStrategy):
    """변동성 돌파 전략

    Parameters:
        atr_period: ATR 기간 (default: 10)
        lookback: 변동성 비교 기간 (default: 20)
        breakout_pct: 돌파 기준 % (default: 3.0)
        stop_loss: 손절 비율 % (default: 5.0)

    Entry Condition (매수):
        ATR < SMA(ATR, lookback) (변동성 축소)
        AND ROC(1) > breakout_pct (가격 돌파)

    Exit Condition (매도):
        ROC(1) < -breakout_pct (급락)
        OR 손절
    """

    # PARAM_DEFINITIONS - Single Source of Truth
    PARAM_DEFINITIONS = {
        "atr_period": {"default": 10, "min": 5, "max": 20, "type": "int", "description": "ATR 기간"},
        "lookback": {"default": 20, "min": 10, "max": 60, "type": "int", "description": "변동성 비교 기간"},
        "breakout_pct": {"default": 3.0, "min": 1.0, "max": 10.0, "type": "float", "description": "돌파 기준 %"},
        "stop_loss_pct": {"default": 5.0, "min": 2, "max": 15, "type": "float", "description": "손절 %"},
    }

    atr_period: int = 10
    lookback: int = 20
    breakout_pct: float = 3.0
    stop_loss_pct: float = 5.0
    
    def __init__(
        self,
        atr_period: int = 10,
        lookback: int = 20,
        breakout_pct: float = 3.0,
        stop_loss_pct: float = 5.0,
    ):
        self.atr_period = atr_period
        self.lookback = lookback
        self.breakout_pct = breakout_pct
        self.stop_loss_pct = stop_loss_pct
    
    @property
    def id(self) -> str:
        return "volatility_breakout"
    
    @property
    def name(self) -> str:
        return "변동성 축소 후 확장"
    
    @property
    def category(self) -> str:
        return "volatility"
    
    @property
    def description(self) -> str:
        return f"ATR 축소 + {self.breakout_pct}% 돌파 시 매수"
    
    def indicators(self) -> list:
        """사용하는 지표 목록"""
        return [
            ATR(self.atr_period, alias="atr"),
            ROC(1, alias="daily_return"),
        ]
    
    def entry_condition(self) -> Condition:
        """진입 조건: 변동성 축소 + 가격 돌파
        
        Note: 간단히 구현을 위해 당일 수익률 > breakout_pct만 사용.
        변동성 축소 조건은 Lean 코드에서 추가 구현.
        """
        roc = ROC(1, alias="daily_return")
        return roc > self.breakout_pct
    
    def exit_condition(self) -> Condition:
        """청산 조건: 급락"""
        roc = ROC(1, alias="daily_return")
        return roc < -self.breakout_pct
    
    def risk_management(self) -> RiskManagement:
        """리스크 관리"""
        return RiskManagement(
            stop_loss_pct=self.stop_loss_pct,
        )

    def get_custom_lean_code(self) -> str:
        """변동성 축소 후 확장 감지 로직

        ATR 히스토리를 추적하여 변동성 축소 여부를 판단합니다.
        """
        return f'''
            # ATR 히스토리 초기화
            if symbol not in self.atr_history:
                self.atr_history[symbol] = []

            # ATR 값 기록
            atr_value = atr
            self.atr_history[symbol].append(atr_value)
            if len(self.atr_history[symbol]) > {self.lookback}:
                self.atr_history[symbol].pop(0)

            # ATR 이동평균 계산
            if len(self.atr_history[symbol]) >= {self.lookback}:
                atr_ma = sum(self.atr_history[symbol]) / len(self.atr_history[symbol])

                # 변동성 축소 조건 추가
                volatility_squeeze = atr_value < atr_ma

                # 진입 조건: 변동성 축소 + 가격 돌파
                entry_signal = entry_signal and volatility_squeeze'''

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
                "custom_logic": True,  # 변동성 비교 로직 필요
            },
        )
    
    def to_lean_params(self) -> Dict[str, Any]:
        """Lean 코드 생성용 파라미터"""
        return {
            "atr": {
                "lean_class": "AverageTrueRange",
                "init": f"AverageTrueRange({self.atr_period}, MovingAverageType.Wilders)",
                "value": "atr.Current.Value",
                "warmup": self.atr_period,
            },
            "atr_avg": {
                "lean_class": "SimpleMovingAverage",
                "init": f"SimpleMovingAverage({self.lookback})",
                "value": "atr_avg.Current.Value",
                "warmup": self.lookback,
                "input": "atr",  # ATR 값을 입력으로 사용
            },
            "daily_return": {
                "lean_class": "RateOfChangePercent",
                "init": "RateOfChangePercent(1)",
                "value": "daily_return.Current.Value",
                "warmup": 2,
            },
            "entry": {
                "type": "volatility_breakout",
                "lean_condition": f"atr < atr_avg and daily_return > {self.breakout_pct}",
            },
            "exit": {
                "type": "less_than",
                "indicator": "daily_return",
                "threshold": -self.breakout_pct,
                "lean_condition": f"daily_return < {-self.breakout_pct}",
            },
        }
