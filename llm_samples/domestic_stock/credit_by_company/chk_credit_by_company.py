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
from credit_by_company import credit_by_company

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 종목정보 > 국내주식 당사 신용가능종목[국내주식-111]
##############################################################################################

COLUMN_MAPPING = {
    'stck_shrn_iscd': '주식 단축 종목코드',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'crdt_rate': '신용 비율'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 종목정보
    국내주식 당사 신용가능종목[국내주식-111]

    국내주식 당사 신용가능종목 테스트 함수
    
    Parameters:
        - fid_rank_sort_cls_code (str): 순위 정렬 구분 코드 (0:코드순, 1:이름순)
        - fid_slct_yn (str): 선택 여부 (0:신용주문가능, 1: 신용주문불가)
        - fid_input_iscd (str): 입력 종목코드 (0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100)
        - fid_cond_scr_div_code (str): 조건 화면 분류 코드 (Unique key(20477))
        - fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (시장구분코드 (주식 J))
    Returns:
        - DataFrame: 국내주식 당사 신용가능종목 결과
    
    Example:
        >>> df = credit_by_company(fid_rank_sort_cls_code="0", fid_slct_yn="0", fid_input_iscd="0000", fid_cond_scr_div_code="20477", fid_cond_mrkt_div_code="J")
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
        result = credit_by_company(
            fid_rank_sort_cls_code="0",  # 순위 정렬 구분 코드
            fid_slct_yn="0",  # 선택 여부
            fid_input_iscd="0000",  # 입력 종목코드
            fid_cond_scr_div_code="20477",  # 조건 화면 분류 코드
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
        logger.info("=== 국내주식 당사 신용가능종목 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
