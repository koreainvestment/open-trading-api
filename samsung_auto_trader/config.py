# 설정값들 한 곳에 모아두기
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

#GitHub Codespaces Secret 또는 환경변수에서 API key, secret, 계좌번호를 불러온다.
APP_KEY = "PSzJDY1n4UEorZOCtijH5BoKKSCldXsr25fU"
APP_SECRET = esK0A1W5CZY3IrkBYkC0Bx2KJ/Lo3tcoFMH/QHuxAl7l8dHA5zcj/qDJa7+mSR43MiYE7u475e3ZAm5NyVxM6OqOadFutx3aHtyU0sctCqsdjjkzp2+bHDY4+0Yu2GZe8yn6KG4rGX40wkgE/5FK4AK70HFiiSHUveO8XNCX/7ThcA/oRno=
ACCOUNT = "5017750401"

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
ORDER_PRICE_GAP = 2000
DEFAULT_ORDER_QTY = 1

REQUEST_TIMEOUT_SECONDS = 20
MAX_RETRIES = 2
RETRY_SLEEP_SECONDS = 1

# API paths
PATH_TOKEN = "/oauth2/tokenP"
PATH_INQUIRE_PRICE = "/uapi/domestic-stock/v1/quotations/inquire-price"
PATH_INQUIRE_BALANCE = "/uapi/domestic-stock/v1/trading/inquire-balance"
PATH_ORDER_CASH = "/uapi/domestic-stock/v1/trading/order-cash"

# TR IDs  # 한국투자 API가 어떤 요청인지 구분하는 코드
TR_ID_PRICE = "FHKST01010100"
TR_ID_BALANCE = "VTTC8434R"
TR_ID_BUY = "VTTC0012U"
TR_ID_SELL = "VTTC0011U"
