from .base import BaseTool
from module import singleton


@singleton
class AuthTool(BaseTool):
    @property
    def tool_name(self) -> str:
        return "auth"
