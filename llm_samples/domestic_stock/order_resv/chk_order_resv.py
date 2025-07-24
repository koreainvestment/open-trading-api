"""
Created on 20250112 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from order_resv import order_resv

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 주식예약주문[v1_국내주식-017]
##############################################################################################

COLUMN_MAPPING = {
    'RSVN_ORD_SEQ': '예약주문 순번'
}

NUMERIC_COLUMNS = []


def main():
    """
    주식예약주문 테스트 함수
    
    이 함수는 주식예약주문 API를 호출하여 결과를 출력합니다.
    
    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 인증 토큰 발급
    ka.auth()

    trenv = ka.getTREnv()

    # case1 조회
    logging.info("=== case1 조회 ===")
    try:
        result = order_resv(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, pdno="005930", ord_qty="1", ord_unpr="55000",
                            sll_buy_dvsn_cd="02", ord_dvsn_cd="00", ord_objt_cblc_dvsn_cd="10")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력

    result = result.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result)


if __name__ == "__main__":
    main()
