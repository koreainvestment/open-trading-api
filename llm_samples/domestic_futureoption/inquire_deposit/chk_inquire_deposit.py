"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_deposit import inquire_deposit

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 총자산현황[v1_국내선물-014]
##############################################################################################

COLUMN_MAPPING = {
    'dnca_tota': '예수금총액',
    'bfdy_chck_amt': '전일수표금액',
    'thdt_chck_amt': '당일수표금액',
    'rlth_uwdl_dpos_amt': '실물인수도예치금액',
    'brkg_mgna_cash': '위탁증거금현금',
    'wdrw_psbl_tot_amt': '인출가능총금액',
    'ord_psbl_cash': '주문가능현금',
    'ord_psbl_tota': '주문가능총액',
    'dnca_sbst': '예수금대용',
    'scts_sbst_amt': '유가증권대용금액',
    'frcr_evlu_amt': '외화평가금액',
    'brkg_mgna_sbst': '위탁증거금대용',
    'sbst_rlse_psbl_amt': '대용해제가능금액',
    'mtnc_rt': '유지비율',
    'add_mgna_tota': '추가증거금총액',
    'add_mgna_cash': '추가증거금현금',
    'rcva': '미수금',
    'futr_trad_pfls': '선물매매손익',
    'opt_trad_pfls_amt': '옵션매매손익금액',
    'trad_pfls_smtl': '매매손익합계',
    'futr_evlu_pfls_amt': '선물평가손익금액',
    'opt_evlu_pfls_amt': '옵션평가손익금액',
    'evlu_pfls_smtl': '평가손익합계',
    'excc_dfpa': '정산차금',
    'opt_dfpa': '옵션차금',
    'brkg_fee': '위탁수수료',
    'nxdy_dnca': '익일예수금',
    'prsm_dpast_amt': '추정예탁자산금액',
    'cash_mntn_amt': '현금유지금액',
    'hack_acdt_acnt_move_amt': '해킹사고계좌이전금액'
}

NUMERIC_COLUMNS = []


def main():
    """
    선물옵션 총자산현황 조회 테스트 함수
    
    이 함수는 선물옵션 총자산현황 API를 호출하여 결과를 출력합니다.
    
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
        result = inquire_deposit(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod)
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
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
