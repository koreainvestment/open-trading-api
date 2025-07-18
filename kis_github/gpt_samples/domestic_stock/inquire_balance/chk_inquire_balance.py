"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_balance import inquire_balance

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 주식잔고조회[v1_국내주식-006]
##############################################################################################

COLUMN_MAPPING = {
    'pdno': '상품번호',
    'prdt_name': '상품명',
    'trad_dvsn_name': '매매구분명',
    'bfdy_buy_qty': '전일매수수량',
    'bfdy_sll_qty': '전일매도수량',
    'thdt_buyqty': '금일매수수량',
    'thdt_sll_qty': '금일매도수량',
    'hldg_qty': '보유수량',
    'ord_psbl_qty': '주문가능수량',
    'pchs_avg_pric': '매입평균가격',
    'pchs_amt': '매입금액',
    'prpr': '현재가',
    'evlu_amt': '평가금액',
    'evlu_pfls_amt': '평가손익금액',
    'evlu_pfls_rt': '평가손익율',
    'evlu_erng_rt': '평가수익율',
    'loan_dt': '대출일자',
    'loan_amt': '대출금액',
    'stln_slng_chgs': '대주매각대금',
    'expd_dt': '만기일자',
    'fltt_rt': '등락율',
    'bfdy_cprs_icdc': '전일대비증감',
    'item_mgna_rt_name': '종목증거금율명',
    'grta_rt_name': '보증금율명',
    'sbst_pric': '대용가격',
    'stck_loan_unpr': '주식대출단가',
    'dnca_tot_amt': '예수금총금액',
    'nxdy_excc_amt': '익일정산금액',
    'prvs_rcdl_excc_amt': '가수도정산금액',
    'cma_evlu_amt': 'CMA평가금액',
    'bfdy_buy_amt': '전일매수금액',
    'thdt_buy_amt': '금일매수금액',
    'nxdy_auto_rdpt_amt': '익일자동상환금액',
    'bfdy_sll_amt': '전일매도금액',
    'thdt_sll_amt': '금일매도금액',
    'd2_auto_rdpt_amt': 'D+2자동상환금액',
    'bfdy_tlex_amt': '전일제비용금액',
    'thdt_tlex_amt': '금일제비용금액',
    'tot_loan_amt': '총대출금액',
    'scts_evlu_amt': '유가평가금액',
    'tot_evlu_amt': '총평가금액',
    'nass_amt': '순자산금액',
    'fncg_gld_auto_rdpt_yn': '융자금자동상환여부',
    'pchs_amt_smtl_amt': '매입금액합계금액',
    'evlu_amt_smtl_amt': '평가금액합계금액',
    'evlu_pfls_smtl_amt': '평가손익합계금액',
    'tot_stln_slng_chgs': '총대주매각대금',
    'bfdy_tot_asst_evlu_amt': '전일총자산평가금액',
    'asst_icdc_amt': '자산증감액',
    'asst_icdc_erng_rt': '자산증감수익율'
}

NUMERIC_COLUMNS = []


def main():
    """
    주식잔고조회 테스트 함수
    
    이 함수는 주식잔고조회 API를 호출하여 결과를 출력합니다.
    
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

    # case1 테스트
    logging.info("=== case1 테스트 ===")
    try:
        result1, result2 = inquire_balance(
            env_dv="real",
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            afhr_flpr_yn="N",
            inqr_dvsn="01",
            unpr_dvsn="01",
            fund_sttl_icld_yn="N",
            fncg_amt_auto_rdpt_yn="N",
            prcs_dvsn="00"
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # output1 결과 처리
    logging.info("=== output1 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())

    # 컬럼명 한글 변환
    result1 = result1.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result1)

    # output2 결과 처리
    logging.info("=== output2 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result2.columns.tolist())

    # 컬럼명 한글 변환
    result2 = result2.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result2)


if __name__ == "__main__":
    main()
