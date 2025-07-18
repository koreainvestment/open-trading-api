# -*- coding: utf-8 -*-
"""
Created on 2025-06-17

@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from search_info import search_info

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 종목정보 > 상품기본조회[v1_국내주식-029]
##############################################################################################

COLUMN_MAPPING = {
    'pdno': '상품번호',
    'prdt_type_cd': '상품유형코드',
    'std_pdno': '표준상품번호',
    'shtn_pdno': '단축상품번호',
    'prdt_sale_stat_cd': '상품판매상태코드',
    'prdt_risk_grad_cd': '상품위험등급코드',
    'prdt_clsf_cd': '상품분류코드',
    'sale_strt_dt': '판매시작일자',
    'sale_end_dt': '판매종료일자',
    'wrap_asst_type_cd': '랩어카운트자산유형코드',
    'ivst_prdt_type_cd': '투자상품유형코드',
    'frst_erlm_dt': '최초등록일자'
}

NUMERIC_COLUMNS = []


def main():
    """
    [국내주식] 종목정보
    상품기본조회[v1_국내주식-029]

    상품기본조회 테스트 함수
    
    Parameters:
        - pdno (str): 상품번호 ('주식(하이닉스) :  000660 (코드 : 300) 선물(101S12) :  KR4101SC0009 (코드 : 301) 미국(AAPL) : AAPL (코드 : 512)')
        - prdt_type_cd (str): 상품유형코드 ('300 주식 301 선물옵션 302 채권 512  미국 나스닥 / 513  미국 뉴욕 / 529  미국 아멕스  515  일본 501  홍콩 / 543  홍콩CNY / 558  홍콩USD 507  베트남 하노이 / 508  베트남 호치민 551  중국 상해A / 552  중국 심천A')
    Returns:
        - DataFrame: 상품기본조회 결과
    
    Example:
        >>> df = search_info(pdno="000660", prdt_type_cd="300")
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
        result = search_info(
            pdno="000660",  # pdno = "AAPL",  # 상품번호
            prdt_type_cd="300",  # prdt_type_cd = "512",  # 상품유형코드
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
        logger.info("=== 상품기본조회 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
