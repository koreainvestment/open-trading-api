"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_time_optchartprice import inquire_time_optchartprice

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외선물옵션] 기본시세 > 해외옵션 분봉조회 [해외선물-040]
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

NUMERIC_COLUMNS = ['자료개수', 'N틱최종개수', '전일대비구분', '전일대비가격', '전일대비율', '시가', '고가', '저가', '체결가격', '체결수량', '누적거래수량']

def main():
    """
    해외옵션 분봉조회 테스트 함수
    
    이 함수는 해외옵션 분봉조회 API를 호출하여 결과를 출력합니다.
    테스트 데이터로 DXM24 (ICE 거래소)를 사용합니다.
    
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
        result1, result2 = inquire_time_optchartprice(srs_cd="DXM24", exch_cd="ICE", qry_cnt="30")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return
    
    # output1 처리
    logging.info("=== output1 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())
    
    result1 = result1.rename(columns=COLUMN_MAPPING)
    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result1)
    
    # output2 처리
    logging.info("=== output2 결과 ===")
    logging.info("사용 가능한 컬럼: %s" % result2.columns.tolist())
    
    result2 = result2.rename(columns=COLUMN_MAPPING)
    
    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result2)

if __name__ == "__main__":
    main() 