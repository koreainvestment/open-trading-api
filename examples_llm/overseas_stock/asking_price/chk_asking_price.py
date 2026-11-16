"""
Created on 20250601
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
    "RSYM": "실시간종목코드",
    "SYMB": "종목코드",
    "ZDIV": "소숫점자리수",
    "XYMD": "현지일자",
    "XHMS": "현지시간",
    "KYMD": "한국일자",
    "KHMS": "한국시간",
    "BVOL": "매수총잔량",
    "AVOL": "매도총잔량",
    "BDVL": "매수총잔량대비",
    "ADVL": "매도총잔량대비",
    "PBID1": "매수호가1",
    "PASK1": "매도호가1",
    "VBID1": "매수잔량1",
    "VASK1": "매도잔량1",
    "DBID1": "매수잔량대비1",
    "DASK1": "매도잔량대비1",
    "PBID2": "매수호가2",
    "PASK2": "매도호가2",
    "VBID2": "매수잔량2",
    "VASK2": "매도잔량2",
    "DBID2": "매수잔량대비2",
    "DASK2": "매도잔량대비2",
    "PBID3": "매수호가3",
    "PASK3": "매도호가3",
    "VBID3": "매수잔량3",
    "VASK3": "매도잔량3",
    "DBID3": "매수잔량대비3",
    "DASK3": "매도잔량대비3",
    "PBID4": "매수호가4",
    "PASK4": "매도호가4",
    "VBID4": "매수잔량4",
    "VASK4": "매도잔량4",
    "DBID4": "매수잔량대비4",
    "DASK4": "매도잔량대비4",
    "PBID5": "매수호가5",
    "PASK5": "매도호가5",
    "VBID5": "매수잔량5",
    "VASK5": "매도잔량5",
    "DBID5": "매수잔량대비5",
    "DASK5": "매도잔량대비5",
    "PBID6": "매수호가6",
    "PASK6": "매도호가6",
    "VBID6": "매수잔량6",
    "VASK6": "매도잔량6",
    "DBID6": "매수잔량대비6",
    "DASK6": "매도잔량대비6",
    "PBID7": "매수호가7",
    "PASK7": "매도호가7",
    "VBID7": "매수잔량7",
    "VASK7": "매도잔량7",
    "DBID7": "매수잔량대비7",
    "DASK7": "매도잔량대비7",
    "PBID8": "매수호가8",
    "PASK8": "매도호가8",
    "VBID8": "매수잔량8",
    "VASK8": "매도잔량8",
    "DBID8": "매수잔량대비8",
    "DASK8": "매도잔량대비8",
    "PBID9": "매수호가9",
    "PASK9": "매도호가9",
    "VBID9": "매수잔량9",
    "VASK9": "매도잔량9",
    "DBID9": "매수잔량대비9",
    "DASK9": "매도잔량대비9",
    "PBID10": "매수호가10",
    "PASK10": "매도호가10",
    "VBID10": "매수잔량10",
    "VASK10": "매도잔량10",
    "DBID10": "매수잔량대비10",
    "DASK10": "매도잔량대비10"
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