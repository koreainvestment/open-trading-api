from .base import BaseTool
from module import singleton


@singleton
class OverseasStockTool(BaseTool):
    @property
    def tool_name(self) -> str:
        return "overseas_stock"
