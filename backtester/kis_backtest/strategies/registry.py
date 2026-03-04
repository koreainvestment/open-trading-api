"""Strategy Registry.

모든 프리셋 전략을 등록하고 조회하는 레지스트리.
전략 빌더와 codegen에서 공통으로 사용.

"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Type

from kis_backtest.strategies.base import BaseStrategy
from kis_backtest.core.strategy import StrategyDefinition


class StrategyRegistry:
    """전략 레지스트리

    프리셋 전략을 등록하고 조회합니다.

    Example:
        # 전략 등록 (데코레이터 사용)
        @StrategyRegistry.register("rsi_oversold")
        class RSIOversoldStrategy(BaseStrategy):
            ...

        # 전략 조회
        strategy_cls = StrategyRegistry.get("rsi_oversold")
        strategy = strategy_cls()
        definition = strategy.build()

        # 파라미터 오버라이드로 빌드
        definition = StrategyRegistry.build_with_params("rsi_oversold", period=21, oversold=25)

        # 파라미터 정의 조회
        params = StrategyRegistry.get_param_definitions("rsi_oversold")
        # {"period": {"default": 14, "min": 2, "max": 100}, ...}

        # 모든 전략 + params 반환
        strategies = StrategyRegistry.list_all_with_params()
    """

    _strategies: Dict[str, Type[BaseStrategy]] = {}
    _metadata: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register(
        cls,
        strategy_id: str,
        *,
        name: Optional[str] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Callable[[Type[BaseStrategy]], Type[BaseStrategy]]:
        """전략 등록 데코레이터
        
        Args:
            strategy_id: 전략 고유 ID
            name: 전략 표시 이름
            category: 카테고리 (trend, momentum, oscillator, volatility, mean_reversion, composite)
            description: 설명
            tags: 태그 목록
        
        Example:
            @StrategyRegistry.register(
                "rsi_oversold",
                name="RSI 과매도 반전",
                category="oscillator",
                description="RSI가 과매도 영역 진입 후 반등 시 매수",
                tags=["rsi", "mean_reversion", "oversold"]
            )
            class RSIOversoldStrategy(BaseStrategy):
                ...
        """
        def decorator(strategy_cls: Type[BaseStrategy]) -> Type[BaseStrategy]:
            cls._strategies[strategy_id] = strategy_cls
            cls._metadata[strategy_id] = {
                "id": strategy_id,
                "name": name or strategy_id,
                "category": category or "uncategorized",
                "description": description or "",
                "tags": tags or [],
            }
            return strategy_cls
        return decorator
    
    @classmethod
    def get(cls, strategy_id: str) -> Optional[Type[BaseStrategy]]:
        """전략 클래스 조회"""
        return cls._strategies.get(strategy_id)
    
    @classmethod
    def get_metadata(cls, strategy_id: str) -> Optional[Dict[str, Any]]:
        """전략 메타데이터 조회"""
        return cls._metadata.get(strategy_id)
    
    @classmethod
    def build(cls, strategy_id: str, **params: Any) -> Optional[StrategyDefinition]:
        """전략 빌드
        
        Args:
            strategy_id: 전략 ID
            **params: 전략 파라미터 (기본값 오버라이드)
        
        Returns:
            StrategyDefinition 또는 None
        """
        strategy_cls = cls.get(strategy_id)
        if strategy_cls is None:
            return None
        
        strategy = strategy_cls(**params)
        return strategy.build()
    
    @classmethod
    def list_all(cls) -> List[Dict[str, Any]]:
        """모든 등록된 전략 목록"""
        return list(cls._metadata.values())
    
    @classmethod
    def clear(cls) -> None:
        """레지스트리 초기화 (테스트용)"""
        cls._strategies.clear()
        cls._metadata.clear()

    @classmethod
    def list(cls) -> Dict[str, Type[BaseStrategy]]:
        """등록된 모든 전략 클래스 반환 (backward compatibility)"""
        return dict(cls._strategies)

    @classmethod
    def build_with_params(
        cls,
        strategy_id: str,
        **param_overrides: Any,
    ) -> Optional[StrategyDefinition]:
        """파라미터 오버라이드로 전략 빌드.

        Args:
            strategy_id: 전략 ID
            **param_overrides: 파라미터 오버라이드 값

        Returns:
            StrategyDefinition 또는 None

        Example:
            definition = StrategyRegistry.build_with_params(
                "rsi_oversold",
                period=21,
                oversold=25,
            )
        """
        strategy_cls = cls.get(strategy_id)
        if strategy_cls is None:
            return None

        # PARAM_DEFINITIONS가 있으면 해당 파라미터만 전달
        if hasattr(strategy_cls, 'PARAM_DEFINITIONS') and strategy_cls.PARAM_DEFINITIONS:
            valid_params = {}
            for name in strategy_cls.PARAM_DEFINITIONS:
                if name in param_overrides:
                    valid_params[name] = param_overrides[name]
            strategy = strategy_cls(**valid_params)
        else:
            # 기존 방식 - 모든 파라미터 전달
            strategy = strategy_cls(**param_overrides)

        return strategy.build()

    @classmethod
    def get_param_definitions(cls, strategy_id: str) -> Dict[str, Dict[str, Any]]:
        """전략의 파라미터 정의 반환.

        Args:
            strategy_id: 전략 ID

        Returns:
            파라미터 정의 딕셔너리
            {"period": {"default": 14, "min": 2, "max": 100, "type": "int"}, ...}
        """
        strategy_cls = cls.get(strategy_id)
        if strategy_cls is None:
            return {}

        if hasattr(strategy_cls, 'PARAM_DEFINITIONS'):
            return strategy_cls.PARAM_DEFINITIONS
        if hasattr(strategy_cls, 'get_param_definitions'):
            return strategy_cls.get_param_definitions()
        return {}

    @classmethod
    def list_all_with_params(cls) -> List[Dict[str, Any]]:
        """모든 등록된 전략 목록 + params 정의 반환.

        프론트엔드에서 전략 목록과 각 전략의 파라미터를 함께 조회할 때 사용.

        Returns:
            전략 목록 (params 포함)
            [{"id": "rsi_oversold", "name": "RSI 과매도", "params": {...}}, ...]
        """
        result = []
        for strategy_id, meta in cls._metadata.items():
            params = cls.get_param_definitions(strategy_id)
            result.append({
                **meta,
                "params": params,
            })
        return result


# Alias for convenience
register = StrategyRegistry.register

# Backward compatibility - STRATEGY_REGISTRY as a reference to the class
STRATEGY_REGISTRY = StrategyRegistry
