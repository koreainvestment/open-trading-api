"""
Created on 20250601
@author: LaivData SJPark with cursor
"""

import sys

sys.path.extend(['../..', '.'])
import kis_auth as ka


##############################################################################################
# [국내선물옵션] 실시간시세 > KRX야간옵션실시간예상체결 [실시간-034]
##############################################################################################

def krx_ngt_option_exp_ccnl(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    [국내선물옵션] 실시간시세 
    KRX야간옵션실시간예상체결 [실시간-034]
    
    [참고자료]

    종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 선물단축종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = krx_ngt_option_exp_ccnl("1", "101W9000")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0EUANC0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "optn_shrn_iscd",
        "bsop_hour",
        "antc_cnpr",
        "antc_cntg_vrss",
        "antc_cntg_vrss_sign",
        "antc_cntg_prdy_ctrt",
        "antc_mkop_cls_code",
        "antc_cnqn"
    ]

    return msg, columns
