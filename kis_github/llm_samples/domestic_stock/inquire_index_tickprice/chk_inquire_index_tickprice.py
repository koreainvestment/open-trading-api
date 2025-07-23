# -*- coding: utf-8 -*-
"""
Created on 2025-06-17

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from inquire_index_tickprice import inquire_index_tickprice

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 업종/기타 > 국내업종 시간별지수(초)[국내주식-064]
##############################################################################################

COLUMN_MAPPING = {
    'stck_cntg_hour': '주식 체결 시간',
    'bstp_nmix_prpr': '업종 지수 현재가',
    'bstp_nmix_prdy_vrss': '업종 지수 전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'bstp_nmix_prdy_ctrt': '업종 지수 전일 대비율',
    'acml_tr_pbmn': '누적 거래 대금',
    'acml_vol': '누적 거래량',
    'cntg_vol': '체결 거래량'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 업종/기타
    국내업종 시간별지수(초)[국내주식-064]

    국내업종 시간별지수(초) 테스트 함수
    
    Parameters:
        - fid_input_iscd (str): 입력 종목코드 (0001:거래소, 1001:코스닥, 2001:코스피200, 3003:KSQ150)
        - fid_cond_mrkt_div_code (str): 시장 분류 코드 (시장구분코드 (업종 U))
    Returns:
        - DataFrame: 국내업종 시간별지수(초) 결과
    
    Example:
        >>> df = inquire_index_tickprice(fid_input_iscd="0001", fid_cond_mrkt_div_code="U")
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
        result = inquire_index_tickprice(
            fid_input_iscd="0001",  # 입력 종목코드
            fid_cond_mrkt_div_code="U",  # 시장 분류 코드
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
        logger.info("=== 국내업종 시간별지수(초) 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
