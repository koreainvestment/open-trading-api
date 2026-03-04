"""Response helper schemas for MCP tools."""

from __future__ import annotations

from typing import Any, Optional


def success_response(data: Any, message: Optional[str] = None) -> dict:
    """표준 성공 응답 포맷."""
    result: dict = {"success": True, "data": data}
    if message:
        result["message"] = message
    return result


def error_response(error: str, details: Optional[Any] = None) -> dict:
    """표준 오류 응답 포맷."""
    result: dict = {"success": False, "error": error}
    if details is not None:
        result["details"] = details
    return result
