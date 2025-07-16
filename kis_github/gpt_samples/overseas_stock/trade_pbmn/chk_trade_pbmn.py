"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from trade_pbmn import trade_pbmn

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외주식] 시세분석 > 해외주식 거래대금순위[해외주식-044]
##############################################################################################

def main():
    """
    해외주식 거래대금순위 조회 테스트 함수
    
    이 함수는 해외주식 거래대금순위 API를 호출하여 결과를 출력합니다.
    테스트 데이터로 나스닥 거래소를 사용합니다.
    
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
        result1, result2 = trade_pbmn(excd="NAS", nday="0", vol_rang="0")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return
    
    # output1 처리
    logging.info("=== output1 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())
    
    # 컬럼명 한글 변환 및 데이터 출력
    column_mapping1 = {
        'zdiv': '소수점자리수',
        'stat': '거래상태정보',
        'crec': '현재조회종목수',
        'trec': '전체조회종목수',
        'nrec': 'RecordCount'
    }
    
    result1 = result1.rename(columns=column_mapping1)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시
    numeric_columns = []
    
    for col in numeric_columns:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result1)
    
    # output2 처리
    logging.info("=== output2 결과 ===")
    logging.info("사용 가능한 컬럼: %s" % result2.columns.tolist())
    
    # 컬럼명 한글 변환 및 데이터 출력
    column_mapping2 = {
        'rsym': '실시간조회심볼',
        'excd': '거래소코드',
        'symb': '종목코드',
        'name': '종목명',
        'last': '현재가',
        'sign': '기호',
        'diff': '대비',
        'rate': '등락율',
        'pask': '매도호가',
        'pbid': '매수호가',
        'tvol': '거래량',
        'tamt': '거래대금',
        'a_tamt': '평균거래대금',
        'rank': '순위',
        'ename': '영문종목명',
        'e_ordyn': '매매가능'
    }
    
    result2 = result2.rename(columns=column_mapping2)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시
    numeric_columns = []
    
    for col in numeric_columns:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result2)

if __name__ == "__main__":
    main() 