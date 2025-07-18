"""
Created on 20250601
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from stock_option_asking_price import stock_option_asking_price

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 실시간시세 > 주식옵션 실시간호가 [실시간-045]
##############################################################################################

COLUMN_MAPPING = {
    "optn_shrn_iscd": "종목코드",
    "bsop_hour": "영업시간",
    "optn_askp1": "옵션매도호가1",
    "optn_askp2": "옵션매도호가2",
    "optn_askp3": "옵션매도호가3",
    "optn_askp4": "옵션매도호가4",
    "optn_askp5": "옵션매도호가5",
    "optn_bidp1": "옵션매수호가1",
    "optn_bidp2": "옵션매수호가2",
    "optn_bidp3": "옵션매수호가3",
    "optn_bidp4": "옵션매수호가4",
    "optn_bidp5": "옵션매수호가5",
    "askp_csnu1": "매도호가건수1",
    "askp_csnu2": "매도호가건수2",
    "askp_csnu3": "매도호가건수3",
    "askp_csnu4": "매도호가건수4",
    "askp_csnu5": "매도호가건수5",
    "bidp_csnu1": "매수호가건수1",
    "bidp_csnu2": "매수호가건수2",
    "bidp_csnu3": "매수호가건수3",
    "bidp_csnu4": "매수호가건수4",
    "bidp_csnu5": "매수호가건수5",
    "askp_rsqn1": "매도호가잔량1",
    "askp_rsqn2": "매도호가잔량2",
    "askp_rsqn3": "매도호가잔량3",
    "askp_rsqn4": "매도호가잔량4",
    "askp_rsqn5": "매도호가잔량5",
    "bidp_rsqn1": "매수호가잔량1",
    "bidp_rsqn2": "매수호가잔량2",
    "bidp_rsqn3": "매수호가잔량3",
    "bidp_rsqn4": "매수호가잔량4",
    "bidp_rsqn5": "매수호가잔량5",
    "total_askp_csnu": "총매도호가건수",
    "total_bidp_csnu": "총매수호가건수",
    "total_askp_rsqn": "총매도호가잔량",
    "total_bidp_rsqn": "총매수호가잔량",
    "total_askp_rsqn_icdc": "총매도호가잔량증감",
    "total_bidp_rsqn_icdc": "총매수호가잔량증감",
    "optn_askp6": "옵션매도호가6",
    "optn_askp7": "옵션매도호가7",
    "optn_askp8": "옵션매도호가8",
    "optn_askp9": "옵션매도호가9",
    "optn_askp10": "옵션매도호가10",
    "optn_bidp6": "옵션매수호가6",
    "optn_bidp7": "옵션매수호가7",
    "optn_bidp8": "옵션매수호가8",
    "optn_bidp9": "옵션매수호가9",
    "optn_bidp10": "옵션매수호가10",
    "askp_csnu6": "매도호가건수6",
    "askp_csnu7": "매도호가건수7",
    "askp_csnu8": "매도호가건수8",
    "askp_csnu9": "매도호가건수9",
    "askp_csnu10": "매도호가건수10",
    "bidp_csnu6": "매수호가건수6",
    "bidp_csnu7": "매수호가건수7",
    "bidp_csnu8": "매수호가건수8",
    "bidp_csnu9": "매수호가건수9",
    "bidp_csnu10": "매수호가건수10",
    "askp_rsqn6": "매도호가잔량6",
    "askp_rsqn7": "매도호가잔량7",
    "askp_rsqn8": "매도호가잔량8",
    "askp_rsqn9": "매도호가잔량9",
    "askp_rsqn10": "매도호가잔량10",
    "bidp_rsqn6": "매수호가잔량6",
    "bidp_rsqn7": "매수호가잔량7",
    "bidp_rsqn8": "매수호가잔량8",
    "bidp_rsqn9": "매수호가잔량9",
    "bidp_rsqn10": "매수호가잔량10"
}

NUMERIC_COLUMNS = []


def main():
    """
    국내선물옵션 주식옵션 실시간호가

    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 인증 토큰 발급
    ka.auth()
    ka.auth_ws()

    # 인증(auth_ws()) 이후에 선언
    kws = ka.KISWebSocket(api_url="/tryitout")

    # 조회
    kws.subscribe(request=stock_option_asking_price, data=["239W08090"])

    # 결과 표시
    def on_result(ws, tr_id: str, result: pd.DataFrame, data_map: dict):

        result = result.rename(columns=COLUMN_MAPPING)

        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

        logging.info("결과:")
        print(result)

    kws.start(on_result=on_result)


if __name__ == "__main__":
    main()
