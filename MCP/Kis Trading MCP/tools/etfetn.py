from .base import BaseTool
from module import singleton


@singleton
class EtfEtnTool(BaseTool):
    @property
    def tool_name(self) -> str:
        return "etfetn"
