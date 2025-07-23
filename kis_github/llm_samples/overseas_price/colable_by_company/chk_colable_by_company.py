"""
Created on 20250101 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from colable_by_company import colable_by_company

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 시세분석 > 당사 해외주식담보대출 가능 종목 [해외주식-051]
##############################################################################################

COLUMN_MAPPING = {
    'pdno': '상품번호',
    'ovrs_item_name': '해외종목명',
    'loan_rt': '대출비율',
    'mgge_mntn_rt': '담보유지비율',
    'mgge_ensu_rt': '담보확보비율',
    'loan_exec_psbl_yn': '대출실행가능여부',
    'stff_name': '직원명',
    'erlm_dt': '등록일자',
    'tr_mket_name': '거래시장명',
    'crcy_cd': '통화코드',
    'natn_kor_name': '국가한글명',
    'ovrs_excg_cd': '해외거래소코드',
    'loan_psbl_item_num': '대출가능종목수'
}

NUMERIC_COLUMNS = []

def main():
    """
    당사 해외주식담보대출 가능 종목 조회 테스트 함수
    
    이 함수는 당사 해외주식담보대출 가능 종목 API를 호출하여 결과를 출력합니다.
    테스트 데이터로 AMD 종목을 사용합니다.
    
    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시
    
    # 인증 토큰 발급
    ka.auth()
    
    # 한줄함수호출 -> 컬럼명 한글 변환 -> 숫자형 컬럼 소수점표시 -> 결과 (case1)
    logger.info("=== case1 조회 ===")
    try:
        result1, result2 = colable_by_company(pdno="AMD", natn_cd="840", inqr_sqn_dvsn="01")
    except ValueError as e:
        logger.error("에러 발생: %s" % str(e))
        return
    
    # output1 처리
    logger.info("=== output1 데이터 ===")
    logger.info("사용 가능한 컬럼: %s", result1.columns.tolist())
    
    result1 = result1.rename(columns=COLUMN_MAPPING)

    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)
    
    logger.info("결과:")
    print(result1)
    
    # output2 처리
    logger.info("=== output2 데이터 ===")
    logger.info("사용 가능한 컬럼: %s", result2.columns.tolist())
    
    result2 = result2.rename(columns=COLUMN_MAPPING)
    
    
    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)
    
    logger.info("결과:")
    print(result2)

if __name__ == "__main__":
    main() 