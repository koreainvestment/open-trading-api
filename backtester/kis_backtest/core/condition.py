"""Condition classes for strategy rules.

Represents comparison conditions between indicators or values.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from kis_backtest.core.indicator import Indicator


@dataclass
class Condition:
    """조건 표현식
    
    두 지표 또는 지표와 상수를 비교하는 조건.
    
    Attributes:
        operator: 비교 연산자 (greater_than, less_than, cross_above, ...)
        left: 왼쪽 피연산자 (Indicator)
        right: 오른쪽 피연산자 (Indicator, float, int)
    
    Example:
        condition = Condition("greater_than", SMA(5), SMA(20))
        # 또는 연산자 오버로딩 사용
        condition = SMA(5) > SMA(20)
    """
    operator: str
    left: Union[Indicator, Condition]
    right: Union[Indicator, float, int, Condition]
    
    def __and__(self, other: Union[Condition, CompositeCondition]) -> CompositeCondition:
        """AND 조합 (&)
        
        Example:
            (SMA(5) > SMA(20)) & (RSI(14) < 70)
        """
        return CompositeCondition("AND", [self, other])
    
    def __or__(self, other: Union[Condition, CompositeCondition]) -> CompositeCondition:
        """OR 조합 (|)
        
        Example:
            (SMA(5) < SMA(20)) | (RSI(14) > 80)
        """
        return CompositeCondition("OR", [self, other])
    
    def to_dict(self) -> Dict[str, Any]:
        """선언적 정의로 변환"""
        # Import here to avoid circular import
        from kis_backtest.core.indicator import Indicator, ScaledIndicator
        
        result: Dict[str, Any] = {"event": self.operator}
        
        if isinstance(self.left, Indicator):
            result["indicator"] = self.left.alias
            result["output"] = self.left.output
            result["indicator_def"] = self.left.to_dict()
        elif isinstance(self.left, ScaledIndicator):
            result["indicator"] = self.left.indicator.alias
            result["output"] = self.left.indicator.output
            result["indicator_def"] = self.left.to_dict()
        
        if isinstance(self.right, Indicator):
            result["compare_to"] = self.right.alias
            result["compare_output"] = self.right.output
            result["compare_def"] = self.right.to_dict()
        elif isinstance(self.right, ScaledIndicator):
            # ScaledIndicator를 비교 대상으로 사용
            result["compare_to"] = self.right.indicator.alias
            result["compare_output"] = self.right.indicator.output
            result["compare_def"] = self.right.to_dict()
            # 스케일 정보 추가
            result["compare_scalar"] = self.right.scalar
            result["compare_operation"] = self.right.operation
        elif isinstance(self.right, (int, float)):
            result["value"] = self.right
        
        return result


@dataclass
class CompositeCondition:
    """복합 조건 (AND/OR)
    
    여러 조건을 논리 연산자로 결합.
    
    Attributes:
        logic: 논리 연산자 ("AND" 또는 "OR")
        conditions: 조건 목록
    
    Example:
        composite = (SMA(5) > SMA(20)) & (RSI(14) < 70) & (ADX(14) > 25)
    """
    logic: Literal["AND", "OR"]
    conditions: List[Union[Condition, CompositeCondition]]
    
    def __and__(self, other: Union[Condition, CompositeCondition]) -> CompositeCondition:
        """AND 조합 (&)"""
        if self.logic == "AND":
            return CompositeCondition("AND", [*self.conditions, other])
        return CompositeCondition("AND", [self, other])
    
    def __or__(self, other: Union[Condition, CompositeCondition]) -> CompositeCondition:
        """OR 조합 (|)"""
        if self.logic == "OR":
            return CompositeCondition("OR", [*self.conditions, other])
        return CompositeCondition("OR", [self, other])
    
    def to_dict(self) -> Dict[str, Any]:
        """선언적 정의로 변환"""
        return {
            "logic": self.logic,
            "conditions": [c.to_dict() for c in self.conditions],
        }


