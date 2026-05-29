from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import time
from pathlib import Path


def _env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def parse_account(account_value: str) -> tuple[str, str]:
    cleaned = re.sub(r"\s+", "", account_value)
    if "-" in cleaned:
        front, back = cleaned.split("-", 1)
        if len(front) == 8 and len(back) == 2 and front.isdigit() and back.isdigit():
            return front, back

    digits = re.sub(r"\D", "", cleaned)
    if len(digits) == 10:
        return digits[:8], digits[8:]

    raise ValueError(
        "GH_ACCOUNT must contain the KIS account number in 8-2 format, for example '12345678-01' or '1234567801'."
    )


@dataclass(frozen=True)
class Settings:
    account_number: str
    account_product_code: str
    appkey: str
    appsecret: str
    base_url: str
    symbol: str = "005930"
    market_code: str = "J"
    order_quantity: int = 1
    price_offset_krw: int = 1000
    poll_interval_seconds: int = 180
    verify_delay_seconds: int = 5
    request_timeout_seconds: int = 10
    retry_count: int = 2
    retry_backoff_seconds: float = 2.0
    trading_start: time = time(9, 10)
    trading_end: time = time(15, 30)
    token_cache_path: Path = Path(__file__).resolve().parent / "token_cache.json"

    @classmethod
    def from_env(cls) -> "Settings":
        account_number, account_product_code = parse_account(_env("GH_ACCOUNT"))
        appkey = _env("GH_APPKEY")
        appsecret = _env("GH_APPSECRET")

        base_url = os.getenv("KIS_BASE_URL", "https://openapivts.koreainvestment.com:29443")
        symbol = os.getenv("TRADING_SYMBOL", "005930")
        market_code = os.getenv("TRADING_MARKET_CODE", "J")
        order_quantity = int(os.getenv("TRADING_ORDER_QTY", "1"))
        price_offset_krw = int(os.getenv("TRADING_PRICE_OFFSET_KRW", "1000"))
        poll_interval_seconds = int(os.getenv("TRADING_POLL_SECONDS", "180"))
        verify_delay_seconds = int(os.getenv("TRADING_VERIFY_DELAY_SECONDS", "5"))
        request_timeout_seconds = int(os.getenv("TRADING_REQUEST_TIMEOUT_SECONDS", "10"))
        retry_count = int(os.getenv("TRADING_RETRY_COUNT", "2"))
        retry_backoff_seconds = float(os.getenv("TRADING_RETRY_BACKOFF_SECONDS", "2"))

        cache_path = Path(os.getenv("TRADING_TOKEN_CACHE_PATH", str(cls.token_cache_path)))

        return cls(
            account_number=account_number,
            account_product_code=account_product_code,
            appkey=appkey,
            appsecret=appsecret,
            base_url=base_url,
            symbol=symbol,
            market_code=market_code,
            order_quantity=order_quantity,
            price_offset_krw=price_offset_krw,
            poll_interval_seconds=poll_interval_seconds,
            verify_delay_seconds=verify_delay_seconds,
            request_timeout_seconds=request_timeout_seconds,
            retry_count=retry_count,
            retry_backoff_seconds=retry_backoff_seconds,
            token_cache_path=cache_path,
        )
