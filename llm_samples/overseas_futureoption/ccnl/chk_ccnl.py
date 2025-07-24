"""
Created on 20250601
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from ccnl import ccnl

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외선물옵션]실시간시세 > 해외선물옵션 실시간체결가[실시간-017]
##############################################################################################

# 상수 정의
COLUMN_MAPPING = {
    "series_cd": "종목코드",
    "bsns_date": "영업일자",
    "mrkt_open_date": "장개시일자",
    "mrkt_open_time": "장개시시각",
    "mrkt_close_date": "장종료일자",
    "mrkt_close_time": "장종료시각",
    "prev_price": "전일종가",
    "recv_date": "수신일자",
    "recv_time": "수신시각",
    "active_flag": "본장_전산장구분",
    "last_price": "체결가격",
    "last_qntt": "체결수량",
    "prev_diff_price": "전일대비가",
    "prev_diff_rate": "등락률",
    "open_price": "시가",
    "high_price": "고가",
    "low_price": "저가",
    "vol": "누적거래량",
    "prev_sign": "전일대비부호",
    "quotsign": "체결구분",
    "recv_time2": "수신시각2 만분의일초",
    "psttl_price": "전일정산가",
    "psttl_sign": "전일정산가대비",
    "psttl_diff_price": "전일정산가대비가격",
    "psttl_diff_rate": "전일정산가대비율"
}

NUMERIC_COLUMNS = ["전일종가", "체결가격", "체결수량", "전일대비가", "등락률", "시가", "고가", "저가", 
                   "누적거래량", "전일정산가", "전일정산가대비가격", "전일정산가대비율"]

def main():
    """
    해외선물옵션 실시간체결가

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
    kws.subscribe(request=ccnl, data=["1OZQ25"])

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