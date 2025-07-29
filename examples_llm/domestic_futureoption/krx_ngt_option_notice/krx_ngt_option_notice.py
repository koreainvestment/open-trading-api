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
# [국내선물옵션] 실시간시세 > KRX야간옵션실시간체결통보 [실시간-067]
##############################################################################################

def krx_ngt_option_notice(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    [참고자료]
    
    종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 고객 ID

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = krx_ngt_option_notice("1", trenv.my_htsid)
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0EUCNI0"

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
        "oder_cond"
    ]

    return msg, columns 