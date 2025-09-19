from .base import BaseTool
from module import singleton


@singleton
class ElwTool(BaseTool):
    @property
    def tool_name(self) -> str:
        return "elw"
