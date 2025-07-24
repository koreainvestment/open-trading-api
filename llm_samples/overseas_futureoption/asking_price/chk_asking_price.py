"""
Created on 20250601
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from asking_price import asking_price

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외선물옵션]실시간시세 > 해외선물옵션 실시간호가[실시간-018]
##############################################################################################

# 상수 정의
COLUMN_MAPPING = {
    "series_cd": "종목코드",
    "recv_date": "수신일자",
    "recv_time": "수신시각",
    "prev_price": "전일종가",
    "bid_qntt_1": "매수1수량",
    "bid_num_1": "매수1번호",
    "bid_price_1": "매수1호가",
    "ask_qntt_1": "매도1수량",
    "ask_num_1": "매도1번호",
    "ask_price_1": "매도1호가",
    "bid_qntt_2": "매수2수량",
    "bid_num_2": "매수2번호",
    "bid_price_2": "매수2호가",
    "ask_qntt_2": "매도2수량",
    "ask_num_2": "매도2번호",
    "ask_price_2": "매도2호가",
    "bid_qntt_3": "매수3수량",
    "bid_num_3": "매수3번호",
    "bid_price_3": "매수3호가",
    "ask_qntt_3": "매도3수량",
    "ask_num_3": "매도3번호",
    "ask_price_3": "매도3호가",
    "bid_qntt_4": "매수4수량",
    "bid_num_4": "매수4번호",
    "bid_price_4": "매수4호가",
    "ask_qntt_4": "매도4수량",
    "ask_num_4": "매도4번호",
    "ask_price_4": "매도4호가",
    "bid_qntt_5": "매수5수량",
    "bid_num_5": "매수5번호",
    "bid_price_5": "매수5호가",
    "ask_qntt_5": "매도5수량",
    "ask_num_5": "매도5번호",
    "ask_price_5": "매도5호가",
    "sttl_price": "전일정산가"
}

NUMERIC_COLUMNS = ["전일종가", "매수1수량", "매수1호가", "매도1수량", "매도1호가", 
                   "매수2수량", "매수2호가", "매도2수량", "매도2호가",
                   "매수3수량", "매수3호가", "매도3수량", "매도3호가",
                   "매수4수량", "매수4호가", "매도4수량", "매도4호가",
                   "매수5수량", "매수5호가", "매도5수량", "매도5호가", "전일정산가"]

def main():
    """
    해외선물옵션 실시간호가 테스트 함수

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
    kws.subscribe(request=asking_price, data=["SPIU25"])

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