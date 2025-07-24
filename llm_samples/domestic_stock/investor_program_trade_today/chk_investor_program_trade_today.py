"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from investor_program_trade_today import investor_program_trade_today

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 프로그램매매 투자자매매동향(당일) [국내주식-116]
##############################################################################################

COLUMN_MAPPING = {
    'invr_cls_code': '투자자코드',
    'all_seln_qty': '전체매도수량',
    'all_seln_amt': '전체매도대금',
    'invr_cls_name': '투자자 구분 명',
    'all_shnu_qty': '전체매수수량',
    'all_shnu_amt': '전체매수대금',
    'all_ntby_amt': '전체순매수대금',
    'arbt_seln_qty': '차익매도수량',
    'all_ntby_qty': '전체순매수수량',
    'arbt_shnu_qty': '차익매수수량',
    'arbt_ntby_qty': '차익순매수수량',
    'arbt_seln_amt': '차익매도대금',
    'arbt_shnu_amt': '차익매수대금',
    'arbt_ntby_amt': '차익순매수대금',
    'nabt_seln_qty': '비차익매도수량',
    'nabt_shnu_qty': '비차익매수수량',
    'nabt_ntby_qty': '비차익순매수수량',
    'nabt_seln_amt': '비차익매도대금',
    'nabt_shnu_amt': '비차익매수대금',
    'nabt_ntby_amt': '비차익순매수대금'
}

NUMERIC_COLUMNS = []


def main():
    """
    프로그램매매 투자자매매동향(당일) 조회 테스트 함수
    
    이 함수는 프로그램매매 투자자매매동향(당일) API를 호출하여 결과를 출력합니다.
    
    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 인증 토큰 발급
    ka.auth()

    # Case 1: 코스피 조회
    logging.info("=== Case 1: 코스피 조회 ===")
    try:
        result = investor_program_trade_today(mrkt_div_cls_code="1")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    result = result.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에 number 자료형이 명시된 컬럼 없음)
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result)


if __name__ == "__main__":
    main()
