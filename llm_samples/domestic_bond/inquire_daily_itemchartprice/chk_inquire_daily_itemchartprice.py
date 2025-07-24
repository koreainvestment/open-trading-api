# -*- coding: utf-8 -*-
"""
Created on 2025-06-19

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from inquire_daily_itemchartprice import inquire_daily_itemchartprice

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [장내채권] 기본시세 > 장내채권 기간별시세(일) [국내주식-159]
##############################################################################################

COLUMN_MAPPING = {
    'stck_bsop_date': '주식영업일자',
    'bond_oprc': '채권시가2',
    'bond_hgpr': '채권고가',
    'bond_lwpr': '채권저가',
    'bond_prpr': '채권현재가',
    'acml_vol': '누적거래량'
}

NUMERIC_COLUMNS = []

def main():
    """
    [장내채권] 기본시세
    장내채권 기간별시세(일)[국내주식-159]

    장내채권 기간별시세(일) 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건 시장 구분 코드 (Unique key(B))
        - fid_input_iscd (str): 입력 종목코드 (채권종목코드)
    Returns:
        - DataFrame: 장내채권 기간별시세(일) 결과
    
    Example:
        >>> df = inquire_daily_itemchartprice(fid_cond_mrkt_div_code="B", fid_input_iscd="KR2033022D33")
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
        logger.info("API 호출 시작: 장내채권 기간별시세(일)")
        result = inquire_daily_itemchartprice(
            fid_cond_mrkt_div_code="B",  # 조건 시장 구분 코드
            fid_input_iscd="KR103502GA34",  # 입력 종목코드
        )
        
        if result is None or result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return
        
        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())

        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)

        # 숫자형 컬럼 변환
        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce')

        # 결과 출력
        logger.info("=== 장내채권 기간별시세(일) 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
