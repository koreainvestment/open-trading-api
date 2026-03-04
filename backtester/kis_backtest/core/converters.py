"""Strategy Converters - 입력 표준화.

다양한 입력 형식을 StrategySchema로 변환합니다.

지원 입력:
1. Python 프리셋 (BaseStrategy 클래스)
2. YAML 파일 (KisStrategyFile)
3. StrategyDefinition (기존 데이터클래스)
4. Dict (API 요청)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from kis_backtest.core.schema import (
    CandlestickSchema,
    ConditionSchema,
    CompositeConditionSchema,
    IndicatorSchema,
    OperatorType,
    RiskSchema,
    StrategySchema,
    PRICE_FIELDS,
    parse_condition,
    parse_indicators,
)
from kis_backtest.core.param_resolver import ParamResolver

if TYPE_CHECKING:
    from kis_backtest.strategies.base import BaseStrategy
    from kis_backtest.core.strategy import StrategyDefinition
    from kis_backtest.core.condition import Condition, CompositeCondition
    from kis_backtest.file.schema import KisStrategyFile


def from_preset(strategy: "BaseStrategy") -> StrategySchema:
    """Python 프리셋 → StrategySchema 변환
    
    BaseStrategy 클래스 인스턴스를 표준 스키마로 변환합니다.
    
    Args:
        strategy: BaseStrategy 인스턴스
    
    Returns:
        StrategySchema
    
    Example:
        from kis_backtest.strategies.preset import MACDSignalStrategy
        
        strategy = MACDSignalStrategy(fast=12, slow=26, signal=9)
        schema = from_preset(strategy)
    """
    # 지표 변환
    indicators = _convert_indicators_from_preset(strategy.indicators())
    
    # 진입/청산 조건 변환
    entry = _convert_condition_from_preset(strategy.entry_condition())
    exit = _convert_condition_from_preset(strategy.exit_condition())
    
    # 리스크 관리 변환
    risk = _convert_risk_from_preset(strategy.risk_management())
    
    return StrategySchema(
        id=strategy.id,
        name=strategy.name,
        category=strategy.category,
        description=strategy.description,
        indicators=indicators,
        entry=entry,
        exit=exit,
        risk=risk,
        params=getattr(strategy, 'params', {}) if hasattr(strategy, 'params') else {},
    )


def from_yaml_file(
    strategy_file: "KisStrategyFile",
    param_overrides: Optional[Dict[str, Any]] = None,
) -> StrategySchema:
    """KisStrategyFile → StrategySchema 변환

    YAML 파일에서 로드된 KisStrategyFile을 표준 스키마로 변환합니다.
    $param_name 참조를 자동으로 해석합니다.

    Args:
        strategy_file: KisStrategyFile 인스턴스
        param_overrides: 파라미터 오버라이드 값 (선택)

    Returns:
        StrategySchema

    Example:
        # 기본값 사용
        schema = from_yaml_file(strategy_file)

        # 파라미터 오버라이드
        schema = from_yaml_file(strategy_file, {"period": 21, "oversold": 25})
    """
    params = strategy_file.strategy.params

    # 지표 변환 - $param_name 치환
    indicators = []
    for ind in strategy_file.strategy.indicators:
        # params에서 $param_name 참조 해석
        resolved_params = ParamResolver.resolve(ind.params, params, param_overrides)
        indicators.append(IndicatorSchema(
            id=ind.id,
            alias=ind.alias or ind.id,
            name=ind.name,  # 표시 이름 전달 (UI·리포트용)
            params=resolved_params,
            output=ind.output,
        ))

    # 캔들스틱 패턴 변환
    candlesticks = []
    if hasattr(strategy_file.strategy, 'candlesticks') and strategy_file.strategy.candlesticks:
        for candle in strategy_file.strategy.candlesticks:
            candlesticks.append(CandlestickSchema(
                id=candle.id,
                alias=candle.alias or candle.id,
            ))

    # 진입 조건 변환 - $param_name 치환
    entry = _convert_condition_group(strategy_file.strategy.entry, params, param_overrides)

    # 청산 조건 변환 - $param_name 치환
    exit = _convert_condition_group(strategy_file.strategy.exit, params, param_overrides)

    # 리스크 관리 변환
    risk = _convert_risk_from_yaml(strategy_file.risk)

    return StrategySchema(
        id=strategy_file.strategy.id,
        name=strategy_file.metadata.name,
        category=strategy_file.strategy.category,
        description=strategy_file.metadata.description,
        indicators=indicators,
        candlesticks=candlesticks,
        entry=entry,
        exit=exit,
        risk=risk,
        params=params,  # 원본 param 정의 유지
        metadata={
            "author": strategy_file.metadata.author,
            "tags": strategy_file.metadata.tags,
        },
        version=strategy_file.version,
    )


def from_definition(definition: "StrategyDefinition") -> StrategySchema:
    """StrategyDefinition → StrategySchema 변환
    
    기존 데이터클래스를 표준 스키마로 변환합니다.
    
    Args:
        definition: StrategyDefinition 인스턴스
    
    Returns:
        StrategySchema
    """
    # 지표 변환
    indicators = parse_indicators(definition.indicators)
    
    # 진입/청산 조건 변환
    entry = parse_condition(definition.entry)
    exit = parse_condition(definition.exit)
    
    # 리스크 관리 변환
    risk = RiskSchema.from_dict(definition.risk_management) if definition.risk_management else None
    
    return StrategySchema(
        id=definition.id,
        name=definition.name,
        category=definition.category,
        description=definition.description,
        indicators=indicators,
        entry=entry,
        exit=exit,
        risk=risk,
        params=definition.params,
        metadata=definition.metadata,
        version=definition.version,
    )


def from_dict(data: Dict[str, Any]) -> StrategySchema:
    """딕셔너리 → StrategySchema 변환
    
    API 요청 등에서 받은 딕셔너리를 표준 스키마로 변환합니다.
    
    Args:
        data: 전략 딕셔너리
    
    Returns:
        StrategySchema
    """
    # 지표 변환
    indicators = parse_indicators(data.get("indicators", []))
    
    # 진입/청산 조건 변환
    entry = parse_condition(data.get("entry", {}))
    exit = parse_condition(data.get("exit", {}))
    
    # 리스크 관리 변환
    risk_data = data.get("risk_management") or data.get("risk", {})
    risk = RiskSchema.from_dict(risk_data) if risk_data else None
    
    return StrategySchema(
        id=data.get("id", ""),
        name=data.get("name", ""),
        category=data.get("category", "custom"),
        description=data.get("description", ""),
        indicators=indicators,
        entry=entry,
        exit=exit,
        risk=risk,
        params=data.get("params", {}),
        metadata=data.get("metadata", {}),
        version=data.get("version", "1.0"),
    )


# ============================================================
# 내부 변환 함수
# ============================================================

def _convert_indicators_from_preset(indicators: list) -> List[IndicatorSchema]:
    """Python 프리셋 지표 변환
    
    Indicator 객체 리스트를 IndicatorSchema 리스트로 변환합니다.
    """
    result = []
    
    for ind in indicators:
        # Indicator 객체인 경우
        if hasattr(ind, 'id') and hasattr(ind, 'alias'):
            result.append(IndicatorSchema(
                id=ind.id,
                alias=ind.alias,
                params=ind.params if hasattr(ind, 'params') else {},
                output=ind.output if hasattr(ind, 'output') else "value",
            ))
        # Dict인 경우 (to_dict() 결과)
        elif isinstance(ind, dict):
            result.append(IndicatorSchema(
                id=ind.get("id", ""),
                alias=ind.get("alias"),
                params=ind.get("params", {}),
                output=ind.get("output", "value"),
            ))
    
    return result


def _convert_condition_from_preset(
    condition: Union["Condition", "CompositeCondition"]
) -> Union[ConditionSchema, CompositeConditionSchema]:
    """Python 프리셋 조건 변환
    
    Condition/CompositeCondition 객체를 스키마로 변환합니다.
    """
    from kis_backtest.core.condition import Condition, CompositeCondition
    
    if isinstance(condition, CompositeCondition):
        return CompositeConditionSchema(
            logic=condition.logic,
            conditions=[_convert_condition_from_preset(c) for c in condition.conditions],
        )
    
    # 왼쪽 피연산자 (Indicator)
    left = condition.left
    if hasattr(left, 'alias'):
        indicator = left.alias
        indicator_output = getattr(left, 'output', 'value')
    else:
        indicator = str(left)
        indicator_output = "value"
    
    # 오른쪽 피연산자 (Indicator 또는 숫자)
    right = condition.right
    compare_to: Optional[str] = None
    compare_output = "value"
    value: Optional[float] = None
    
    if hasattr(right, 'alias'):
        compare_to = right.alias
        compare_output = getattr(right, 'output', 'value')
    elif isinstance(right, (int, float)):
        value = float(right)
    
    # 연산자 변환
    operator = _normalize_operator(condition.operator)
    
    return ConditionSchema(
        operator=operator,
        indicator=indicator,
        indicator_output=indicator_output,
        compare_to=compare_to,
        compare_output=compare_output,
        value=value,
    )


def _convert_condition_group(
    group,
    params: Optional[Dict[str, Any]] = None,
    overrides: Optional[Dict[str, Any]] = None,
) -> Union[ConditionSchema, CompositeConditionSchema]:
    """YAML 조건 그룹 변환

    ConditionGroupConfig를 스키마로 변환합니다.
    $param_name 참조를 자동으로 해석합니다.

    Args:
        group: ConditionGroupConfig 객체
        params: 파라미터 정의 딕셔너리 (선택)
        overrides: 파라미터 오버라이드 값 (선택)
    """
    if not group.conditions:
        # 빈 조건 - 기본값 반환
        return ConditionSchema(
            operator=OperatorType.GREATER_THAN,
            indicator="price",
            value=0,
        )

    if len(group.conditions) == 1:
        # 단일 조건
        cond = group.conditions[0]
        return _convert_yaml_condition(cond, params, overrides)

    # 복합 조건
    return CompositeConditionSchema(
        logic=group.logic,
        conditions=[_convert_yaml_condition(c, params, overrides) for c in group.conditions],
    )


def _convert_yaml_condition(
    cond,
    params: Optional[Dict[str, Any]] = None,
    overrides: Optional[Dict[str, Any]] = None,
) -> ConditionSchema:
    """YAML 단일 조건 변환

    ConditionConfig를 ConditionSchema로 변환합니다.
    $param_name 참조를 자동으로 해석합니다.

    Args:
        cond: ConditionConfig 객체
        params: 파라미터 정의 딕셔너리 (선택)
        overrides: 파라미터 오버라이드 값 (선택)
    """
    params = params or {}

    # 캔들스틱 조건 처리
    if hasattr(cond, 'candlestick') and cond.candlestick:
        return ConditionSchema(
            candlestick=cond.candlestick,
            signal=getattr(cond, 'signal', None) or "detected",
        )

    # operator 정규화 (캔들스틱이 아닌 경우에만)
    operator = _normalize_operator(cond.operator) if cond.operator else OperatorType.GREATER_THAN

    # indicator - 가격 필드 처리
    indicator = cond.indicator or "price"
    indicator_output = cond.output or "value"

    # compare_to - 문자열이면 지표 또는 $param_name, 숫자면 value
    compare_to: Optional[str] = None
    compare_output = cond.compare_output or "value"
    value: Optional[float] = None

    if isinstance(cond.compare_to, str):
        # $param_name 참조 확인
        resolved = ParamResolver.resolve(cond.compare_to, params, overrides)
        if isinstance(resolved, (int, float)):
            value = float(resolved)
        else:
            compare_to = resolved
    elif isinstance(cond.compare_to, (int, float)):
        value = float(cond.compare_to)

    # cond.value가 있으면 우선 - $param_name 참조 해석
    if cond.value is not None:
        resolved_value = ParamResolver.resolve(cond.value, params, overrides)
        if isinstance(resolved_value, (int, float)):
            value = float(resolved_value)
        elif isinstance(resolved_value, str):
            # $param_name이 아닌 일반 문자열 (지표 alias 등)
            try:
                value = float(resolved_value)
            except ValueError:
                # 숫자로 변환 불가 - 그대로 유지 (예: 지표 alias)
                compare_to = resolved_value
                value = None
        compare_to = None if value is not None else compare_to

    compare_scalar = getattr(cond, 'compare_scalar', None)
    compare_operation = getattr(cond, 'compare_operation', None)

    return ConditionSchema(
        operator=operator,
        indicator=indicator,
        indicator_output=indicator_output,
        compare_to=compare_to,
        compare_output=compare_output,
        compare_scalar=compare_scalar,
        compare_operation=compare_operation,
        value=value,
    )


def _convert_risk_from_preset(risk) -> Optional[RiskSchema]:
    """Python 프리셋 리스크 변환"""
    if risk is None:
        return None
    
    # RiskManagement 객체인 경우
    if hasattr(risk, 'to_dict'):
        risk_dict = risk.to_dict()
    elif isinstance(risk, dict):
        risk_dict = risk
    else:
        return None
    
    return RiskSchema(
        stop_loss_pct=risk_dict.get("stop_loss_pct"),
        take_profit_pct=risk_dict.get("take_profit_pct"),
        trailing_stop_pct=risk_dict.get("trailing_stop_pct"),
        max_position_size=risk_dict.get("max_position_size"),
    )


def _convert_risk_from_yaml(risk) -> Optional[RiskSchema]:
    """YAML 리스크 변환"""
    if risk is None:
        return None
    
    # RiskConfig 객체인 경우
    stop_loss = getattr(risk, 'stop_loss', None)
    take_profit = getattr(risk, 'take_profit', None)
    trailing_stop = getattr(risk, 'trailing_stop', None)
    
    return RiskSchema(
        stop_loss_pct=(
            stop_loss.get("percent") 
            if stop_loss and stop_loss.get("enabled") 
            else None
        ),
        take_profit_pct=(
            take_profit.get("percent")
            if take_profit and take_profit.get("enabled")
            else None
        ),
        trailing_stop_pct=(
            trailing_stop.get("percent")
            if trailing_stop and trailing_stop.get("enabled")
            else None
        ),
        max_position_size=getattr(risk, 'max_position_size', None),
    )


def _normalize_operator(op: str) -> OperatorType:
    """연산자 문자열을 OperatorType으로 변환"""
    from kis_backtest.core.schema import OPERATOR_ALIASES
    
    if isinstance(op, OperatorType):
        return op
    
    op_lower = op.lower().strip()
    
    # 별칭 맵 확인
    if op_lower in OPERATOR_ALIASES:
        return OPERATOR_ALIASES[op_lower]
    
    # 직접 변환
    try:
        return OperatorType(op_lower)
    except ValueError:
        pass
    
    # "crosses_" → "cross_" 정규화
    normalized = op_lower.replace("crosses_", "cross_")
    try:
        return OperatorType(normalized)
    except ValueError:
        pass
    
    raise ValueError(f"Unknown operator: {op}")
