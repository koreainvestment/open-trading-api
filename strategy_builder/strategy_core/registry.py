"""
전략 레지스트리

@register 데코레이터로 전략을 등록하고, StrategyRegistry로 조회합니다.
클래스 속성에서 메타데이터를 자동 수집합니다.
"""

from typing import Any, Dict, List, Optional


_REGISTRY: Dict[str, Dict[str, Any]] = {}


def register(strategy_id: str, category: str):
    """전략 등록 데코레이터

    클래스 속성에서 메타데이터를 자동 수집합니다:
    - name: 전략명 (기본값: strategy_id)
    - description: 설명 (기본값: '')
    - params: UI 파라미터 목록 (기본값: [])
    - param_map: frontend→backend 파라미터 매핑 (기본값: {})
    - builder_state: Visual Builder용 상태 (기본값: {})
    - strategy_class: 실행 클래스 (None이면 builder-only)
    """
    def decorator(cls):
        _REGISTRY[strategy_id] = {
            'id': strategy_id,
            'category': category,
            'name': getattr(cls, 'name', strategy_id),
            'description': getattr(cls, 'description', ''),
            'params': getattr(cls, 'params', []),
            'param_map': getattr(cls, 'param_map', {}),
            'builder_state': getattr(cls, 'builder_state', {}),
            'strategy_class': getattr(cls, 'strategy_class', None),
        }
        return cls
    return decorator


class StrategyRegistry:
    """전략 레지스트리 - 전략 조회/검색"""

    @staticmethod
    def get(strategy_id: str) -> Optional[Dict[str, Any]]:
        """전략 ID로 조회"""
        return _REGISTRY.get(strategy_id)

    @staticmethod
    def get_all() -> Dict[str, Dict[str, Any]]:
        """전체 전략 딕셔너리 반환"""
        return dict(_REGISTRY)

    @staticmethod
    def get_list() -> List[Dict[str, Any]]:
        """전략 목록 (API 응답용)"""
        return [
            {
                'id': s['id'],
                'name': s['name'],
                'description': s['description'],
                'category': s['category'],
                'params': s['params'],
                'builder_state': s['builder_state'],
            }
            for s in _REGISTRY.values()
        ]

    @staticmethod
    def get_executable() -> Dict[str, Dict[str, Any]]:
        """실행 가능한 전략만 (strategy_class가 있는 것)"""
        return {
            sid: schema
            for sid, schema in _REGISTRY.items()
            if schema.get('strategy_class') is not None
        }

    @staticmethod
    def has(strategy_id: str) -> bool:
        """전략 존재 여부"""
        return strategy_id in _REGISTRY

    @staticmethod
    def is_builder_only(strategy_id: str) -> bool:
        """빌더 전용 전략 여부 (strategy_class가 None)"""
        schema = _REGISTRY.get(strategy_id)
        if schema is None:
            return False
        return schema.get('strategy_class') is None
