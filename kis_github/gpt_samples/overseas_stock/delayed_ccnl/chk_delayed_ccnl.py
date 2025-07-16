"""
Created on 20250601
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from delayed_ccnl import delayed_ccnl

# 로깅 설정
logging.basicConfig(level=logging.INFO)


##############################################################################################
# [해외주식] 실시간시세 > 해외주식 실시간지연체결가[실시간-007]
##############################################################################################

def main():
    """
    해외주식 실시간지연체결가

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
    kws.subscribe(request=delayed_ccnl, data=["DHKS00003"])

    # 결과 표시
    def on_result(ws, tr_id: str, result: pd.DataFrame, data_map: dict):

        column_mapping = {
            "SYMB": "종목코드",
            "ZDIV": "수수점자리수",
            "TYMD": "현지영업일자",
            "XYMD": "현지일자",
            "XHMS": "현지시간",
            "KYMD": "한국일자",
            "KHMS": "한국시간",
            "OPEN": "시가",
            "HIGH": "고가",
            "LOW": "저가",
            "LAST": "현재가",
            "SIGN": "대비구분",
            "DIFF": "전일대비",
            "RATE": "등락율",
            "PBID": "매수호가",
            "PASK": "매도호가",
            "VBID": "매수잔량",
            "VASK": "매도잔량",
            "EVOL": "체결량",
            "TVOL": "거래량",
            "TAMT": "거래대금",
            "BIVL": "매도체결량",
            "ASVL": "매수체결량",
            "STRN": "체결강도",
            "MTYP": "시장구분"
        }

        numeric_columns = []

        result = result.rename(columns=column_mapping)

        for col in numeric_columns:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

        logging.info("결과:")
        print(result)

    kws.start(on_result=on_result)


if __name__ == "__main__":
    main() 