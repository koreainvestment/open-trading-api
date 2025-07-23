# -*- coding: utf-8 -*-
"""
Created on 2025-07-03

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_deposit import inquire_deposit

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 예수금현황 [해외선물-012]
##############################################################################################

# 상수 정의
COLUMN_MAPPING = {
    'fm_nxdy_dncl_amt': 'FM익일예수금액',
    'fm_tot_asst_evlu_amt': 'FM총자산평가금액',
    'cano': '종합계좌번호',
    'acnt_prdt_cd': '계좌상품코드',
    'crcy_cd': '통화코드',
    'resp_dt': '응답일자',
    'fm_dnca_rmnd': 'FM예수금잔액',
    'fm_lqd_pfls_amt': 'FM청산손익금액',
    'fm_fee': 'FM수수료',
    'fm_fuop_evlu_pfls_amt': 'FM선물옵션평가손익금액',
    'fm_rcvb_amt': 'FM미수금액',
    'fm_brkg_mgn_amt': 'FM위탁증거금액',
    'fm_mntn_mgn_amt': 'FM유지증거금액',
    'fm_add_mgn_amt': 'FM추가증거금액',
    'fm_risk_rt': 'FM위험율',
    'fm_ord_psbl_amt': 'FM주문가능금액',
    'fm_drwg_psbl_amt': 'FM출금가능금액',
    'fm_echm_rqrm_amt': 'FM환전요청금액',
    'fm_drwg_prar_amt': 'FM출금예정금액',
    'fm_opt_tr_chgs': 'FM옵션거래대금',
    'fm_opt_icld_asst_evlu_amt': 'FM옵션포함자산평가금액',
    'fm_opt_evlu_amt': 'FM옵션평가금액',
    'fm_crcy_sbst_amt': 'FM통화대용금액',
    'fm_crcy_sbst_use_amt': 'FM통화대용사용금액',
    'fm_crcy_sbst_stup_amt': 'FM통화대용설정금액'
}
NUMERIC_COLUMNS = ['FM총자산평가금액', 'FM예수금잔액', 'FM청산손익금액', 'FM수수료', 'FM선물옵션평가손익금액', 'FM미수금액', 'FM위탁증거금액', 'FM유지증거금액', 'FM추가증거금액', 
                   'FM위험율', 'FM주문가능금액', 'FM출금가능금액', 'FM환전요청금액', 'FM출금예정금액', 'FM옵션거래대금', 'FM옵션포함자산평가금액', 'FM옵션평가금액', 'FM통화대용금액', 'FM통화대용사용금액', 'FM통화대용설정금액']

def main():
    """
    [해외선물옵션] 주문/계좌
    해외선물옵션 예수금현황[해외선물-012]

    해외선물옵션 예수금현황 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        - crcy_cd (str): 통화코드 (TUS: TOT_USD  / TKR: TOT_KRW KRW: 한국  / USD: 미국 EUR: EUR   / HKD: 홍콩 CNY: 중국  / JPY: 일본 VND: 베트남)
        - inqr_dt (str): 조회일자 ()

    Returns:
        - DataFrame: 해외선물옵션 예수금현황 결과
    
    Example:
        >>> df = inquire_deposit(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, crcy_cd="TUS", inqr_dt="20250630")
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
        logger.info("API 호출 시작: 해외선물옵션 예수금현황")
        result = inquire_deposit(
            cano=trenv.my_acct,  # 종합계좌번호
            acnt_prdt_cd=trenv.my_prod,  # 계좌상품코드
            crcy_cd="TUS",  # 통화코드
            inqr_dt="20250630",  # 조회일자
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
        logger.info("=== 해외선물옵션 예수금현황 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
