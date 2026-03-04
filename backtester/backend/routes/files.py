"""Files API Routes.

전략 파일 Import/Export (.kis.yaml, .py, .zip)
"""

from typing import List, Literal
from pathlib import Path
import tempfile
import zipfile
import io

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse, StreamingResponse

from backend.schemas.file import (
    FileImportResponse,
    TemplateListResponse,
)

router = APIRouter()


@router.get(
    "/templates",
    response_model=TemplateListResponse,
    summary="템플릿 목록 조회",
)
async def list_templates() -> TemplateListResponse:
    """사용 가능한 전략 템플릿 목록"""
    from kis_backtest.file.templates import list_templates, get_template_path
    from kis_backtest.file.loader import StrategyFileLoader
    
    templates = []
    for name in list_templates():
        try:
            path = get_template_path(name)
            strategy_file = StrategyFileLoader.load(path)
            templates.append({
                "id": name,
                "name": strategy_file.metadata.name,
                "description": strategy_file.metadata.description,
                "category": strategy_file.strategy.category,
                "tags": strategy_file.metadata.tags,
            })
        except Exception:
            continue
    
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
    from kis_backtest.file.templates import get_template_path
    from kis_backtest.file.loader import StrategyFileLoader
    from kis_backtest.file.saver import StrategyFileSaver
    
    try:
        path = get_template_path(template_id)
        strategy_file = StrategyFileLoader.load(path)
        yaml_content = StrategyFileSaver.to_yaml_string(strategy_file)
        
        return {
            "success": True,
            "data": {
                "id": template_id,
                "name": strategy_file.metadata.name,
                "yaml": yaml_content,
            },
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")


@router.get(
    "/templates/{template_id}/python",
    summary="템플릿 Python 코드 조회",
)
async def get_template_python(template_id: str) -> dict:
    """템플릿을 Python DSL 코드로 변환"""
    from kis_backtest.file.templates import get_template_path
    from kis_backtest.file.loader import StrategyFileLoader
    from kis_backtest.file.python_exporter import PythonExporter

    try:
        path = get_template_path(template_id)
        strategy_file = StrategyFileLoader.load(path)
        python_content = PythonExporter.to_python_string(strategy_file)

        return {
            "success": True,
            "data": {
                "id": template_id,
                "name": strategy_file.metadata.name,
                "python": python_content,
            },
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")


@router.get(
    "/templates/{template_id}/download",
    summary="템플릿 다운로드",
)
async def download_template(template_id: str) -> FileResponse:
    """템플릿 파일 다운로드"""
    from kis_backtest.file.templates import get_template_path
    
    try:
        path = get_template_path(template_id)
        return FileResponse(
            path=path,
            filename=f"{template_id}.kis.yaml",
            media_type="application/x-yaml",
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")


@router.post(
    "/import",
    response_model=FileImportResponse,
    summary="전략 파일 Import",
)
async def import_strategy(file: UploadFile = File(...)) -> FileImportResponse:
    """YAML 파일을 업로드하여 전략 Import"""
    from kis_backtest.file.loader import StrategyFileLoader
    
    # 파일 검증
    if not file.filename.endswith((".yaml", ".yml")):
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
        strategy_file = StrategyFileLoader.load_from_string(content_str)
        definition = strategy_file.to_strategy_definition()
        
        return FileImportResponse(
            success=True,
            data={
                "id": definition.id,
                "name": definition.name,
                "category": definition.category,
                "description": definition.description,
                "definition": definition.to_dict(),
            },
            message="전략 Import 성공",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid strategy file: {e}")


@router.post(
    "/export/{strategy_id}",
    summary="전략 Export",
)
async def export_strategy(
    strategy_id: str,
    format: Literal["yaml", "python", "zip"] = Query("yaml", description="Export 형식"),
):
    """전략을 YAML, Python, 또는 ZIP 파일로 Export

    Args:
        strategy_id: 전략 ID
        format: 출력 형식 (yaml, python, zip)

    Returns:
        FileResponse or StreamingResponse
    """
    from kis_backtest.strategies.registry import StrategyRegistry
    from kis_backtest.file.saver import StrategyFileSaver
    from kis_backtest.file.python_exporter import PythonExporter
    import kis_backtest.strategies.preset  # 전략 자동 등록

    try:
        definition = StrategyRegistry.build(strategy_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Strategy not found: {strategy_id}")

    if format == "yaml":
        # YAML Export
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".kis.yaml",
            delete=False,
            encoding="utf-8"
        ) as f:
            yaml_content = StrategyFileSaver.to_yaml_string(definition)
            f.write(yaml_content)
            temp_path = f.name

        return FileResponse(
            path=temp_path,
            filename=f"{strategy_id}.kis.yaml",
            media_type="application/x-yaml",
        )

    elif format == "python":
        # Python Export
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8"
        ) as f:
            python_content = PythonExporter.to_python_string(definition)
            f.write(python_content)
            temp_path = f.name

        return FileResponse(
            path=temp_path,
            filename=f"{strategy_id}.py",
            media_type="text/x-python",
        )

    elif format == "zip":
        # ZIP Export (YAML + Python)
        yaml_content = StrategyFileSaver.to_yaml_string(definition)
        python_content = PythonExporter.to_python_string(definition)

        # 메모리에 ZIP 생성
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"{strategy_id}.kis.yaml", yaml_content)
            zf.writestr(f"{strategy_id}.py", python_content)

        zip_buffer.seek(0)

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{strategy_id}.zip"'
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
    from kis_backtest.file.loader import StrategyFileLoader
    
    try:
        content = await file.read()
        content_str = content.decode("utf-8")
        strategy_file = StrategyFileLoader.load_from_string(content_str)
        
        # 추가 검증
        errors = []
        if not strategy_file.strategy.indicators:
            errors.append("No indicators defined")
        if not strategy_file.strategy.entry.conditions:
            errors.append("No entry conditions defined")
        if not strategy_file.strategy.exit.conditions:
            errors.append("No exit conditions defined")
        
        return {
            "success": len(errors) == 0,
            "data": {
                "id": strategy_file.strategy.id,
                "name": strategy_file.metadata.name,
                "valid": len(errors) == 0,
                "errors": errors,
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
