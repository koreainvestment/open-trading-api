# -*- coding: utf-8 -*-
"""
Created on 2025-06-27

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from inquire_search import inquire_search

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 시세분석 > 해외주식조건검색[v1_해외주식-015]
##############################################################################################

COLUMN_MAPPING = {
    'zdiv': '소수점자리수',
    'stat': '거래상태정보',
    'crec': '현재조회종목수',
    'trec': '전체조회종목수',
    'nrec': 'Record Count',
    'rsym': '실시간조회심볼',
    'excd': '거래소코드',
    'symb': '종목코드',
    'last': '현재가',
    'shar': '발행주식',
    'valx': '시가총액',
    'plow': '저가',
    'phigh': '고가',
    'popen': '시가',
    'tvol': '거래량',
    'rate': '등락율',
    'diff': '대비',
    'sign': '기호',
    'avol': '거래대금',
    'eps': 'EPS',
    'per': 'PER',
    'rank': '순위',
    'e_ordyn': '매매가능'
}

NUMERIC_COLUMNS = ['소수점자리수', '현재가', '발행주식', '시가총액', '저가', '고가', '시가', '거래량', '등락율', '대비', '기호', '거래대금', 'EPS', 'PER', '순위', '매매가능']

def main():
    """
    [해외주식] 기본시세
    해외주식조건검색[v1_해외주식-015]

    해외주식조건검색 테스트 함수
    
    Parameters:
        - auth (str): 사용자권한정보 ("" (Null 값 설정))
        - excd (str): 거래소코드 (NYS : 뉴욕, NAS : 나스닥,  AMS : 아멕스  HKS : 홍콩, SHS : 상해 , SZS : 심천 HSX : 호치민, HNX : 하노이 TSE : 도쿄)
        - co_yn_pricecur (str): 현재가선택조건 (해당조건 사용시(1), 미사용시 필수항목아님)
        - co_st_pricecur (str): 현재가시작범위가 (단위: 각국통화(JPY, USD, HKD, CNY, VND))
        - co_en_pricecur (str): 현재가끝범위가 (단위: 각국통화(JPY, USD, HKD, CNY, VND))
        - co_yn_rate (str): 등락율선택조건 (해당조건 사용시(1), 미사용시 필수항목아님)
        - co_st_rate (str): 등락율시작율 (%)
        - co_en_rate (str): 등락율끝율 (%)
        - co_yn_valx (str): 시가총액선택조건 (해당조건 사용시(1), 미사용시 필수항목아님)
        - co_st_valx (str): 시가총액시작액 (단위: 천)
        - co_en_valx (str): 시가총액끝액 (단위: 천)
        - co_yn_shar (str): 발행주식수선택조건 (해당조건 사용시(1), 미사용시 필수항목아님)
        - co_st_shar (str): 발행주식시작수 (단위: 천)
        - co_en_shar (str): 발행주식끝수 (단위: 천)
        - co_yn_volume (str): 거래량선택조건 (해당조건 사용시(1), 미사용시 필수항목아님)
        - co_st_volume (str): 거래량시작량 (단위: 주)
        - co_en_volume (str): 거래량끝량 (단위: 주)
        - co_yn_amt (str): 거래대금선택조건 (해당조건 사용시(1), 미사용시 필수항목아님)
        - co_st_amt (str): 거래대금시작금 (단위: 천)
        - co_en_amt (str): 거래대금끝금 (단위: 천)
        - co_yn_eps (str): EPS선택조건 (해당조건 사용시(1), 미사용시 필수항목아님)
        - co_st_eps (str): EPS시작 ()
        - co_en_eps (str): EPS끝 ()
        - co_yn_per (str): PER선택조건 (해당조건 사용시(1), 미사용시 필수항목아님)
        - co_st_per (str): PER시작 ()
        - co_en_per (str): PER끝 ()
        - keyb (str): NEXT KEY BUFF ("" 공백 입력)

    Returns:
        - DataFrame: 해외주식조건검색 결과
    
    Example:
        >>> df1, df2 = inquire_search(auth="", excd="NYS", co_yn_pricecur="1", co_st_pricecur="100", co_en_pricecur="200", co_yn_rate="1", co_st_rate="5", co_en_rate="10", co_yn_valx="1", co_st_valx="1000", co_en_valx="5000", co_yn_shar="1", co_st_shar="100", co_en_shar="500", co_yn_volume="1", co_st_volume="1000", co_en_volume="5000", co_yn_amt="1", co_st_amt="1000", co_en_amt="5000", co_yn_eps="1", co_st_eps="1", co_en_eps="5", co_yn_per="1", co_st_per="10", co_en_per="20", keyb="")
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
        logger.info("API 호출 시작: 해외주식조건검색")
        result1, result2 = inquire_search(
            auth = "",
            excd = "NAS",
            co_yn_pricecur = "1",
            co_st_pricecur = "160",
            co_en_pricecur = "170",
            co_yn_rate = "",
            co_st_rate = "",
            co_en_rate = "",
            co_yn_valx = "",
            co_st_valx = "",
            co_en_valx = "",
            co_yn_shar = "",
            co_st_shar = "",
            co_en_shar = "",
            co_yn_volume = "",
            co_st_volume = "",
            co_en_volume = "",
            co_yn_amt = "",
            co_st_amt = "",
            co_en_amt = "",
            co_yn_eps = "",
            co_st_eps = "",
            co_en_eps = "",
            co_yn_per = "",
            co_st_per = "",
            co_en_per = "",
            keyb = "",
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
