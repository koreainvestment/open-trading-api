"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from intgr_margin import intgr_margin

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 주식통합증거금 현황 [국내주식-191]
##############################################################################################

COLUMN_MAPPING = {
    'acmga_rt': '계좌증거금율',
    'acmga_pct100_aptm_rson': '계좌증거금100퍼센트지정사유',
    'stck_cash_objt_amt': '주식현금대상금액',
    'stck_sbst_objt_amt': '주식대용대상금액',
    'stck_evlu_objt_amt': '주식평가대상금액',
    'stck_ruse_psbl_objt_amt': '주식재사용가능대상금액',
    'stck_fund_rpch_chgs_objt_amt': '주식펀드환매대금대상금액',
    'stck_fncg_rdpt_objt_atm': '주식융자상환금대상금액',
    'bond_ruse_psbl_objt_amt': '채권재사용가능대상금액',
    'stck_cash_use_amt': '주식현금사용금액',
    'stck_sbst_use_amt': '주식대용사용금액',
    'stck_evlu_use_amt': '주식평가사용금액',
    'stck_ruse_psbl_amt_use_amt': '주식재사용가능금사용금액',
    'stck_fund_rpch_chgs_use_amt': '주식펀드환매대금사용금액',
    'stck_fncg_rdpt_amt_use_amt': '주식융자상환금사용금액',
    'bond_ruse_psbl_amt_use_amt': '채권재사용가능금사용금액',
    'stck_cash_ord_psbl_amt': '주식현금주문가능금액',
    'stck_sbst_ord_psbl_amt': '주식대용주문가능금액',
    'stck_evlu_ord_psbl_amt': '주식평가주문가능금액',
    'stck_ruse_psbl_ord_psbl_amt': '주식재사용가능주문가능금액',
    'stck_fund_rpch_ord_psbl_amt': '주식펀드환매주문가능금액',
    'bond_ruse_psbl_ord_psbl_amt': '채권재사용가능주문가능금액',
    'rcvb_amt': '미수금액',
    'stck_loan_grta_ruse_psbl_amt': '주식대출보증금재사용가능금액',
    'stck_cash20_max_ord_psbl_amt': '주식현금20최대주문가능금액',
    'stck_cash30_max_ord_psbl_amt': '주식현금30최대주문가능금액',
    'stck_cash40_max_ord_psbl_amt': '주식현금40최대주문가능금액',
    'stck_cash50_max_ord_psbl_amt': '주식현금50최대주문가능금액',
    'stck_cash60_max_ord_psbl_amt': '주식현금60최대주문가능금액',
    'stck_cash100_max_ord_psbl_amt': '주식현금100최대주문가능금액',
    'stck_rsip100_max_ord_psbl_amt': '주식재사용불가100최대주문가능',
    'bond_max_ord_psbl_amt': '채권최대주문가능금액',
    'stck_fncg45_max_ord_psbl_amt': '주식융자45최대주문가능금액',
    'stck_fncg50_max_ord_psbl_amt': '주식융자50최대주문가능금액',
    'stck_fncg60_max_ord_psbl_amt': '주식융자60최대주문가능금액',
    'stck_fncg70_max_ord_psbl_amt': '주식융자70최대주문가능금액',
    'stck_stln_max_ord_psbl_amt': '주식대주최대주문가능금액',
    'lmt_amt': '한도금액',
    'ovrs_stck_itgr_mgna_dvsn_name': '해외주식통합증거금구분명',
    'usd_objt_amt': '미화대상금액',
    'usd_use_amt': '미화사용금액',
    'usd_ord_psbl_amt': '미화주문가능금액',
    'hkd_objt_amt': '홍콩달러대상금액',
    'hkd_use_amt': '홍콩달러사용금액',
    'hkd_ord_psbl_amt': '홍콩달러주문가능금액',
    'jpy_objt_amt': '엔화대상금액',
    'jpy_use_amt': '엔화사용금액',
    'jpy_ord_psbl_amt': '엔화주문가능금액',
    'cny_objt_amt': '위안화대상금액',
    'cny_use_amt': '위안화사용금액',
    'cny_ord_psbl_amt': '위안화주문가능금액',
    'usd_ruse_objt_amt': '미화재사용대상금액',
    'usd_ruse_amt': '미화재사용금액',
    'usd_ruse_ord_psbl_amt': '미화재사용주문가능금액',
    'hkd_ruse_objt_amt': '홍콩달러재사용대상금액',
    'hkd_ruse_amt': '홍콩달러재사용금액',
    'hkd_ruse_ord_psbl_amt': '홍콩달러재사용주문가능금액',
    'jpy_ruse_objt_amt': '엔화재사용대상금액',
    'jpy_ruse_amt': '엔화재사용금액',
    'jpy_ruse_ord_psbl_amt': '엔화재사용주문가능금액',
    'cny_ruse_objt_amt': '위안화재사용대상금액',
    'cny_ruse_amt': '위안화재사용금액',
    'cny_ruse_ord_psbl_amt': '위안화재사용주문가능금액',
    'usd_gnrl_ord_psbl_amt': '미화일반주문가능금액',
    'usd_itgr_ord_psbl_amt': '미화통합주문가능금액',
    'hkd_gnrl_ord_psbl_amt': '홍콩달러일반주문가능금액',
    'hkd_itgr_ord_psbl_amt': '홍콩달러통합주문가능금액',
    'jpy_gnrl_ord_psbl_amt': '엔화일반주문가능금액',
    'jpy_itgr_ord_psbl_amt': '엔화통합주문가능금액',
    'cny_gnrl_ord_psbl_amt': '위안화일반주문가능금액',
    'cny_itgr_ord_psbl_amt': '위안화통합주문가능금액',
    'stck_itgr_cash20_ord_psbl_amt': '주식통합현금20주문가능금액',
    'stck_itgr_cash30_ord_psbl_amt': '주식통합현금30주문가능금액',
    'stck_itgr_cash40_ord_psbl_amt': '주식통합현금40주문가능금액',
    'stck_itgr_cash50_ord_psbl_amt': '주식통합현금50주문가능금액',
    'stck_itgr_cash60_ord_psbl_amt': '주식통합현금60주문가능금액',
    'stck_itgr_cash100_ord_psbl_amt': '주식통합현금100주문가능금액',
    'stck_itgr_100_ord_psbl_amt': '주식통합100주문가능금액',
    'stck_itgr_fncg45_ord_psbl_amt': '주식통합융자45주문가능금액',
    'stck_itgr_fncg50_ord_psbl_amt': '주식통합융자50주문가능금액',
    'stck_itgr_fncg60_ord_psbl_amt': '주식통합융자60주문가능금액',
    'stck_itgr_fncg70_ord_psbl_amt': '주식통합융자70주문가능금액',
    'stck_itgr_stln_ord_psbl_amt': '주식통합대주주문가능금액',
    'bond_itgr_ord_psbl_amt': '채권통합주문가능금액',
    'stck_cash_ovrs_use_amt': '주식현금해외사용금액',
    'stck_sbst_ovrs_use_amt': '주식대용해외사용금액',
    'stck_evlu_ovrs_use_amt': '주식평가해외사용금액',
    'stck_re_use_amt_ovrs_use_amt': '주식재사용금액해외사용금액',
    'stck_fund_rpch_ovrs_use_amt': '주식펀드환매해외사용금액',
    'stck_fncg_rdpt_ovrs_use_amt': '주식융자상환해외사용금액',
    'bond_re_use_ovrs_use_amt': '채권재사용해외사용금액',
    'usd_oth_mket_use_amt': '미화타시장사용금액',
    'jpy_oth_mket_use_amt': '엔화타시장사용금액',
    'cny_oth_mket_use_amt': '위안화타시장사용금액',
    'hkd_oth_mket_use_amt': '홍콩달러타시장사용금액',
    'usd_re_use_oth_mket_use_amt': '미화재사용타시장사용금액',
    'jpy_re_use_oth_mket_use_amt': '엔화재사용타시장사용금액',
    'cny_re_use_oth_mket_use_amt': '위안화재사용타시장사용금액',
    'hkd_re_use_oth_mket_use_amt': '홍콩달러재사용타시장사용금액',
    'hgkg_cny_re_use_amt': '홍콩위안화재사용금액',
    'usd_frst_bltn_exrt': '미국달러최초고시환율',
    'hkd_frst_bltn_exrt': '홍콩달러최초고시환율',
    'jpy_frst_bltn_exrt': '일본엔화최초고시환율',
    'cny_frst_bltn_exrt': '중국위안화최초고시환율'
}

