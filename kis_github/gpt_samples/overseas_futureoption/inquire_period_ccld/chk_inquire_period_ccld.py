# -*- coding: utf-8 -*-
"""
Created on 2025-07-02

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_period_ccld import inquire_period_ccld

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 기간계좌손익 일별 [해외선물-010]
##############################################################################################

# 상수 정의
COLUMN_MAPPING = {
    'cano': '종합계좌번호',
    'acnt_prdt_cd': '계좌상품코드',
    'crcy_cd': '통화코드',
    'fm_buy_qty': 'FM매수수량',
    'fm_sll_qty': 'FM매도수량',
    'fm_lqd_pfls_amt': 'FM청산손익금액',
    'fm_fee': 'FM수수료',
    'fm_net_pfls_amt': 'FM순손익금액',
    'fm_ustl_buy_qty': 'FM미결제매수수량',
    'fm_ustl_sll_qty': 'FM미결제매도수량',
    'fm_ustl_evlu_pfls_amt': 'FM미결제평가손익금액',
    'fm_ustl_evlu_pfls_amt2': 'FM미결제평가손익금액2',
    'fm_ustl_evlu_pfls_icdc_amt': 'FM미결제평가손익증감금액',
    'fm_ustl_agrm_amt': 'FM미결제약정금액',
    'fm_opt_lqd_amt': 'FM옵션청산금액',
    'cano': '종합계좌번호',
    'acnt_prdt_cd': '계좌상품코드',
    'ovrs_futr_fx_pdno': '해외선물FX상품번호',
    'crcy_cd': '통화코드',
    'fm_buy_qty': 'FM매수수량',
    'fm_sll_qty': 'FM매도수량',
    'fm_lqd_pfls_amt': 'FM청산손익금액',
    'fm_fee': 'FM수수료',
    'fm_net_pfls_amt': 'FM순손익금액',
    'fm_ustl_buy_qty': 'FM미결제매수수량',
    'fm_ustl_sll_qty': 'FM미결제매도수량',
    'fm_ustl_evlu_pfls_amt': 'FM미결제평가손익금액',
    'fm_ustl_evlu_pfls_amt2': 'FM미결제평가손익금액2',
    'fm_ustl_evlu_pfls_icdc_amt': 'FM미결제평가손익증감금액',
    'fm_ccld_avg_pric': 'FM체결평균가격',
    'fm_ustl_agrm_amt': 'FM미결제약정금액',
    'fm_opt_lqd_amt': 'FM옵션청산금액'
}
NUMERIC_COLUMNS = ['FM매수수량', 'FM매도수량', 'FM청산손익금액', 'FM수수료', 'FM순손익금액', 'FM미결제매수수량', 'FM미결제매도수량', 'FM미결제평가손익금액', 
                   'FM미결제평가손익금액2', 'FM미결제평가손익증감금액', 'FM미결제약정금액', 'FM옵션청산금액', 'FM체결평균가격']

def main():
    """
    [해외선물옵션] 주문/계좌
    해외선물옵션 기간계좌손익 일별[해외선물-010]

    해외선물옵션 기간계좌손익 일별 테스트 함수
    
    Parameters:
        - inqr_term_from_dt (str): 조회기간FROM일자 ()
        - inqr_term_to_dt (str): 조회기간TO일자 ()
        - cano (str): 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        - crcy_cd (str): 통화코드 ('%%% : 전체 TUS: TOT_USD  / TKR: TOT_KRW KRW: 한국  / USD: 미국 EUR: EUR   / HKD: 홍콩 CNY: 중국  / JPY: 일본')
        - whol_trsl_yn (str): 전체환산여부 (N)
        - fuop_dvsn (str): 선물옵션구분 (00:전체 / 01:선물 / 02:옵션)
        - ctx_area_fk200 (str): 연속조회검색조건200 ()
        - ctx_area_nk200 (str): 연속조회키200 ()

    Returns:
        - DataFrame: 해외선물옵션 기간계좌손익 일별 결과
    
    Example:
        >>> df1, df2 = inquire_period_ccld(inqr_term_from_dt="20250601", inqr_term_to_dt="20250630", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, crcy_cd="%%%", whol_trsl_yn="N", fuop_dvsn="00", ctx_area_fk200="", ctx_area_nk200="")
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
        logger.info("API 호출 시작: 해외선물옵션 기간계좌손익 일별")
        result1, result2 = inquire_period_ccld(
            inqr_term_from_dt="20250601",  # 조회기간FROM일자
            inqr_term_to_dt="20250630",  # 조회기간TO일자
            cano=trenv.my_acct,  # 종합계좌번호
            acnt_prdt_cd=trenv.my_prod,  # 계좌상품코드
            crcy_cd="%%%",  # 통화코드
            whol_trsl_yn="N",  # 전체환산여부
            fuop_dvsn="00",  # 선물옵션구분
            ctx_area_fk200="",  # 연속조회검색조건200
            ctx_area_nk200="",  # 연속조회키200
        )
        
        # 결과 확인
        results = [result1, result2]
        if all(result is None or result.empty for result in results):
            logger.warning("조회된 데이터가 없습니다.")
            return
        

        # output1 결과 처리
        logger.info("=== output1 조회 ===")
        if not result1.empty:
            logger.info("사용 가능한 컬럼: %s", result1.columns.tolist())
            
            # 통합 컬럼명 한글 변환 (필요한 컬럼만 자동 매핑됨)
            result1 = result1.rename(columns=COLUMN_MAPPING)
            for col in NUMERIC_COLUMNS:
                if col in result1.columns:
                    result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)
            logger.info("output1 결과:")
            print(result1)
        else:
            logger.info("output1 데이터가 없습니다.")

        # output2 결과 처리
        logger.info("=== output2 조회 ===")
        if not result2.empty:
            logger.info("사용 가능한 컬럼: %s", result2.columns.tolist())
            
            # 통합 컬럼명 한글 변환 (필요한 컬럼만 자동 매핑됨)
            result2 = result2.rename(columns=COLUMN_MAPPING)
            for col in NUMERIC_COLUMNS:
                if col in result2.columns:
                    result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)
            logger.info("output2 결과:")
            print(result2)
        else:
            logger.info("output2 데이터가 없습니다.")

        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
