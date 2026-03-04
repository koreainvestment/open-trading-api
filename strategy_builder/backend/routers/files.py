"""Files API Routes.

전략 파일 Import/Export (.kis.yaml, .py)
- kis2 의존성 제거됨
- 프론트엔드에서 직접 YAML 생성/파싱하므로 간단한 검증만 제공
"""

from typing import Literal
import tempfile
import zipfile
import io
import yaml

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel


router = APIRouter()


# ============================================
# Response Models
# ============================================

class FileImportResponse(BaseModel):
    success: bool
    data: dict | None = None
    message: str | None = None


class TemplateInfo(BaseModel):
    id: str
    name: str
    description: str
    category: str
    tags: list[str] = []


class TemplateListResponse(BaseModel):
    success: bool
    data: list[TemplateInfo]
    total: int


# ============================================
# Built-in Templates (kis2 대신 하드코딩)
# ============================================

BUILT_IN_TEMPLATES = {
    "golden_cross": {
        "id": "golden_cross",
        "name": "골든크로스",
        "description": "단기 이평선이 장기 이평선을 상향 돌파 시 매수",
        "category": "trend",
        "tags": ["ma", "추세추종", "골든크로스"],
        "yaml": """version: "1.0"

metadata:
  name: "골든크로스"
  description: "단기 이평선이 장기 이평선을 상향 돌파 시 매수"
  author: "KIS Builder"
  tags: [ma, 추세추종, 골든크로스]

strategy:
  id: golden_cross
  category: trend
  
  indicators:
    - id: sma
      alias: sma_fast
      params:
        period: 5
    - id: sma
      alias: sma_slow
      params:
        period: 20
  
  entry:
    logic: AND
    conditions:
      - indicator: sma_fast
        operator: cross_above
        compare_to: sma_slow
  
  exit:
    logic: AND
    conditions:
      - indicator: sma_fast
        operator: cross_below
        compare_to: sma_slow

risk:
  stop_loss:
    enabled: true
    percent: 5.0
"""
    }
}


# ============================================
# API Endpoints
# ============================================

@router.get(
    "/templates",
    response_model=TemplateListResponse,
    summary="템플릿 목록 조회",
)
async def list_templates() -> TemplateListResponse:
    """사용 가능한 전략 템플릿 목록"""
    templates = [
        TemplateInfo(
            id=t["id"],
            name=t["name"],
            description=t["description"],
            category=t["category"],
            tags=t["tags"],
        )
        for t in BUILT_IN_TEMPLATES.values()
    ]
    
    return TemplateListResponse(
        success=True,
        data=templates,
        total=len(templates),
    )


@router.get(
    "/templates/{template_id}",
    summary="템플릿 상세 조회",
)
async def get_template(template_id: str) -> dict:
    """템플릿 상세 정보 (YAML 포함)"""
    if template_id not in BUILT_IN_TEMPLATES:
        raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")
    
    template = BUILT_IN_TEMPLATES[template_id]
    return {
        "success": True,
        "data": {
            "id": template["id"],
            "name": template["name"],
            "yaml": template["yaml"],
        },
    }


@router.get(
    "/templates/{template_id}/download",
    summary="템플릿 다운로드",
)
async def download_template(template_id: str) -> StreamingResponse:
    """템플릿 파일 다운로드"""
    if template_id not in BUILT_IN_TEMPLATES:
        raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")
    
    template = BUILT_IN_TEMPLATES[template_id]
    content = template["yaml"].encode("utf-8")
    
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/x-yaml",
        headers={
            "Content-Disposition": f'attachment; filename="{template_id}.kis.yaml"'
        },
    )


@router.post(
    "/import",
    response_model=FileImportResponse,
    summary="전략 파일 Import",
)
async def import_strategy(file: UploadFile = File(...)) -> FileImportResponse:
    """YAML 파일을 업로드하여 전략 Import"""
    
    # 파일 검증
    if not file.filename or not file.filename.endswith((".yaml", ".yml")):
        raise HTTPException(
            status_code=400,
            detail="Only .yaml or .yml files are allowed"
        )
    
    # 파일 읽기
    try:
        content = await file.read()
        content_str = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")
    
    # YAML 파싱 및 검증
    try:
        data = yaml.safe_load(content_str)
        
        # 필수 필드 검증
        if "strategy" not in data:
            raise ValueError("Missing 'strategy' section")
        
        strategy = data["strategy"]
        metadata = data.get("metadata", {})
        
        if "id" not in strategy:
            raise ValueError("Missing strategy.id")
        if "indicators" not in strategy:
            raise ValueError("Missing strategy.indicators")
        if "entry" not in strategy:
            raise ValueError("Missing strategy.entry")
        if "exit" not in strategy:
            raise ValueError("Missing strategy.exit")
        
        return FileImportResponse(
            success=True,
            data={
                "id": strategy.get("id"),
                "name": metadata.get("name", strategy.get("id")),
                "category": strategy.get("category", "custom"),
                "description": metadata.get("description", ""),
                "yaml": content_str,
            },
            message="전략 Import 성공",
        )
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid strategy file: {e}")


@router.post(
    "/export",
    summary="전략 Export",
)
async def export_strategy(
    yaml_content: str,
    filename: str = Query("strategy", description="파일명 (확장자 제외)"),
    format: Literal["yaml", "zip"] = Query("yaml", description="Export 형식"),
):
    """전략을 YAML 또는 ZIP 파일로 Export

    Args:
        yaml_content: YAML 문자열
        filename: 파일명
        format: 출력 형식 (yaml, zip)

    Returns:
        StreamingResponse
    """
    if format == "yaml":
        content = yaml_content.encode("utf-8")
        return StreamingResponse(
            io.BytesIO(content),
            media_type="application/x-yaml",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}.kis.yaml"'
            },
        )
    
    elif format == "zip":
        # ZIP Export (YAML만)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"{filename}.kis.yaml", yaml_content)
        
        zip_buffer.seek(0)
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}.zip"'
            },
        )
    
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")


@router.post(
    "/validate",
    summary="전략 파일 검증",
)
async def validate_strategy(file: UploadFile = File(...)) -> dict:
    """YAML 파일 검증"""
    try:
        content = await file.read()
        content_str = content.decode("utf-8")
        data = yaml.safe_load(content_str)
        
        errors = []
        
        # 필수 필드 검증
        if "strategy" not in data:
            errors.append("Missing 'strategy' section")
        else:
            strategy = data["strategy"]
            if not strategy.get("indicators"):
                errors.append("No indicators defined")
            if not strategy.get("entry", {}).get("conditions"):
                errors.append("No entry conditions defined")
            if not strategy.get("exit", {}).get("conditions"):
                errors.append("No exit conditions defined")
        
        strategy_id = data.get("strategy", {}).get("id", "unknown")
        strategy_name = data.get("metadata", {}).get("name", strategy_id)
        
        return {
            "success": len(errors) == 0,
            "data": {
                "id": strategy_id,
                "name": strategy_name,
                "valid": len(errors) == 0,
                "errors": errors,
            },
        }
    except yaml.YAMLError as e:
        return {
            "success": False,
            "data": {
                "valid": False,
                "errors": [f"Invalid YAML: {e}"],
            },
        }
    except Exception as e:
        return {
            "success": False,
            "data": {
                "valid": False,
                "errors": [str(e)],
            },
        }
