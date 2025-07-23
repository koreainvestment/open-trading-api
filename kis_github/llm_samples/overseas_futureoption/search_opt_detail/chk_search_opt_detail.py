"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from search_opt_detail import search_opt_detail

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외선물옵션] 기본시세 > 해외옵션 상품기본정보 [해외선물-041]
##############################################################################################

# 컬럼명 매핑
COLUMN_MAPPING = {
    'exch_cd': '거래소코드',
    'clas_cd': '품목종류',
    'crc_cd': '거래통화',
    'sttl_price': '정산가',
    'sttl_date': '정산일',
    'trst_mgn': '증거금',
    'disp_digit': '가격표시진법',
    'tick_sz': '틱사이즈',
    'tick_val': '틱가치',
    'mrkt_open_date': '장개시일자',
    'mrkt_open_time': '장개시시각',
    'mrkt_close_date': '장마감일자',
    'mrkt_close_time': '장마감시각',
    'trd_fr_date': '상장일',
    'expr_date': '만기일',
    'trd_to_date': '최종거래일',
    'remn_cnt': '잔존일수',
    'stat_tp': '매매여부',
    'ctrt_size': '계약크기',
    'stl_tp': '최종결제구분',
    'frst_noti_date': '최초식별일'
}

# 숫자형 컬럼
NUMERIC_COLUMNS = []

def main():
    """
    해외옵션 상품기본정보 조회 테스트 함수
    
    이 함수는 해외옵션 상품기본정보 API를 호출하여 결과를 출력합니다.
    테스트 데이터로 6AM24 종목코드를 사용합니다.
    
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
        result = search_opt_detail(qry_cnt="1", srs_cd_01="6AM24")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return
    
    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())
    
    # 한글 컬럼명으로 변환
    result = result.rename(columns=COLUMN_MAPPING)
    
    # 메타데이터에 자료형이 명시적으로 'number'로 선언된 필드 없음
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result)

if __name__ == "__main__":
    main() 