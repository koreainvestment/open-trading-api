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
# [국내선물옵션] 실시간시세 > 상품선물 실시간호가[실시간-023]
##############################################################################################

def commodity_futures_realtime_quote(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    상품선물 실시간호가 API입니다.
    실시간 웹소켓 연결을 통해 상품선물 매도/매수 호가 정보를 실시간으로 수신할 수 있습니다.
    실전계좌만 지원되며, 모의투자는 지원하지 않습니다.
    선물옵션 호가 데이터는 0.2초 필터링 옵션이 적용됩니다.

    Args:
        tr_type (str): [필수] 구독 등록/해제 여부 (ex. "1": 구독, "2": 해제)
        tr_key (str): [필수] 종목코드 (ex. 101S12)

    Returns:
        message (str): 메시지 데이터

    Example:
        >>> msg, columns = commodity_futures_realtime_quote("1", "101S12")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0CFASP0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "futs_shrn_iscd",
        "bsop_hour",
        "futs_askp1",
        "futs_askp2",
        "futs_askp3",
        "futs_askp4",
        "futs_askp5",
        "futs_bidp1",
        "futs_bidp2",
        "futs_bidp3",
        "futs_bidp4",
        "futs_bidp5",
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