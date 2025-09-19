from .base import BaseTool
from module import singleton


@singleton
class DomesticStockTool(BaseTool):
    @property
    def tool_name(self) -> str:
        return "domestic_stock"
