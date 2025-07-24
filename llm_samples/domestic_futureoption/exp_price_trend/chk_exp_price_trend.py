"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""
import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from exp_price_trend import exp_price_trend

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 기본시세 > 선물옵션 일중예상체결추이[국내선물-018]
##############################################################################################

COLUMN_MAPPING = {
    'hts_kor_isnm': '영업 시간',
    'futs_antc_cnpr': '업종 지수 현재가',
    'antc_cntg_vrss_sign': '업종 지수 전일 대비',
    'futs_antc_cntg_vrss': '전일 대비 부호',
    'antc_cntg_prdy_ctrt': '업종 지수 전일 대비율',
    'futs_sdpr': '누적 거래 대금',
    'stck_cntg_hour': '주식체결시간',
    'futs_antc_cnpr': '선물예상체결가',
    'antc_cntg_vrss_sign': '예상체결대비부호',
    'futs_antc_cntg_vrss': '선물예상체결대비',
    'antc_cntg_prdy_ctrt': '예상체결전일대비율'
}

NUMERIC_COLUMNS = []


def main():
    """
    선물옵션 일중예상체결추이 조회 테스트 함수
    
    이 함수는 선물옵션 일중예상체결추이 API를 호출하여 결과를 출력합니다.
    
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
        result1, result2 = exp_price_trend(fid_input_iscd="101W09", fid_cond_mrkt_div_code="F")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return
    
    # output1 결과 처리
    logging.info("사용 가능한 컬럼 (output1): %s", result1.columns.tolist())
    
    # 컬럼명 한글 변환 및 데이터 출력 (output1)
    result1 = result1.rename(columns=COLUMN_MAPPING)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시 (output1)
    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)
    
    logging.info("결과 (output1):")
    print(result1)
    
    # output2 결과 처리
    logging.info("사용 가능한 컬럼 (output2): %s", result2.columns.tolist())
    
    # 컬럼명 한글 변환 및 데이터 출력 (output2)
    result2 = result2.rename(columns=COLUMN_MAPPING)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시 (output2)
    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)
    
    logging.info("결과 (output2):")
    print(result2)

if __name__ == "__main__":
    main() 