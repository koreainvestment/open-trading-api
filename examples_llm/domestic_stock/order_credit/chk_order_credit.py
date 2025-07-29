"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from order_credit import order_credit

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 주식주문(신용)[v1_국내주식-002]
##############################################################################################

COLUMN_MAPPING = {
    'krx_fwdg_ord_orgno': '한국거래소전송주문조직번호',
    'odno': '주문번호',
    'ord_tmd': '주문시간'
}

NUMERIC_COLUMNS = []


def main():
    """
    주식주문(신용) 조회 테스트 함수
    
    이 함수는 주식주문(신용) API를 호출하여 결과를 출력합니다.
    테스트 데이터로 삼성전자(005930) 신용매수 주문을 사용합니다.
    
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
        result = order_credit(
            ord_dv="buy",
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            pdno="005930",
            crdt_type="21",
            loan_dt="20220810",
            ord_dvsn="00",
            ord_qty="1",
            ord_unpr="55000"
        )
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
