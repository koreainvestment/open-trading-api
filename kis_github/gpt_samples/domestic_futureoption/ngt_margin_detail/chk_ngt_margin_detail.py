"""
Created on 20250116 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from ngt_margin_detail import ngt_margin_detail

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 주문/계좌 > (야간)선물옵션 증거금 상세 [국내선물-024]
##############################################################################################

COLUMN_MAPPING = {
    'futr_new_mgn_amt': '선물신규증거금액',
    'futr_sprd_ord_mgna': '선물스프레드주문증거금',
    'opt_sll_new_mgn_amt': '옵션매도신규증거금액',
    'opt_buy_new_mgn_amt': '옵션매수신규증거금액',
    'new_mgn_amt': '신규증거금액',
    'opt_pric_mgna': '옵션가격증거금',
    'fuop_pric_altr_mgna': '선물옵션가격변동증거금',
    'futr_sprd_mgna': '선물스프레드증거금',
    'uwdl_mgna': '인수도증거금',
    'ctrt_per_min_mgna': '계약당최소증거금',
    'tot_risk_mgna': '총위험증거금',
    'netrisk_brkg_mgna': '순위험위탁증거금',
    'opt_sll_chgs': '옵션매도대금',
    'opt_buy_chgs': '옵션매수대금',
    'futr_loss_amt': '선물손실금액',
    'futr_prft_amt': '선물이익금액',
    'thdt_ccld_net_loss_amt': '당일체결순손실금액',
    'brkg_mgna': '위탁증거금',
    'futr_new_mgn_amt': '선물신규증거금액',
    'futr_sprd_ord_mgna': '선물스프레드주문증거금',
    'opt_sll_new_mgn_amt': '옵션매도신규증거금액',
    'opt_buy_new_mgn_amt': '옵션매수신규증거금액',
    'new_mgn_amt': '신규증거금액',
    'opt_pric_mgna': '옵션가격증거금',
    'fuop_pric_altr_mgna': '선물옵션가격변동증거금',
    'futr_sprd_mgna': '선물스프레드증거금',
    'uwdl_mgna': '인수도증거금',
    'ctrt_per_min_mgna': '계약당최소증거금',
    'tot_risk_mgna': '총위험증거금',
    'netrisk_brkg_mgna': '순위험위탁증거금',
    'opt_sll_chgs': '옵션매도대금',
    'opt_buy_chgs': '옵션매수대금',
    'futr_loss_amt': '선물손실금액',
    'futr_prft_amt': '선물이익금액',
    'thdt_ccld_net_loss_amt': '당일체결순손실금액',
    'brkg_mgna': '위탁증거금',
    'dnca_cash': '예수금현금',
    'dnca_sbst': '예수금대용',
    'dnca_tota': '예수금총액',
    'wdrw_psbl_cash_amt': '인출가능현금금액',
    'wdrw_psbl_sbsa': '인출가능대용금액',
    'wdrw_psbl_tot_amt': '인출가능총금액',
    'ord_psbl_cash_amt': '주문가능현금금액',
    'ord_psbl_sbsa': '주문가능대용금액',
    'ord_psbl_tot_amt': '주문가능총금액',
    'brkg_mgna_cash_amt': '위탁증거금현금금액',
    'brkg_mgna_sbst': '위탁증거금대용',
    'brkg_mgna_tot_amt': '위탁증거금총금액',
    'add_mgna_cash_amt': '추가증거금현금금액',
    'add_mgna_sbsa': '추가증거금대용금액',
    'add_mgna_tot_amt': '추가증거금총금액',
    'bfdy_sbst_sll_sbst_amt': '전일대용매도대용금액',
    'thdt_sbst_sll_sbst_amt': '당일대용매도대용금액',
    'bfdy_sbst_sll_ccld_amt': '전일대용매도체결금액',
    'thdt_sbst_sll_ccld_amt': '당일대용매도체결금액',
    'opt_dfpa': '옵션차금',
    'excc_dfpa': '정산차금',
    'fee_amt': '수수료금액',
    'nxdy_dncl_amt': '익일예수금액',
    'prsm_dpast_amt': '추정예탁자산금액',
    'opt_buy_exus_acnt_yn': '옵션매수전용계좌여부',
    'base_dpsa_gdat_grad_cd': '기본예탁금차등등급코드',
    'opt_base_dpsa_gdat_grad_cd': '옵션기본예탁금차등등급코드'
}

NUMERIC_COLUMNS = []


def main():
    """
    (야간)선물옵션 증거금 상세 조회 테스트 함수
    
    이 함수는 (야간)선물옵션 증거금 상세 API를 호출하여 결과를 출력합니다.
    
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
        result1, result2, result3 = ngt_margin_detail(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, mgna_dvsn_cd="01")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # output1 처리
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

    # output2 처리
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

    # output3 처리
    logging.info("=== output3 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result3.columns.tolist())

    # 컬럼명 한글 변환
    result3 = result3.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result3.columns:
            result3[col] = pd.to_numeric(result3[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result3)


if __name__ == "__main__":
    main()
