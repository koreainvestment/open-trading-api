"""
Created on 20250601
@author: LaivData SJPark with cursor
"""

import logging
import sys
from typing import Optional, Tuple

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 실시간시세 > 선물옵션 실시간체결통보[실시간-012]
##############################################################################################

def fuopt_ccnl_notice(
        tr_type: str,
        tr_key: str,
):
    """
    선물옵션 실시간체결통보 API입니다.
    실시간 웹소켓 연결을 통해 선물옵션 거래의 실시간 체결 통보를 수신할 수 있습니다.
    주문접수, 체결, 정정, 취소 등의 거래 상태 변화를 실시간으로 통보받을 수 있습니다.
    고객ID, 계좌번호, 주문번호, 체결수량, 체결단가 등의 상세 거래 정보를 포함합니다.
    실전계좌와 모의투자 모두 지원됩니다.

    Args:
        tr_type (str): [필수] 구독 등록/해제 여부 (ex. "1": 구독, "2": 해제)
        tr_key (str): [필수] 코드 (ex. dttest11)

    Returns:
        message (str): 메시지 데이터

    Example:
        >>> msg, columns = fuopt_ccnl_notice("1", trenv.my_htsid)
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0IFCNI0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "cust_id",
        "acnt_no", 
        "oder_no",
        "ooder_no",
        "seln_byov_cls",
        "rctf_cls",
        "oder_kind2",
        "stck_shrn_iscd",
        "cntg_qty",
        "cntg_unpr",
        "stck_cntg_hour",
        "rfus_yn",
        "cntg_yn",
        "acpt_yn",
        "brnc_no",
        "oder_qty",
        "acnt_name",
        "cntg_isnm",
        "oder_cond",
        "ord_grp",
        "ord_grpseq",
        "order_prc"
    ]

    return msg, columns 