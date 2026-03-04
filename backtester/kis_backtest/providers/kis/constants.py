"""한국투자증권 API 상수

TR ID, API 경로, 주문 구분 코드 등 상수 정의.
URL은 kis_auth.py에서 관리하므로 여기서는 제거됨.
"""

# ============================================
# TR ID (트랜잭션 ID)
# ============================================

class TrId:
    """트랜잭션 ID 상수"""
    
    # 일봉 조회
    DAILY_PRICE = "FHKST03010100"
    
    # 분봉 조회
    MINUTE_PRICE = "FHKST03010200"
    
    # 호가 조회
    ASKING_PRICE = "FHKST01010200"
    
    # 현금 매수 (실전)
    CASH_BUY_REAL = "TTTC0802U"
    # 현금 매도 (실전)
    CASH_SELL_REAL = "TTTC0801U"
    # 현금 매수 (모의)
    CASH_BUY_PAPER = "VTTC0802U"
    # 현금 매도 (모의)
    CASH_SELL_PAPER = "VTTC0801U"
    
    # 주문 취소 (실전/모의)
    ORDER_CANCEL_REAL = "TTTC0803U"
    ORDER_CANCEL_PAPER = "VTTC0803U"
    
    # 잔고 조회 (실전/모의)
    BALANCE_REAL = "TTTC8434R"
    BALANCE_PAPER = "VTTC8434R"
    
    # 체결 조회 (실전/모의)
    ORDERS_REAL = "TTTC8001R"
    ORDERS_PAPER = "VTTC8001R"
    
    # 해외주식 일봉
    OVERSEAS_DAILY = "HHDFS76240000"
    
    # 웹소켓 실시간
    WS_REALTIME_PRICE = "H0STCNT0"      # 실시간 체결가
    WS_REALTIME_NOTICE = "H0STCNI0"     # 체결 통보

    # 업종 지수
    INDEX_DAILY = "FHKUP03500100"       # 업종기간별시세 (KOSPI: 0001, KOSDAQ: 1001)


# ============================================
# API 경로
# ============================================

class ApiPath:
    """API 경로"""
    
    # 인증
    TOKEN = "/oauth2/tokenP"
    
    # 국내주식 시세
    DOMESTIC_DAILY = "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
    DOMESTIC_MINUTE = "/uapi/domestic-stock/v1/quotations/inquire-time-dailychartprice"
    DOMESTIC_ASKING = "/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn"
    
    # 국내주식 주문
    DOMESTIC_ORDER = "/uapi/domestic-stock/v1/trading/order-cash"
    DOMESTIC_CANCEL = "/uapi/domestic-stock/v1/trading/order-rvsecncl"
    
    # 국내주식 조회
    DOMESTIC_BALANCE = "/uapi/domestic-stock/v1/trading/inquire-balance"
    DOMESTIC_ORDERS = "/uapi/domestic-stock/v1/trading/inquire-daily-ccld"
    
    # 해외주식
    OVERSEAS_DAILY = "/uapi/overseas-price/v1/quotations/dailyprice"

    # 업종 지수
    INDEX_DAILY = "/uapi/domestic-stock/v1/quotations/inquire-daily-indexchartprice"


# ============================================
# 주문 구분 코드
# ============================================

class OrderDivision:
    """주문구분코드"""
    
    LIMIT = "00"       # 지정가
    MARKET = "01"      # 시장가
    CONDITION = "02"   # 조건부지정가
    BEST = "03"        # 최유리지정가
    FIRST = "04"       # 최우선지정가


# ============================================
# 거래소 코드 매핑
# ============================================

EXCHANGE_TO_KIS = {
    "nasdaq": "NAS",
    "nyse": "NYS",
    "amex": "AMS",
    "hkex": "HKS",
    "shse": "SHS",
    "szse": "SZS",
    "tse": "TSE",
}
