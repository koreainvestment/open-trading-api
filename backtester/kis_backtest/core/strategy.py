"""Strategy Definition - Core domain model.

Immutable dataclass representing a complete strategy definition.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class StrategyDefinition:
    """전략 정의 (불변)
    
    전략의 모든 구성 요소를 포함하는 불변 데이터 클래스.
    
    Attributes:
        id: 전략 고유 식별자
        name: 전략 이름
        description: 전략 설명
        category: 전략 카테고리 (trend, momentum, mean_reversion, volatility, composite)
        indicators: 사용되는 기술적 지표 목록
        entry: 진입 조건 정의
        exit: 청산 조건 정의
        params: 파라미터 정의 (이름 -> {default, min, max, step, description})
        validation: 파라미터 검증 규칙 목록
        risk_management: 리스크 관리 설정
        version: 전략 버전
    
    Example:
        strategy = StrategyDefinition(
            id="sma_crossover",
            name="SMA 골든/데드 크로스",
            description="단기 이평선이 장기 이평선을 상향/하향 돌파 시 매매",
            category="trend",
            indicators=[
                {"id": "sma", "alias": "sma_short", "params": {"period": "$short_window"}},
                {"id": "sma", "alias": "sma_long", "params": {"period": "$long_window"}},
            ],
            entry={
                "logic": "AND",
                "conditions": [
                    {"indicator": "sma_short", "event": "cross_above", "compare_to": "sma_long"}
                ]
            },
            exit={
                "logic": "AND",
                "conditions": [
                    {"indicator": "sma_short", "event": "cross_below", "compare_to": "sma_long"}
                ]
            },
            params={
                "short_window": {"default": 5, "min": 2, "max": 50, "step": 1},
                "long_window": {"default": 20, "min": 10, "max": 200, "step": 5},
            },
            validation=[
                {"rule": "short_window < long_window", "message": "단기 이평선 기간이 장기보다 짧아야 합니다"}
            ],
        )
    """
    id: str
    name: str
    description: str
    category: str
    indicators: List[Dict[str, Any]]
    entry: Dict[str, Any]
    exit: Dict[str, Any]
    params: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    validation: List[Dict[str, str]] = field(default_factory=list)
    risk_management: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StrategyDefinition:
        """딕셔너리에서 생성"""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            category=data.get("category", "custom"),
            indicators=data.get("indicators", []),
            entry=data.get("entry", {"logic": "AND", "conditions": []}),
            exit=data.get("exit", {"logic": "AND", "conditions": []}),
            params=data.get("params", {}),
            validation=data.get("validation", []),
            risk_management=data.get("risk_management", {}),
            metadata=data.get("metadata", {}),
            version=data.get("version", "1.0.0"),
        )
    
    def with_params(self, **kwargs: Any) -> StrategyDefinition:
        """파라미터 기본값을 오버라이드한 새 정의 반환"""
        new_params = dict(self.params)
        for key, value in kwargs.items():
            if key in new_params:
                new_params[key] = {**new_params[key], "default": value}
        
        return StrategyDefinition(
            id=self.id,
            name=self.name,
            description=self.description,
            category=self.category,
            indicators=self.indicators,
            entry=self.entry,
            exit=self.exit,
            params=new_params,
            validation=self.validation,
            risk_management=self.risk_management,
            metadata=self.metadata,
            version=self.version,
        )
    
    def get_default_params(self) -> Dict[str, Any]:
        """모든 파라미터의 기본값 반환"""
        return {
            name: param_def.get("default")
            for name, param_def in self.params.items()
        }
    
    def validate_params(self, params: Dict[str, Any]) -> List[str]:
        """파라미터 검증, 오류 메시지 목록 반환"""
        errors = []
        
        # 범위 검증
        for param_name, value in params.items():
            if param_name not in self.params:
                continue
            
            param_def = self.params[param_name]
            min_val = param_def.get("min")
            max_val = param_def.get("max")
            
            if min_val is not None and value < min_val:
                errors.append(f"{param_name}은(는) {min_val} 이상이어야 합니다 (현재: {value})")
            if max_val is not None and value > max_val:
                errors.append(f"{param_name}은(는) {max_val} 이하여야 합니다 (현재: {value})")
        
        return errors
