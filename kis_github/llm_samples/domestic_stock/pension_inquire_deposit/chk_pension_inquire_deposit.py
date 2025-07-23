"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from pension_inquire_deposit import pension_inquire_deposit

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 퇴직연금 예수금조회[v1_국내주식-035]
##############################################################################################

COLUMN_MAPPING = {
    'dnca_tota': '예수금총액',
    'nxdy_excc_amt': '익일정산액',
    'nxdy_sttl_amt': '익일결제금액',
    'nx2_day_sttl_amt': '2익일결제금액'
}

NUMERIC_COLUMNS = ['예수금총액', '익일정산액', '익일결제금액', '2익일결제금액']


def main():
    """
    퇴직연금 예수금조회 테스트 함수
    
    이 함수는 퇴직연금 예수금조회 API를 호출하여 결과를 출력합니다.
    
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
        result = pension_inquire_deposit(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, acca_dvsn_cd="00")
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
