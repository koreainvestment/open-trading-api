"""Rule Builder - Fluent API for strategy creation.

Provides method chaining interface for building strategies without code.

Example:
    from kis_backtest.dsl import RuleBuilder, SMA, RSI
    
    strategy = (
        RuleBuilder("골든크로스_RSI필터")
        .description("SMA 골든크로스 + RSI 과매도 필터")
        .buy_when((SMA(5) > SMA(20)) & (RSI(14) < 70))
        .sell_when((SMA(5) < SMA(20)) | (RSI(14) > 80))
        .stop_loss(5.0)
        .take_profit(10.0)
        .build()
    )
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from kis_backtest.core.indicator import Indicator
from kis_backtest.core.condition import Condition, CompositeCondition
from kis_backtest.core.risk import RiskManagement
from kis_backtest.core.strategy import StrategyDefinition


@dataclass
class StrategyRule:
    """빌드된 전략 규칙
    
    RuleBuilder.build()로 생성되는 최종 전략 정의.
    
    Attributes:
        name: 전략 이름
        entry_condition: 진입 조건
        exit_condition: 청산 조건
        indicators: 사용된 지표 목록
        risk_management: 리스크 관리 설정
        description: 전략 설명
    """
    name: str
    entry_condition: Union[Condition, CompositeCondition]
    exit_condition: Union[Condition, CompositeCondition]
    indicators: List[Indicator]
    risk_management: RiskManagement
    description: str = ""
    category: str = "custom"
    
    def to_strategy_definition(self) -> StrategyDefinition:
        """StrategyDefinition으로 변환"""
        return StrategyDefinition(
            id=self._generate_id(),
            name=self.name,
            description=self.description or f"RuleBuilder로 생성된 전략: {self.name}",
            category=self.category,
            indicators=[ind.to_dict() for ind in self.indicators],
            entry=self._condition_to_entry(self.entry_condition),
            exit=self._condition_to_exit(self.exit_condition),
            params={},
            validation=[],
            risk_management=self.risk_management.to_dict(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return self.to_strategy_definition().to_dict()
    
    def _generate_id(self) -> str:
        """전략 ID 생성"""
        # 이름에서 ID 생성 (공백 -> 언더스코어, 소문자)
        return self.name.lower().replace(" ", "_").replace("-", "_")
    
    def _condition_to_entry(self, cond: Union[Condition, CompositeCondition]) -> Dict[str, Any]:
        """조건을 entry 형식으로 변환"""
        if isinstance(cond, CompositeCondition):
            return {
                "logic": cond.logic,
                "conditions": [c.to_dict() for c in cond.conditions],
            }
        return {
            "logic": "AND",
            "conditions": [cond.to_dict()],
        }
    
    def _condition_to_exit(self, cond: Union[Condition, CompositeCondition]) -> Dict[str, Any]:
        """조건을 exit 형식으로 변환"""
        return self._condition_to_entry(cond)
    
    def summary(self) -> str:
        """전략 요약 문자열"""
        lines = [
            f"전략명: {self.name}",
            f"설명: {self.description or '(없음)'}",
            f"카테고리: {self.category}",
            f"사용 지표: {len(self.indicators)}개",
        ]
        
        for ind in self.indicators:
            params_str = ", ".join(f"{k}={v}" for k, v in ind.params.items())
            lines.append(f"  - {ind.id}({params_str})")
        
        risk = self.risk_management
        if risk.stop_loss_pct:
            lines.append(f"손절: {risk.stop_loss_pct}%")
        if risk.take_profit_pct:
            lines.append(f"익절: {risk.take_profit_pct}%")
        if risk.trailing_stop_pct:
            lines.append(f"트레일링 스탑: {risk.trailing_stop_pct}%")
        
        return "\n".join(lines)


class RuleBuilder:
    """전략 규칙 빌더
    
    메서드 체이닝 방식으로 직관적인 전략 정의 가능.
    
    Example:
        strategy = (
            RuleBuilder("골든크로스")
            .buy_when(SMA(5) > SMA(20))
            .sell_when(SMA(5) < SMA(20))
            .stop_loss(5.0)
            .take_profit(10.0)
            .build()
        )
    
    복합 조건 예:
        strategy = (
            RuleBuilder("복합 전략")
            .buy_when((SMA(5) > SMA(20)) & (RSI(14) < 70))
            .sell_when((SMA(5) < SMA(20)) | (RSI(14) > 80))
            .build()
        )
    """
    
    def __init__(self, name: str = "CustomStrategy"):
        """
        Args:
            name: 전략 이름
        """
        self.name = name
        self._description: str = ""
        self._category: str = "custom"
        self._entry_condition: Optional[Union[Condition, CompositeCondition]] = None
        self._exit_condition: Optional[Union[Condition, CompositeCondition]] = None
        self._indicators: List[Indicator] = []
        self._risk = RiskManagement()
    
    def description(self, text: str) -> RuleBuilder:
        """전략 설명 설정
        
        Args:
            text: 전략 설명
        
        Returns:
            self (체이닝용)
        """
        self._description = text
        return self
    
    def category(self, cat: str) -> RuleBuilder:
        """전략 카테고리 설정
        
        Args:
            cat: 카테고리 (trend, momentum, mean_reversion, volatility, composite)
        
        Returns:
            self (체이닝용)
        """
        self._category = cat
        return self
    
    def buy_when(self, condition: Union[Condition, CompositeCondition]) -> RuleBuilder:
        """매수 조건 설정
        
        Args:
            condition: 매수 조건 (Condition 또는 CompositeCondition)
        
        Returns:
            self (체이닝용)
        
        Example:
            .buy_when(SMA(5) > SMA(20))
            .buy_when((SMA(5) > SMA(20)) & (RSI(14) < 70))
        """
        self._entry_condition = condition
        self._collect_indicators(condition)
        return self
    
    def sell_when(self, condition: Union[Condition, CompositeCondition]) -> RuleBuilder:
        """매도 조건 설정
        
        Args:
            condition: 매도 조건 (Condition 또는 CompositeCondition)
        
        Returns:
            self (체이닝용)
        
        Example:
            .sell_when(SMA(5) < SMA(20))
            .sell_when((SMA(5) < SMA(20)) | (RSI(14) > 80))
        """
        self._exit_condition = condition
        self._collect_indicators(condition)
        return self
    
    def stop_loss(self, percent: float) -> RuleBuilder:
        """손절 설정
        
        Args:
            percent: 손절 퍼센트 (예: 5.0 = 5%)
        
        Returns:
            self (체이닝용)
        
        Example:
            .stop_loss(5.0)  # 5% 손절
        """
        self._risk.stop_loss_pct = percent
        return self
    
    def take_profit(self, percent: float) -> RuleBuilder:
        """익절 설정
        
        Args:
            percent: 익절 퍼센트 (예: 10.0 = 10%)
        
        Returns:
            self (체이닝용)
        
        Example:
            .take_profit(10.0)  # 10% 익절
        """
        self._risk.take_profit_pct = percent
        return self
    
    def trailing_stop(self, percent: float) -> RuleBuilder:
        """트레일링 스탑 설정
        
        고점 대비 일정 비율 하락 시 청산.
        
        Args:
            percent: 트레일링 스탑 퍼센트
        
        Returns:
            self (체이닝용)
        
        Example:
            .trailing_stop(3.0)  # 고점 대비 3% 하락 시 청산
        """
        self._risk.trailing_stop_pct = percent
        return self
    
    def max_position(self, percent: float) -> RuleBuilder:
        """최대 포지션 비중 설정
        
        Args:
            percent: 최대 포지션 비중 (예: 80 = 80%)
        
        Returns:
            self (체이닝용)
        
        Example:
            .max_position(80)  # 최대 80% 비중
        """
        self._risk.max_position_pct = percent / 100
        return self
    
    def build(self) -> StrategyRule:
        """전략 규칙 빌드
        
        설정된 조건들을 검증하고 StrategyRule 객체 생성.
        
        Returns:
            StrategyRule: 빌드된 전략 규칙
        
        Raises:
            ValueError: 필수 조건이 설정되지 않은 경우
        """
        if self._entry_condition is None:
            raise ValueError("매수 조건이 설정되지 않았습니다. buy_when()을 호출하세요.")
        if self._exit_condition is None:
            raise ValueError("매도 조건이 설정되지 않았습니다. sell_when()을 호출하세요.")
        
        # 중복 지표 제거
        unique_indicators = self._deduplicate_indicators()
        
        return StrategyRule(
            name=self.name,
            entry_condition=self._entry_condition,
            exit_condition=self._exit_condition,
            indicators=unique_indicators,
            risk_management=self._risk,
            description=self._description,
            category=self._category,
        )
    
    def _collect_indicators(self, condition: Union[Condition, CompositeCondition]) -> None:
        """조건에서 사용된 지표 수집 (재귀적)"""
        if isinstance(condition, Condition):
            if isinstance(condition.left, Indicator):
                self._add_indicator(condition.left)
            if isinstance(condition.right, Indicator):
                self._add_indicator(condition.right)
        elif isinstance(condition, CompositeCondition):
            for c in condition.conditions:
                self._collect_indicators(c)
    
    def _add_indicator(self, indicator: Indicator) -> None:
        """지표 추가 (가격 제외)"""
        # 가격은 지표가 아니므로 제외
        if indicator.id in ("price", "volume"):
            return
        
        self._indicators.append(indicator)
    
    def _deduplicate_indicators(self) -> List[Indicator]:
        """중복 지표 제거"""
        seen = set()
        unique = []
        
        for ind in self._indicators:
            key = (ind.id, tuple(sorted(ind.params.items())), ind.output)
            if key not in seen:
                seen.add(key)
                unique.append(ind)
        
        return unique
