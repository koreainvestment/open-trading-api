# -*- coding: utf-8 -*-
"""
Created on 2025-07-03

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from inquire_asking_price import inquire_asking_price

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물 호가 [해외선물-031]
##############################################################################################

# 상수 정의
COLUMN_MAPPING = {
    'open_price': '시가',
    'high_price': '고가',
    'lowp_rice': '저가',
    'last_price': '현재가',
    'prev_price': '전일종가',
    'vol': '거래량',
    'prev_diff_price': '전일대비가',
    'prev_diff_rate': '전일대비율',
    'quot_date': '호가수신일자',
    'quot_time': '호가수신시각',
    'bid_qntt': '매수수량',
    'bid_num': '매수번호',
    'bid_price': '매수호가',
    'ask_qntt': '매도수량',
    'ask_num': '매도번호',
    'ask_price': '매도호가'
}

NUMERIC_COLUMNS = ['시가', '고가', '저가', '현재가', '전일종가', '거래량', '전일대비가', '전일대비율', 
                   '매수수량', '매수호가', '매도수량', '매도호가']

def main():
    """
    [해외선물옵션] 기본시세
    해외선물 호가[해외선물-031]

    해외선물 호가 테스트 함수
    
    Parameters:
        - srs_cd (str): 종목명 (종목코드)

    Returns:
        - DataFrame: 해외선물 호가 결과
    
    Example:
        >>> df1, df2 = inquire_asking_price(srs_cd="ESZ23")
    """
    try:
        # pandas 출력 옵션 설정
        pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
        pd.set_option('display.width', None)  # 출력 너비 제한 해제
        pd.set_option('display.max_rows', None)  # 모든 행 표시

        # 토큰 발급
        ka.auth()

        # API 호출
        logger.info("API 호출")
        result1, result2 = inquire_asking_price(srs_cd="ESZ25")
        
        # 결과 확인
        results = [result1, result2]
        if all(result is None or result.empty for result in results):
            logger.warning("조회된 데이터가 없습니다.")
            return

        # output1 결과 처리
        logger.info("=== output1 조회 ===")
        if not result1.empty:
            logger.info("사용 가능한 컬럼: %s", result1.columns.tolist())
            
            # 통합 컬럼명 한글 변환 (필요한 컬럼만 자동 매핑됨)
            result1 = result1.rename(columns=COLUMN_MAPPING)
            
            # 숫자형 컬럼 처리
            for col in NUMERIC_COLUMNS:
                if col in result1.columns:
                    result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)
            
            logger.info("output1 결과:")
            print(result1)
        else:
            logger.info("output1 데이터가 없습니다.")

        # output2 결과 처리
        logger.info("=== output2 조회 ===")
        if not result2.empty:
            logger.info("사용 가능한 컬럼: %s", result2.columns.tolist())
            
            # 통합 컬럼명 한글 변환 (필요한 컬럼만 자동 매핑됨)
            result2 = result2.rename(columns=COLUMN_MAPPING)
            
            # 숫자형 컬럼 처리
            for col in NUMERIC_COLUMNS:
                if col in result2.columns:
                    result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)
            
            logger.info("output2 결과:")
            print(result2)
        else:
            logger.info("output2 데이터가 없습니다.")

        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
