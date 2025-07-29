"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from quot_inquire_ccnl import quot_inquire_ccnl

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 기본시세 > 해외주식 체결추이[해외주식-037]
##############################################################################################

COLUMN_MAPPING = {
    'vpow': '체결강도',
    'evol': '체결량',
    'khms': '한국기준시간',
    'tvol': '거래량',
    'last': '체결가',
    'mtyp': '시장구분',
    'sign': '기호',
    'pbid': '매수호가',
    'diff': '대비',
    'pask': '매도호가',
    'rate': '등락율'
}

NUMERIC_COLUMNS = ['체결강도', '체결량', '거래량', '대비', '등락율', '매수호가', '매도호가']

def main():
    """
    해외주식 체결추이 조회 테스트 함수
    
    이 함수는 해외주식 체결추이 API를 호출하여 결과를 출력합니다.
    테스트 데이터로 TSLA를 사용합니다.
    
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
        result = quot_inquire_ccnl(excd="NAS", tday="0", symb="TSLA")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return
    
    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())
    
    result = result.rename(columns=COLUMN_MAPPING)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result)

if __name__ == "__main__":
    main() 