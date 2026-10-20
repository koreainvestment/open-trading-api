"""Configuration for Samsung auto trader."""

from __future__ import annotations

import os
from datetime import datetime, time
from zoneinfo import ZoneInfo
from pathlib import Path

# Credentials from Codespaces/GitHub secrets
GH_ACCOUNT = os.getenv("GH_ACCOUNT", "").strip()
GH_APPKEY = os.getenv("GH_APPKEY", "").strip()
GH_APPSECRET = os.getenv("GH_APPSECRET", "").strip()

# Market and strategy config
STOCK_CODE = "005930"
STOCK_NAME = "Samsung Electronics"
PRICE_OFFSET = 100
ORDER_QUANTITY = 1
MAX_HOLDINGS_QTY = 12
CONSECUTIVE_BUY_LIMIT = 3
BUY_PAUSE_SECONDS = 120

# Run window in Korea time
KST = ZoneInfo("Asia/Seoul")
TRADING_START = time(9, 10)
TRADING_END = time(15, 30)

# API config
API_BASE_URL = "https://openapivts.koreainvestment.com:29443"
ACNT_PRDT_CD = "01"
ORD_DVSN_LIMIT = "00"

# Correct domestic price quote TR/endpoint pair
TR_ID_GET_PRICE = "FHKST01010100"
TR_ID_INQUIRE_BALANCE = "TTTC8434R"
TR_ID_BUY_ORDER = "TTTC0802U"
TR_ID_SELL_ORDER = "TTTC0801U"
TR_ID_INQUIRE_DAILY_CCLD = "TTTC8001R"
TR_ID_ORDER_CANCEL = "TTTC0803U"

# Runtime
POLLING_INTERVAL = 8
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2
BUY_EXECUTION_WAIT_SECONDS = 20
BUY_EXECUTION_POLL_SECONDS = 3
API_MIN_REQUEST_INTERVAL_SECONDS = 0.7
RATE_LIMIT_BACKOFF_SECONDS = 2
PENDING_CANCEL_AFTER_SECONDS = 45
TOKEN_CACHE_FILE = "token_cache.json"
BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = str(BASE_DIR / "logs" / "trader.log")


def validate_credentials() -> None:
	missing = []
	if not GH_ACCOUNT:
		missing.append("GH_ACCOUNT")
	if not GH_APPKEY:
		missing.append("GH_APPKEY")
	if not GH_APPSECRET:
		missing.append("GH_APPSECRET")
	if missing:
		raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


def now_kst() -> datetime:
	return datetime.now(tz=KST)


def is_within_trading_window(dt: datetime | None = None) -> bool:
	current = dt or now_kst()
	t = current.time()
	return TRADING_START <= t <= TRADING_END

