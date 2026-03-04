"""Core domain models for KIS Backtest Strategy Framework."""

from kis_backtest.core.strategy import StrategyDefinition
from kis_backtest.core.indicator import (
    Indicator,
    INDICATOR_REGISTRY,
    get_indicator_info,
)
from kis_backtest.core.condition import (
    Condition,
    CompositeCondition,
)
from kis_backtest.core.risk import RiskManagement

# 스키마 기반 Single Source of Truth
from kis_backtest.core.schema import (
    StrategySchema,
    IndicatorSchema,
    ConditionSchema,
    CompositeConditionSchema,
    RiskSchema,
    OperatorType,
    PRICE_FIELDS,
    parse_condition,
    parse_indicators,
)
from kis_backtest.core.converters import (
    from_preset,
    from_yaml_file,
    from_definition,
    from_dict,
)

__all__ = [
    # 기존
    "StrategyDefinition",
    "Indicator",
    "INDICATOR_REGISTRY",
    "get_indicator_info",
    "Condition",
    "CompositeCondition",
    "RiskManagement",
    # 스키마
    "StrategySchema",
    "IndicatorSchema",
    "ConditionSchema",
    "CompositeConditionSchema",
    "RiskSchema",
    "OperatorType",
    "PRICE_FIELDS",
    "parse_condition",
    "parse_indicators",
    # 변환
    "from_preset",
    "from_yaml_file",
    "from_definition",
    "from_dict",
]
