"""
Created on 2025-07-09
@author: LaivData jjlee with cursor
"""

import logging
import sys

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간호가 (NXT)
##############################################################################################



def asking_price_nxt(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간호가 (NXT)[H0NXASP0] 구독 함수
    국내주식 실시간호가 (NXT) API를 통해 실시간 데이터를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 값
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)

    Returns:
        message (dict): 실시간 데이터 메시지
        columns (list[str]): 데이터의 컬럼 정보

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = subscribe_asking_price("1", "005930")
        >>> print(msg, columns)

    Note:
        이 함수는 웹소켓을 통해 실시간 데이터를 구독합니다. 구독을 시작하면 실시간으로 데이터가 수신됩니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 빈 문자열일 수 없습니다.")

    tr_id = "H0NXASP0"

    params = {
        "tr_key": tr_key,
    }

    # 웹소켓을 통해 실시간 데이터 구독
    msg = ka.data_fetch(tr_id, tr_type, params)

    # API 메타데이터 기반 컬럼 정보
    columns = [
        "MKSC_SHRN_ISCD",
        "BSOP_HOUR",
        "HOUR_CLS_CODE",
        "ASKP1",
        "ASKP2",
        "ASKP3",
        "ASKP4",
        "ASKP5",
        "ASKP6",
        "ASKP7",
        "ASKP8",
        "ASKP9",
        "ASKP10",
        "BIDP1",
        "BIDP2",
        "BIDP3",
        "BIDP4",
        "BIDP5",
        "BIDP6",
        "BIDP7",
        "BIDP8",
        "BIDP9",
        "BIDP10",
        "ASKP_RSQN1",
        "ASKP_RSQN2",
        "ASKP_RSQN3",
        "ASKP_RSQN4",
        "ASKP_RSQN5",
        "ASKP_RSQN6",
        "ASKP_RSQN7",
        "ASKP_RSQN8",
        "ASKP_RSQN9",
        "ASKP_RSQN10",
        "BIDP_RSQN1",
        "BIDP_RSQN2",
        "BIDP_RSQN3",
        "BIDP_RSQN4",
        "BIDP_RSQN5",
        "BIDP_RSQN6",
        "BIDP_RSQN7",
        "BIDP_RSQN8",
        "BIDP_RSQN9",
        "BIDP_RSQN10",
        "TOTAL_ASKP_RSQN",
        "TOTAL_BIDP_RSQN",
        "OVTM_TOTAL_ASKP_RSQN",
        "OVTM_TOTAL_BIDP_RSQN",
        "ANTC_CNPR",
        "ANTC_CNQN",
        "ANTC_VOL",
        "ANTC_CNTG_VRSS",
        "ANTC_CNTG_VRSS_SIGN",
        "ANTC_CNTG_PRDY_CTRT",
        "ACML_VOL",
        "TOTAL_ASKP_RSQN_ICDC",
        "TOTAL_BIDP_RSQN_ICDC",
        "OVTM_TOTAL_ASKP_ICDC",
        "OVTM_TOTAL_BIDP_ICDC",
        "STCK_DEAL_CLS_CODE",
        "KMID_PRC",
        "KMID_TOTAL_RSQN",
        "KMID_CLS_CODE",
        "NMID_PRC",
        "NMID_TOTAL_RSQN",
        "NMID_CLS_CODE",
    ]

    return msg, columns
