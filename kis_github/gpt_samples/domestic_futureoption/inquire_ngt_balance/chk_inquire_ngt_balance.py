"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_ngt_balance import inquire_ngt_balance

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 주문/계좌 > (야간)선물옵션 잔고현황 [국내선물-010]
##############################################################################################

COLUMN_MAPPING = {
    'cano': '종합계좌번호',
    'acnt_prdt_cd': '계좌상품코드',
    'pdno': '상품번호',
    'prdt_type_cd': '상품유형코드',
    'shtn_pdno': '단축상품번호',
    'prdt_name': '상품명',
    'sll_buy_dvsn_name': '매도매수구분명',
    'sll_buy_dvsn_cd': '매도매수구분코드',
    'trad_dvsn_name': '매매구분명',
    'cblc_qty': '잔고수량',
    'excc_unpr': '정산단가',
    'ccld_avg_unpr1': '체결평균단가1',
    'idx_clpr': '지수종가',
    'pchs_amt': '매입금액',
    'evlu_amt': '평가금액',
    'evlu_pfls_amt': '평가손익금액',
    'trad_pfls_amt': '매매손익금액',
    'lqd_psbl_qty': '청산가능수량',
    'dnca_cash': '예수금현금',
    'frcr_dncl_amt': '외화예수금액',
    'dnca_sbst': '예수금대용',
    'tot_dncl_amt': '총예수금액',
    'cash_mgna': '현금증거금',
    'sbst_mgna': '대용증거금',
    'mgna_tota': '증거금총액',
    'opt_dfpa': '옵션차금',
    'thdt_dfpa': '당일차금',
    'rnwl_dfpa': '갱신차금',
    'fee': '수수료',
    'nxdy_dnca': '익일예수금',
    'nxdy_dncl_amt': '익일예수금액',
    'prsm_dpast': '추정예탁자산',
    'pprt_ord_psbl_cash': '적정주문가능현금',
    'add_mgna_cash': '추가증거금현금',
    'add_mgna_tota': '추가증거금총액',
    'futr_trad_pfls_amt': '선물매매손익금액',
    'opt_trad_pfls_amt': '옵션매매손익금액',
    'futr_evlu_pfls_amt': '선물평가손익금액',
    'opt_evlu_pfls_amt': '옵션평가손익금액',
    'trad_pfls_amt_smtl': '매매손익금액합계',
    'evlu_pfls_amt_smtl': '평가손익금액합계',
    'wdrw_psbl_tot_amt': '인출가능총금액',
    'ord_psbl_cash': '주문가능현금',
    'ord_psbl_sbst': '주문가능대용',
    'ord_psbl_tota': '주문가능총액',
    'mmga_tot_amt': '유지증거금총금액',
    'mmga_cash_amt': '유지증거금현금금액',
    'mtnc_rt': '유지비율',
    'isfc_amt': '부족금액',
    'pchs_amt_smtl': '매입금액합계',
    'evlu_amt_smtl': '평가금액합계'
}

NUMERIC_COLUMNS = []


def main():
    """
    (야간)선물옵션 잔고현황 조회 테스트 함수
    
    이 함수는 (야간)선물옵션 잔고현황 API를 호출하여 결과를 출력합니다.
    
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

    # Case 1 조회
    logging.info("=== Case 1 조회 ===")
    try:
        result1, result2 = inquire_ngt_balance(
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            mgna_dvsn="01",
            excc_stat_cd="1"
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
