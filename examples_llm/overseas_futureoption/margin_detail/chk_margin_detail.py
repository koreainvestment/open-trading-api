# -*- coding: utf-8 -*-
"""
Created on 2025-07-02

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from margin_detail import margin_detail

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 증거금상세 [해외선물-032]
##############################################################################################

# 상수 정의
COLUMN_MAPPING = {
    'cano': '종합계좌번호',
    'acnt_prdt_cd': '계좌상품코드',
    'crcy_cd': '통화코드',
    'resp_dt': '응답일자',
    'acnt_net_risk_mgna_aply_yn': '계좌순위험증거금적용여부',
    'fm_ord_psbl_amt': 'FM주문가능금액',
    'fm_add_mgn_amt': 'FM추가증거금액',
    'fm_brkg_mgn_amt': 'FM위탁증거금액',
    'fm_excc_brkg_mgn_amt': 'FM정산위탁증거금액',
    'fm_ustl_mgn_amt': 'FM미결제증거금액',
    'fm_mntn_mgn_amt': 'FM유지증거금액',
    'fm_ord_mgn_amt': 'FM주문증거금액',
    'fm_futr_ord_mgn_amt': 'FM선물주문증거금액',
    'fm_opt_buy_ord_amt': 'FM옵션매수주문금액',
    'fm_opt_sll_ord_mgn_amt': 'FM옵션매도주문증거금액',
    'fm_opt_buy_ord_mgn_amt': 'FM옵션매수주문증거금액',
    'fm_ecis_rsvn_mgn_amt': 'FM행사예약증거금액',
    'fm_span_brkg_mgn_amt': 'FMSPAN위탁증거금액',
    'fm_span_pric_altr_mgn_amt': 'FMSPAN가격변동증거금액',
    'fm_span_term_sprd_mgn_amt': 'FMSPAN기간스프레드증거금액',
    'fm_span_buy_opt_min_mgn_amt': 'FMSPAN옵션가격증거금액',
    'fm_span_opt_min_mgn_amt': 'FMSPAN옵션최소증거금액',
    'fm_span_tot_risk_mgn_amt': 'FMSPAN총위험증거금액',
    'fm_span_mntn_mgn_amt': 'FMSPAN유지증거금액',
    'fm_span_mntn_pric_altr_mgn_amt': 'FMSPAN유지가격변동증거금액',
    'fm_span_mntn_term_sprd_mgn_amt': 'FMSPAN유지기간스프레드증거금액',
    'fm_span_mntn_opt_pric_mgn_amt': 'FMSPAN유지옵션가격증거금액',
    'fm_span_mntn_opt_min_mgn_amt': 'FMSPAN유지옵션최소증거금액',
    'fm_span_mntn_tot_risk_mgn_amt': 'FMSPAN유지총위험증거금액',
    'fm_eurx_brkg_mgn_amt': 'FMEUREX위탁증거금액',
    'fm_eurx_pric_altr_mgn_amt': 'FMEUREX가격변동증거금액',
    'fm_eurx_term_sprd_mgn_amt': 'FMEUREX기간스프레드증거금액',
    'fm_eurx_opt_pric_mgn_amt': 'FMEUREX옵션가격증거금액',
    'fm_eurx_buy_opt_min_mgn_amt': 'FMEUREX매수옵션최소증거금액',
    'fm_eurx_tot_risk_mgn_amt': 'FMEUREX총위험증거금액',
    'fm_eurx_mntn_mgn_amt': 'FMEUREX유지증거금액',
    'fm_eurx_mntn_pric_altr_mgn_amt': 'FMEUREX유지가격변동증거금액',
    'fm_eurx_mntn_term_sprd_mgn_amt': 'FMEUREX기간스프레드증거금액',
    'fm_eurx_mntn_opt_pric_mgn_amt': 'FMEUREX유지옵션가격증거금액',
    'fm_eurx_mntn_tot_risk_mgn_amt': 'FMEUREX유지총위험증거금액',
    'fm_gnrl_brkg_mgn_amt': 'FM일반위탁증거금액',
    'fm_futr_ustl_mgn_amt': 'FM선물미결제증거금액',
    'fm_sll_opt_ustl_mgn_amt': 'FM매도옵션미결제증거금액',
    'fm_buy_opt_ustl_mgn_amt': 'FM매수옵션미결제증거금액',
    'fm_sprd_ustl_mgn_amt': 'FM스프레드미결제증거금액',
    'fm_avg_dsct_mgn_amt': 'FMAVG할인증거금액',
    'fm_gnrl_mntn_mgn_amt': 'FM일반유지증거금액',
    'fm_futr_mntn_mgn_amt': 'FM선물유지증거금액',
    'fm_opt_mntn_mgn_amt': 'FM옵션유지증거금액'
}

NUMERIC_COLUMNS = []

def main():
    """
    [해외선물옵션] 주문/계좌
    해외선물옵션 증거금상세[해외선물-032]

    해외선물옵션 증거금상세 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 ()
        - acnt_prdt_cd (str): 계좌상품코드 ()
        - crcy_cd (str): 통화코드 ('TKR(TOT_KRW), TUS(TOT_USD),  USD(미국달러), HKD(홍콩달러), CNY(중국위안화), JPY )일본엔화), VND(베트남동)')
        - inqr_dt (str): 조회일자 ()

    Returns:
        - DataFrame: 해외선물옵션 증거금상세 결과
    
    Example:
        >>> df = margin_detail(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, crcy_cd="USD", inqr_dt="20250701")
    """
    try:
        # pandas 출력 옵션 설정
        pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
        pd.set_option('display.width', None)  # 출력 너비 제한 해제
        pd.set_option('display.max_rows', None)  # 모든 행 표시

        # 토큰 발급
        ka.auth()
        trenv = ka.getTREnv()

        # API 호출
        logger.info("API 호출")
        result = margin_detail(
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            crcy_cd="TKR",
            inqr_dt="20250625"
        )
        
        if result is None or result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return
        
        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())

        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)
        
        # 숫자형 컬럼 처리
        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
        
        # 결과 출력
        logger.info("=== 해외선물옵션 증거금상세 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
