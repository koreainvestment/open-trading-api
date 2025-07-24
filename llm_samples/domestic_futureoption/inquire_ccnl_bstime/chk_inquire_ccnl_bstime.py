"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_ccnl_bstime import inquire_ccnl_bstime

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 기준일체결내역[v1_국내선물-016]
##############################################################################################

COLUMN_MAPPING = {
    'pdno': '상품번호',
    'prdt_name': '상품명',
    'odno': '주문번호',
    'tr_type_name': '거래유형명',
    'last_sttldt': '최종결제일',
    'ccld_idx': '체결지수',
    'ccld_qty': '체결량',
    'trad_amt': '매매금액',
    'fee': '수수료',
    'ccld_btwn': '체결시간',
    'tot_ccld_qty_smtl': '총체결수량합계',
    'tot_ccld_amt_smtl': '총체결금액합계',
    'fee_adjt': '수수료조정',
    'fee_smtl': '수수료합계'
}

NUMERIC_COLUMNS = []


def main():
    """
    선물옵션 기준일체결내역 조회 테스트 함수
    
    이 함수는 선물옵션 기준일체결내역 API를 호출하여 결과를 출력합니다.
    
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
        result1, result2 = inquire_ccnl_bstime(
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            ord_dt="20230920",
            fuop_tr_strt_tmd="000000",
            fuop_tr_end_tmd="240000"
        )
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
    logging.info("사용 가능한 컬럼: %s", result2.columns.tolist())

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
