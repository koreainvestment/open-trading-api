"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from chk_holiday import chk_holiday

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 업종/기타 > 국내휴장일조회[국내주식-040]
##############################################################################################

COLUMN_MAPPING = {
    'bass_dt': '기준일자',
    'wday_dvsn_cd': '요일구분코드',
    'bzdy_yn': '영업일여부',
    'tr_day_yn': '거래일여부',
    'opnd_yn': '개장일여부',
    'sttl_day_yn': '결제일여부'
}

NUMERIC_COLUMNS = []


def main():
    """
    국내휴장일조회 테스트 함수
    
    이 함수는 국내휴장일조회 API를 호출하여 결과를 출력합니다.
    
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
        result = chk_holiday(bass_dt="20250630")
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
