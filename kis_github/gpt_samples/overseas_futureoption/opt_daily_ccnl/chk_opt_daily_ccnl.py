"""
Created on 20250129 
@author: LaivData SJPark with cursor
"""
import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from opt_daily_ccnl import opt_daily_ccnl

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외선물옵션] 기본시세 > 해외옵션 체결추이(일간) [해외선물-037]
##############################################################################################

# 상수 정의
COLUMN_MAPPING = {
    'ret_cnt': '자료개수',
    'last_n_cnt': 'N틱최종개수',
    'index_key': '이전조회KEY',
    'data_date': '일자',
    'data_time': '시간',
    'open_price': '시가',
    'high_price': '고가',
    'low_price': '저가',
    'last_price': '체결가격',
    'last_qntt': '체결수량',
    'vol': '누적거래수량',
    'prev_diff_flag': '전일대비구분',
    'prev_diff_price': '전일대비가격',
    'prev_diff_rate': '전일대비율'
}

NUMERIC_COLUMNS = ['자료개수', 'N틱최종개수', '시가', '고가', '저가', '체결가격', '체결수량', '누적거래수량', '전일대비가격', '전일대비율']

def main():
    """
    해외옵션 체결추이(일간) 조회 테스트 함수
    
    이 함수는 해외옵션 체결추이(일간) API를 호출하여 결과를 출력합니다.
    
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
        result1, result2 = opt_daily_ccnl(srs_cd="DXM24", exch_cd="ICE", qry_cnt="30")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return
    
    # output1 처리
    logging.info("=== output1 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())
    
    # 컬럼명 한글 변환 및 데이터 출력
    result1 = result1.rename(columns=COLUMN_MAPPING)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result1)
    
    # output2 처리
    logging.info("=== output2 결과 ===")
    logging.info("사용 가능한 컬럼: %s" % result2.columns.tolist())
    
    # 컬럼명 한글 변환 및 데이터 출력
    result2 = result2.rename(columns=COLUMN_MAPPING)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result2)

if __name__ == "__main__":
    main() 