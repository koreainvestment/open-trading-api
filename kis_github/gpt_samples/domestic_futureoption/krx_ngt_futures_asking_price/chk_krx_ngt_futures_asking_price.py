"""
Created on 20250601
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from krx_ngt_futures_asking_price import krx_ngt_futures_asking_price

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 실시간시세 > KRX야간선물 실시간호가 [실시간-065]
##############################################################################################

COLUMN_MAPPING = {
    "futs_shrn_iscd": "선물 단축 종목코드",
    "bsop_hour": "영업 시간",
    "futs_askp1": "선물 매도호가1",
    "futs_askp2": "선물 매도호가2",
    "futs_askp3": "선물 매도호가3",
    "futs_askp4": "선물 매도호가4",
    "futs_askp5": "선물 매도호가5",
    "futs_bidp1": "선물 매수호가1",
    "futs_bidp2": "선물 매수호가2",
    "futs_bidp3": "선물 매수호가3",
    "futs_bidp4": "선물 매수호가4",
    "futs_bidp5": "선물 매수호가5",
    "askp_csnu1": "매도호가 건수1",
    "askp_csnu2": "매도호가 건수2",
    "askp_csnu3": "매도호가 건수3",
    "askp_csnu4": "매도호가 건수4",
    "askp_csnu5": "매도호가 건수5",
    "bidp_csnu1": "매수호가 건수1",
    "bidp_csnu2": "매수호가 건수2",
    "bidp_csnu3": "매수호가 건수3",
    "bidp_csnu4": "매수호가 건수4",
    "bidp_csnu5": "매수호가 건수5",
    "askp_rsqn1": "매도호가 잔량1",
    "askp_rsqn2": "매도호가 잔량2",
    "askp_rsqn3": "매도호가 잔량3",
    "askp_rsqn4": "매도호가 잔량4",
    "askp_rsqn5": "매도호가 잔량5",
    "bidp_rsqn1": "매수호가 잔량1",
    "bidp_rsqn2": "매수호가 잔량2",
    "bidp_rsqn3": "매수호가 잔량3",
    "bidp_rsqn4": "매수호가 잔량4",
    "bidp_rsqn5": "매수호가 잔량5",
    "total_askp_csnu": "총 매도호가 건수",
    "total_bidp_csnu": "총 매수호가 건수",
    "total_askp_rsqn": "총 매도호가 잔량",
    "total_bidp_rsqn": "총 매수호가 잔량",
    "total_askp_rsqn_icdc": "총 매도호가 잔량 증감",
    "total_bidp_rsqn_icdc": "총 매수호가 잔량 증감"
}

NUMERIC_COLUMNS = []


def main():
    """
    KRX야간선물 실시간호가 조회 테스트 함수

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
    kws.subscribe(request=krx_ngt_futures_asking_price, data=["101W09"])

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
