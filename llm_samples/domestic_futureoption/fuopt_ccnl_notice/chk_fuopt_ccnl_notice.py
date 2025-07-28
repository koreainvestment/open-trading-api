"""
Created on 20250601
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

from fuopt_ccnl_notice import fuopt_ccnl_notice

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 실시간시세 > 선물옵션 실시간체결통보[실시간-012]
##############################################################################################

COLUMN_MAPPING = {
    "cust_id": "고객 ID",
    "acnt_no": "계좌번호",
    "oder_no": "주문번호",
    "ooder_no": "원주문번호",
    "seln_byov_cls": "매도매수구분",
    "rctf_cls": "정정구분",
    "oder_kind2": "주문종류2",
    "stck_shrn_iscd": "주식 단축 종목코드",
    "cntg_qty": "체결 수량",
    "cntg_unpr": "체결단가",
    "stck_cntg_hour": "주식 체결 시간",
    "rfus_yn": "거부여부",
    "cntg_yn": "체결여부",
    "acpt_yn": "접수여부",
    "brnc_no": "지점번호",
    "oder_qty": "주문수량",
    "acnt_name": "계좌명",
    "cntg_isnm": "체결종목명",
    "oder_cond": "주문조건",
    "ord_grp": "주문그룹ID",
    "ord_grpseq": "주문그룹SEQ",
    "order_prc": "주문가격"
}

NUMERIC_COLUMNS = []


def main():
    """
   선물옵션 실시간체결통보

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

    # 조회
    kws.subscribe(request=fuopt_ccnl_notice, data=[trenv.my_htsid])

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
