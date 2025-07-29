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
# [해외주식] 실시간시세 > 해외주식 실시간체결통보[실시간-009]
##############################################################################################

def ccnl_notice(
        tr_type: str,
        tr_key: str,
        env_dv: str,
) -> tuple[dict, list[str]]:
    """
    해외주식 실시간체결통보 API입니다.

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 종목코드
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = ccnl_notice("1", trenv.my_htsid, "real")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real', 'demo')")

    # tr_id 구분
    if env_dv == "real":
        tr_id = "H0GSCNI0"
    elif env_dv == "demo":
        tr_id = "H0GSCNI9"
    else:
        raise ValueError("env_dv can only be real or demo")

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "CUST_ID",
        "ACNT_NO",
        "ODER_NO",
        "OODER_NO",
        "SELN_BYOV_CLS",
        "RCTF_CLS",
        "ODER_KIND2",
        "STCK_SHRN_ISCD",
        "CNTG_QTY",
        "CNTG_UNPR",
        "STCK_CNTG_HOUR",
        "RFUS_YN",
        "CNTG_YN",
        "ACPT_YN",
        "BRNC_NO",
        "ODER_QTY",
        "ACNT_NAME",
        "CNTG_ISNM",
        "ODER_COND",
        "DEBT_GB",
        "DEBT_DATE",
        "START_TM",
        "END_TM",
        "TM_DIV_TP"
    ]

    return msg, columns 