# -*- coding: utf-8 -*-
"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from news_title import news_title

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 시세분석 > 해외뉴스종합(제목) [해외주식-053]
##############################################################################################

COLUMN_MAPPING = {
    'info_gb': '뉴스구분',
    'news_key': '뉴스키',
    'data_dt': '조회일자',
    'data_tm': '조회시간',
    'class_cd': '중분류',
    'class_name': '중분류명',
    'source': '자료원',
    'nation_cd': '국가코드',
    'exchange_cd': '거래소코드',
    'symb': '종목코드',
    'symb_name': '종목명',
    'title': '제목'
}

NUMERIC_COLUMNS = []

def main():
    """
    해외뉴스종합 테스트 함수
    """
    try:
        # 토큰 발급
        logger.info("토큰 발급 중...")
        ka.auth()
        logger.info("토큰 발급 완료")

        # API 호출
        logger.info("API 호출")
        result = news_title(
            info_gb="",
            class_cd="",
            nation_cd="",
            exchange_cd="",
            symb="",
            data_dt="",
            data_tm="",
            cts=""
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
        logger.info("=== 해외뉴스종합 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main() 