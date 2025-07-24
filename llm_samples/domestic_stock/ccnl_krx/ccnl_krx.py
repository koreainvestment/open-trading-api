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
# [국내주식] 실시간시세 > 국내주식 실시간체결가(KRX) [실시간-003]
##############################################################################################

def ccnl_krx(
        tr_type: str,
        tr_key: str,
        env_dv: str = "real",  # 실전모의구분
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간체결가 (KRX)[H0STCNT0] 구독 함수

    이 함수는 한국투자증권 웹소켓 API를 통해 국내 주식의 실시간 체결가 데이터를 구독합니다.
    실시간 데이터를 구독하거나 구독 해제할 수 있습니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)
        env_dv (str): 실전모의구분 (real:실전, demo:모의)

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Raises:
        ValueError: tr_key가 빈 문자열인 경우
        ValueError: env_dv가 'real' 또는 'demo'가 아닌 경우

    Example:
        >>> msg, columns = ccnl_krx("1", "005930", env_dv="real")
        >>> print(msg, columns)

    실시간 데이터는 웹소켓을 통해 지속적으로 업데이트됩니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key is required and cannot be an empty string")

    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real":
        tr_id = "H0STCNT0"  # 실전투자용 TR ID
    elif env_dv == "demo":
        tr_id = "H0STCNT0"  # 모의투자용 TR ID (웹소켓은 동일한 TR ID 사용)
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "tr_key": tr_key,
    }

    # 데이터 구독 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
    columns = [
        "MKSC_SHRN_ISCD", "STCK_CNTG_HOUR", "STCK_PRPR", "PRDY_VRSS_SIGN",
        "PRDY_VRSS", "PRDY_CTRT", "WGHN_AVRG_STCK_PRC", "STCK_OPRC",
        "STCK_HGPR", "STCK_LWPR", "ASKP1", "BIDP1", "CNTG_VOL", "ACML_VOL",
        "ACML_TR_PBMN", "SELN_CNTG_CSNU", "SHNU_CNTG_CSNU", "NTBY_CNTG_CSNU",
        "CTTR", "SELN_CNTG_SMTN", "SHNU_CNTG_SMTN", "CCLD_DVSN", "SHNU_RATE",
        "PRDY_VOL_VRSS_ACML_VOL_RATE", "OPRC_HOUR", "OPRC_VRSS_PRPR_SIGN",
        "OPRC_VRSS_PRPR", "HGPR_HOUR", "HGPR_VRSS_PRPR_SIGN", "HGPR_VRSS_PRPR",
        "LWPR_HOUR", "LWPR_VRSS_PRPR_SIGN", "LWPR_VRSS_PRPR", "BSOP_DATE",
        "NEW_MKOP_CLS_CODE", "TRHT_YN", "ASKP_RSQN1", "BIDP_RSQN1",
        "TOTAL_ASKP_RSQN", "TOTAL_BIDP_RSQN", "VOL_TNRT",
        "PRDY_SMNS_HOUR_ACML_VOL", "PRDY_SMNS_HOUR_ACML_VOL_RATE",
        "HOUR_CLS_CODE", "MRKT_TRTM_CLS_CODE", "VI_STND_PRC"
    ]

    return msg, columns
