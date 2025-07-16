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
# [국내선물옵션] 실시간시세 > 주식옵션 실시간호가 [실시간-045]
##############################################################################################

def stock_option_asking_price(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    국내선물옵션 주식옵션 실시간호가 API입니다.

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 선물단축종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = stock_option_asking_price("1", "111W80")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0ZOASP0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "optn_shrn_iscd",
        "bsop_hour",
        "optn_askp1",
        "optn_askp2",
        "optn_askp3",
        "optn_askp4",
        "optn_askp5",
        "optn_bidp1",
        "optn_bidp2",
        "optn_bidp3",
        "optn_bidp4",
        "optn_bidp5",
        "askp_csnu1",
        "askp_csnu2",
        "askp_csnu3",
        "askp_csnu4",
        "askp_csnu5",
        "bidp_csnu1",
        "bidp_csnu2",
        "bidp_csnu3",
        "bidp_csnu4",
        "bidp_csnu5",
        "askp_rsqn1",
        "askp_rsqn2",
        "askp_rsqn3",
        "askp_rsqn4",
        "askp_rsqn5",
        "bidp_rsqn1",
        "bidp_rsqn2",
        "bidp_rsqn3",
        "bidp_rsqn4",
        "bidp_rsqn5",
        "total_askp_csnu",
        "total_bidp_csnu",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "total_askp_rsqn_icdc",
        "total_bidp_rsqn_icdc",
        "optn_askp6",
        "optn_askp7",
        "optn_askp8",
        "optn_askp9",
        "optn_askp10",
        "optn_bidp6",
        "optn_bidp7",
        "optn_bidp8",
        "optn_bidp9",
        "optn_bidp10",
        "askp_csnu6",
        "askp_csnu7",
        "askp_csnu8",
        "askp_csnu9",
        "askp_csnu10",
        "bidp_csnu6",
        "bidp_csnu7",
        "bidp_csnu8",
        "bidp_csnu9",
        "bidp_csnu10",
        "askp_rsqn6",
        "askp_rsqn7",
        "askp_rsqn8",
        "askp_rsqn9",
        "askp_rsqn10",
        "bidp_rsqn6",
        "bidp_rsqn7",
        "bidp_rsqn8",
        "bidp_rsqn9",
        "bidp_rsqn10"
    ]

    return msg, columns 