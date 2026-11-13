"""
Created on 2025-07-09
"""

import logging
import sys

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간체결가 (NXT)
##############################################################################################


def ccnl_nxt(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간체결가 (NXT)[H0NXCNT0]
    국내주식 실시간체결가 (NXT) API를 통해 실시간 데이터를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 값
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)

    Returns:
        message (dict): 실시간 체결가 데이터 메시지
        columns (list[str]): 데이터의 컬럼 정보 리스트

    Example:
        >>> msg, columns = ccnl_nxt("1", "005930")
        >>> print(msg, columns)

    Note:
        이 함수는 웹소켓을 통해 실시간 데이터를 구독합니다. 구독을 시작하려면 tr_type을 "1"로 설정하고,
        구독을 해제하려면 "0"으로 설정하세요. tr_key는 유효한 종목코드를 입력해야 합니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 필수 입력값입니다. 유효한 종목코드를 입력하세요.")

    tr_id = "H0NXCNT0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 페치
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 컬럼 정보
    columns = [
        "MKSC_SHRN_ISCD", "BSOP_HOUR", "HOUR_CLS_CODE",
        "ASKP1", "ASKP2", "ASKP3", "ASKP4", "ASKP5",
        "ASKP6", "ASKP7", "ASKP8", "ASKP9", "ASKP10",
        "BIDP1", "BIDP2", "BIDP3", "BIDP4", "BIDP5",
        "BIDP6", "BIDP7", "BIDP8", "BIDP9", "BIDP10",
        "ASKP_RSQN1", "ASKP_RSQN2", "ASKP_RSQN3", "ASKP_RSQN4", "ASKP_RSQN5",
        "ASKP_RSQN6", "ASKP_RSQN7", "ASKP_RSQN8", "ASKP_RSQN9", "ASKP_RSQN10",
        "BIDP_RSQN1", "BIDP_RSQN2", "BIDP_RSQN3", "BIDP_RSQN4", "BIDP_RSQN5",
        "BIDP_RSQN6", "BIDP_RSQN7", "BIDP_RSQN8", "BIDP_RSQN9", "BIDP_RSQN10",
        "TOTAL_ASKP_RSQN", "TOTAL_BIDP_RSQN", "OVTM_TOTAL_ASKP_RSQN", "OVTM_TOTAL_BIDP_RSQN",
        "ANTC_CNPR", "ANTC_CNQN", "ANTC_VOL", "ANTC_CNTG_VRSS", "ANTC_CNTG_VRSS_SIGN",
        "ANTC_CNTG_PRDY_CTRT", "ACML_VOL", "TOTAL_ASKP_RSQN_ICDC", "TOTAL_BIDP_RSQN_ICDC",
        "OVTM_TOTAL_ASKP_ICDC", "OVTM_TOTAL_BIDP_ICDC", "STCK_DEAL_CLS_CODE",
        "NMID_PRC", "NMID_TOTAL_RSQN", "NMID_CLS_CODE"
    ]

    return msg, columns
