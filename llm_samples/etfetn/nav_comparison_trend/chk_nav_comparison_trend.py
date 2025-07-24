"""
Created on 20250112 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from nav_comparison_trend import nav_comparison_trend

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 기본시세 > NAV 비교추이(종목)[v1_국내주식-069]
##############################################################################################

# 컬럼명 매핑
COLUMN_MAPPING = {
    'stck_prpr': '주식 현재가',
    'prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비율',
    'acml_vol': '누적 거래량',
    'acml_tr_pbmn': '누적 거래 대금',
    'stck_prdy_clpr': '주식 전일 종가',
    'stck_oprc': '주식 시가2',
    'stck_hgpr': '주식 최고가',
    'stck_lwpr': '주식 최저가',
    'stck_mxpr': '주식 상한가',
    'stck_llam': '주식 하한가',
    'nav': 'NAV',
    'nav_prdy_vrss_sign': 'NAV 전일 대비 부호',
    'nav_prdy_vrss': 'NAV 전일 대비',
    'nav_prdy_ctrt': 'NAV 전일 대비율',
    'prdy_clpr_nav': 'NAV전일종가',
    'oprc_nav': 'NAV시가',
    'hprc_nav': 'NAV고가',
    'lprc_nav': 'NAV저가'
}

# 숫자형 컬럼
NUMERIC_COLUMNS = ['주식 현재가', '전일 대비', '전일 대비율', '누적 거래량', '누적 거래 대금', '주식 전일 종가', '주식 시가2', '주식 최고가', '주식 최저가', 
                   '주식 상한가', '주식 하한가', 'NAV', 'NAV 전일 대비', 'NAV 전일 대비율', 'NAV전일종가', 'NAV시가', 'NAV고가', 'NAV저가']

def main():
    """
    NAV 비교추이(종목) 조회 테스트 함수
    
    이 함수는 NAV 비교추이(종목) API를 호출하여 결과를 출력합니다.
    테스트 데이터로 KODEX 200 ETF(069500)를 사용합니다.
    
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
    logging.info("=== Case1: KODEX 200 ETF(069500) 조회 ===")
    try:
        result1, result2 = nav_comparison_trend(fid_cond_mrkt_div_code="J", fid_input_iscd="069500")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return
    
    # output1 데이터 처리
    logging.info("=== output1 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())
    
    # 한글 컬럼명으로 변환
    result1 = result1.rename(columns=COLUMN_MAPPING)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)
    
    logging.info("output1 결과:")
    print(result1)
    
    # output2 데이터 처리
    logging.info("=== output2 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result2.columns.tolist())
    
    # 한글 컬럼명으로 변환
    result2 = result2.rename(columns=COLUMN_MAPPING)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)
    
    logging.info("output2 결과:")
    print(result2)

if __name__ == "__main__":
    main() 