"""Unified Strategy Schema - Single Source of Truth.

모든 전략 입력(Python 프리셋, YAML 파일)을 표준화하는 Pydantic 스키마.
Generator, Loader, API 등 모든 컴포넌트가 이 스키마를 사용합니다.

핵심 원칙:
1. 단일 키 표준화 (operator, NOT event/type)
2. 타입 안전성 (Pydantic 검증)
3. 자동 정규화 (crosses_above → cross_above)
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

logger = logging.getLogger(__name__)

from pydantic import BaseModel, Field, field_validator, model_validator


class OperatorType(str, Enum):
    """조건 연산자 - 단일 정의
    
    모든 입력 형식(event, type, operator)을 이 Enum으로 통일합니다.
    """
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    CROSS_ABOVE = "cross_above"
    CROSS_BELOW = "cross_below"
    EQUAL = "equal"
    NOT_EQUAL = "not_equal"
    BREAKS = "breaks"
    BETWEEN = "between"


# 연산자 정규화 맵
OPERATOR_ALIASES = {
    # Python 프리셋에서 사용 (Condition.to_dict)
    "indicator_cross_above": OperatorType.CROSS_ABOVE,
    "indicator_cross_below": OperatorType.CROSS_BELOW,
    # 추가 별칭
    "crosses_above": OperatorType.CROSS_ABOVE,
    "crosses_below": OperatorType.CROSS_BELOW,
    "crossover": OperatorType.CROSS_ABOVE,
    "crossunder": OperatorType.CROSS_BELOW,
    ">": OperatorType.GREATER_THAN,
    "<": OperatorType.LESS_THAN,
    ">=": OperatorType.GREATER_EQUAL,
    "<=": OperatorType.LESS_EQUAL,
    "==": OperatorType.EQUAL,
    "!=": OperatorType.NOT_EQUAL,
    "not_equal": OperatorType.NOT_EQUAL,
    "breaks": OperatorType.BREAKS,
    "gt": OperatorType.GREATER_THAN,
    "lt": OperatorType.LESS_THAN,
    "gte": OperatorType.GREATER_EQUAL,
    "lte": OperatorType.LESS_EQUAL,
}


# 가격 예약어 (지표가 아닌 가격 데이터)
PRICE_FIELDS = frozenset({"close", "open", "high", "low", "volume", "price"})


class CandlestickSchema(BaseModel):
    """캔들스틱 패턴 스키마

    캔들스틱 패턴은 파라미터가 없고, 신호값(-1, 0, +1)을 반환합니다.

    Attributes:
        id: 패턴 ID (marubozu, doji, engulfing, ...)
        alias: 패턴 별칭 (참조용, 없으면 id 사용)
    """
    id: str = Field(..., description="패턴 ID (marubozu, doji, engulfing, ...)")
    alias: Optional[str] = Field(default=None, description="패턴 별칭 (참조용)")

    @model_validator(mode='after')
    def set_default_alias(self) -> 'CandlestickSchema':
        """alias가 없으면 id를 기본값으로"""
        if self.alias is None:
            self.alias = self.id
        return self


class IndicatorSchema(BaseModel):
    """지표 스키마

    지표의 모든 정보를 표준화합니다.

    Attributes:
        id: 지표 ID (sma, ema, rsi, macd, ...)
        alias: 지표 내부 키 (자동 생성, Python 식별자, 조건 참조용, 불변)
        name: 표시 이름 (사용자 입력, 특수문자·한글 허용, UI·리포트용)
        params: 지표 파라미터
        output: 출력값 (macd: value/signal/histogram, bollinger: middle/upper/lower)
    """
    id: str = Field(..., description="지표 ID (sma, ema, rsi, macd, ...)")
    alias: Optional[str] = Field(default=None, description="지표 내부 키 (참조용, 불변)")
    name: Optional[str] = Field(default=None, description="표시 이름 (UI·리포트용)")
    params: Dict[str, Any] = Field(default_factory=dict, description="지표 파라미터")
    output: str = Field(default="value", description="출력값")
    
    @field_validator('id')
    @classmethod
    def validate_indicator_id(cls, v: str) -> str:
        """지표 ID 검증"""
        # 가격 필드는 허용
        if v in PRICE_FIELDS:
            return v
        
        # 순환 import 방지 — 지표 레지스트리 검증은 loader.py에서 수행
        return v
    
    @model_validator(mode='after')
    def set_default_alias(self) -> 'IndicatorSchema':
        """alias가 없으면 id를 기본값으로"""
        if self.alias is None:
            self.alias = self.id
        return self
    
    def get_unique_key(self) -> str:
        """멀티 아웃풋 지표의 고유 키 (중복 초기화 방지)
        
        Returns:
            id + params 해시 (output은 제외)
        """
        params_str = str(sorted(self.params.items()))
        return f"{self.id}:{params_str}"


class ConditionSchema(BaseModel):
    """단일 조건 스키마

    두 지표 또는 지표와 상수를 비교하는 조건.
    캔들스틱 패턴의 신호(bullish/bearish/detected)도 지원.

    Attributes:
        operator: 비교 연산자 (표준화됨) - 캔들스틱 조건 시 None 가능
        indicator: 왼쪽 지표 alias 또는 가격 (close/open/high/low)
        indicator_output: 왼쪽 지표 출력값
        compare_to: 오른쪽 지표 alias (지표 비교 시) 또는 None
        compare_output: 오른쪽 지표 출력값
        compare_scalar: 오른쪽 지표에 적용할 스칼라 (예: MA * 0.9의 0.9)
        compare_operation: 스칼라 연산 종류 (mul, div)
        value: 비교 상수 (숫자 비교 시)
        candlestick: 캔들스틱 패턴 alias (캔들스틱 조건 시)
        signal: 캔들스틱 신호 타입 (bullish, bearish, detected)
    """
    operator: Optional[OperatorType] = Field(default=None, description="비교 연산자")
    indicator: str = Field(default="", description="왼쪽 지표 alias 또는 가격")
    indicator_output: str = Field(default="value", description="왼쪽 지표 출력값")
    compare_to: Optional[str] = Field(default=None, description="오른쪽 지표 alias")
    compare_output: str = Field(default="value", description="오른쪽 지표 출력값")
    compare_scalar: Optional[float] = Field(default=None, description="오른쪽 지표 스칼라/오프셋")
    compare_operation: Optional[str] = Field(default=None, description="연산 종류 (mul, div, add, sub)")
    value: Optional[float] = Field(default=None, description="비교 상수")
    candlestick: Optional[str] = Field(default=None, description="캔들스틱 패턴 alias")
    signal: Optional[str] = Field(default=None, description="캔들스틱 신호 (bullish, bearish, detected)")

    @field_validator('operator', mode='before')
    @classmethod
    def normalize_operator(cls, v: Any) -> Optional[OperatorType]:
        """다양한 입력 형식을 표준화

        - "crosses_above" → CROSS_ABOVE
        - "indicator_cross_above" → CROSS_ABOVE
        - ">" → GREATER_THAN
        - None → None (캔들스틱 조건용)
        """
        if v is None:
            return None

        if isinstance(v, OperatorType):
            return v

        if isinstance(v, str):
            v_lower = v.lower().strip()

            # 별칭 맵 확인
            if v_lower in OPERATOR_ALIASES:
                return OPERATOR_ALIASES[v_lower]

            # Enum 값으로 직접 변환 시도
            try:
                return OperatorType(v_lower)
            except ValueError:
                pass

            # "crosses_" → "cross_" 정규화
            normalized = v_lower.replace("crosses_", "cross_")
            try:
                return OperatorType(normalized)
            except ValueError:
                pass

        raise ValueError(f"Unknown operator: {v}")

    @model_validator(mode='after')
    def validate_comparison(self) -> 'ConditionSchema':
        """비교 대상 검증"""
        # 캔들스틱 조건은 signal만 있으면 됨
        if self.candlestick is not None:
            if self.signal is None:
                self.signal = "detected"  # 기본값: 패턴 감지
            # operator는 캔들스틱 조건에서 사용되지 않으므로 기본값 설정
            if self.operator is None:
                self.operator = OperatorType.GREATER_THAN  # 더미 값
            return self

        # 일반 조건: operator 필수
        if self.operator is None:
            raise ValueError("operator is required for non-candlestick conditions")

        # 일반 조건: compare_to 또는 value 중 하나 필요 (또는 compare_scalar)
        if self.compare_to is None and self.value is None and self.compare_scalar is None:
            raise ValueError("Either compare_to (indicator) or value (number) must be provided")
        return self

    def is_candlestick_condition(self) -> bool:
        """캔들스틱 조건인지"""
        return self.candlestick is not None
    
    def is_price_comparison(self) -> bool:
        """왼쪽이 가격 데이터인지"""
        return self.indicator in PRICE_FIELDS
    
    def is_cross_condition(self) -> bool:
        """교차 조건인지"""
        return self.operator in (OperatorType.CROSS_ABOVE, OperatorType.CROSS_BELOW)
    
    def is_scaled_comparison(self) -> bool:
        """오른쪽이 스케일된 지표인지 (예: MA * 0.9)"""
        return self.compare_scalar is not None


class CompositeConditionSchema(BaseModel):
    """복합 조건 스키마 (AND/OR)
    
    여러 조건을 논리 연산자로 결합합니다.
    
    Attributes:
        logic: 논리 연산자 (AND/OR)
        conditions: 조건 목록
    """
    logic: Literal["AND", "OR"] = Field(..., description="논리 연산자")
    conditions: List[Union[ConditionSchema, "CompositeConditionSchema"]] = Field(
        ..., description="조건 목록"
    )
    
    @field_validator('logic', mode='before')
    @classmethod
    def normalize_logic(cls, v: str) -> str:
        """논리 연산자 대문자 정규화"""
        if isinstance(v, str):
            return v.upper()
        return v


# 재귀 참조 해결
CompositeConditionSchema.model_rebuild()


class RiskSchema(BaseModel):
    """리스크 관리 스키마
    
    손절/익절/트레일링 스탑 설정을 표준화합니다.
    """
    stop_loss_pct: Optional[float] = Field(default=None, ge=0, le=100, description="손절 %")
    take_profit_pct: Optional[float] = Field(default=None, ge=0, le=100, description="익절 %")
    trailing_stop_pct: Optional[float] = Field(default=None, ge=0, le=100, description="트레일링 스탑 %")
    max_position_size: Optional[float] = Field(default=None, ge=0, le=1, description="최대 포지션 비율")
    
    def to_dict(self) -> Dict[str, Any]:
        """risk_management 딕셔너리 형식으로 변환 (하위 호환)"""
        result = {}
        
        if self.stop_loss_pct is not None:
            result["stop_loss"] = {"enabled": True, "percent": self.stop_loss_pct}
        
        if self.take_profit_pct is not None:
            result["take_profit"] = {"enabled": True, "percent": self.take_profit_pct}
        
        if self.trailing_stop_pct is not None:
            result["trailing_stop"] = {"enabled": True, "percent": self.trailing_stop_pct}
        
        if self.max_position_size is not None:
            result["max_position_size"] = self.max_position_size
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RiskSchema":
        """기존 risk_management 딕셔너리에서 생성
        
        지원 형식:
        1. {stop_loss: {enabled: true, percent: 5.0}, ...}
        2. {stop_loss_pct: 5.0, ...}
        """
        stop_loss = data.get("stop_loss", {})
        take_profit = data.get("take_profit", {})
        trailing_stop = data.get("trailing_stop", {})
        
        return cls(
            stop_loss_pct=(
                stop_loss.get("percent") if stop_loss.get("enabled")
                else data.get("stop_loss_pct")
            ),
            take_profit_pct=(
                take_profit.get("percent") if take_profit.get("enabled")
                else data.get("take_profit_pct")
            ),
            trailing_stop_pct=(
                trailing_stop.get("percent") if trailing_stop.get("enabled")
                else data.get("trailing_stop_pct")
            ),
            max_position_size=data.get("max_position_size"),
        )


class StrategySchema(BaseModel):
    """전략 스키마 - Single Source of Truth

    모든 전략 입력을 이 스키마로 통일합니다.
    Python 프리셋, YAML 파일 모두 이 형식으로 변환된 후 처리됩니다.

    Attributes:
        id: 전략 고유 ID
        name: 전략 이름
        category: 카테고리 (trend, momentum, volatility, ...)
        description: 전략 설명
        indicators: 사용 지표 목록
        candlesticks: 사용 캔들스틱 패턴 목록
        entry: 진입 조건
        exit: 청산 조건
        risk: 리스크 관리
        params: 사용자 조정 가능 파라미터
        metadata: 추가 메타데이터
    """
    id: str = Field(..., description="전략 ID")
    name: str = Field(..., description="전략 이름")
    category: str = Field(default="custom", description="카테고리")
    description: str = Field(default="", description="전략 설명")
    indicators: List[IndicatorSchema] = Field(..., description="사용 지표 목록")
    candlesticks: List[CandlestickSchema] = Field(default_factory=list, description="사용 캔들스틱 패턴 목록")
    entry: Union[ConditionSchema, CompositeConditionSchema] = Field(..., description="진입 조건")
    exit: Union[ConditionSchema, CompositeConditionSchema] = Field(..., description="청산 조건")
    risk: Optional[RiskSchema] = Field(default=None, description="리스크 관리")
    params: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="파라미터 정의")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="메타데이터")
    version: str = Field(default="1.0", description="버전")

    @model_validator(mode='after')
    def auto_populate_candlesticks(self) -> 'StrategySchema':
        """조건에서 참조된 캔들스틱 패턴 자동 추가

        YAML에서 candlesticks: 섹션 없이 조건에서 캔들스틱을 참조하면
        자동으로 candlesticks 목록에 추가합니다.

        예: entry.conditions에 candlestick: gravestone_doji_1 이 있으면
        candlesticks: [{id: gravestone_doji, alias: gravestone_doji_1}] 자동 추가
        """
        import re
        from kis_backtest.core.candlestick import CANDLESTICK_REGISTRY

        # 기존 캔들스틱 alias 수집
        existing_aliases = {cs.alias or cs.id for cs in self.candlesticks}

        def collect_candlestick_aliases(cond) -> set:
            """조건에서 캔들스틱 alias 수집"""
            aliases = set()
            if isinstance(cond, CompositeConditionSchema):
                for c in cond.conditions:
                    aliases |= collect_candlestick_aliases(c)
            elif isinstance(cond, ConditionSchema) and cond.candlestick:
                aliases.add(cond.candlestick)
            return aliases

        # entry/exit 조건에서 캔들스틱 alias 수집
        referenced_aliases = set()
        referenced_aliases |= collect_candlestick_aliases(self.entry)
        referenced_aliases |= collect_candlestick_aliases(self.exit)

        # 누락된 캔들스틱 추가
        for alias in referenced_aliases:
            if alias not in existing_aliases:
                # alias에서 base pattern ID 추출 (예: gravestone_doji_1 → gravestone_doji)
                pattern_id = self._extract_pattern_id(alias, CANDLESTICK_REGISTRY)
                if pattern_id:
                    self.candlesticks.append(CandlestickSchema(id=pattern_id, alias=alias))
                else:
                    # 패턴을 찾지 못하면 alias를 그대로 id로 사용 (에러 발생 유도)
                    self.candlesticks.append(CandlestickSchema(id=alias, alias=alias))

        return self

    @staticmethod
    def _extract_pattern_id(alias: str, registry: dict) -> Optional[str]:
        """alias에서 CANDLESTICK_REGISTRY에 있는 pattern ID 추출

        예:
        - gravestone_doji_1 → gravestone_doji
        - doji → doji
        - hammer_2 → hammer
        """
        import re

        # 정확히 일치하면 반환
        if alias in registry:
            return alias

        # _숫자 접미사 제거 후 확인 (예: gravestone_doji_1 → gravestone_doji)
        match = re.match(r'^(.+)_\d+$', alias)
        if match:
            base_id = match.group(1)
            if base_id in registry:
                return base_id

        # 찾지 못함
        return None

    def get_indicator_by_alias(self, alias: str) -> Optional[IndicatorSchema]:
        """별칭으로 지표 찾기"""
        for ind in self.indicators:
            if ind.alias == alias:
                return ind
        return None
    
    def get_unique_indicators(self) -> List[IndicatorSchema]:
        """중복 제거된 지표 목록 (같은 alias는 한 번만 초기화)

        alias가 같으면 같은 Lean 지표 객체를 공유합니다.
        alias가 다르면 각각 별도의 객체로 초기화합니다.
        (예: bb_upper, bb_lower → 각각 BollingerBands 초기화)
        """
        seen_aliases: set = set()
        result: List[IndicatorSchema] = []

        for ind in self.indicators:
            # 가격 필드는 제외
            if ind.id in PRICE_FIELDS:
                continue

            alias = ind.alias or ind.id
            if alias not in seen_aliases:
                seen_aliases.add(alias)
                result.append(ind)

        return result
    
    def collect_all_indicators(self) -> Dict[str, IndicatorSchema]:
        """모든 지표를 alias → IndicatorSchema 맵으로 수집 (first-wins 정책)"""
        result: Dict[str, IndicatorSchema] = {}
        for ind in self.indicators:
            alias = ind.alias or ind.id
            if alias in result:
                logger.warning(
                    f"중복 alias 감지: '{alias}' — 첫 번째 지표만 사용됩니다 "
                    f"(중복: id='{ind.id}')"
                )
                continue
            result[alias] = ind
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """하위 호환성: 기존 Dict 형식으로 변환"""
        def condition_to_dict(cond: Union[ConditionSchema, CompositeConditionSchema]) -> Dict[str, Any]:
            if isinstance(cond, CompositeConditionSchema):
                return {
                    "logic": cond.logic,
                    "conditions": [condition_to_dict(c) for c in cond.conditions],
                }
            else:
                return {
                    "event": cond.operator.value,  # 하위 호환: event 키 사용
                    "indicator": cond.indicator,
                    "output": cond.indicator_output,
                    "compare_to": cond.compare_to,
                    "compare_output": cond.compare_output,
                    "value": cond.value,
                }
        
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "indicators": [ind.model_dump() for ind in self.indicators],
            "candlesticks": [cs.model_dump() for cs in self.candlesticks],
            "entry": condition_to_dict(self.entry),
            "exit": condition_to_dict(self.exit),
            "risk_management": self.risk.to_dict() if self.risk else {},
            "params": self.params,
            "metadata": self.metadata,
            "version": self.version,
        }


# ============================================================
# 팩토리 함수
# ============================================================

def parse_condition(data: Dict[str, Any]) -> Union[ConditionSchema, CompositeConditionSchema]:
    """딕셔너리에서 조건 스키마 파싱

    지원 형식:
    1. Python 프리셋: {"event": "cross_above", "indicator": "...", ...}
    2. YAML 파일: {"operator": "cross_above", "indicator": "...", ...}
    3. 복합 조건: {"logic": "AND", "conditions": [...]}
    4. ScaledIndicator: {"compare_scalar": 0.9, "compare_operation": "mul", ...}
    5. 캔들스틱: {"candlestick": "marubozu_1", "signal": "bullish"}
    """
    # 복합 조건 확인
    if "logic" in data and "conditions" in data:
        return CompositeConditionSchema(
            logic=data["logic"],
            conditions=[parse_condition(c) for c in data["conditions"]],
        )

    # 캔들스틱 조건 확인
    if "candlestick" in data:
        return ConditionSchema(
            operator=OperatorType.GREATER_THAN,  # 캔들스틱은 > 0 (bullish) 또는 < 0 (bearish)
            indicator="",
            candlestick=data.get("candlestick"),
            signal=data.get("signal", "detected"),
        )

    # 단일 조건 - operator 키 우선, 없으면 event/type
    operator_value = (
        data.get("operator") or
        data.get("event") or
        data.get("type")
    )

    if not operator_value:
        raise ValueError(f"Condition missing operator/event/type: {data}")

    # output 필드 정규화 (YAML과 Python 모두 지원)
    indicator_output = data.get("indicator_output") or data.get("output", "value")
    compare_output = data.get("compare_output", "value")

    # ScaledIndicator 지원
    compare_scalar = data.get("compare_scalar")
    compare_operation = data.get("compare_operation")

    return ConditionSchema(
        operator=operator_value,
        indicator=data.get("indicator", ""),
        indicator_output=indicator_output,
        compare_to=data.get("compare_to"),
        compare_output=compare_output,
        compare_scalar=compare_scalar,
        compare_operation=compare_operation,
        value=data.get("value"),
    )


def parse_indicators(data: List[Dict[str, Any]]) -> List[IndicatorSchema]:
    """딕셔너리 리스트에서 지표 스키마 파싱"""
    result = []
    for ind_dict in data:
        result.append(IndicatorSchema(
            id=ind_dict.get("id", ""),
            alias=ind_dict.get("alias"),
            name=ind_dict.get("name"),
            params=ind_dict.get("params", {}),
            output=ind_dict.get("output", "value"),
        ))
    return result


