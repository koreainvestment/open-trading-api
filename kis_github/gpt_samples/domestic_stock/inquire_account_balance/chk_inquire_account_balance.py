"""
Created on 20250131
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_account_balance import inquire_account_balance

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 투자계좌자산현황조회[v1_국내주식-048]
##############################################################################################

COLUMN_MAPPING = {
    'pchs_amt': '매입금액',
    'evlu_amt': '평가금액',
    'evlu_pfls_amt': '평가손익금액',
    'crdt_lnd_amt': '신용대출금액',
    'real_nass_amt': '실제순자산금액',
    'whol_weit_rt': '전체비중율',
    'pchs_amt_smtl': '매입금액합계',
    'nass_tot_amt': '순자산총금액',
    'loan_amt_smtl': '대출금액합계',
    'evlu_pfls_amt_smtl': '평가손익금액합계',
    'evlu_amt_smtl': '평가금액합계',
    'tot_asst_amt': '총자산금액',
    'tot_lnda_tot_ulst_lnda': '총대출금액총융자대출금액',
    'cma_auto_loan_amt': 'CMA자동대출금액',
    'tot_mgln_amt': '총담보대출금액',
    'stln_evlu_amt': '대주평가금액',
    'crdt_fncg_amt': '신용융자금액',
    'ocl_apl_loan_amt': 'OCL_APL대출금액',
    'pldg_stup_amt': '질권설정금액',
    'frcr_evlu_tota': '외화평가총액',
    'tot_dncl_amt': '총예수금액',
    'cma_evlu_amt': 'CMA평가금액',
    'dncl_amt': '예수금액',
    'tot_sbst_amt': '총대용금액',
    'thdt_rcvb_amt': '당일미수금액',
    'ovrs_stck_evlu_amt1': '해외주식평가금액1',
    'ovrs_bond_evlu_amt': '해외채권평가금액',
    'mmf_cma_mgge_loan_amt': 'MMFCMA담보대출금액',
    'sbsc_dncl_amt': '청약예수금액',
    'pbst_sbsc_fnds_loan_use_amt': '공모주청약자금대출사용금액',
    'etpr_crdt_grnt_loan_amt': '기업신용공여대출금액'
}

NUMERIC_COLUMNS = ['매입금액', '평가금액', '평가손익금액', '신용대출금액', '실제순자산금액', '전체비중율', '매입금액합계', '순자산총금액', '대출금액합계', '평가손익금액합계',
                   '평가금액합계', '총자산금액', '총대출금액총융자대출금액', 'CMA자동대출금액', '총담보대출금액', '대주평가금액', '신용융자금액', 'OCL_APL대출금액',
                   '질권설정금액', '외화평가총액', '총예수금액', 'CMA평가금액', '예수금액', '총대용금액', '당일미수금액', '해외주식평가금액1', '해외채권평가금액',
                   'MMFCMA담보대출금액', '청약예수금액', '공모주청약자금대출사용금액', '기업신용공여대출금액']


def main():
    """
    투자계좌자산현황조회 테스트 함수
    
    이 함수는 투자계좌자산현황조회 API를 호출하여 결과를 출력합니다.
    
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

    # case1 조회
    logging.info("=== case1 조회 ===")
    try:
        result1, result2 = inquire_account_balance(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod)
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # output1 처리
    logging.info("=== output1 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    result1 = result1.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result1)

    # output2 처리
    logging.info("=== output2 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result2.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    result2 = result2.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result2)


if __name__ == "__main__":
    main()
