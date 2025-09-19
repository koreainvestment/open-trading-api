from .base import BaseTool
from module import singleton


@singleton
class OverseasFutureOptionTool(BaseTool):
    @property
    def tool_name(self) -> str:
        return "overseas_futureoption"
