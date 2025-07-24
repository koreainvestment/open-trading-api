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
# [국내주식] 실시간시세 > 국내주식 실시간호가 (KRX) [실시간-004]
##############################################################################################

def asking_price_krx(
        tr_type: str,
        tr_key: str,
        env_dv: str = "real",  # 실전모의구분
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간 호가 데이터 구독 (KRX)[H0STASP0]
    
    이 함수는 한국투자증권 웹소켓 API를 통해 실시간으로 국내주식의 호가 데이터를 구독합니다.
    웹소켓을 통해 실시간 데이터를 수신하며, 구독 등록 및 해제 기능을 제공합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)
        env_dv (str): 실전모의구분 (real: 실전, demo: 모의)

    Returns:
        message (dict): 실시간 데이터 구독에 대한 메시지 데이터
        columns (list[str]): 실시간 데이터의 컬럼 정보

    Raises:
        ValueError: 필수 파라미터가 누락되었거나 잘못된 경우 발생

    Example:
        >>> msg, columns = subscribe_krx_realtime_asking_price("1", "005930", env_dv="real")
        >>> print(msg, columns)

    실시간 데이터는 웹소켓을 통해 지속적으로 수신되며, 구독 해제 시까지 계속됩니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 필수 입력값입니다.")

    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real":
        tr_id = "H0STASP0"  # 실전투자용 TR ID
    elif env_dv == "demo":
        tr_id = "H0STASP0"  # 모의투자용 TR ID (웹소켓은 동일한 TR ID 사용)
    else:
        raise ValueError("env_dv는 'real' 또는 'demo'만 가능합니다.")

    params = {
        "tr_key": tr_key,
    }

    # 데이터 구독 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
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
        "OVTM_TOTAL_ASKP_ICDC", "OVTM_TOTAL_BIDP_ICDC", "STCK_DEAL_CLS_CODE"
    ]

    return msg, columns
