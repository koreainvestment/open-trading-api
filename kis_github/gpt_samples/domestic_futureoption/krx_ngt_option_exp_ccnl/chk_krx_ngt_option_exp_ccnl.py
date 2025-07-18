"""
Created on 20250601
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from krx_ngt_option_exp_ccnl import krx_ngt_option_exp_ccnl

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 실시간시세 > KRX야간옵션실시간예상체결 [실시간-034]
##############################################################################################

COLUMN_MAPPING = {
    "optn_shrn_iscd": "옵션단축종목코드",
    "bsop_hour": "영업시간",
    "antc_cnpr": "예상체결가",
    "antc_cntg_vrss": "예상체결대비",
    "antc_cntg_vrss_sign": "예상체결대비부호",
    "antc_cntg_prdy_ctrt": "예상체결전일대비율",
    "antc_mkop_cls_code": "예상장운영구분코드",
    "antc_cnqn": "예상체결수량"
}

NUMERIC_COLUMNS = []


def main():
    """
    KRX야간옵션실시간예상체결 조회 테스트 함수

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
    kws.subscribe(request=krx_ngt_option_exp_ccnl, data=["101W9000"])

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
