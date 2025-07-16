"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_ccnl import inquire_ccnl

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외주식] 기본시세 > 해외주식 체결추이[해외주식-037]
##############################################################################################

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
        result = inquire_ccnl(excd="NAS", tday="0", symb="TSLA")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return
    
    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())
    
    # 컬럼명 한글 변환 및 데이터 출력
    column_mapping = {
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
    
    result = result.rename(columns=column_mapping)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시
    numeric_columns = []
    
    for col in numeric_columns:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result)

if __name__ == "__main__":
    main() 