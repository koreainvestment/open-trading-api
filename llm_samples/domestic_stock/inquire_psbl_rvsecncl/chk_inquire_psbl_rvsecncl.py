"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_psbl_rvsecncl import inquire_psbl_rvsecncl

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 주식정정취소가능주문조회[v1_국내주식-004]
##############################################################################################

COLUMN_MAPPING = {
    'ord_gno_brno': '주문채번지점번호',
    'odno': '주문번호',
    'orgn_odno': '원주문번호',
    'ord_dvsn_name': '주문구분명',
    'pdno': '상품번호',
    'prdt_name': '상품명',
    'rvse_cncl_dvsn_name': '정정취소구분명',
    'ord_qty': '주문수량',
    'ord_unpr': '주문단가',
    'ord_tmd': '주문시각',
    'tot_ccld_qty': '총체결수량',
    'tot_ccld_amt': '총체결금액',
    'psbl_qty': '가능수량',
    'sll_buy_dvsn_cd': '매도매수구분코드',
    'ord_dvsn_cd': '주문구분코드',
    'mgco_aptm_odno': '운용사지정주문번호',
    'excg_dvsn_cd': '거래소구분코드',
    'excg_id_dvsn_cd': '거래소ID구분코드',
    'excg_id_dvsn_name': '거래소ID구분명',
    'stpm_cndt_pric': '스톱지정가조건가격',
    'stpm_efct_occr_yn': '스톱지정가효력발생여부'
}

NUMERIC_COLUMNS = []


def main():
    """
    주식정정취소가능주문조회 테스트 함수
    
    이 함수는 주식정정취소가능주문조회 API를 호출하여 결과를 출력합니다.
    
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
        result = inquire_psbl_rvsecncl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, inqr_dvsn_1="1", inqr_dvsn_2="0")
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
