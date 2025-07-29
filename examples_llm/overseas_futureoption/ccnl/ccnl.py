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
# [해외선물옵션]실시간시세 > 해외선물옵션 실시간체결가[실시간-017]
##############################################################################################

def ccnl(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    ※ CME, SGX 실시간시세 유료시세 신청 필수 (KIS포털 > FAQ > 자주 묻는 질문 > 해외선물옵션 API 유료시세 신청방법(CME, SGX 거래소))
    - CME, SGX 거래소 실시간시세는 유료시세 신청 후 이용하시는 모든 계좌에 대해서 접근토큰발급 API 호출하셔야 하며, 
    접근토큰발급 이후 2시간 이내로 신청정보가 동기화되어 유료시세 수신이 가능해집니다.
    - CME, SGX 거래소 종목은 유료시세 신청되어 있지 않으면 실시간시세 종목등록이 불가하며, 
    등록 시도 시 "SUBSCRIBE ERROR : mci send failed" 에러가 발생합니다.

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = ccnl("1", "DNASAAPL")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "HDFFF020"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "series_cd",
        "bsns_date",
        "mrkt_open_date",
        "mrkt_open_time",
        "mrkt_close_date",
        "mrkt_close_time",
        "prev_price",
        "recv_date",
        "recv_time",
        "active_flag",
        "last_price",
        "last_qntt",
        "prev_diff_price",
        "prev_diff_rate",
        "open_price",
        "high_price",
        "low_price",
        "vol",
        "prev_sign",
        "quotsign",
        "recv_time2",
        "psttl_price",
        "psttl_sign",
        "psttl_diff_price",
        "psttl_diff_rate"
    ]

    return msg, columns 