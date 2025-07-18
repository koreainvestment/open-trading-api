"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from pension_inquire_psbl_order import pension_inquire_psbl_order

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 퇴직연금 매수가능조회[v1_국내주식-034]
##############################################################################################

COLUMN_MAPPING = {
    'ord_psbl_cash': '주문가능현금',
    'ruse_psbl_amt': '재사용가능금액',
    'psbl_qty_calc_unpr': '가능수량계산단가',
    'max_buy_amt': '최대매수금액',
    'max_buy_qty': '최대매수수량'
}

NUMERIC_COLUMNS = ['주문가능현금', '재사용가능금액', '가능수량계산단가', '최대매수금액', '최대매수수량']


def main():
    """
    퇴직연금 매수가능조회 테스트 함수
    
    이 함수는 퇴직연금 매수가능조회 API를 호출하여 결과를 출력합니다.
    
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
        result = pension_inquire_psbl_order(
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            pdno="069500",
            acca_dvsn_cd="00",
            cma_evlu_amt_icld_yn="Y",
            ord_unpr="30800",
            ord_dvsn="00"
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
