"""
strategy_core - 통합 전략 모듈

전략 등록/조회/실행을 하나의 모듈로 통합합니다.

사용:
    from strategy_core import StrategyRegistry

    # 전략 목록
    strategies = StrategyRegistry.get_all()

    # 전략 조회
    schema = StrategyRegistry.get('golden_cross')

    # 전략 실행
    from strategy_core.executor import execute_strategy
    results = execute_strategy(schema, stocks, log, get_stock_name, api_sleep)
"""

from strategy_core.registry import StrategyRegistry

__all__ = ["StrategyRegistry"]
