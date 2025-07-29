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
# [해외선물옵션]실시간시세 > 해외선물옵션 실시간호가[실시간-018]
##############################################################################################

def asking_price(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    [해외선물옵션]실시간시세 > 해외선물옵션 실시간호가[실시간-018]
    
    ※ CME, SGX 실시간시세 유료시세 신청 필수 (KIS포털 > FAQ > 자주 묻는 질문 > 해외선물옵션 API 유료시세 신청방법(CME, SGX 거래소))
    - CME, SGX 거래소 실시간시세는 유료시세 신청 후 이용하시는 모든 계좌에 대해서 접근토큰발급 API 호출하셔야 하며, 
    접근토큰발급 이후 2시간 이내로 신청정보가 동기화되어 유료시세 수신이 가능해집니다.
    - CME, SGX 거래소 종목은 유료시세 신청되어 있지 않으면 실시간시세 종목등록이 불가하며, 
    등록 시도 시 "SUBSCRIBE ERROR : mci send failed" 에러가 발생합니다.

    (중요) 해외선물옵션시세 출력값을 해석하실 때 ffcode.mst(해외선물종목마스터 파일)에 있는 sCalcDesz(계산 소수점) 값을 활용하셔야 정확한 값을 받아오실 수 있습니다.

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = asking_price("1", "DNASAAPL")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "HDFFF010"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "series_cd",
        "recv_date",
        "recv_time",
        "prev_price",
        "bid_qntt_1",
        "bid_num_1",
        "bid_price_1",
        "ask_qntt_1",
        "ask_num_1",
        "ask_price_1",
        "bid_qntt_2",
        "bid_num_2",
        "bid_price_2",
        "ask_qntt_2",
        "ask_num_2",
        "ask_price_2",
        "bid_qntt_3",
        "bid_num_3",
        "bid_price_3",
        "ask_qntt_3",
        "ask_num_3",
        "ask_price_3",
        "bid_qntt_4",
        "bid_num_4",
        "bid_price_4",
        "ask_qntt_4",
        "ask_num_4",
        "ask_price_4",
        "bid_qntt_5",
        "bid_num_5",
        "bid_price_5",
        "ask_qntt_5",
        "ask_num_5",
        "ask_price_5",
        "sttl_price"
    ]

    return msg, columns 