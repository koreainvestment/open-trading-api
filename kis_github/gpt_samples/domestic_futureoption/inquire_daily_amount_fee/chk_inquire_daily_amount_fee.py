"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_daily_amount_fee import inquire_daily_amount_fee

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션기간약정수수료일별[v1_국내선물-017]
##############################################################################################

COLUMN_MAPPING = {
    'ord_dt': '주문일자',
    'pdno': '상품번호',
    'item_name': '종목명',
    'sll_agrm_amt': '매도약정금액',
    'sll_fee': '매도수수료',
    'buy_agrm_amt': '매수약정금액',
    'buy_fee': '매수수수료',
    'tot_fee_smtl': '총수수료합계',
    'trad_pfls': '매매손익',
    'futr_agrm': '선물약정',
    'futr_agrm_amt': '선물약정금액',
    'futr_agrm_amt_smtl': '선물약정금액합계',
    'futr_sll_fee_smtl': '선물매도수수료합계',
    'futr_buy_fee_smtl': '선물매수수수료합계',
    'futr_fee_smtl': '선물수수료합계',
    'opt_agrm': '옵션약정',
    'opt_agrm_amt': '옵션약정금액',
    'opt_agrm_amt_smtl': '옵션약정금액합계',
    'opt_sll_fee_smtl': '옵션매도수수료합계',
    'opt_buy_fee_smtl': '옵션매수수수료합계',
    'opt_fee_smtl': '옵션수수료합계',
    'prdt_futr_agrm': '상품선물약정',
    'prdt_fuop': '상품선물옵션',
    'prdt_futr_evlu_amt': '상품선물평가금액',
    'futr_fee': '선물수수료',
    'opt_fee': '옵션수수료',
    'fee': '수수료',
    'sll_agrm_amt': '매도약정금액',
    'buy_agrm_amt': '매수약정금액',
    'agrm_amt_smtl': '약정금액합계',
    'sll_fee': '매도수수료',
    'buy_fee': '매수수수료',
    'fee_smtl': '수수료합계',
    'trad_pfls_smtl': '매매손익합계'
}

NUMERIC_COLUMNS = []


def main():
    """
    선물옵션기간약정수수료일별 조회 테스트 함수
    
    이 함수는 선물옵션기간약정수수료일별 API를 호출하여 결과를 출력합니다.
    테스트 데이터로 메타데이터에서 제공하는 case1 데이터를 사용합니다.
    
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
        result1, result2 = inquire_daily_amount_fee(
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            inqr_strt_day="20240401",
            inqr_end_day="20240625"
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # output1 블록
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

    # output2 블록
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
