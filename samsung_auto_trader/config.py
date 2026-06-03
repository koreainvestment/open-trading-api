import os

APP_KEY = os.getenv("GH_APPKEY")
APP_SECRET = os.getenv("GH_APPSECRET")
ACCOUNT = os.getenv("GH_ACCOUNT")

SYMBOL = "005930"

TRADING_START = "09:10"
TRADING_END = "15:30"

POLL_INTERVAL_SECONDS = 60
ORDER_PRICE_GAP = 1000

MOCK_BASE_URL = "https://openapivts.koreainvestment.com:29443"
