"""Strategy File Schema.

.kis.yaml 파일의 Pydantic 스키마 정의.

"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class StrategyMetadata(BaseModel):
    """전략 메타데이터"""
    name: str = Field(..., description="전략 이름")
    description: str = Field(default="", description="전략 설명")
    author: str = Field(default="user", description="작성자")
    created_at: Optional[datetime] = Field(default=None, description="생성일시")
    updated_at: Optional[datetime] = Field(default=None, description="수정일시")
    tags: List[str] = Field(default_factory=list, description="태그 목록")
    

class IndicatorConfig(BaseModel):
    """지표 설정"""
    id: str = Field(..., description="지표 ID (sma, rsi, macd 등)")
    alias: Optional[str] = Field(default=None, description="지표 내부 키 (Python 식별자, 조건 참조용)")
    name: Optional[str] = Field(default=None, description="사용자 표시 이름 (자유 입력, 리포트·UI 표시용)")
    params: Dict[str, Any] = Field(default_factory=dict, description="지표 파라미터")
    output: str = Field(default="value", description="출력값 (macd: value, signal, histogram)")


class ConditionConfig(BaseModel):
    """조건 설정"""
    indicator: Optional[str] = Field(default=None, description="지표 별칭")
    operator: Optional[str] = Field(default=None, description="연산자 (greater_than, less_than, cross_above, cross_below)")
    compare_to: Optional[Union[str, float, int]] = Field(default=None, description="비교 대상 (지표 별칭 또는 숫자)")
    value: Optional[Union[str, float, int]] = Field(default=None, description="비교 값 (숫자 또는 $param_name 참조)")
    output: Optional[str] = Field(default=None, description="지표 출력값")
    compare_output: Optional[str] = Field(default=None, description="비교 지표 출력값")
    compare_scalar: Optional[float] = Field(default=None, description="비교 지표 스칼라/오프셋 (예: 0.9, 1000)")
    compare_operation: Optional[str] = Field(default=None, description="연산 종류 (mul, div, add, sub)")
    # 캔들스틱 조건용 필드
    candlestick: Optional[str] = Field(default=None, description="캔들스틱 패턴 별칭")
    signal: Optional[str] = Field(default=None, description="캔들스틱 시그널 (bullish, bearish, detected)")


class ConditionGroupConfig(BaseModel):
    """조건 그룹 설정"""
    logic: Literal["AND", "OR"] = Field(default="AND", description="조건 결합 로직")
    conditions: List[ConditionConfig] = Field(default_factory=list, description="조건 목록")


class RiskConfig(BaseModel):
    """리스크 관리 설정"""
    stop_loss: Optional[Dict[str, Any]] = Field(
        default=None,
        description="손절 설정 {enabled: bool, percent: float}"
    )
    take_profit: Optional[Dict[str, Any]] = Field(
        default=None,
        description="익절 설정 {enabled: bool, percent: float}"
    )
    trailing_stop: Optional[Dict[str, Any]] = Field(
        default=None,
        description="트레일링 스탑 {enabled: bool, percent: float}"
    )
    max_position_size: Optional[float] = Field(
        default=None,
        description="최대 포지션 크기 (비율)"
    )
    
    def to_risk_management_dict(self) -> Dict[str, Any]:
        """RiskManagement 형식으로 변환"""
        result = {}
        
        if self.stop_loss and self.stop_loss.get("enabled"):
            result["stop_loss_pct"] = self.stop_loss.get("percent")
        
        if self.take_profit and self.take_profit.get("enabled"):
            result["take_profit_pct"] = self.take_profit.get("percent")
        
        if self.trailing_stop and self.trailing_stop.get("enabled"):
            result["trailing_stop_pct"] = self.trailing_stop.get("percent")
        
        if self.max_position_size:
            result["max_position_size"] = self.max_position_size
        
        return result


class CandlestickConfig(BaseModel):
    """캔들스틱 패턴 설정"""
    id: str = Field(..., description="패턴 ID (doji, hammer, engulfing 등)")
    alias: Optional[str] = Field(default=None, description="패턴 별칭")


class StrategyConfig(BaseModel):
    """전략 설정"""
    id: str = Field(..., description="전략 고유 ID")
    category: str = Field(
        default="custom",
        description="카테고리 (trend, momentum, mean_reversion, volatility, oscillator, composite)"
    )
    indicators: List[IndicatorConfig] = Field(
        default_factory=list,
        description="사용 지표 목록"
    )
    candlesticks: List[CandlestickConfig] = Field(
        default_factory=list,
        description="사용 캔들스틱 패턴 목록"
    )
    entry: ConditionGroupConfig = Field(
        default_factory=lambda: ConditionGroupConfig(logic="AND", conditions=[]),
        description="진입 조건"
    )
    exit: ConditionGroupConfig = Field(
        default_factory=lambda: ConditionGroupConfig(logic="OR", conditions=[]),
        description="청산 조건"
    )
    params: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="파라미터 정의"
    )

    # $param_name 패턴 (전체 문자열이 $로 시작하는 파라미터 참조인 경우)
    _PARAM_PATTERN = re.compile(r'^\$([a-zA-Z_][a-zA-Z0-9_]*)$')

    @model_validator(mode='before')
    @classmethod
    def auto_fill_aliases(cls, values: dict) -> dict:
        """alias 없는 지표에 {id}_{counter} 패턴으로 자동 생성 (frontend와 동일 패턴)

        같은 id를 가진 지표가 여러 개일 때 alias 없이 YAML을 작성해도
        sma_1, sma_2 형태로 자동 부여하여 중복 에러를 방지합니다.
        """
        if not isinstance(values, dict):
            return values
        id_counters: dict = {}
        for ind in values.get('indicators', []):
            if isinstance(ind, dict) and not ind.get('alias'):
                ind_id = ind.get('id', '')
                id_counters[ind_id] = id_counters.get(ind_id, 0) + 1
                ind['alias'] = f"{ind_id}_{id_counters[ind_id]}"
        for cs in values.get('candlesticks', []):
            if isinstance(cs, dict) and not cs.get('alias'):
                cs_id = cs.get('id', '')
                id_counters[cs_id] = id_counters.get(cs_id, 0) + 1
                cs['alias'] = f"{cs_id}_{id_counters[cs_id]}"
        return values

    @model_validator(mode='after')
    def validate_unique_aliases(self) -> 'StrategyConfig':
        """auto_fill 후 중복 검증 (auto_fill이 먼저 실행되어 중복 거의 없음)"""
        seen: set = set()
        for ind in self.indicators:
            alias = ind.alias  # auto_fill_aliases가 이미 채워준 상태
            if alias in seen:
                raise ValueError(f"중복된 indicator alias: '{alias}'")
            seen.add(alias)
        for cs in self.candlesticks:
            alias = cs.alias  # auto_fill_aliases가 이미 채워준 상태
            if alias in seen:
                raise ValueError(f"중복된 candlestick alias: '{alias}'")
            seen.add(alias)
        return self

    @model_validator(mode='after')
    def validate_param_references(self) -> 'StrategyConfig':
        """$param_name 참조 검증

        indicators의 params와 conditions의 value에서 $param_name 참조가
        params 딕셔너리에 정의되어 있는지 검증합니다.
        """
        available = set(self.params.keys())

        def check(value: Any, context: str) -> None:
            """값에서 $param_name 참조 검증"""
            if isinstance(value, str):
                match = self._PARAM_PATTERN.match(value)
                if match:
                    param_name = match.group(1)
                    if param_name not in available:
                        raise ValueError(f"{context}: Unknown param ${param_name}")
            elif isinstance(value, dict):
                for k, v in value.items():
                    check(v, f"{context}.{k}")
            elif isinstance(value, list):
                for i, v in enumerate(value):
                    check(v, f"{context}[{i}]")

        # indicators의 params 검증
        for ind in self.indicators:
            for k, v in ind.params.items():
                check(v, f"indicators[{ind.alias or ind.id}].params.{k}")

        # entry/exit conditions의 value 검증
        for cond in self.entry.conditions:
            if cond.value is not None:
                check(cond.value, f"entry.conditions[].value")
            if cond.compare_to is not None:
                check(cond.compare_to, f"entry.conditions[].compare_to")

        for cond in self.exit.conditions:
            if cond.value is not None:
                check(cond.value, f"exit.conditions[].value")
            if cond.compare_to is not None:
                check(cond.compare_to, f"exit.conditions[].compare_to")

        return self


class KisStrategyFile(BaseModel):
    """KIS 전략 파일 (.kis.yaml)

    전략 파일의 전체 구조를 정의합니다.

    Example:
        ```yaml
        version: "1.0"
        metadata:
          name: "내 골든크로스 전략"
          description: "단기 이평이 장기 이평 돌파 시 매수"
          author: "user"
          tags: ["trend", "sma"]

        strategy:
          id: my_golden_cross
          category: trend
          indicators:
            - id: sma
              alias: fast
              params: { period: 5 }
            - id: sma
              alias: slow
              params: { period: 20 }
          entry:
            logic: AND
            conditions:
              - indicator: fast
                operator: cross_above
                compare_to: slow
          exit:
            logic: OR
            conditions:
              - indicator: fast
                operator: cross_below
                compare_to: slow

        risk:
          stop_loss: { enabled: true, percent: 5.0 }
          take_profit: { enabled: true, percent: 15.0 }
          trailing_stop: { enabled: false }
        ```
    """
    version: str = Field(default="1.0", description="파일 버전")
    metadata: StrategyMetadata = Field(..., description="전략 메타데이터")
    strategy: StrategyConfig = Field(..., description="전략 설정")
    risk: Optional[RiskConfig] = Field(
        default=None,
        description="리스크 관리 설정"
    )

    @field_validator("risk", mode="before")
    @classmethod
    def default_risk_config(cls, v):
        """None이면 기본 RiskConfig 반환"""
        if v is None:
            return RiskConfig()
        return v
    
    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """버전 형식 검증"""
        if not v or not v.replace(".", "").isdigit():
            raise ValueError(f"Invalid version format: {v}")
        return v
    
    def to_strategy_definition(self):
        """StrategyDefinition으로 변환"""
        from kis_backtest.core.strategy import StrategyDefinition
        
        # 지표 변환 (auto_fill_aliases가 이미 alias를 채워준 상태)
        indicators = [
            {
                "id": ind.id,
                "alias": ind.alias,
                "name": ind.name,
                "params": ind.params,
                "output": ind.output,
            }
            for ind in self.strategy.indicators
        ]
        
        # 진입 조건 변환 - operator 키를 event 키로도 추가 (하위 호환)
        entry = {
            "logic": self.strategy.entry.logic,
            "conditions": [
                {
                    **cond.model_dump(exclude_none=True),
                    "event": cond.operator,  # 하위 호환: event 키 추가
                }
                for cond in self.strategy.entry.conditions
            ],
        }
        
        # 청산 조건 변환 - operator 키를 event 키로도 추가 (하위 호환)
        exit = {
            "logic": self.strategy.exit.logic,
            "conditions": [
                {
                    **cond.model_dump(exclude_none=True),
                    "event": cond.operator,  # 하위 호환: event 키 추가
                }
                for cond in self.strategy.exit.conditions
            ],
        }
        
        return StrategyDefinition(
            id=self.strategy.id,
            name=self.metadata.name,
            description=self.metadata.description,
            category=self.strategy.category,
            indicators=indicators,
            entry=entry,
            exit=exit,
            params=self.strategy.params,
            risk_management=self.risk.to_risk_management_dict(),
            metadata={
                "author": self.metadata.author,
                "tags": self.metadata.tags,
                "created_at": self.metadata.created_at.isoformat() if self.metadata.created_at else None,
                "updated_at": self.metadata.updated_at.isoformat() if self.metadata.updated_at else None,
            },
            version=self.version,
        )
    
    def to_strategy_schema(self):
        """StrategySchema로 변환 (권장)"""
        from kis_backtest.core.converters import from_yaml_file
        return from_yaml_file(self)
    
    @classmethod
    def from_strategy_definition(cls, definition) -> "KisStrategyFile":
        """StrategyDefinition에서 생성"""
        from kis_backtest.core.strategy import StrategyDefinition
        
        def normalize_condition(cond: dict) -> dict:
            """조건 딕셔너리 정규화 (event → operator)"""
            result = dict(cond)
            # event 키를 operator로 변환
            if "event" in result and "operator" not in result:
                result["operator"] = result.pop("event")
            # type 키도 operator로 변환
            if "type" in result and "operator" not in result:
                result["operator"] = result.pop("type")
            # indicator_def, compare_def는 ConditionConfig에 없으므로 제거
            result.pop("indicator_def", None)
            result.pop("compare_def", None)
            return result
        
        # 지표 변환
        indicators = [
            IndicatorConfig(
                id=ind.get("id", ""),
                alias=ind.get("alias"),
                params=ind.get("params", {}),
                output=ind.get("output", "value"),
            )
            for ind in definition.indicators
        ]
        
        # 진입 조건 변환 - 단일 조건 또는 복합 조건 처리
        entry_conditions = []
        if "conditions" in definition.entry:
            # 복합 조건 (logic + conditions)
            for cond in definition.entry.get("conditions", []):
                entry_conditions.append(ConditionConfig(**normalize_condition(cond)))
        elif "event" in definition.entry or "operator" in definition.entry:
            # 단일 조건
            entry_conditions.append(ConditionConfig(**normalize_condition(definition.entry)))
        
        # 청산 조건 변환 - 단일 조건 또는 복합 조건 처리
        exit_conditions = []
        if "conditions" in definition.exit:
            # 복합 조건 (logic + conditions)
            for cond in definition.exit.get("conditions", []):
                exit_conditions.append(ConditionConfig(**normalize_condition(cond)))
        elif "event" in definition.exit or "operator" in definition.exit:
            # 단일 조건
            exit_conditions.append(ConditionConfig(**normalize_condition(definition.exit)))
        
        # 리스크 설정 변환
        risk = RiskConfig()
        rm = definition.risk_management
        if rm.get("stop_loss_pct"):
            risk.stop_loss = {"enabled": True, "percent": rm["stop_loss_pct"]}
        if rm.get("take_profit_pct"):
            risk.take_profit = {"enabled": True, "percent": rm["take_profit_pct"]}
        if rm.get("trailing_stop_pct"):
            risk.trailing_stop = {"enabled": True, "percent": rm["trailing_stop_pct"]}
        
        return cls(
            version=definition.version,
            metadata=StrategyMetadata(
                name=definition.name,
                description=definition.description,
                author=definition.metadata.get("author", "user") if definition.metadata else "user",
                tags=definition.metadata.get("tags", []) if definition.metadata else [],
            ),
            strategy=StrategyConfig(
                id=definition.id,
                category=definition.category,
                indicators=indicators,
                entry=ConditionGroupConfig(
                    logic=definition.entry.get("logic", "AND"),
                    conditions=entry_conditions,
                ),
                exit=ConditionGroupConfig(
                    logic=definition.exit.get("logic", "OR"),
                    conditions=exit_conditions,
                ),
                params=definition.params,
            ),
            risk=risk,
        )
