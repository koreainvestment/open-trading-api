"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from investor_trend_estimate import investor_trend_estimate

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 종목별 외인기관 추정가집계[v1_국내주식-046]
##############################################################################################

COLUMN_MAPPING = {
    'bsop_hour_gb': '입력구분',
    'frgn_fake_ntby_qty': '외국인수량(가집계)',
    'orgn_fake_ntby_qty': '기관수량(가집계)',
    'sum_fake_ntby_qty': '합산수량(가집계)'
}

NUMERIC_COLUMNS = []


def main():
    """
    종목별 외인기관 추정가집계 조회 테스트 함수
    
    이 함수는 종목별 외인기관 추정가집계 API를 호출하여 결과를 출력합니다.
    테스트 데이터로 삼성전자(005930)를 사용합니다.
    
    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 인증 토큰 발급
    ka.auth()

    logging.info("=== 종목별 외인기관 추정가집계 조회 ===")
    try:
        result = investor_trend_estimate(mksc_shrn_iscd="005930")
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
