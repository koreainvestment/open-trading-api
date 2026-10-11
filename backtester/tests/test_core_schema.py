import pytest
from pydantic import ValidationError

from kis_backtest.core.converters import from_dict
from kis_backtest.core.schema import (
    CompositeConditionSchema,
    ConditionSchema,
    IndicatorSchema,
    OperatorType,
    RiskSchema,
    parse_condition,
)


@pytest.mark.parametrize(
    ("alias", "expected"),
    [
        ("crosses_above", OperatorType.CROSS_ABOVE),
        (">=", OperatorType.GREATER_EQUAL),
        ("lt", OperatorType.LESS_THAN),
    ],
)
def test_condition_operator_aliases_are_normalized(alias, expected):
    condition = ConditionSchema(operator=alias, indicator="close", value=100)
    assert condition.operator is expected


def test_condition_requires_a_comparison_target():
    with pytest.raises(ValidationError, match="compare_to"):
        ConditionSchema(operator="greater_than", indicator="close")


def test_parse_nested_condition_normalizes_logic_and_operators():
    condition = parse_condition(
        {
            "logic": "and",
            "conditions": [
                {"event": "crosses_above", "indicator": "fast", "compare_to": "slow"},
                {"type": ">", "indicator": "close", "value": 100},
            ],
        }
    )
    assert isinstance(condition, CompositeConditionSchema)
    assert condition.logic == "AND"
    assert [item.operator for item in condition.conditions] == [
        OperatorType.CROSS_ABOVE,
        OperatorType.GREATER_THAN,
    ]


def test_risk_schema_round_trip_preserves_enabled_limits():
    source = {
        "stop_loss": {"enabled": True, "percent": 5.0},
        "take_profit": {"enabled": True, "percent": 12.5},
        "max_position_size": 0.25,
    }
    risk = RiskSchema.from_dict(source)
    assert risk.to_dict() == source


def test_from_dict_builds_strategy_and_deduplicates_indicator_aliases():
    strategy = from_dict(
        {
            "id": "regression",
            "name": "Regression strategy",
            "indicators": [
                {"id": "sma", "alias": "trend", "params": {"period": 20}},
                {"id": "ema", "alias": "trend", "params": {"period": 10}},
                {"id": "close"},
            ],
            "entry": {"operator": ">", "indicator": "close", "compare_to": "trend"},
            "exit": {"operator": "<", "indicator": "close", "compare_to": "trend"},
            "risk": {"stop_loss_pct": 4.0},
        }
    )

    assert strategy.get_unique_indicators() == [strategy.indicators[0]]
    assert strategy.collect_all_indicators()["trend"] == strategy.indicators[0]
    assert strategy.risk == RiskSchema(stop_loss_pct=4.0)


def test_indicator_defaults_alias_to_id():
    indicator = IndicatorSchema(id="rsi", params={"period": 14})
    assert indicator.alias == "rsi"
