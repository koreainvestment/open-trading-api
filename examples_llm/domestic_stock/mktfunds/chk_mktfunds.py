"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from mktfunds import mktfunds

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 국내 증시자금 종합 [국내주식-193]
##############################################################################################

COLUMN_MAPPING = {
    'bsop_date': '영업일자',
    'bstp_nmix_prpr': '업종지수현재가',
    'bstp_nmix_prdy_vrss': '업종지수전일대비',
    'prdy_vrss_sign': '전일대비부호',
    'prdy_ctrt': '전일대비율',
    'hts_avls': 'HTS시가총액',
    'cust_dpmn_amt': '고객예탁금금액',
    'cust_dpmn_amt_prdy_vrss': '고객예탁금금액전일대비',
    'amt_tnrt': '금액회전율',
    'uncl_amt': '미수금액',
    'crdt_loan_rmnd': '신용융자잔고',
    'futs_tfam_amt': '선물예수금금액',
    'sttp_amt': '주식형금액',
    'mxtp_amt': '혼합형금액',
    'bntp_amt': '채권형금액',
    'mmf_amt': 'MMF금액',
    'secu_lend_amt': '담보대출잔고금액'
}

NUMERIC_COLUMNS = []


def main():
    """
    국내 증시자금 종합 조회 테스트 함수
    
    이 함수는 국내 증시자금 종합 API를 호출하여 결과를 출력합니다.
    
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
        result = mktfunds(fid_input_date_1="")
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
