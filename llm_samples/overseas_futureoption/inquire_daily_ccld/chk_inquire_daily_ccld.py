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
from inquire_daily_ccld import inquire_daily_ccld

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 일별체결내역[해외선물-011]
##############################################################################################

COLUMN_MAPPING = {
    'fm_tot_ccld_qty': 'FM총체결수량',
    'fm_tot_futr_agrm_amt': 'FM총선물약정금액',
    'fm_tot_opt_agrm_amt': 'FM총옵션약정금액',
    'fm_fee_smtl': 'FM수수료합계',
    'dt': '일자',
    'ccno': '체결번호',
    'ovrs_futr_fx_pdno': '해외선물FX상품번호',
    'sll_buy_dvsn_cd': '매도매수구분코드',
    'fm_ccld_qty': 'FM체결수량',
    'fm_ccld_amt': 'FM체결금액',
    'fm_futr_ccld_amt': 'FM선물체결금액',
    'fm_opt_ccld_amt': 'FM옵션체결금액',
    'crcy_cd': '통화코드',
    'fm_fee': 'FM수수료',
    'fm_futr_pure_agrm_amt': 'FM선물순약정금액',
    'fm_opt_pure_agrm_amt': 'FM옵션순약정금액',
    'ccld_dtl_dtime': '체결상세일시',
    'ord_dt': '주문일자',
    'odno': '주문번호',
    'ord_mdia_dvsn_name': '주문매체구분명'
}

NUMERIC_COLUMNS = ['FM총체결수량', 'FM총선물약정금액', 'FM총옵션약정금액', 'FM수수료합계', 'FM체결수량', 'FM체결금액', 'FM선물체결금액',
                    'FM옵션체결금액', 'FM수수료', 'FM선물순약정금액', 'FM옵션순약정금액']


def main():
    """
    [해외선물옵션] 주문/계좌
    해외선물옵션 일별 체결내역[해외선물-011]

    해외선물옵션 일별 체결내역 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        - strt_dt (str): 시작일자 (시작일자(YYYYMMDD))
        - end_dt (str): 종료일자 (종료일자(YYYYMMDD))
        - fuop_dvsn_cd (str): 선물옵션구분코드 (00:전체 / 01:선물 / 02:옵션)
        - fm_pdgr_cd (str): FM상품군코드 (공란(Default))
        - crcy_cd (str): 통화코드 (%%% : 전체 TUS: TOT_USD  / TKR: TOT_KRW KRW: 한국  / USD: 미국 EUR: EUR   / HKD: 홍콩 CNY: 중국  / JPY: 일본 VND: 베트남)
        - fm_item_ftng_yn (str): FM종목합산여부 ("N"(Default))
        - sll_buy_dvsn_cd (str): 매도매수구분코드 (%%: 전체 / 01 : 매도 / 02 : 매수)
        - ctx_area_fk200 (str): 연속조회검색조건200 ()
        - ctx_area_nk200 (str): 연속조회키200 ()

    Returns:
        - DataFrame: 해외선물옵션 일별 체결내역 결과
    
    Example:
        >>> df1, df2 = inquire_daily_ccld(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, strt_dt="20250101", end_dt="20250131", fuop_dvsn_cd="00", fm_pdgr_cd="", crcy_cd="%%%", fm_item_ftng_yn="N", sll_buy_dvsn_cd="%%", ctx_area_fk200="", ctx_area_nk200="")
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
        logger.info("API 호출 시작: 해외선물옵션 일별 체결내역")
        result1, result2 = inquire_daily_ccld(
            cano=trenv.my_acct,  # 종합계좌번호
            acnt_prdt_cd=trenv.my_prod,  # 계좌상품코드
            strt_dt="20250601",  # 시작일자
            end_dt="20250702",  # 종료일자
            fuop_dvsn_cd="00",  # 선물옵션구분코드
            fm_pdgr_cd="",  # FM상품군코드
            crcy_cd="%%%",  # 통화코드
            fm_item_ftng_yn="N",  # FM종목합산여부
            sll_buy_dvsn_cd="%%",  # 매도매수구분코드
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
