"""전략 시스템

선언적 전략 정의 및 Lean 코드 생성.
"""

from kis_backtest.strategies.base import BaseStrategy
from kis_backtest.strategies.registry import StrategyRegistry, register, STRATEGY_REGISTRY

# Import all preset strategies to trigger registration
from kis_backtest.strategies.preset import (
    SMACrossoverStrategy,
    MomentumStrategy,
    Week52HighStrategy,
    ConsecutiveMovesStrategy,
    MADivergenceStrategy,
    FalseBreakoutStrategy,
    StrongCloseStrategy,
    VolatilityBreakoutStrategy,
    ShortTermReversalStrategy,
    TrendFilterSignalStrategy,
)

# Re-export DSL components from dsl module
from kis_backtest.dsl.builder import RuleBuilder, StrategyRule
from kis_backtest.dsl.helpers import (
    SMA,
    EMA,
    RSI,
    MACD,
    ATR,
    STOCH,
    ADX,
    CCI,
    BB,
    BollingerBands,
    Price,
    ROC,
    WMA,
    TEMA,
    DEMA,
    KAMA,
    MOMENTUM,
    WILLIAMS_R,
    OBV,
    VWAP,
)

# Aliases for backward compatibility
MOM = MOMENTUM
WILLR = WILLIAMS_R

# Re-export core components
from kis_backtest.core.condition import Condition, CompositeCondition
from kis_backtest.core.risk import RiskManagement


def get_strategy(strategy_id: str) -> BaseStrategy:
    """Get a strategy by ID."""
    return StrategyRegistry.get(strategy_id)


def get_all_strategies() -> list:
    """Get all registered strategies metadata."""
    return StrategyRegistry.list_all_with_params()


__all__ = [
    # Registry
    "STRATEGY_REGISTRY",
    "StrategyRegistry",
    "register",
    "BaseStrategy",
    "get_strategy",
    "get_all_strategies",
    # Rule Builder
    "RuleBuilder",
    "StrategyRule",
    # Core
    "Condition",
    "CompositeCondition",
    "RiskManagement",
    # Indicator factories
    "SMA",
    "EMA",
    "RSI",
    "MACD",
    "ATR",
    "STOCH",
    "ADX",
    "CCI",
    "BB",
    "BollingerBands",
    "Price",
    "ROC",
    "WMA",
    "TEMA",
    "DEMA",
    "KAMA",
    "MOMENTUM",
    "WILLIAMS_R",
    "MOM",  # alias
    "WILLR",  # alias
    "OBV",
    "VWAP",
    # Preset Strategies
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
