"""
Created on 20250601
@author: LaivData SJPark with cursor
"""

import logging
import sys

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외선물옵션]실시간시세 > 해외선물옵션 실시간주문내역통보[실시간-019]
##############################################################################################

def order_notice(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    [참고자료]

    종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] HTS ID

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = order_notice("1", trenv.my_htsid)
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "HDFFF1C0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "acct_no",
        "ord_dt",
        "odno",
        "orgn_ord_dt",
        "orgn_odno",
        "series",
        "rvse_cncl_dvsn_cd",
        "sll_buy_dvsn_cd",
        "cplx_ord_dvsn_cd",
        "prce_tp",
        "fm_excg_rcit_dvsn_cd",
        "ord_qty",
        "fm_lmt_pric",
        "fm_stop_ord_pric",
        "tot_ccld_qty",
        "tot_ccld_uv",
        "ord_remq",
        "fm_ord_grp_dt",
        "ord_grp_stno",
        "ord_dtl_dtime",
        "oprt_dtl_dtime",
        "work_empl",
        "crcy_cd",
        "lqd_yn",
        "lqd_lmt_pric",
        "lqd_stop_pric",
        "trd_cond",
        "term_ord_vald_dtime",
        "spec_tp",
        "ecis_rsvn_ord_yn",
        "fuop_item_dvsn_cd",
        "auto_ord_dvsn_cd"
    ]

    return msg, columns 