"""
프리셋 전략 자동 등록

이 패키지를 import하면 10개 전략이 StrategyRegistry에 자동 등록됩니다.
"""

from strategy_core.preset import (
    golden_cross,
    momentum,
    week52_high,
    consecutive,
    disparity,
    breakout_fail,
    strong_close,
    volatility,
    mean_reversion,
    trend_filter,
)
