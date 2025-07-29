"""
Created on 2025-07-09
@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from program_trade_total import program_trade_total

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간프로그램매매 (통합)
##############################################################################################

COLUMN_MAPPING = {
    "MKSC_SHRN_ISCD": "유가증권 단축 종목코드",
    "STCK_CNTG_HOUR": "주식 체결 시간",
    "SELN_CNQN": "매도 체결량",
    "SELN_TR_PBMN": "매도 거래 대금",
    "SHNU_CNQN": "매수2 체결량",
    "SHNU_TR_PBMN": "매수2 거래 대금",
    "NTBY_CNQN": "순매수 체결량",
    "NTBY_TR_PBMN": "순매수 거래 대금",
    "SELN_RSQN": "매도호가잔량",
    "SHNU_RSQN": "매수호가잔량",
    "WHOL_NTBY_QTY": "전체순매수호가잔량"
}

NUMERIC_COLUMNS = [
    "매도 체결량", "매도 거래 대금", "매수2 체결량", "매수2 거래 대금",
    "순매수 체결량", "순매수 거래 대금", "매도호가잔량", "매수호가잔량", "전체순매수호가잔량"
]


def main():
    """
    국내주식 실시간프로그램매매 (통합)
    
    국내주식 실시간프로그램매매 (통합) API입니다.
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
    kws.subscribe(request=program_trade_total, data=["005930", "000660"])

    # 결과 표시
    def on_result(ws, tr_id: str, result: pd.DataFrame, data_map: dict):
        try:
            # 컬럼 매핑
            result.rename(columns=COLUMN_MAPPING, inplace=True)

            # 숫자형 컬럼 변환
            for col in NUMERIC_COLUMNS:
                if col in result.columns:
                    result[col] = pd.to_numeric(result[col], errors='coerce')

            logging.info("결과:")
            print(result)
        except Exception as e:
            logging.error(f"결과 처리 중 오류: {e}")
            logging.error(f"받은 데이터: {result}")

    kws.start(on_result=on_result)


if __name__ == "__main__":
    main()
