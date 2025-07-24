"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_psbl_ngt_order import inquire_psbl_ngt_order

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 주문/계좌 > (야간)선물옵션 주문가능 조회 [국내선물-011]
##############################################################################################

COLUMN_MAPPING = {
    'max_ord_psbl_qty': '최대주문가능수량',
    'tot_psbl_qty': '최대주문가능수량',
    'lqd_psbl_qty': '청산가능수량',
    'lqd_psbl_qty_1': '청산가능수량',
    'ord_psbl_qty': '주문가능수량',
    'bass_idx': '기준지수'
}

NUMERIC_COLUMNS = []


def main():
    """
    (야간)선물옵션 주문가능 조회 테스트 함수
    
    이 함수는 (야간)선물옵션 주문가능 조회 API를 호출하여 결과를 출력합니다.
    
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
        result = inquire_psbl_ngt_order(
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            pdno="101W09",
            prdt_type_cd="301",
            sll_buy_dvsn_cd="02",
            unit_price="322",
            ord_dvsn_cd="01"
        )
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
