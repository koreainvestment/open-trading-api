"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_algo_ccnl import inquire_algo_ccnl

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 지정가체결내역조회 [해외주식-070]
##############################################################################################

# 컬럼 매핑 정의
COLUMN_MAPPING = {
    'CCLD_SEQ': '체결순번',
    'CCLD_BTWN': '체결시간',
    'PDNO': '상품번호',
    'ITEM_NAME': '종목명',
    'FT_CCLD_QTY': 'FT체결수량',
    'FT_CCLD_UNPR3': 'FT체결단가',
    'FT_CCLD_AMT3': 'FT체결금액',
    'ODNO': '주문번호',
    'TRAD_DVSN_NAME': '매매구분명',
    'FT_ORD_QTY': 'FT주문수량',
    'FT_ORD_UNPR3': 'FT주문단가',
    'ORD_TMD': '주문시각',
    'SPLT_BUY_ATTR_NAME': '분할매수속성명',
    'TR_CRCY': '거래통화',
    'CCLD_CNT': '체결건수'
}

# 숫자형 컬럼 정의
NUMERIC_COLUMNS = []

def main():
    """
    해외주식 지정가체결내역조회 테스트 함수
    
    이 함수는 해외주식 지정가체결내역조회 API를 호출하여 결과를 출력합니다.
    테스트 데이터로 case1의 파라미터를 사용합니다.
    
    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시
    
    # 인증 토큰 발급
    ka.auth()

    trenv = ka.getTREnv()

    # API 호출
    logging.info("API 호출")
    try:
        result, result3 = inquire_algo_ccnl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod,)
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return
    
    # output 결과 처리
    logging.info("=== output 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())
    
    # 한글 컬럼명으로 변환
    result = result.rename(columns=COLUMN_MAPPING)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result)
    
    # output3 결과 처리
    logging.info("=== output3 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result3.columns.tolist())
    
    # 한글 컬럼명으로 변환
    result3 = result3.rename(columns=COLUMN_MAPPING)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result3.columns:
            result3[col] = pd.to_numeric(result3[col], errors='coerce').round(2)
    
    logging.info("결과(output3):")
    print(result3)

if __name__ == "__main__":
    main() 