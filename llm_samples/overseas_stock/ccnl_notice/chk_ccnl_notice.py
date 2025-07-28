"""
Created on 20250601
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from ccnl_notice import ccnl_notice

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외주식] 실시간시세 > 해외주식 실시간체결통보[실시간-009]
##############################################################################################

# 컬럼 매핑 정의
COLUMN_MAPPING = {
    "CUST_ID": "고객 ID",
    "ACNT_NO": "계좌번호",
    "ODER_NO": "주문번호",
    "OODER_NO": "원주문번호",
    "SELN_BYOV_CLS": "매도매수구분",
    "RCTF_CLS": "정정구분",
    "ODER_KIND2": "주문종류2",
    "STCK_SHRN_ISCD": "주식 단축 종목코드",
    "CNTG_QTY": "체결수량",
    "CNTG_UNPR": "체결단가",
    "STCK_CNTG_HOUR": "주식 체결 시간",
    "RFUS_YN": "거부여부",
    "CNTG_YN": "체결여부",
    "ACPT_YN": "접수여부",
    "BRNC_NO": "지점번호",
    "ODER_QTY": "주문 수량",
    "ACNT_NAME": "계좌명",
    "CNTG_ISNM": "체결종목명",
    "ODER_COND": "해외종목구분",
    "DEBT_GB": "담보유형코드",
    "DEBT_DATE": "담보대출일자",
    "START_TM": "분할매수/매도 시작시간",
    "END_TM": "분할매수/매도 종료시간",
    "TM_DIV_TP": "시간분할타입유형"
}

# 숫자형 컬럼 정의
NUMERIC_COLUMNS = []

def main():
    """
    해외주식 실시간체결통보

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
    trenv = ka.getTREnv()

    # 인증(auth_ws()) 이후에 선언
    kws = ka.KISWebSocket(api_url="/tryitout")

    # 조회
    kws.subscribe(request=ccnl_notice, data=[trenv.my_htsid], kwargs={"env_dv": "real"})

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