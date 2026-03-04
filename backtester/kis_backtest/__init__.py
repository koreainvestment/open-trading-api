"""KIS Backtest Library

QuantConnect Lean CLI를 Python 라이브러리로 래핑하고,
한국투자증권 API를 데이터/주문 제공자로 통합한 백테스팅 라이브러리.
"""

from kis_backtest.client import LeanClient
from kis_backtest.models import (
    Bar,
    Quote,
    Order,
    Position,
    OrderSide,
    OrderType,
    OrderStatus,
    Resolution,
    BacktestResult,
    OptimizationResult,
)
from kis_backtest.exceptions import (
    LeanError,
    ConfigurationError,
    AlgorithmError,
    DockerError,
    KISError,
    KISAuthError,
    KISOrderError,
)

# 전략 시스템
from kis_backtest.strategies import (
    STRATEGY_REGISTRY,
    StrategyRegistry,
    BaseStrategy,
    get_strategy,
    get_all_strategies,
    register,
    Condition,
    CompositeCondition,
    RiskManagement,
)
from kis_backtest.strategies.risk import PositionSizer, SizingMethod

# 코드 생성
from kis_backtest.codegen import LeanCodeGenerator, IndicatorValidator

# 파일 처리 (YAML)
from kis_backtest.file import StrategyFileLoader, StrategyFileSaver, PythonExporter

# DSL
from kis_backtest.dsl import RuleBuilder, StrategyRule
from kis_backtest.dsl.helpers import (
    SMA, EMA, WMA, TEMA, DEMA, KAMA,
    RSI, MACD, STOCH, ADX, CCI, MOMENTUM, ROC, WILLIAMS_R,
    ATR, BB, BollingerBands,
    OBV, VWAP,
    Price,
)

# Aliases for backward compatibility
MOM = MOMENTUM
WILLR = WILLIAMS_R

# Core schemas
from kis_backtest.core import (
    StrategySchema,
    IndicatorSchema,
    ConditionSchema,
    CompositeConditionSchema,
    RiskSchema,
    OperatorType,
    from_preset,
    from_yaml_file,
    from_dict,
)

# 포트폴리오 분석
from kis_backtest.portfolio import (
    PortfolioAnalyzer,
    PortfolioMetrics,
    RebalanceSimulator,
    RebalanceResult,
    PortfolioVisualizer,
)

__version__ = "1.0.0"
__all__ = [
    "LeanClient",
    # Models
    "Bar",
    "Quote",
    "Order",
    "Position",
    "OrderSide",
    "OrderType",
    "OrderStatus",
    "Resolution",
    "BacktestResult",
    "OptimizationResult",
    # Exceptions
    "LeanError",
    "ConfigurationError",
    "AlgorithmError",
    "DockerError",
    "KISError",
    "KISAuthError",
    "KISOrderError",
    # Strategies
    "STRATEGY_REGISTRY",
    "StrategyRegistry",
    "BaseStrategy",
    "get_strategy",
    "get_all_strategies",
    "register",
    "PositionSizer",
    "SizingMethod",
    # Code Generation
    "LeanCodeGenerator",
    "IndicatorValidator",
    # File (YAML)
    "StrategyFileLoader",
    "StrategyFileSaver",
    "PythonExporter",
    # Rule Builder / DSL
    "RuleBuilder",
    "StrategyRule",
    "Condition",
    "CompositeCondition",
    "RiskManagement",
    # Indicators
    "SMA", "EMA", "WMA", "TEMA", "DEMA", "KAMA",
    "RSI", "MACD", "STOCH", "ADX", "CCI", "MOMENTUM", "MOM", "ROC", "WILLIAMS_R", "WILLR",
    "ATR", "BB", "BollingerBands",
    "OBV", "VWAP",
    "Price",
    # Core schemas
    "StrategySchema",
    "IndicatorSchema",
    "ConditionSchema",
    "CompositeConditionSchema",
    "RiskSchema",
    "OperatorType",
    "from_preset",
    "from_yaml_file",
    "from_dict",
    # Portfolio Analysis
    "PortfolioAnalyzer",
    "PortfolioMetrics",
    "RebalanceSimulator",
    "RebalanceResult",
    "PortfolioVisualizer",
]
