"""Strategy API Schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StrategyListResponse(BaseModel):
    """전략 목록 응답"""
    success: bool = True
    data: List[Dict[str, Any]]
    total: int


class StrategyDetailResponse(BaseModel):
    """전략 상세 응답"""
    success: bool = True
    data: Dict[str, Any]


class StrategyBuildRequest(BaseModel):
    """전략 빌드 요청"""
    id: str = Field(..., description="전략 ID")
    name: str = Field(..., description="전략 이름")
    description: Optional[str] = Field(None, description="전략 설명")
    category: str = Field(default="custom", description="카테고리")
    indicators: List[Dict[str, Any]] = Field(..., description="지표 목록")
    entry: Dict[str, Any] = Field(..., description="진입 조건")
    exit: Dict[str, Any] = Field(..., description="청산 조건")
    params: Optional[Dict[str, Dict[str, Any]]] = Field(None, description="파라미터")
    risk_management: Optional[Dict[str, Any]] = Field(None, description="리스크 관리")


class StrategyBuildResponse(BaseModel):
    """전략 빌드 응답"""
    success: bool = True
    data: Dict[str, Any]
    message: Optional[str] = None
