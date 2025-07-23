"""
Created on 20250115 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from nav_comparison_time_trend import nav_comparison_time_trend

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 기본시세 > NAV 비교추이(분)[v1_국내주식-070]
##############################################################################################

# 컬럼명 매핑
COLUMN_MAPPING = {
    'bsop_hour': '영업 시간',
    'nav': 'NAV',
    'nav_prdy_vrss_sign': 'NAV 전일 대비 부호',
    'nav_prdy_vrss': 'NAV 전일 대비',
    'nav_prdy_ctrt': 'NAV 전일 대비율',
    'nav_vrss_prpr': 'NAV 대비 현재가',
    'dprt': '괴리율',
    'stck_prpr': '주식 현재가',
    'prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비율',
    'acml_vol': '누적 거래량',
    'cntg_vol': '체결 거래량'
}

# 숫자형 컬럼
NUMERIC_COLUMNS = ['NAV 전일 대비', 'NAV 전일 대비율', '전일 대비', '전일 대비율']

def main():
    """
    NAV 비교추이(분) 조회 테스트 함수
    
    이 함수는 NAV 비교추이(분) API를 호출하여 결과를 출력합니다.
    
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
    logging.info("API 호출")
    try:
        result = nav_comparison_time_trend(fid_cond_mrkt_div_code="E", fid_input_iscd="069500", fid_hour_cls_code="60")
    except ValueError as e:
        logging.error("에러 발생: %s", str(e))
        return
    
    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())
    
    # 한글 컬럼명으로 변환
    result = result.rename(columns=COLUMN_MAPPING)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result)

if __name__ == "__main__":
    main() 