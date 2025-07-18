"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from daily_credit_balance import daily_credit_balance

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 국내주식 신용잔고 일별추이[국내주식-110]
##############################################################################################

COLUMN_MAPPING = {
    'deal_date': '매매 일자',
    'stck_prpr': '주식 현재가',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_vrss': '전일 대비',
    'prdy_ctrt': '전일 대비율',
    'acml_vol': '누적 거래량',
    'stlm_date': '결제 일자',
    'whol_loan_new_stcn': '전체 융자 신규 주수',
    'whol_loan_rdmp_stcn': '전체 융자 상환 주수',
    'whol_loan_rmnd_stcn': '전체 융자 잔고 주수',
    'whol_loan_new_amt': '전체 융자 신규 금액',
    'whol_loan_rdmp_amt': '전체 융자 상환 금액',
    'whol_loan_rmnd_amt': '전체 융자 잔고 금액',
    'whol_loan_rmnd_rate': '전체 융자 잔고 비율',
    'whol_loan_gvrt': '전체 융자 공여율',
    'whol_stln_new_stcn': '전체 대주 신규 주수',
    'whol_stln_rdmp_stcn': '전체 대주 상환 주수',
    'whol_stln_rmnd_stcn': '전체 대주 잔고 주수',
    'whol_stln_new_amt': '전체 대주 신규 금액',
    'whol_stln_rdmp_amt': '전체 대주 상환 금액',
    'whol_stln_rmnd_amt': '전체 대주 잔고 금액',
    'whol_stln_rmnd_rate': '전체 대주 잔고 비율',
    'whol_stln_gvrt': '전체 대주 공여율',
    'stck_oprc': '주식 시가2',
    'stck_hgpr': '주식 최고가',
    'stck_lwpr': '주식 최저가'
}

NUMERIC_COLUMNS = ['전일 대비율', '누적 거래량', '전체 융자 신규 주수', '전체 융자 상환 주수', '전체 융자 잔고 주수',
                   '전체 융자 신규 금액', '전체 융자 상환 금액', '전체 융자 잔고 금액', '전체 융자 잔고 비율', '전체 융자 공여율',
                   '전체 대주 신규 주수', '전체 대주 상환 주수', '전체 대주 잔고 주수', '전체 대주 신규 금액', '전체 대주 상환 금액',
                   '전체 대주 잔고 금액', '전체 대주 잔고 비율', '전체 대주 공여율', '주식 시가2', '주식 최고가', '주식 최저가']


def main():
    """
    국내주식 신용잔고 일별추이 조회 테스트 함수
    
    이 함수는 국내주식 신용잔고 일별추이 API를 호출하여 결과를 출력합니다.
    테스트 데이터로 셀트리온(068270)을 사용합니다.
    
    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 인증 토큰 발급
    ka.auth()

    # case1 조회
    logging.info("=== case1 조회 ===")
    try:
        result1 = daily_credit_balance(fid_cond_mrkt_div_code="J", fid_cond_scr_div_code="20476",
                                       fid_input_iscd="068270", fid_input_date_1="20240508")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    result1 = result1.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시

    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result1)

    # case2 조회
    logging.info("=== case2 조회 ===")
    try:
        result2 = daily_credit_balance(fid_cond_mrkt_div_code="J", fid_cond_scr_div_code="20476",
                                       fid_input_iscd="068270", fid_input_date_1="20240501")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

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
