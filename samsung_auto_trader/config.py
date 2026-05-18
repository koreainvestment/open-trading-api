import os
from pathlib import Path
from dataclasses import dataclass

BASE_DIR = Path(__file__).resolve().parent
TOKEN_CACHE_FILE = BASE_DIR / "token_cache.json"

@dataclass(frozen=True)
class AppConfig:
    account_no: str
    app_key: str
    app_secret: str
    token_url: str
    base_url: str
    polling_interval_seconds: int
    trading_start: str
    trading_end: str


def load_config() -> AppConfig:
    account_no = os.environ.get("GH_ACCOUNT", "")
    app_key = os.environ.get("GH_APPKEY", "")
    app_secret = os.environ.get("GH_APPSECRET", "")

    if not account_no or not app_key or not app_secret:
        raise EnvironmentError(
            "Missing required environment variables: GH_ACCOUNT, GH_APPKEY, GH_APPSECRET"
        )

    return AppConfig(
        account_no=account_no,
        app_key=app_key,
        app_secret=app_secret,
        token_url="https://openapivts.koreainvestment.com:29443/oauth2/tokenP",
        base_url="https://openapivts.koreainvestment.com:29443",
        polling_interval_seconds=60,
        trading_start="09:10",
        trading_end="15:30",
    )


# Endpoints can be adjusted if the exact coverage differs from the official KIS Open API.
ENDPOINTS = {
    "price_inquiry": "/uapi/domestic-stock/v1/quotations/inquire-price",
    "balance_inquiry": "/uapi/domestic-stock/v1/trading/inquire-balance",
    "holdings_inquiry": "/uapi/domestic-stock/v1/trading/inquire-psbl-stock",
    "order_submission": "/uapi/domestic-stock/v1/trading/order-cash",
}
