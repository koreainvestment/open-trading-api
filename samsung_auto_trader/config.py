import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

APP_KEY = os.getenv("GH_APPKEY")
APP_SECRET = os.getenv("GH_APPSECRET")
ACCOUNT = os.getenv("GH_ACCOUNT")

if not APP_KEY:
    raise RuntimeError("GH_APPKEY environment variable is missing.")
if not APP_SECRET:
    raise RuntimeError("GH_APPSECRET environment variable is missing.")
if not ACCOUNT:
    raise RuntimeError("GH_ACCOUNT environment variable is missing.")

# GH_ACCOUNT 예시:
# 12345678-01 또는 1234567801
ACCOUNT_CLEAN = ACCOUNT.replace("-", "")
CANO = ACCOUNT_CLEAN[:8]
ACNT_PRDT_CD = ACCOUNT_CLEAN[8:10]

SYMBOL = "005930"
MARKET_DIV_CODE = "J"

MOCK_BASE_URL = "https://openapivts.koreainvestment.com:29443"

TOKEN_CACHE_FILE = BASE_DIR / "token_cache.json"

TRADING_START = "09:10"
TRADING_END = "15:30"

POLL_INTERVAL_SECONDS = 60
ORDER_PRICE_GAP = 1000
DEFAULT_ORDER_QTY = 1

REQUEST_TIMEOUT_SECONDS = 10
MAX_RETRIES = 2
RETRY_SLEEP_SECONDS = 1

# API paths
PATH_TOKEN = "/oauth2/tokenP"
PATH_INQUIRE_PRICE = "/uapi/domestic-stock/v1/quotations/inquire-price"
PATH_INQUIRE_BALANCE = "/uapi/domestic-stock/v1/trading/inquire-balance"
PATH_ORDER_CASH = "/uapi/domestic-stock/v1/trading/order-cash"

# TR IDs
TR_ID_PRICE = "FHKST01010100"
TR_ID_BALANCE_DEMO = "VTTC8434R"
TR_ID_BUY_DEMO = "VTTC0012U"
TR_ID_SELL_DEMO = "VTTC0011U"
