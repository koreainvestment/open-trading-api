import sys
import os
import logging
import time
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

order_cash = domestic_stock_functions.order_cash
inquire_price = domestic_stock_functions.inquire_price
inquire_balance = domestic_stock_functions.inquire_balance

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

STOCK_CODE = "034020"  # 두산에너빌리티
INTERVAL = 60 * 10     # 10분

BUY_RULES = [
    (-30, 0.25),    # -30% 이하 하락 시 현금의 50% 매수
    (-25, 0.05),    # -25% 이하 하락 시 현금의 40% 매수
    (-20, 0.10),    # -20% 이하 하락 시 현금의 30% 매수
    (-15, 0.20),    # -15% 이하 하락 시 현금의 20% 매수
    (-10, 0.30),    # -10% 이하 하락 시 현금의 10% 매수
    (-5, 0.40),    # -5% 이하 하락 시 현금의 5% 매수
    (-2.5, 0.50),    # -2.5% 이하 하락 시 현금의 2.5% 매수
]

SELL_RULES = [
    (30, 0.75),     # +30% 이상 상승 시 보유수량의 75% 매도
    (25, 0.625),     # +25% 이상 상승 시 보유수량의 62.5% 매도
    (20, 0.5),     # +20% 이상 상승 시 보유수량의 50% 매도
    (15, 0.375),     # +15% 이상 상승 시 보유수량의 37.5% 매도
    (10, 0.25),     # +10% 이상 상승 시 보유수량의 25% 매도
    (5, 0.125),     # +5% 이상 상승 시 보유수량의 12.5% 매도
    (2.5, 0.0625),     # +2.5% 이상 상승 시 보유수량의 6.25% 매도

]

ka.auth(svr="vps", product="01")
trenv = ka.getTREnv()

logging.info("모의투자 인증 완료")


def get_action_and_qty(change_rate, current_price, holding_qty):
    """
    등락률에 따라 매수/매도 방향과 수량을 결정한다.
    매수: 현재 현금의 일정 비율로 매수
    매도: 현재 보유수량의 일정 비율로 매도
    """

    # 하락 시 현금 비율 기반 매수
    for rate, cash_ratio in BUY_RULES:
        if change_rate <= rate:
            estimated_cash = get_available_cash()
            buy_amount = estimated_cash * cash_ratio
            qty = int(buy_amount // current_price)

            return "buy", max(qty, 0)

    # 상승 시 보유수량 비율 기반 매도
    for rate, sell_ratio in SELL_RULES:
        if change_rate >= rate:
            qty = int(holding_qty * sell_ratio)

            return "sell", max(qty, 0)

    return "hold", 0


def get_current_holding_qty():
    balance_df, summary_df = inquire_balance(
        env_dv="demo",
        cano=trenv.my_acct,
        acnt_prdt_cd=trenv.my_prod,
        afhr_flpr_yn="N",
        inqr_dvsn="01",
        unpr_dvsn="01",
        fund_sttl_icld_yn="N",
        fncg_amt_auto_rdpt_yn="N",
        prcs_dvsn="00"
    )

    if balance_df is None or len(balance_df) == 0:
        return 0

    doosan = balance_df[balance_df["pdno"] == STOCK_CODE]

    if len(doosan) == 0:
        return 0

    return int(doosan.iloc[0]["hldg_qty"])

def get_available_cash():
    balance_df, summary_df = inquire_balance(
        env_dv="demo",
        cano=trenv.my_acct,
        acnt_prdt_cd=trenv.my_prod,
        afhr_flpr_yn="N",
        inqr_dvsn="01",
        unpr_dvsn="01",
        fund_sttl_icld_yn="N",
        fncg_amt_auto_rdpt_yn="N",
        prcs_dvsn="00"
    )

    if summary_df is None or len(summary_df) == 0:
        return 0

    # 주문가능현금 컬럼 후보들
    cash_columns = [
        "dnca_tot_amt",
        "ord_psbl_cash",
        "nass_amt",
        "tot_evlu_amt",
    ]

    for col in cash_columns:
        if col in summary_df.columns:
            try:
                return int(float(summary_df.iloc[0][col]))
            except:
                pass

    return 0

cash = get_available_cash()
logging.info(f"주문가능현금: {cash:,}원")

def initial_buy():
    holding_qty = get_current_holding_qty()

    if holding_qty >= 30:
        logging.info("초기 보유수량 충족")
        return

    buy_qty = 30 - holding_qty

    logging.info(f"초기 진입 → 두산에너빌리티 {buy_qty}주 매수")

    df = order_cash(
        env_dv="demo",
        ord_dv="buy",
        cano=trenv.my_acct,
        acnt_prdt_cd=trenv.my_prod,
        pdno=STOCK_CODE,
        ord_dvsn="01",
        ord_qty=str(buy_qty),
        ord_unpr="0",
        excg_id_dvsn_cd="KRX"
    )

    print(df)

initial_buy()

while True:
    try:
        price_df = inquire_price("demo", "J", STOCK_CODE)

        current_price = int(price_df["stck_prpr"][0])
        previous_close = int(price_df["stck_sdpr"][0])

        change_rate = ((current_price - previous_close) / previous_close) * 100

        holding_qty = get_current_holding_qty()

        logging.info(f"종목: {STOCK_CODE}")
        logging.info(f"현재가: {current_price:,}")
        logging.info(f"전일종가: {previous_close:,}")
        logging.info(f"전일종가 대비 등락률: {change_rate:.2f}%")
        logging.info(f"현재 보유수량: {holding_qty}주")

        ACTION, QTY = get_action_and_qty(change_rate, current_price, holding_qty)

        if ACTION == "hold":
            logging.info("조건 미충족 → 주문하지 않음")

        elif ACTION == "sell":
            sell_qty = min(QTY, holding_qty)

            if sell_qty <= 0:
                logging.info("매도 조건 충족했지만 보유수량이 없어 매도하지 않음")

            else:
                logging.info(f"매도 조건 충족 → 시장가 매도 {sell_qty}주")

                df = order_cash(
                    env_dv="demo",
                    ord_dv="sell",
                    cano=trenv.my_acct,
                    acnt_prdt_cd=trenv.my_prod,
                    pdno=STOCK_CODE,
                    ord_dvsn="01",
                    ord_qty=str(sell_qty),
                    ord_unpr="0",
                    excg_id_dvsn_cd="KRX"
                )

                logging.info("주문 결과")
                print(df)

        elif ACTION == "buy":
            if QTY <= 0:
                logging.info("매수 조건 충족했지만 주문가능현금이 부족하여 매수하지 않음")
                continue

            logging.info(f"매수 조건 충족 → 시장가 매수 {QTY}주")
            df = order_cash(
                env_dv="demo",
                ord_dv="buy",
                cano=trenv.my_acct,
                acnt_prdt_cd=trenv.my_prod,
                pdno=STOCK_CODE,
                ord_dvsn="01",
                ord_qty=str(QTY),
                ord_unpr="0",
                excg_id_dvsn_cd="KRX"
            )

            logging.info("주문 결과")
            print(df)

    except Exception as e:
        logging.error(f"오류 발생: {e}")

    logging.info("10분 대기 후 다시 실행")
    time.sleep(INTERVAL)