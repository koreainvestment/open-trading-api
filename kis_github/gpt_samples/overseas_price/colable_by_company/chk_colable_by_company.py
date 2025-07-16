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
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외주식] 시세분석 > 당사 해외주식담보대출 가능 종목 [해외주식-051]
##############################################################################################

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
    logging.info("=== case1 조회 ===")
    try:
        result1, result2 = colable_by_company(pdno="AMD", natn_cd="840", inqr_sqn_dvsn="01")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return
    
    # output1 처리
    logging.info("=== output1 데이터 ===")
    logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())
    
    # 컬럼명 한글 변환
    column_mapping1 = {
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
        'ovrs_excg_cd': '해외거래소코드'
    }
    
    result1 = result1.rename(columns=column_mapping1)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에 number로 명시된 필드 없음)
    numeric_columns = []
    
    for col in numeric_columns:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result1)
    
    # output2 처리
    logging.info("=== output2 데이터 ===")
    logging.info("사용 가능한 컬럼: %s", result2.columns.tolist())
    
    # 컬럼명 한글 변환
    column_mapping2 = {
        'loan_psbl_item_num': '대출가능종목수'
    }
    
    result2 = result2.rename(columns=column_mapping2)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에 number로 명시된 필드 없음)
    numeric_columns = []
    
    for col in numeric_columns:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result2)

if __name__ == "__main__":
    main() 