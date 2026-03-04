"""Preset Strategies.

Expert Sample 10종 전략 정의.
모든 전략은 StrategyRegistry에 자동 등록됩니다.
"""

# ========================================
# Expert Sample 10종 전략
# ========================================

# 1. SMA 골든/데드 크로스
from kis_backtest.strategies.preset.sma_crossover import SMACrossoverStrategy

# 2. 모멘텀
from kis_backtest.strategies.preset.momentum import MomentumStrategy

# 3. 52주 신고가 돌파
from kis_backtest.strategies.preset.week52_high import Week52HighStrategy

# 4. n일 연속 상승·하락
from kis_backtest.strategies.preset.consecutive_moves import ConsecutiveMovesStrategy

# 5. 이동평균 이격도
from kis_backtest.strategies.preset.ma_divergence import MADivergenceStrategy

# 6. 추세 돌파 후 이탈 (가짜 돌파)
from kis_backtest.strategies.preset.false_breakout import FalseBreakoutStrategy

# 7. 전일 대비 강한 종가 상승
from kis_backtest.strategies.preset.strong_close import StrongCloseStrategy

# 8. 변동성 축소 후 확장
from kis_backtest.strategies.preset.volatility_breakout import VolatilityBreakoutStrategy

# 9. 단기 반전
from kis_backtest.strategies.preset.short_term_reversal import ShortTermReversalStrategy

# 10. 추세 필터 + 시그널
from kis_backtest.strategies.preset.trend_filter_signal import TrendFilterSignalStrategy


__all__ = [
    "SMACrossoverStrategy",
    "MomentumStrategy",
    "Week52HighStrategy",
    "ConsecutiveMovesStrategy",
    "MADivergenceStrategy",
    "FalseBreakoutStrategy",
    "StrongCloseStrategy",
    "VolatilityBreakoutStrategy",
    "ShortTermReversalStrategy",
    "TrendFilterSignalStrategy",
]
