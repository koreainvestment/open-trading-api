"""Strategy MCP tools — 4 tools.

list_presets, get_preset_yaml, validate_yaml, list_indicators
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import kis_backtest.strategies.preset  # 전략 자동 등록
from kis_backtest.strategies.registry import StrategyRegistry
from kis_backtest.file.saver import StrategyFileSaver
from kis_backtest.file.loader import StrategyFileLoader
from kis_backtest.core.indicator import INDICATOR_REGISTRY
from kis_mcp.schemas import success_response, error_response

logger = logging.getLogger(__name__)


def list_presets() -> dict:
    """10개 프리셋 전략 목록과 파라미터 정의를 반환합니다.

    Returns:
        10개 전략 목록 — id, name, category, description, tags, params
    """
    try:
        strategies = StrategyRegistry.list_all_with_params()
        return success_response(strategies)
    except Exception as exc:
        logger.exception("list_presets 실패")
        return error_response(str(exc))


def get_preset_yaml(
    strategy_id: str,
    param_overrides: Optional[Dict[str, Any]] = None,
) -> dict:
    """프리셋 전략을 .kis.yaml 문자열로 반환합니다.

    Args:
        strategy_id: 전략 ID (예: "sma_crossover", "momentum")
        param_overrides: 파라미터 오버라이드 (예: {"period": 21, "oversold": 25})

    Returns:
        .kis.yaml 포맷 문자열
    """
    try:
        overrides = param_overrides or {}
        definition = StrategyRegistry.build_with_params(strategy_id, **overrides)
        if definition is None:
            return error_response(
                f"전략 '{strategy_id}'를 찾을 수 없습니다.",
                details={"available": [s["id"] for s in StrategyRegistry.list_all()]},
            )
        yaml_str = StrategyFileSaver.to_yaml_string(definition)
        return success_response({"strategy_id": strategy_id, "yaml": yaml_str})
    except Exception as exc:
        logger.exception("get_preset_yaml 실패")
        return error_response(str(exc))


def validate_yaml(yaml_content: str) -> dict:
    """YAML 전략 문자열의 유효성을 검증합니다.

    Args:
        yaml_content: .kis.yaml 포맷 문자열

    Returns:
        검증 결과 — valid(bool), errors(list), warnings(list)
    """
    try:
        schema = StrategyFileLoader.load_schema_with_params(yaml_content)
    except ValueError as exc:
        return success_response({"valid": False, "errors": [str(exc)], "warnings": []})
    except Exception as exc:
        logger.exception("validate_yaml 실패")
        return error_response(str(exc))

    # alias 정합성 검증 (load_schema_with_params는 스키마 파싱만 수행하므로 별도 검증)
    alias_errors = StrategyFileLoader.validate_content(yaml_content)
    if alias_errors:
        return success_response({"valid": False, "errors": alias_errors, "warnings": []})

    return success_response(
        {
            "valid": True,
            "errors": [],
            "warnings": [],
            "strategy_name": schema.name if hasattr(schema, "name") else None,
        }
    )


def list_indicators() -> dict:
    """지원하는 기술적 지표 목록과 파라미터 정의를 반환합니다.

    Returns:
        지표 목록 — id, name, description, params, lean_class
    """
    try:
        indicators: List[Dict[str, Any]] = []
        for ind_id, info in INDICATOR_REGISTRY.items():
            indicators.append(
                {
                    "id": ind_id,
                    "name": info.name,
                    "description": info.description,
                    "params": info.params,
                    "lean_class": info.lean_class,
                    "outputs": list(info.outputs.keys()) if info.outputs else ["value"],
                }
            )
        return success_response(indicators)
    except Exception as exc:
        logger.exception("list_indicators 실패")
        return error_response(str(exc))
