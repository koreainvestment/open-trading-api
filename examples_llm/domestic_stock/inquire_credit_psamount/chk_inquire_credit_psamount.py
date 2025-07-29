"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_credit_psamount import inquire_credit_psamount

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 신용매수가능조회[v1_국내주식-042]
##############################################################################################

COLUMN_MAPPING = {
    'ord_psbl_cash': '주문가능현금',
    'ord_psbl_sbst': '주문가능대용',
    'ruse_psbl_amt': '재사용가능금액',
    'fund_rpch_chgs': '펀드환매대금',
    'psbl_qty_calc_unpr': '가능수량계산단가',
    'nrcvb_buy_amt': '미수없는매수금액',
    'nrcvb_buy_qty': '미수없는매수수량',
    'max_buy_amt': '최대매수금액',
    'max_buy_qty': '최대매수수량',
    'cma_evlu_amt': 'CMA평가금액',
    'ovrs_re_use_amt_wcrc': '해외재사용금액원화',
    'ord_psbl_frcr_amt_wcrc': '주문가능외화금액원화'
}

NUMERIC_COLUMNS = []


def main():
    """
    신용매수가능조회 테스트 함수
    
    이 함수는 신용매수가능조회 API를 호출하여 결과를 출력합니다.
    
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
        result = inquire_credit_psamount(
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            pdno="005930",
            ord_dvsn="00",
            crdt_type="21",
            cma_evlu_amt_icld_yn="N",
            ovrs_icld_yn="N"
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
