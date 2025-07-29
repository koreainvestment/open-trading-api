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
# [국내선물옵션] 실시간시세 > 주식선물 실시간예상체결 [실시간-031]
##############################################################################################

def futures_exp_ccnl(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    [국내선물옵션] 실시간시세 > 주식선물 실시간예상체결 [실시간-031]
    
    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = futures_exp_ccnl("1", "111W07")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0ZFANC0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "futs_shrn_iscd",
        "bsop_hour",
        "antc_cnpr",
        "antc_cntg_vrss",
        "antc_cntg_vrss_sign",
        "antc_cntg_prdy_ctrt",
        "antc_mkop_cls_code",
        "antc_cnqn"
    ]

    return msg, columns 