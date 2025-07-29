# -*- coding: utf-8 -*-
"""
Created on 2025-06-16

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from dividend_rate import dividend_rate

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 순위분석 > 국내주식 배당률 상위[국내주식-106]
##############################################################################################

COLUMN_MAPPING = {
    'rank': '순위',
    'sht_cd': '종목코드',
    'record_date': '기준일',
    'per_sto_divi_amt': '현금/주식배당금',
    'divi_rate': '현금/주식배당률(%)',
    'divi_kind': '배당종류'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 순위분석
    국내주식 배당률 상위[국내주식-106]

    국내주식 배당률 상위 테스트 함수
    
    Parameters:
        - cts_area (str): CTS_AREA (공백)
        - gb1 (str): KOSPI (0:전체, 1:코스피,  2: 코스피200, 3: 코스닥)
        - upjong (str): 업종구분 ('코스피(0001:종합, 0002:대형주.…0027:제조업 ),  코스닥(1001:종합, …. 1041:IT부품 코스피200 (2001:KOSPI200, 2007:KOSPI100, 2008:KOSPI50)')
        - gb2 (str): 종목선택 (0:전체, 6:보통주, 7:우선주)
        - gb3 (str): 배당구분 (1:주식배당, 2: 현금배당)
        - f_dt (str): 기준일From ()
        - t_dt (str): 기준일To ()
        - gb4 (str): 결산/중간배당 (0:전체, 1:결산배당, 2:중간배당)
    Returns:
        - DataFrame: 국내주식 배당률 상위 결과
    
    Example:
        >>> df = dividend_rate(cts_area="", gb1="0", upjong="0001", gb2="0", gb3="1", f_dt="20230101", t_dt="20231231", gb4="0")
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
        result = dividend_rate(
            cts_area="",  # CTS_AREA
            gb1="0",  # KOSPI
            upjong="0001",  # 업종구분
            gb2="0",  # 종목선택
            gb3="1",  # 배당구분
            f_dt="20230101",  # 기준일From
            t_dt="20231231",  # 기준일To
            gb4="0",  # 결산/중간배당
        )

        if result is None or result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return

        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())

        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)

        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

        # 결과 출력
        logger.info("=== 국내주식 배당률 상위 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)

    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise


if __name__ == "__main__":
    main()
