"""
Created on 20250115 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from pension_inquire_present_balance import pension_inquire_present_balance

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 퇴직연금 체결기준잔고[v1_국내주식-032]
##############################################################################################

COLUMN_MAPPING = {
    'cblc_dvsn': '잔고구분',
    'cblc_dvsn_name': '잔고구분명',
    'pdno': '상품번호',
    'prdt_name': '상품명',
    'hldg_qty': '보유수량',
    'slpsb_qty': '매도가능수량',
    'pchs_avg_pric': '매입평균가격',
    'evlu_pfls_amt': '평가손익금액',
    'evlu_pfls_rt': '평가손익율',
    'prpr': '현재가',
    'evlu_amt': '평가금액',
    'pchs_amt': '매입금액',
    'cblc_weit': '잔고비중',
    'pchs_amt_smtl_amt': '매입금액합계금액',
    'evlu_amt_smtl_amt': '평가금액합계금액',
    'evlu_pfls_smtl_amt': '평가손익합계금액',
    'trad_pfls_smtl': '매매손익합계',
    'thdt_tot_pfls_amt': '당일총손익금액',
    'pftrt': '수익률'
}

NUMERIC_COLUMNS = ['보유수량', '매도가능수량', '매입평균가격', '평가손익금액',
                   '평가손익율', '현재가', '평가금액', '매입금액', '잔고비중', '매입금액합계금액', '평가금액합계금액', '평가손익합계금액',
                   '매매손익합계', '당일총손익금액', '수익률']


def main():
    """
    퇴직연금 체결기준잔고 조회 테스트 함수
    
    이 함수는 퇴직연금 체결기준잔고 API를 호출하여 결과를 출력합니다.
    
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

    # Case 1: 퇴직연금 체결기준잔고 조회
    logging.info("=== 퇴직연금 체결기준잔고 조회 ===")
    try:
        result1, result2 = pension_inquire_present_balance(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod,
                                                           user_dvsn_cd="00"
                                                           )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # output1 처리
    logging.info("=== output1 (보유종목 정보) ===")
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
    logging.info("=== output2 (계좌 요약 정보) ===")
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
