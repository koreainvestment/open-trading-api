"""
전략 모듈

기본 10개 전략 + 커스텀 전략이 포함됩니다.
strategy_builder로 새 전략을 생성하면 이 디렉토리에 파일이 추가됩니다.
"""

from strategy.base_strategy import BaseStrategy

# 기본 10개 전략
from strategy.strategy_01_golden_cross import GoldenCrossStrategy
from strategy.strategy_02_momentum import MomentumStrategy
from strategy.strategy_03_week52_high import Week52HighStrategy
from strategy.strategy_04_consecutive import ConsecutiveStrategy
from strategy.strategy_05_disparity import DisparityStrategy
from strategy.strategy_06_breakout_fail import BreakoutFailStrategy
from strategy.strategy_07_strong_close import StrongCloseStrategy
from strategy.strategy_08_volatility import VolatilityStrategy
from strategy.strategy_09_mean_reversion import MeanReversionStrategy
from strategy.strategy_10_trend_filter import TrendFilterStrategy

# 전략 매핑 (CLI용)
STRATEGY_MAP = {
    "golden_cross": GoldenCrossStrategy,
    "momentum": MomentumStrategy,
    "week52_high": Week52HighStrategy,
    "consecutive": ConsecutiveStrategy,
    "disparity": DisparityStrategy,
    "breakout_fail": BreakoutFailStrategy,
    "strong_close": StrongCloseStrategy,
    "volatility": VolatilityStrategy,
    "mean_reversion": MeanReversionStrategy,
    "trend_filter": TrendFilterStrategy,
}

__all__ = [
    "BaseStrategy",
    "GoldenCrossStrategy",
    "MomentumStrategy",
    "Week52HighStrategy",
    "ConsecutiveStrategy",
    "DisparityStrategy",
    "BreakoutFailStrategy",
    "StrongCloseStrategy",
    "VolatilityStrategy",
    "MeanReversionStrategy",
    "TrendFilterStrategy",
    "STRATEGY_MAP",
]
