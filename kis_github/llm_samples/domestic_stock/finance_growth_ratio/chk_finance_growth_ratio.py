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
from finance_growth_ratio import finance_growth_ratio

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 종목정보 > 국내주식 성장성비율 [v1_국내주식-085]
##############################################################################################

COLUMN_MAPPING = {
    'stac_yymm': '결산 년월',
    'grs': '매출액 증가율',
    'bsop_prfi_inrt': '영업 이익 증가율',
    'equt_inrt': '자기자본 증가율',
    'totl_aset_inrt': '총자산 증가율'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 종목정보
    국내주식 성장성비율[v1_국내주식-085]

    국내주식 성장성비율 테스트 함수
    
    Parameters:
        - fid_input_iscd (str): 입력 종목코드 (ex : 000660)
        - fid_div_cls_code (str): 분류 구분 코드 (0: 년, 1: 분기)
        - fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (시장구분코드 (주식 J))
    Returns:
        - DataFrame: 국내주식 성장성비율 결과
    
    Example:
        >>> df = finance_growth_ratio(fid_input_iscd="000660", fid_div_cls_code="0", fid_cond_mrkt_div_code="J")
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
        result = finance_growth_ratio(
            fid_input_iscd="000660",  # 입력 종목코드
            fid_div_cls_code="0",  # 분류 구분 코드
            fid_cond_mrkt_div_code="J",  # 조건 시장 분류 코드
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
        logger.info("=== 국내주식 성장성비율 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
