"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_ccnl import inquire_ccnl

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 주문체결내역조회[v1_국내선물-003]
##############################################################################################

COLUMN_MAPPING = {
    'ord_gno_brno': '주문채번지점번호',
    'cano': '종합계좌번호',
    'csac_name': '종합계좌명',
    'acnt_prdt_cd': '계좌상품코드',
    'ord_dt': '주문일자',
    'odno': '주문번호',
    'orgn_odno': '원주문번호',
    'sll_buy_dvsn_cd': '매도매수구분코드',
    'trad_dvsn_name': '매매구분명',
    'nmpr_type_cd': '호가유형코드',
    'nmpr_type_name': '호가유형명',
    'pdno': '상품번호',
    'prdt_name': '상품명',
    'prdt_type_cd': '상품유형코드',
    'ord_qty': '주문수량',
    'ord_idx': '주문지수',
    'qty': '잔량',
    'ord_tmd': '주문시각',
    'tot_ccld_qty': '총체결수량',
    'avg_idx': '평균지수',
    'tot_ccld_amt': '총체결금액',
    'rjct_qty': '거부수량',
    'ingr_trad_rjct_rson_cd': '장내매매거부사유코드',
    'ingr_trad_rjct_rson_name': '장내매매거부사유명',
    'ord_stfno': '주문직원번호',
    'sprd_item_yn': '스프레드종목여부',
    'ord_ip_addr': '주문IP주소',
    'tot_ord_qty': '총주문수량',
    'tot_ccld_amt_smtl': '총체결금액합계',
    'tot_ccld_qty_smtl': '총체결수량합계',
    'fee_smtl': '수수료합계',
    'ctac_tlno': '연락전화번호'
}

NUMERIC_COLUMNS = []


def main():
    """
    선물옵션 주문체결내역조회 테스트 함수
    
    이 함수는 선물옵션 주문체결내역조회 API를 호출하여 결과를 출력합니다.
    
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
        result1, result2 = inquire_ccnl(
            env_dv="real",
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            strt_ord_dt="20220730",
            end_ord_dt="20220830",
            sll_buy_dvsn_cd="00",
            ccld_nccs_dvsn="00",
            sort_sqn="DS"
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # output1 결과 처리
    logging.info("=== output1 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())

    # 컬럼명 한글 변환
    result1 = result1.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result1)

    # output2 결과 처리
    logging.info("=== output2 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result2.columns.tolist())

    # 컬럼명 한글 변환
    result2 = result2.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result2)


if __name__ == "__main__":
    main()
