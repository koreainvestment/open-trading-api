"""Strategy Generator - Compatibility Layer.

Provides backward-compatible generate_strategy() and StrategyGenerator.
Internally uses LeanCodeGenerator for actual code generation.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from kis_backtest.strategies.registry import StrategyRegistry
from kis_backtest.codegen.generator import LeanCodeGenerator, CodeGenConfig
from kis_backtest.core.schema import StrategySchema
from kis_backtest.core.converters import from_preset

logger = logging.getLogger(__name__)


class StrategyGenerator:
    """전략 코드 생성기 (Compatibility Layer)

    내부적으로 LeanCodeGenerator를 사용합니다.

    Example:
        generator = StrategyGenerator(
            strategy_id="sma_crossover",
            symbols=["005930"],
            start_date="2024-01-01",
            end_date="2024-12-31",
        )
        code = generator.generate()
    """

    def __init__(
        self,
        strategy_id: str,
        symbols: List[str],
        start_date: str,
        end_date: str,
        *,
        initial_capital: float = 100_000_000,
        market_type: str = "krx",
        params: Optional[Dict[str, Any]] = None,
        risk_config: Optional[Dict[str, Any]] = None,
    ):
        self.strategy_id = strategy_id
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.market_type = market_type
        self.params = params or {}
        self.risk_config = risk_config

        # 전략 스키마 생성
        self._schema = self._build_schema()

    def _build_schema(self) -> StrategySchema:
        """전략 스키마 빌드"""
        # 레지스트리에서 전략 클래스 가져오기
        strategy_cls = StrategyRegistry.get(self.strategy_id)
        if strategy_cls is None:
            raise ValueError(f"Unknown strategy: {self.strategy_id}")

        # 파라미터로 인스턴스 생성
        strategy_instance = strategy_cls(**self.params)

        # BaseStrategy 인스턴스를 스키마로 변환
        schema = from_preset(strategy_instance)

        if schema is None:
            raise ValueError(f"Failed to create schema for strategy: {self.strategy_id}")

        return schema

    def generate(self) -> str:
        """Lean 코드 생성"""
        config = CodeGenConfig(
            market=self.market_type,
            initial_capital=self.initial_capital,
        )

        generator = LeanCodeGenerator(self._schema, config=config)

        return generator.generate(
            symbols=self.symbols,
            start_date=self.start_date,
            end_date=self.end_date,
        )

    @property
    def schema(self) -> StrategySchema:
        """전략 스키마"""
        return self._schema


def generate_strategy(
    strategy_id: str,
    symbols: List[str],
    start_date: str,
    end_date: str,
    *,
    initial_capital: float = 100_000_000,
    market_type: str = "krx",
    params: Optional[Dict[str, Any]] = None,
) -> str:
    """전략 코드 생성 편의 함수

    Args:
        strategy_id: 전략 ID (sma_crossover, rsi_oversold, etc.)
        symbols: 종목 코드 리스트
        start_date: 시작일 (YYYY-MM-DD)
        end_date: 종료일 (YYYY-MM-DD)
        initial_capital: 초기 자본금
        market_type: 시장 타입 (krx, us)
        params: 전략 파라미터 오버라이드

    Returns:
        생성된 Lean Python 코드

    Example:
        code = generate_strategy(
            strategy_id="sma_crossover",
            symbols=["005930"],
            start_date="2024-01-01",
            end_date="2024-12-31",
            params={"short_window": 10, "long_window": 30},
        )
    """
    generator = StrategyGenerator(
        strategy_id=strategy_id,
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        market_type=market_type,
        params=params,
    )

    return generator.generate()
