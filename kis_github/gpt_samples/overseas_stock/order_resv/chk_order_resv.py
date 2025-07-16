"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from order_resv import order_resv

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 예약주문접수[v1_해외주식-002]
##############################################################################################

def main():
    """
    해외주식 예약주문접수 조회 테스트 함수
    
    이 함수는 해외주식 예약주문접수 API를 호출하여 결과를 출력합니다.
    테스트 데이터로 TSLA 주식을 사용합니다.
    
    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시
    
    # 인증 토큰 발급
    ka.auth()
    
    # case1 조회
    logging.info("=== case1 조회 ===")
    try:
        result = order_resv(env_dv="real", ord_dv="usBuy", cano="81180744", acnt_prdt_cd="01", pdno="TSLA", ovrs_excg_cd="NASD", ft_ord_qty="1", ft_ord_unpr3="900")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return
    
    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())
    
    # 컬럼명 한글 변환 및 데이터 출력
    column_mapping = {
        'ODNO': '한국거래소전송주문조직번호',
        'RSVN_ORD_RCIT_DT': '예약주문접수일자',
        'OVRS_RSVN_ODNO': '해외예약주문번호'
    }
    
    result = result.rename(columns=column_mapping)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시
    numeric_columns = []
    
    for col in numeric_columns:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result)

if __name__ == "__main__":
    main() 