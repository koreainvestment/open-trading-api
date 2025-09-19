from .base import BaseTool
from module import singleton


@singleton
class DomesticBondTool(BaseTool):
    @property
    def tool_name(self) -> str:
        return "domestic_bond"
    
