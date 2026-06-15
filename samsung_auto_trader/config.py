import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    symbol: str = "005930"
    market_division_code: str = "J"
    order_offset_krw: int = 2000
    start_time_str: str = "09:10"
    end_time_str: str = "15:30"
    token_cache_file: str = "token_cache.json"
    default_product_code: str = "01"
    dry_run: bool = True
    paper_trading: bool = True
    polling_interval_seconds: int = 30
    order_timeout_seconds: int = 10
    retry_interval_seconds: int = 5
    max_retries: int = 2

    @property
    def gh_account(self) -> str:
        return os.getenv("GH_ACCOUNT", "").strip()

    @property
    def gh_appkey(self) -> str:
        return os.getenv("GH_APPKEY", "").strip()

    @property
    def gh_appsecret(self) -> str:
        return os.getenv("GH_APPSECRET", "").strip()

    @property
    def gh_product_code(self) -> str:
        return os.getenv("GH_PRODUCT_CODE", self.default_product_code).strip()

    @property
    def is_trading_window_enabled(self) -> bool:
        return bool(self.gh_appkey and self.gh_appsecret and self.gh_account)


config = Config()
