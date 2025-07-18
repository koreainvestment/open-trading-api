"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from brknews_title import brknews_title

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 시세분석 > 해외속보(제목) [해외주식-055]
##############################################################################################

COLUMN_MAPPING = {
    'cntt_usiq_srno': '내용조회용일련번호',
    'news_ofer_entp_code': '뉴스제공업체코드',
    'data_dt': '작성일자',
    'data_tm': '작성시간',
    'hts_pbnt_titl_cntt': 'HTS공시제목내용',
    'news_lrdv_code': '뉴스대구분',
    'dorg': '자료원',
    'iscd1': '종목코드1',
    'iscd2': '종목코드2',
    'iscd3': '종목코드3',
    'iscd4': '종목코드4',
    'iscd5': '종목코드5',
    'iscd6': '종목코드6',
    'iscd7': '종목코드7',
    'iscd8': '종목코드8',
    'iscd9': '종목코드9',
    'iscd10': '종목코드10',
    'kor_isnm1': '한글종목명1',
    'kor_isnm2': '한글종목명2',
    'kor_isnm3': '한글종목명3',
    'kor_isnm4': '한글종목명4',
    'kor_isnm5': '한글종목명5',
    'kor_isnm6': '한글종목명6',
    'kor_isnm7': '한글종목명7',
    'kor_isnm8': '한글종목명8',
    'kor_isnm9': '한글종목명9',
    'kor_isnm10': '한글종목명10'
}

NUMERIC_COLUMNS = []

def main():
    """
    해외속보(제목) 조회 테스트 함수
    
    이 함수는 해외속보(제목) API를 호출하여 결과를 출력합니다.
    
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
        result = brknews_title(fid_news_ofer_entp_code="0", fid_cond_scr_div_code="11801")
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