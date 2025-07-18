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
# [해외주식] 실시간시세 > 해외주식 실시간호가[실시간-021]
##############################################################################################

# 컬럼 매핑 정의
COLUMN_MAPPING = {
    "symb": "종목코드",
    "zdiv": "소숫점자리수",
    "xymd": "현지일자",
    "xhms": "현지시간",
    "kymd": "한국일자",
    "khms": "한국시간",
    "bvol": "매수총잔량",
    "avol": "매도총잔량",
    "bdvl": "매수총잔량대비",
    "advl": "매도총잔량대비",
    "pbid1": "매수호가1",
    "pask1": "매도호가1",
    "vbid1": "매수잔량1",
    "vask1": "매도잔량1",
    "dbid1": "매수잔량대비1",
    "dask1": "매도잔량대비1"
}

# 숫자형 컬럼 정의
NUMERIC_COLUMNS = []

def main():
    """
   해외주식 실시간호가

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
    kws.subscribe(request=asking_price, data=["RBAQAAPL"])

    # 결과 표시
    def on_result(ws, tr_id: str, result: pd.DataFrame, data_map: dict):

        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)

        # 숫자형 컬럼 소수점 둘째자리까지 표시
        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

        logging.info("결과:")
        print(result)

    kws.start(on_result=on_result)

if __name__ == "__main__":
    main() 