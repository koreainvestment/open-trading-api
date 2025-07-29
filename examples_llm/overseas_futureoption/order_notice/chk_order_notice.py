"""
Created on 20250601
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from order_notice import order_notice

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외선물옵션]실시간시세 > 해외선물옵션 실시간주문내역통보[실시간-019]
##############################################################################################

# 컬럼명 매핑
COLUMN_MAPPING = {            
        "acct_no": "계좌번호",
        "ord_dt": "주문일자",
        "odno": "주문번호",
        "orgn_ord_dt": "원주문일자",
        "orgn_odno": "원주문번호",
        "series": "종목명",
        "rvse_cncl_dvsn_cd": "정정취소구분코드",
        "sll_buy_dvsn_cd": "매도매수구분코드",
        "cplx_ord_dvsn_cd": "복합주문구분코드",
        "prce_tp": "가격구분코드",
        "fm_excg_rcit_dvsn_cd": "FM거래소접수구분코드",
        "ord_qty": "주문수량",
        "fm_lmt_pric": "FMLIMIT가격",
        "fm_stop_ord_pric": "FMSTOP주문가격",
        "tot_ccld_qty": "총체결수량",
        "tot_ccld_uv": "총체결단가",
        "ord_remq": "잔량",
        "fm_ord_grp_dt": "FM주문그룹일자",
        "ord_grp_stno": "주문그룹번호",
        "ord_dtl_dtime": "주문상세일시",
        "oprt_dtl_dtime": "조작상세일시",
        "work_empl": "주문자",
        "crcy_cd": "통화코드",
        "lqd_yn": "청산여부(Y/N)",
        "lqd_lmt_pric": "청산LIMIT가격",
        "lqd_stop_pric": "청산STOP가격",
        "trd_cond": "체결조건코드",
        "term_ord_vald_dtime": "기간주문유효상세일시",
        "spec_tp": "계좌청산유형구분코드",
        "ecis_rsvn_ord_yn": "행사예약주문여부",
        "fuop_item_dvsn_cd": "선물옵션종목구분코드",
        "auto_ord_dvsn_cd": "자동주문 전략구분"
}

# 숫자형 컬럼
NUMERIC_COLUMNS = ["주문수량", "총체결수량", "총체결단가", "잔량", "청산LIMIT가격", "청산STOP가격"]

def main():
    """
    해외선물옵션 실시간주문내역통보

    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 인증 토큰 발급
    ka.auth()
    ka.auth_ws()
    trenv = ka.getTREnv()

    # 인증(auth_ws()) 이후에 선언
    kws = ka.KISWebSocket(api_url="/tryitout")

    # 조회 case1
    kws.subscribe(request=order_notice, data=[trenv.my_htsid])

    # 결과 표시
    def on_result(ws, tr_id: str, result: pd.DataFrame, data_map: dict):

        result = result.rename(columns=COLUMN_MAPPING)

        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

        logging.info("결과:")
        print(result)

    kws.start(on_result=on_result)


if __name__ == "__main__":
    main() 