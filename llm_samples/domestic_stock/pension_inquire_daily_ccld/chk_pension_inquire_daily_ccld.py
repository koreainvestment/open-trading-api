"""
Created on 20250112 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from pension_inquire_daily_ccld import pension_inquire_daily_ccld

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 퇴직연금 미체결내역[v1_국내주식-033]
##############################################################################################

COLUMN_MAPPING = {
    'ord_gno_brno': '주문채번지점번호',
    'sll_buy_dvsn_cd': '매도매수구분코드',
    'trad_dvsn_name': '매매구분명',
    'odno': '주문번호',
    'pdno': '상품번호',
    'prdt_name': '상품명',
    'ord_unpr': '주문단가',
    'ord_qty': '주문수량',
    'tot_ccld_qty': '총체결수량',
    'nccs_qty': '미체결수량',
    'ord_dvsn_cd': '주문구분코드',
    'ord_dvsn_name': '주문구분명',
    'orgn_odno': '원주문번호',
    'ord_tmd': '주문시각',
    'objt_cust_dvsn_name': '대상고객구분명',
    'pchs_avg_pric': '매입평균가격'
}

NUMERIC_COLUMNS = []


def main():
    """
    퇴직연금 미체결내역 조회 테스트 함수
    
    이 함수는 퇴직연금 미체결내역 API를 호출하여 결과를 출력합니다.
    
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
        result = pension_inquire_daily_ccld(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, user_dvsn_cd="%%", sll_buy_dvsn_cd="00",
                                            ccld_nccs_dvsn="%%", inqr_dvsn_3="00")
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
