"""이슈 #23: 코드젠 검증/주입 방지 회귀 테스트 (오프라인)."""
import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from kis_backtest.codegen.validator import IndicatorValidator
from kis_backtest.core.indicator import INDICATOR_REGISTRY

INJECTION = "1, 1) if __import__('os').system('x') else AroonOscillator(1"


def _sample_value(rule):
    expected = rule.get("type")
    if expected is int:
        lo, hi = rule.get("min", 1), rule.get("max", 1000)
        return max(lo, min(hi, 14))
    if expected is float:
        lo, hi = rule.get("min", 0.0), rule.get("max", 1.0)
        mid = (lo + hi) / 2.0
        return max(lo, min(hi, mid if mid != 0 else lo))
    if expected is str:
        allowed = rule.get("allowed", [])
        return allowed[0] if allowed else "x"
    raise AssertionError(f"unsupported rule type: {expected!r}")


def test_unknown_param_rejected():
    result = IndicatorValidator.validate("sma", {"period": 14, "evil": 1})
    assert not result.is_valid
    assert any(e.param_name == "evil" for e in result.errors)
    with pytest.raises(ValueError):
        IndicatorValidator.get_lean_init_code("sma", {"period": 14, "evil": 1})


def test_injection_string_rejected():
    result = IndicatorValidator.validate(
        "aroon", {"up_period": INJECTION, "down_period": 25}
    )
    assert not result.is_valid
    with pytest.raises(ValueError):
        IndicatorValidator.get_lean_init_code(
            "aroon", {"up_period": INJECTION, "down_period": 25}
        )


def test_bool_rejected_for_numeric_rules():
    assert not IndicatorValidator.validate("sma", {"period": True}).is_valid
    assert not IndicatorValidator.validate(
        "bollinger", {"period": 20, "std": True}
    ).is_valid


def test_all_indicators_validate_with_rule_conformant_samples():
    missing_rules = []
    for indicator_id, info in INDICATOR_REGISTRY.items():
        params = {}
        for pname in info.params:
            rule = IndicatorValidator.PARAM_RULES.get(pname)
            if rule is None:
                missing_rules.append(f"{indicator_id}.{pname}")
                continue
            params[pname] = _sample_value(rule)
        if indicator_id == "macd":
            params.update({"fast": 12, "slow": 26, "signal": 9})
        result = IndicatorValidator.validate(indicator_id, params)
        assert result.is_valid, f"{indicator_id}: {[str(e) for e in result.errors]}"
    assert not missing_rules, f"params without rules: {missing_rules}"

def test_generated_init_code_numeric_shape():
    checked = 0
    for indicator_id, info in INDICATOR_REGISTRY.items():
        if indicator_id == "consecutive":
            continue  # 커스텀 카운터 템플릿("0")은 수치형 코드가 아님
        params = {}
        for pname in info.params:
            rule = IndicatorValidator.PARAM_RULES[pname]
            params[pname] = _sample_value(rule)
        if indicator_id == "macd":
            params.update({"fast": 12, "slow": 26, "signal": 9})
        code, _warmup = IndicatorValidator.get_lean_init_code(
            indicator_id, params, name="ind"
        )
        assert INJECTION not in code
        # 템플릿 상수(MovingAverageType.*, int(), 따옴표 변수명)를 제거하면
        # 괄호 안에는 숫자/구분자만 남아야 한다.
        scrubbed = re.sub(r"MovingAverageType\.\w+", "", code)
        scrubbed = re.sub(r'"[^"]*"', "", scrubbed)
        scrubbed = scrubbed.replace("int(", "(")
        for group in re.findall(r"\(([^()]*)\)", scrubbed):
            assert re.match(r"^[0-9., e+\-]*$", group), (
                f"{indicator_id}: letters inside parens: {group!r} in {code!r}"
            )
            assert "__" not in group and "import" not in group
        checked += 1
    assert checked > 0


def test_sma_code_matches_strict_shape():
    code, _ = IndicatorValidator.get_lean_init_code("sma", {"period": 14}, name="ind")
    assert re.match(r"^[\w.]+ = [\w.]+\([0-9., e+\-]*\)$", code), code


def test_bad_name_rejected():
    for bad in ["1abc", "a-b", "a b", "__import__('os')", "", "a;b", "한글"]:
        with pytest.raises(ValueError):
            IndicatorValidator.get_lean_init_code("sma", {"period": 14}, name=bad)


def test_safe_format_value():
    assert IndicatorValidator._safe_format_value("period", 14) == "14"
    assert IndicatorValidator._safe_format_value("std", 2) == "2.0"
    with pytest.raises(ValueError):
        IndicatorValidator._safe_format_value("period", True)
    with pytest.raises(ValueError):
        IndicatorValidator._safe_format_value("period", "14")
    with pytest.raises(ValueError):
        IndicatorValidator._safe_format_value("nope", 1)
    with pytest.raises(ValueError):
        IndicatorValidator._safe_format_value("direction", "sideways")
    assert IndicatorValidator._safe_format_value("direction", "up") == "up"
