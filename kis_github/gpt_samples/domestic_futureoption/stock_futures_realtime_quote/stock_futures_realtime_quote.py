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
# [국내선물옵션] 실시간시세 > 주식선물 실시간호가 [실시간-030]
##############################################################################################

def stock_futures_realtime_quote(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    주식선물 실시간호가 API입니다.
    실시간 웹소켓 연결을 통해 주식선물의 실시간 호가 정보를 수신할 수 있습니다.
    매도/매수 호가 1~10단계까지의 확장된 호가 정보를 제공하는 특별한 API입니다.
    호가별 건수, 호가별 잔량 등의 상세 정보를 포함합니다.
    선물옵션 호가 데이터는 0.2초 필터링 옵션이 적용됩니다.
    실전계좌만 지원되며 모의투자는 미지원됩니다.

    Args:
        tr_type (str): [필수] 구독 등록/해제 여부 (ex. "1": 구독, "2": 해제)
        tr_key (str): [필수] 종목코드 (ex. 101S12)

    Returns:
        message (str): 메시지 데이터

    Example:
        >>> msg, columns = stock_futures_realtime_quote("1", "101S12")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0ZFASP0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "futs_shrn_iscd",
        "bsop_hour",
        "askp1",
        "askp2",
        "askp3",
        "askp4",
        "askp5",
        "askp6",
        "askp7",
        "askp8",
        "askp9",
        "askp10",
        "bidp1",
        "bidp2",
        "bidp3",
        "bidp4",
        "bidp5",
        "bidp6",
        "bidp7",
        "bidp8",
        "bidp9",
        "bidp10",
        "askp_csnu1",
        "askp_csnu2",
        "askp_csnu3",
        "askp_csnu4",
        "askp_csnu5",
        "askp_csnu6",
        "askp_csnu7",
        "askp_csnu8",
        "askp_csnu9",
        "askp_csnu10",
        "bidp_csnu1",
        "bidp_csnu2",
        "bidp_csnu3",
        "bidp_csnu4",
        "bidp_csnu5",
        "bidp_csnu6",
        "bidp_csnu7",
        "bidp_csnu8",
        "bidp_csnu9",
        "bidp_csnu10",
        "askp_rsqn1",
        "askp_rsqn2",
        "askp_rsqn3",
        "askp_rsqn4",
        "askp_rsqn5",
        "askp_rsqn6",
        "askp_rsqn7",
        "askp_rsqn8",
        "askp_rsqn9",
        "askp_rsqn10",
        "bidp_rsqn1",
        "bidp_rsqn2",
        "bidp_rsqn3",
        "bidp_rsqn4",
        "bidp_rsqn5",
        "bidp_rsqn6",
        "bidp_rsqn7",
        "bidp_rsqn8",
        "bidp_rsqn9",
        "bidp_rsqn10",
        "total_askp_csnu",
        "total_bidp_csnu",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "total_askp_rsqn_icdc",
        "total_bidp_rsqn_icdc"
    ]

    return msg, columns 