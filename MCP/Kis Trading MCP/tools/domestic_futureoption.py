from .base import BaseTool
from module import singleton
import pandas as pd
import urllib.request
import ssl
import zipfile
import os


@singleton
class DomesticFutureOptionTool(BaseTool):
    @property
    def tool_name(self) -> str:
        return "domestic_futureoption"
    