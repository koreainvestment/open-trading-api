import logging

from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext

try:
    from fastmcp.server.dependencies import get_http_headers
except ImportError:
    get_http_headers = None


class McpAuthMiddleware(Middleware):
    """SSE/HTTP MCP 전송 시 액세스 토큰 검증"""

    def __init__(self, mcp_type: str, access_token: str | None):
        self.mcp_type = mcp_type
        self.access_token = access_token

    def _requires_auth(self) -> bool:
        return self.mcp_type in ("sse", "streamable-http")

    async def on_request(self, context: MiddlewareContext, call_next):
        if not self._requires_auth():
            return await call_next(context)

        if not self.access_token:
            raise ToolError("Unauthorized: MCP_ACCESS_TOKEN is not configured")

        if get_http_headers is None:
            raise ToolError("Unauthorized: HTTP authentication is not available")

        headers = get_http_headers() or {}
        auth_header = headers.get("authorization") or headers.get("Authorization", "")
        api_key = headers.get("x-api-key") or headers.get("X-Api-Key", "")

        if auth_header == f"Bearer {self.access_token}" or api_key == self.access_token:
            return await call_next(context)

        raise ToolError("Unauthorized: invalid or missing MCP access token")


def ensure_http_access_token(mcp_type: str, access_token: str | None) -> str:
    """HTTP/SSE 모드에서는 MCP_ACCESS_TOKEN 필수"""
    token = (access_token or "").strip()
    if mcp_type in ("sse", "streamable-http") and not token:
        logging.error(
            "MCP_ACCESS_TOKEN must be set when MCP_TYPE is '%s'. "
            "Generate a strong random token and pass it to the server and MCP clients.",
            mcp_type,
        )
        raise SystemExit(1)
    return token
