"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from industry_price import industry_price

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외주식] 기본시세 > 해외주식 업종별코드조회[해외주식-049]
##############################################################################################

COLUMN_MAPPING = {
    'nrec': 'RecordCount',
    'icod': '업종코드',
    'name': '업종명'
}

NUMERIC_COLUMNS = []

def main():
    """
    해외주식 업종별코드조회 테스트 함수
    이 함수는 해외주식 업종별코드조회 API를 호출하여 결과를 출력합니다.

    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 인증 토큰 발급
    ka.auth()

    # case1: EXCD=NAS
    logging.info("=== case1: EXCD=NAS ===")
    try:
        result1, result2 = industry_price(excd="NAS")
    except ValueError as e:
        logging.error("에러 발생: %s", str(e))
        return

    # output1 처리
    logging.info("=== output1 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())

    # 컬럼명 한글 변환 및 숫자형 변환
    result1 = result1.rename(columns=COLUMN_MAPPING)
    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result1)

    # output2 처리
    logging.info("=== output2 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result2.columns.tolist())

    # 컬럼명 한글 변환 및 숫자형 변환
    result2 = result2.rename(columns=COLUMN_MAPPING)
    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result2)

if __name__ == "__main__":
    main() 