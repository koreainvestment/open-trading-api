import sys
import os
import logging
import importlib.util

# 현재 스크립트의 디렉토리 기준으로 경로 설정
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
sys.path.insert(0, os.path.join(script_dir, "examples_llm"))
sys.path.insert(0, os.path.join(script_dir, "examples_user/domestic_stock"))

import kis_auth as ka

# 모듈 직접 로드
spec = importlib.util.spec_from_file_location("domestic_stock_functions", 
                                               os.path.join(script_dir, "examples_user/domestic_stock/domestic_stock_functions.py"))
domestic_stock_functions = importlib.util.module_from_spec(spec)
sys.modules["domestic_stock_functions"] = domestic_stock_functions
spec.loader.exec_module(domestic_stock_functions)

inquire_daily_price = domestic_stock_functions.inquire_daily_price

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

STOCK_CODE = "005930"        # 삼성전자
INITIAL_CASH = 100_000_000   # 초기자본 1억원
INITIAL_STOCK_QTY = 0        # 초기 보유수량

# 하락 시: 현금 비율 기반 매수
BUY_RULES = [
    (-5, 0.30),    # -5% 이하 하락 → 현금 30% 매수
    (-3, 0.20),    # -3% 이하 하락 → 현금 20% 매수
    (-1.5, 0.10),  # -1.5% 이하 하락 → 현금 10% 매수
]

# 상승 시: 보유수량 비율 기반 매도
SELL_RULES = [
    (7, 0.45),     # +7% 이상 상승 → 보유수량 75% 매도
    (4, 0.30),     # +4% 이상 상승 → 보유수량 50% 매도
    (2, 0.15),     # +2% 이상 상승 → 보유수량 25% 매도
]

ka.auth(svr="vps", product="01")

df = inquire_daily_price(
    "demo",
    "J",
    STOCK_CODE,
    "D",
    "1"
)

df = df.iloc[::-1].reset_index(drop=True)

first_close = int(df.loc[0, "stck_clpr"])

cash = INITIAL_CASH - first_close * INITIAL_STOCK_QTY
stock_qty = INITIAL_STOCK_QTY

print("========== 백테스트 시작 ==========")

for i in range(1, len(df)):
    date = df.loc[i, "stck_bsop_date"]

    today_close = int(df.loc[i, "stck_clpr"])
    yesterday_close = int(df.loc[i - 1, "stck_clpr"])

    change_rate = ((today_close - yesterday_close) / yesterday_close) * 100

    action = "hold"
    qty = 0
    trade_amount = 0

    # 매수 조건: 현금 비율 기반
    for rate, cash_ratio in BUY_RULES:
        if change_rate <= rate:
            action = "buy"
            buy_amount = cash * cash_ratio
            qty = int(buy_amount // today_close)
            trade_amount = qty * today_close
            break

    # 매도 조건: 보유수량 비율 기반
    for rate, sell_ratio in SELL_RULES:
        if change_rate >= rate:
            action = "sell"
            qty = int(stock_qty * sell_ratio)
            trade_amount = qty * today_close
            break

    if action == "buy":
        if qty > 0 and cash >= trade_amount:
            cash -= trade_amount
            stock_qty += qty
        else:
            action = "hold"
            qty = 0
            trade_amount = 0

    elif action == "sell":
        sell_qty = min(qty, stock_qty)

        if sell_qty > 0:
            qty = sell_qty
            trade_amount = qty * today_close
            cash += trade_amount
            stock_qty -= qty
        else:
            action = "hold"
            qty = 0
            trade_amount = 0

    total_asset = cash + stock_qty * today_close

    logging.info(
        f"{date} | "
        f"종가 {today_close:,} | "
        f"등락률 {change_rate:.2f}% | "
        f"{action} {qty}주 | "
        f"거래금액 {trade_amount:,.0f} | "
        f"현금 {cash:,.0f} | "
        f"보유 {stock_qty}주 | "
        f"총자산 {total_asset:,.0f}"
    )

final_price = int(df.iloc[-1]["stck_clpr"])
final_asset = cash + stock_qty * final_price
profit = final_asset - INITIAL_CASH
profit_rate = profit / INITIAL_CASH * 100

print("\n========== 백테스트 결과 ==========")
print(f"초기자본: {INITIAL_CASH:,.0f}원")
print(f"초기 보유수량: {INITIAL_STOCK_QTY}주")
print(f"최종자산: {final_asset:,.0f}원")
print(f"손익: {profit:,.0f}원")
print(f"수익률: {profit_rate:.2f}%")
print(f"최종 보유수량: {stock_qty}주")
