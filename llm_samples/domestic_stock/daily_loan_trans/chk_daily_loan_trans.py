"""
Created on 20250114
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from daily_loan_trans import daily_loan_trans

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 종목별 일별 대차거래추이 [국내주식-135]
##############################################################################################

COLUMN_MAPPING = {
    'bsop_date': '일자',
    'stck_prpr': '주식 종가',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_vrss': '전일 대비',
    'prdy_ctrt': '전일 대비율',
    'acml_vol': '누적 거래량',
    'new_stcn': '당일 증가 주수 (체결)',
    'rdmp_stcn': '당일 감소 주수 (상환)',
    'prdy_rmnd_vrss': '대차거래 증감',
    'rmnd_stcn': '당일 잔고 주수',
    'rmnd_amt': '당일 잔고 금액'
}

NUMERIC_COLUMNS = []


def main():
    """
    종목별 일별 대차거래추이 조회 테스트 함수

    이 함수는 종목별 일별 대차거래추이 API를 호출하여 결과를 출력합니다.

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
        result = daily_loan_trans(
            mrkt_div_cls_code="1",
            mksc_shrn_iscd="005930",
            start_date="20240301",
            end_date="20240328"
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
