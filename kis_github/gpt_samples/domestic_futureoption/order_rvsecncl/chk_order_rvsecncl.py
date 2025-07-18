"""
Created on 20250114 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from order_rvsecncl import order_rvsecncl

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 정정취소주문[v1_국내선물-002]
##############################################################################################

COLUMN_MAPPING = {
    'ACNT_NAME': '계좌명',
    'TRAD_DVSN_NAME': '매매구분명',
    'ITEM_NAME': '종목명',
    'ORD_TMD': '주문시각',
    'ORD_GNO_BRNO': '주문채번지점번호',
    'ORGN_ODNO': '원주문번호',
    'ODNO': '주문번호'
}

NUMERIC_COLUMNS = []


def main():
    """
    선물옵션 정정취소주문 조회 테스트 함수
    
    이 함수는 선물옵션 정정취소주문 API를 호출하여 결과를 출력합니다.
    
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

    # case1 테스트
    logging.info("=== case1 테스트 ===")
    try:
        result = order_rvsecncl(
            env_dv="real",
            day_dv="day",
            ord_prcs_dvsn_cd="02",
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            rvse_cncl_dvsn_cd="02",
            orgn_odno="0000004018",
            ord_qty="0",
            unit_price="0",
            nmpr_type_cd="02",
            krx_nmpr_cndt_cd="0",
            rmn_qty_yn="Y",
            ord_dvsn_cd="01"
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())

    # 컬럼명 한글 변환

    result = result.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result)


if __name__ == "__main__":
    main()
