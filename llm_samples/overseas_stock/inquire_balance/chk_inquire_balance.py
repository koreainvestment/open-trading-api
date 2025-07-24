"""
Created on 2025-06-30

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from inquire_balance import inquire_balance

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 잔고 [v1_해외주식-006]
##############################################################################################

COLUMN_MAPPING = {
    'cano': '종합계좌번호',
    'acnt_prdt_cd': '계좌상품코드',
    'prdt_type_cd': '상품유형코드',
    'ovrs_pdno': '해외상품번호',
    'frcr_evlu_pfls_amt': '외화평가손익금액',
    'evlu_pfls_rt': '평가손익율',
    'pchs_avg_pric': '매입평균가격',
    'ovrs_cblc_qty': '해외잔고수량',
    'ord_psbl_qty': '주문가능수량',
    'frcr_pchs_amt1': '외화매입금액1',
    'ovrs_stck_evlu_amt': '해외주식평가금액',
    'now_pric2': '현재가격2',
    'tr_crcy_cd': '거래통화코드',
    'ovrs_excg_cd': '해외거래소코드',
    'loan_type_cd': '대출유형코드',
    'loan_dt': '대출일자',
    'expd_dt': '만기일자',
    'frcr_pchs_amt1': '외화매입금액1',
    'ovrs_rlzt_pfls_amt': '해외실현손익금액',
    'ovrs_tot_pfls': '해외총손익',
    'rlzt_erng_rt': '실현수익율',
    'tot_evlu_pfls_amt': '총평가손익금액',
    'tot_pftrt': '총수익률',
    'frcr_buy_amt_smtl1': '외화매수금액합계1',
    'ovrs_rlzt_pfls_amt2': '해외실현손익금액2',
    'frcr_buy_amt_smtl2': '외화매수금액합계2'
}

# 숫자형 컬럼 정의
NUMERIC_COLUMNS = []

def main():
    """
    [해외주식] 주문/계좌
    해외주식 잔고[해외주식-006]

    해외주식 잔고 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 ()
        - acnt_prdt_cd (str): 계좌상품코드 ()
        - ovrs_excg_cd (str): 해외거래소코드 ()
        - tr_crcy_cd (str): 거래통화코드 ()
        - FK200 (str): 연속조회검색조건200 ()
        - NK200 (str): 연속조회키200 ()

    Returns:
        - DataFrame: 해외주식 잔고 결과
    
    Example:
        >>> df = inquire_balance(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, ovrs_excg_cd="NASD", tr_crcy_cd="USD")
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
        trenv = ka.getTREnv()

        # API 호출
        logger.info("API 호출")
        result1, result2 = inquire_balance(
            cano=trenv.my_acct,  # 종합계좌번호
            acnt_prdt_cd=trenv.my_prod,  # 계좌상품코드
            ovrs_excg_cd="NASD",  # 해외거래소코드
            tr_crcy_cd="USD",  # 거래통화코드
            FK200="",  # 연속조회검색조건200
            NK200="",  # 연속조회키200
        )
        
        # output1 결과 처리
        logging.info("=== output1 결과 ===")
        logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())
        
        # 한글 컬럼명으로 변환
        result1 = result1.rename(columns=COLUMN_MAPPING)
        
        # 숫자형 컬럼 소수점 둘째자리까지 표시
        for col in NUMERIC_COLUMNS:
            if col in result1.columns:
                result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)
        
        logging.info("결과:")
        print(result1)
        
        # output3 결과 처리
        logging.info("=== output2 결과 ===")
        logging.info("사용 가능한 컬럼: %s", result2.columns.tolist())
        
        # 한글 컬럼명으로 변환
        result2 = result2.rename(columns=COLUMN_MAPPING)
        
        # 숫자형 컬럼 소수점 둘째자리까지 표시
        for col in NUMERIC_COLUMNS:
            if col in result2.columns:
                result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)
        
        logging.info("결과(output2):")
        print(result2)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
