"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""
import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_balance_settlement_pl import inquire_balance_settlement_pl

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 잔고정산손익내역[v1_국내선물-013]
##############################################################################################

COLUMN_MAPPING = {
    'pdno': '상품번호',
    'prdt_name': '상품명',
    'trad_dvsn_name': '매매구분명',
    'bfdy_cblc_qty': '전일잔고수량',
    'new_qty': '신규수량',
    'mnpl_rpch_qty': '전매환매수량',
    'cblc_qty': '잔고수량',
    'cblc_amt': '잔고금액',
    'trad_pfls_amt': '매매손익금액',
    'evlu_amt': '평가금액',
    'evlu_pfls_amt': '평가손익금액',
    'nxdy_dnca': '익일예수금',
    'mmga_cash': '유지증거금현금',
    'brkg_mgna_cash': '위탁증거금현금',
    'opt_buy_chgs': '옵션매수대금',
    'opt_lqd_evlu_amt': '옵션청산평가금액',
    'dnca_sbst': '예수금대용',
    'mmga_tota': '유지증거금총액',
    'brkg_mgna_tota': '위탁증거금총액',
    'opt_sll_chgs': '옵션매도대금',
    'fee': '수수료',
    'thdt_dfpa': '당일차금',
    'rnwl_dfpa': '갱신차금',
    'dnca_cash': '예수금현금'
}

NUMERIC_COLUMNS = []


def main():
    """
    선물옵션 잔고정산손익내역 조회 테스트 함수
    
    이 함수는 선물옵션 잔고정산손익내역 API를 호출하여 결과를 출력합니다.
    
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

    # Case 1
    logging.info("=== Case 1 ===")
    try:
        result1, result2 = inquire_balance_settlement_pl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, inqr_dt="20230906")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    logging.info("사용 가능한 컬럼 (output1): %s", result1.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력 (output1)

    result1 = result1.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시

    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

    logging.info("결과 (output1):")
    print(result1)

    logging.info("사용 가능한 컬럼 (output2): %s", result2.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력 (output2)
    result2 = result2.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시

    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

    logging.info("결과 (output2):")
    print(result2)


if __name__ == "__main__":
    main()
