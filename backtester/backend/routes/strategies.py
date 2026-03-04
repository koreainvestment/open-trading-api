"""Strategies API Routes.

전략 목록 조회, 상세 정보, 빌드 등.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from backend.schemas.strategy import (
    StrategyListResponse,
    StrategyDetailResponse,
    StrategyBuildRequest,
    StrategyBuildResponse,
)
from kis_backtest.strategies.registry import StrategyRegistry
import kis_backtest.strategies.preset  # 전략 자동 등록

router = APIRouter()


@router.get(
    "",
    response_model=StrategyListResponse,
    summary="전략 목록 조회",
    description="등록된 모든 전략 목록을 조회합니다. params 필드에 파라미터 정의 포함.",
)
async def list_strategies(
    category: Optional[str] = Query(None, description="카테고리 필터"),
) -> StrategyListResponse:
    """전략 목록 조회 (params 포함)

    응답 예시:
        {
            "id": "rsi_oversold",
            "name": "RSI 과매도 반전",
            "params": {
                "period": {"default": 14, "min": 2, "max": 100, "type": "int"},
                ...
            }
        }
    """

    # params 포함하여 반환
    strategies = StrategyRegistry.list_all_with_params()

    # 카테고리 필터
    if category:
        strategies = [s for s in strategies if s.get("category") == category]

    return StrategyListResponse(
        success=True,
        data=strategies,
        total=len(strategies),
    )


@router.get(
    "/categories",
    summary="카테고리 목록 조회",
)
async def list_categories() -> dict:
    """사용 가능한 카테고리 목록"""
    return {
        "success": True,
        "data": [
            {"id": "trend", "name": "추세"},
            {"id": "momentum", "name": "모멘텀"},
            {"id": "mean_reversion", "name": "평균 회귀"},
            {"id": "volatility", "name": "변동성"},
            {"id": "oscillator", "name": "오실레이터"},
            {"id": "composite", "name": "복합"},
        ],
    }


@router.get(
    "/{strategy_id}",
    response_model=StrategyDetailResponse,
    summary="전략 상세 조회",
)
async def get_strategy(strategy_id: str) -> StrategyDetailResponse:
    """전략 상세 정보 조회"""
    try:
        definition = StrategyRegistry.build(strategy_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Strategy not found: {strategy_id}")
    
    return StrategyDetailResponse(
        success=True,
        data=definition.to_dict(),
    )


@router.post(
    "/build",
    response_model=StrategyBuildResponse,
    summary="커스텀 전략 빌드",
    description="DSL 정의로 커스텀 전략을 빌드합니다.",
)
async def build_strategy(request: StrategyBuildRequest) -> StrategyBuildResponse:
    """커스텀 전략 빌드"""
    from kis_backtest.core.strategy import StrategyDefinition
    
    try:
        definition = StrategyDefinition(
            id=request.id,
            name=request.name,
            description=request.description or "",
            category=request.category,
            indicators=request.indicators,
            entry=request.entry,
            exit=request.exit,
            params=request.params or {},
            risk_management=request.risk_management or {},
        )
        
        return StrategyBuildResponse(
            success=True,
            data=definition.to_dict(),
            message="전략 빌드 성공",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{strategy_id}/yaml",
    summary="전략 YAML 조회",
)
async def get_strategy_yaml(strategy_id: str) -> dict:
    """전략을 YAML 문자열로 조회"""
    from kis_backtest.file.saver import StrategyFileSaver
    
    try:
        definition = StrategyRegistry.build(strategy_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Strategy not found: {strategy_id}")
    
    try:
        yaml_content = StrategyFileSaver.to_yaml_string(definition)
        return {
            "success": True,
            "data": {
                "id": strategy_id,
                "name": definition.name,
                "yaml": yaml_content,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"YAML 생성 실패: {e}")


@router.get(
    "/{strategy_id}/python",
    summary="전략 Python 코드 조회",
)
async def get_strategy_python(strategy_id: str) -> dict:
    """전략을 Python DSL 코드로 조회"""
    from kis_backtest.file.python_exporter import PythonExporter

    try:
        definition = StrategyRegistry.build(strategy_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Strategy not found: {strategy_id}")

    try:
        python_content = PythonExporter.to_python_string(definition)
        return {
            "success": True,
            "data": {
                "id": strategy_id,
                "name": definition.name,
                "python": python_content,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Python 코드 생성 실패: {e}")


@router.get(
    "/{strategy_id}/lean-params",
    summary="Lean 코드 생성 파라미터 조회",
)
async def get_lean_params(strategy_id: str) -> dict:
    """Lean 코드 생성용 파라미터 조회"""
    strategy_class = StrategyRegistry.get(strategy_id)
    if strategy_class is None:
        raise HTTPException(status_code=404, detail=f"Strategy not found: {strategy_id}")
    
    try:
        strategy = strategy_class()
        lean_params = strategy.to_lean_params()
        
        return {
            "success": True,
            "data": lean_params,
        }
    except AttributeError:
        raise HTTPException(status_code=400, detail="Strategy does not support Lean params")
