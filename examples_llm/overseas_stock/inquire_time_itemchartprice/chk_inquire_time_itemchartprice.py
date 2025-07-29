# -*- coding: utf-8 -*-
"""
Created on 2025-06-30

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from inquire_time_itemchartprice import inquire_time_itemchartprice

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 기본시세 > 해외주식분봉조회[v1_해외주식-030]
##############################################################################################

COLUMN_MAPPING = {
    'rsym': '실시간종목코드',
    'zdiv': '소수점자리수',
    'stim': '장시작현지시간',
    'etim': '장종료현지시간',
    'sktm': '장시작한국시간',
    'ektm': '장종료한국시간',
    'next': '다음가능여부',
    'more': '추가데이타여부',
    'nrec': '레코드갯수',
    'tymd': '현지영업일자',
    'xymd': '현지기준일자',
    'xhms': '현지기준시간',
    'kymd': '한국기준일자',
    'khms': '한국기준시간',
    'open': '시가',
    'high': '고가',
    'low': '저가',
    'last': '종가',
    'evol': '체결량',
    'eamt': '체결대금'
}

NUMERIC_COLUMNS = ['소수점자리수', '시가', '고가', '저가', '종가', '체결량', '체결대금']

def main():
    """
    [해외주식] 기본시세
    해외주식분봉조회[v1_해외주식-030]

    해외주식분봉조회 테스트 함수
    
    Parameters:
        - auth (str): 사용자권한정보 ("" 공백으로 입력)
        - excd (str): 거래소코드 (NYS : 뉴욕 NAS : 나스닥 AMS : 아멕스  HKS : 홍콩 SHS : 상해  SZS : 심천 HSX : 호치민 HNX : 하노이 TSE : 도쿄   ※ 주간거래는 최대 1일치 분봉만 조회 가능 BAY : 뉴욕(주간) BAQ : 나스닥(주간) BAA : 아멕스(주간))
        - symb (str): 종목코드 (종목코드(ex. TSLA))
        - nmin (str): 분갭 (분단위(1: 1분봉, 2: 2분봉, ...))
        - pinc (str): 전일포함여부 (0:당일 1:전일포함 ※ 다음조회 시 반드시 "1"로 입력)
        - next (str): 다음여부 (처음조회 시, "" 공백 입력 다음조회 시, "1" 입력)
        - nrec (str): 요청갯수 (레코드요청갯수 (최대 120))
        - fill (str): 미체결채움구분 ("" 공백으로 입력)
        - keyb (str): NEXT KEY BUFF (처음 조회 시, "" 공백 입력 다음 조회 시, 이전 조회 결과의 마지막 분봉 데이터를 이용하여, 1분 전 혹은 n분 전의 시간을 입력  (형식: YYYYMMDDHHMMSS, ex. 20241014140100))

    Returns:
        - DataFrame: 해외주식분봉조회 결과
    
    Example:
        >>> df1, df2 = inquire_time_itemchartprice(auth="", excd="NAS", symb="TSLA", nmin="5", pinc="1", next="", nrec="120", fill="", keyb="")
    """
    try:
        # pandas 출력 옵션 설정
        pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
        pd.set_option('display.width', None)  # 출력 너비 제한 해제
        pd.set_option('display.max_rows', None)  # 모든 행 표시

        # 토큰 발급
        logger.info("토큰 발급 중...")
        ka.auth()
        logger.info("토큰 발급 완료")


        
        # API 호출
        logger.info("API 호출 시작: 해외주식분봉조회")
        result1, result2 = inquire_time_itemchartprice(
            auth="",
            excd="NAS",
            symb="TSLA",
            nmin="5",
            pinc="1",
            next="",
            nrec="120",
            fill="",
            keyb="",
        )
        
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