NUMERIC_COLUMNS = [
    '계좌증거금율',
    '주식현금대상금액',
    '주식대용대상금액',
    '주식평가대상금액',
    '주식재사용가능대상금액',
    '주식펀드환매대금대상금액',
    '주식융자상환금대상금액',
    '채권재사용가능대상금액',
    '주식현금사용금액',
    '주식대용사용금액',
    '주식평가사용금액',
    '주식재사용가능금사용금액',
    '주식펀드환매대금사용금액',
    '주식융자상환금사용금액',
    '채권재사용가능금사용금액',
    '주식현금주문가능금액',
    '주식대용주문가능금액',
    '주식평가주문가능금액',
    '주식재사용가능주문가능금액',
    '주식펀드환매주문가능금액',
    '채권재사용가능주문가능금액',
    '미수금액',
    '주식대출보증금재사용가능금액',
    '주식현금20최대주문가능금액',
    '주식현금30최대주문가능금액',
    '주식현금40최대주문가능금액',
    '주식현금50최대주문가능금액',
    '주식현금60최대주문가능금액',
    '주식현금100최대주문가능금액',
    '주식재사용불가100최대주문가능',
    '채권최대주문가능금액',
    '주식융자45최대주문가능금액',
    '주식융자50최대주문가능금액',
    '주식융자60최대주문가능금액',
    '주식융자70최대주문가능금액',
    '주식대주최대주문가능금액',
    '한도금액',
    '미화대상금액',
    '미화사용금액',
    '미화주문가능금액',
    '홍콩달러대상금액',
    '홍콩달러사용금액',
    '홍콩달러주문가능금액',
    '엔화대상금액',
    '엔화사용금액',
    '엔화주문가능금액',
    '위안화대상금액',
    '위안화사용금액',
    '위안화주문가능금액',
    '미화재사용대상금액',
    '미화재사용금액',
    '미화재사용주문가능금액',
    '홍콩달러재사용대상금액',
    '홍콩달러재사용금액',
    '홍콩달러재사용주문가능금액',
    '엔화재사용대상금액',
    '엔화재사용금액',
    '엔화재사용주문가능금액',
    '위안화재사용대상금액',
    '위안화재사용금액',
    '위안화재사용주문가능금액',
    '미화일반주문가능금액',
    '미화통합주문가능금액',
    '홍콩달러일반주문가능금액',
    '홍콩달러통합주문가능금액',
    '엔화일반주문가능금액',
    '엔화통합주문가능금액',
    '위안화일반주문가능금액',
    '위안화통합주문가능금액',
    '주식통합현금20주문가능금액',
    '주식통합현금30주문가능금액',
    '주식통합현금40주문가능금액',
    '주식통합현금50주문가능금액',
    '주식통합현금60주문가능금액',
    '주식통합현금100주문가능금액',
    '주식통합100주문가능금액',
    '주식통합융자45주문가능금액',
    '주식통합융자50주문가능금액',
    '주식통합융자60주문가능금액',
    '주식통합융자70주문가능금액',
    '주식통합대주주문가능금액',
    '채권통합주문가능금액',
    '주식현금해외사용금액',
    '주식대용해외사용금액',
    '주식평가해외사용금액',
    '주식재사용금액해외사용금액',
    '주식펀드환매해외사용금액',
    '주식융자상환해외사용금액',
    '채권재사용해외사용금액',
    '미화타시장사용금액',
    '엔화타시장사용금액',
    '위안화타시장사용금액',
    '홍콩달러타시장사용금액',
    '미화재사용타시장사용금액',
    '엔화재사용타시장사용금액',
    '위안화재사용타시장사용금액',
    '홍콩달러재사용타시장사용금액',
    '홍콩위안화재사용금액',
    '미국달러최초고시환율',
    '홍콩달러최초고시환율',
    '일본엔화최초고시환율',
    '중국위안화최초고시환율'
]


def main():
    """
    주식통합증거금 현황 조회 테스트 함수
    
    이 함수는 주식통합증거금 현황 API를 호출하여 결과를 출력합니다.
    
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
        result = intgr_margin(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, cma_evlu_amt_icld_yn="N", wcrc_frcr_dvsn_cd="01",
                              fwex_ctrt_frcr_dvsn_cd="01")
    except ValueError as e:
        logging.error("에러 발생: %s", str(e))
        return

    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    result = result.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result)


if __name__ == "__main__":
    main()
