"""
Created on 20250601
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from index_option_realtime_quote import index_option_realtime_quote

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 실시간시세 > 지수옵션 실시간호가[실시간-015]
##############################################################################################

COLUMN_MAPPING = {
    "optn_shrn_iscd": "옵션 단축 종목코드",
    "bsop_hour": "영업 시간",
    "optn_askp1": "옵션 매도호가1",
    "optn_askp2": "옵션 매도호가2",
    "optn_askp3": "옵션 매도호가3",
    "optn_askp4": "옵션 매도호가4",
    "optn_askp5": "옵션 매도호가5",
    "optn_bidp1": "옵션 매수호가1",
    "optn_bidp2": "옵션 매수호가2",
    "optn_bidp3": "옵션 매수호가3",
    "optn_bidp4": "옵션 매수호가4",
    "optn_bidp5": "옵션 매수호가5",
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
   지수옵션 실시간호가

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
    kws.subscribe(request=index_option_realtime_quote, data=["201W08427"])

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
