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
# [국내선물옵션] 실시간시세 > 지수옵션 실시간호가[실시간-015]
##############################################################################################

def index_option_realtime_quote(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    지수옵션 실시간호가 API입니다.
    실시간 웹소켓 연결을 통해 지수옵션 매도/매수 호가 정보를 실시간으로 수신할 수 있습니다.
    실전계좌만 지원되며, 모의투자는 지원하지 않습니다.

    Args:
        tr_type (str): [필수] 구독 등록/해제 여부 (ex. "1": 구독, "2": 해제)
        tr_key (str): [필수] 코드 (ex. 201S11305)

    Returns:
        message (str): 메시지 데이터

    Example:
        >>> msg, columns = index_option_realtime_quote("1", "201S11305")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0IOASP0"

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
        "total_bidp_rsqn_icdc"
    ]

    return msg, columns 