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
from finance_income_statement import finance_income_statement

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 종목정보 > 국내주식 손익계산서 [v1_국내주식-079]
##############################################################################################

COLUMN_MAPPING = {
    'stac_yymm': '결산 년월',
    'sale_account': '매출액',
    'sale_cost': '매출 원가',
    'sale_totl_prfi': '매출 총 이익',
    'depr_cost': '감가상각비',
    'sell_mang': '판매 및 관리비',
    'bsop_prti': '영업 이익',
    'bsop_non_ernn': '영업 외 수익',
    'bsop_non_expn': '영업 외 비용',
    'op_prfi': '경상 이익',
    'spec_prfi': '특별 이익',
    'spec_loss': '특별 손실',
    'thtr_ntin': '당기순이익'
}

NUMERIC_COLUMNS = []


def main():
    """
    [국내주식] 종목정보
    국내주식 손익계산서[v1_국내주식-079]

    국내주식 손익계산서 테스트 함수
    
    Parameters:
        - fid_div_cls_code (str): 분류 구분 코드 (0: 년, 1: 분기  ※ 분기데이터는 연단위 누적합산)
        - fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (J)
        - fid_input_iscd (str): 입력 종목코드 (000660 : 종목코드)
    Returns:
        - DataFrame: 국내주식 손익계산서 결과
    
    Example:
        >>> df = finance_income_statement(fid_div_cls_code="0", fid_cond_mrkt_div_code="J", fid_input_iscd="000660")
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
        result = finance_income_statement(
            fid_div_cls_code="0",  # 분류 구분 코드
            fid_cond_mrkt_div_code="J",  # 조건 시장 분류 코드
            fid_input_iscd="000660",  # 입력 종목코드
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
        logger.info("=== 국내주식 손익계산서 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)

    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise


if __name__ == "__main__":
    main()
