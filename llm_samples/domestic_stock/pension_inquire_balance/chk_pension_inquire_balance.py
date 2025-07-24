"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from pension_inquire_balance import pension_inquire_balance

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 퇴직연금 잔고조회[v1_국내주식-036]
##############################################################################################

COLUMN_MAPPING = {
    'cblc_dvsn_name': '잔고구분명',
    'prdt_name': '상품명',
    'pdno': '상품번호',
    'item_dvsn_name': '종목구분명',
    'thdt_buyqty': '금일매수수량',
    'thdt_sll_qty': '금일매도수량',
    'hldg_qty': '보유수량',
    'ord_psbl_qty': '주문가능수량',
    'pchs_avg_pric': '매입평균가격',
    'pchs_amt': '매입금액',
    'prpr': '현재가',
    'evlu_amt': '평가금액',
    'evlu_pfls_amt': '평가손익금액',
    'evlu_erng_rt': '평가수익율',
    'dnca_tot_amt': '예수금총금액',
    'nxdy_excc_amt': '익일정산금액',
    'prvs_rcdl_excc_amt': '가수도정산금액',
    'thdt_buy_amt': '금일매수금액',
    'thdt_sll_amt': '금일매도금액',
    'thdt_tlex_amt': '금일제비용금액',
    'scts_evlu_amt': '유가평가금액',
    'tot_evlu_amt': '총평가금액'
}

NUMERIC_COLUMNS = [
    '금일매수수량',
    '금일매도수량',
    '보유수량',
    '주문가능수량',
    '매입평균가격',
    '매입금액',
    '현재가',
    '평가금액',
    '평가손익금액',
    '평가수익율',
    '예수금총금액',
    '익일정산금액',
    '가수도정산금액',
    '금일매수금액',
    '금일매도금액',
    '금일제비용금액',
    '유가평가금액',
    '총평가금액'
]


def main():
    """
    퇴직연금 잔고조회 테스트 함수
    
    이 함수는 퇴직연금 잔고조회 API를 호출하여 결과를 출력합니다.
    
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
        result1, result2 = pension_inquire_balance(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, acca_dvsn_cd="00",
                                                   inqr_dvsn="00")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # output1 처리
    logging.info("=== output1 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    result1 = result1.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result1)

    # output2 처리
    logging.info("=== output2 결과 ===")
    logging.info("사용 가능한 컬럼: %s" % result2.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    result2 = result2.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result2)


if __name__ == "__main__":
    main()
