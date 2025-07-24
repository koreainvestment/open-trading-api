"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_time_itemconclusion import inquire_time_itemconclusion

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 기본시세 > 주식현재가 당일시간대별체결[v1_국내주식-023]
##############################################################################################

COLUMN_MAPPING = {
    'stck_prpr': '주식 현재가',
    'prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비율',
    'acml_vol': '누적 거래량',
    'prdy_vol': '전일 거래량',
    'rprs_mrkt_kor_name': '대표 시장 한글 명',
    'stck_cntg_hour': '주식 체결 시간',
    'stck_pbpr': '주식 현재가',
    'prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비율',
    'askp': '매도호가',
    'bidp': '매수호가',
    'tday_rltv': '당일 체결강도',
    'acml_vol': '누적 거래량',
    'cnqn': '체결량'
}

NUMERIC_COLUMNS = []


def main():
    """
    주식현재가 당일시간대별체결 조회 테스트 함수
    
    이 함수는 주식현재가 당일시간대별체결 API를 호출하여 결과를 출력합니다.
    
    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 인증 토큰 발급
    ka.auth()

    # case1 테스트
    logging.info("=== case1 테스트 ===")
    try:
        result1, result2 = inquire_time_itemconclusion(
            env_dv="real",
            fid_cond_mrkt_div_code="J",
            fid_input_iscd="005930",
            fid_input_hour_1="115959"
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # output1 결과 처리
    logging.info("=== output1 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())

    # 컬럼명 한글 변환
    result1 = result1.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에 number 자료형이 명시되지 않음)
    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result1)

    # output2 결과 처리
    logging.info("=== output2 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result2.columns.tolist())

    # 컬럼명 한글 변환
    result2 = result2.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에 number 자료형이 명시되지 않음)
    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result2)


if __name__ == "__main__":
    main()
