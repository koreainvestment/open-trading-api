"""File API Schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TemplateListResponse(BaseModel):
    """템플릿 목록 응답"""
    success: bool = True
    data: List[Dict[str, Any]]
    total: int


class FileImportResponse(BaseModel):
    """파일 Import 응답"""
    success: bool = True
    data: Dict[str, Any]
    message: Optional[str] = None


