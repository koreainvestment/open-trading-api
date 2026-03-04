"""Base Strategy abstract class.

All preset strategies inherit from this class.

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, ClassVar

from kis_backtest.core.strategy import StrategyDefinition
from kis_backtest.core.condition import Condition, CompositeCondition
from kis_backtest.core.risk import RiskManagement


class BaseStrategy(ABC):
    """기본 전략 추상 클래스

    모든 프리셋 전략은 이 클래스를 상속.

    PARAM_DEFINITIONS 패턴:
        서브클래스에서 PARAM_DEFINITIONS를 정의하면, 해당 전략의 파라미터를
        프론트엔드에서 동적으로 조회/수정할 수 있습니다.

    Example:
        class MyStrategy(BaseStrategy):
            PARAM_DEFINITIONS = {
                "period": {"default": 14, "min": 2, "max": 100, "type": "int", "description": "기간"},
                "threshold": {"default": 30, "min": 0, "max": 100, "type": "float", "description": "임계값"},
            }

            def __init__(self, period=14, threshold=30):
                self.period = period
                self.threshold = threshold

            @property
            def id(self) -> str:
                return "my_strategy"

            def build(self) -> StrategyDefinition:
                return StrategyDefinition(
                    ...,
                    params=self._build_params(),  # BaseStrategy 메서드 사용
                )
    """

    # 서브클래스에서 오버라이드
    PARAM_DEFINITIONS: ClassVar[Dict[str, Dict[str, Any]]] = {}

    @classmethod
    def get_param_definitions(cls) -> Dict[str, Dict[str, Any]]:
        """파라미터 정의 반환 (프론트엔드/API용).

        Returns:
            파라미터 정의 딕셔너리
            {"period": {"default": 14, "min": 2, "max": 100, "type": "int"}, ...}
        """
        return cls.PARAM_DEFINITIONS

    def _build_params(self) -> Dict[str, Dict[str, Any]]:
        """현재 인스턴스 값으로 params dict 생성.

        PARAM_DEFINITIONS에 정의된 파라미터의 default 값을
        현재 인스턴스의 속성값으로 업데이트합니다.

        Returns:
            params 딕셔너리 (StrategyDefinition.params 용)
        """
        result = {}
        for name, definition in self.PARAM_DEFINITIONS.items():
            # 인스턴스 속성값 조회 (없으면 정의의 default 사용)
            current_value = getattr(self, name, definition.get("default"))
            result[name] = {
                **definition,
                "default": current_value,
            }
        return result

    @property
    @abstractmethod
    def id(self) -> str:
        """전략 고유 식별자"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """전략 이름"""
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        """전략 카테고리"""
        pass

    @property
    def description(self) -> str:
        """전략 설명"""
        return ""

    @abstractmethod
    def indicators(self) -> list:
        """사용하는 지표 목록"""
        pass

    @abstractmethod
    def entry_condition(self) -> Condition:
        """진입 조건"""
        pass

    @abstractmethod
    def exit_condition(self) -> Condition:
        """청산 조건"""
        pass

    def risk_management(self) -> RiskManagement:
        """리스크 관리 (기본값: None)"""
        return RiskManagement()

    def get_custom_lean_code(self) -> str | None:
        """Lean 알고리즘에 삽입할 커스텀 로직 (선택적)

        연속 상승/하락 카운터, 보유일 추적 등 지표로 표현할 수 없는
        로직이 필요한 전략에서 오버라이드합니다.

        Returns:
            커스텀 Python 코드 문자열 (OnData 내부에 삽입됨)
            None이면 커스텀 로직 없음
        """
        return None

    @abstractmethod
    def build(self) -> StrategyDefinition:
        """전략 정의 빌드"""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return self.build().to_dict()
