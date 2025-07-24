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
# [국내주식] 실시간시세 > 국내주식 실시간 체결가 (NXT) [H0NXCNT0]
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
        "MKSC_SHRN_ISCD", "STCK_CNTG_HOUR", "STCK_PRPR", "PRDY_VRSS_SIGN",
        "PRDY_VRSS", "PRDY_CTRT", "WGHN_AVRG_STCK_PRC", "STCK_OPRC",
        "STCK_HGPR", "STCK_LWPR", "ASKP1", "BIDP1", "CNTG_VOL", "ACML_VOL",
        "ACML_TR_PBMN", "SELN_CNTG_CSNU", "SHNU_CNTG_CSNU", "NTBY_CNTG_CSNU",
        "CTTR", "SELN_CNTG_SMTN", "SHNU_CNTG_SMTN", "CNTG_CLS_CODE",
        "SHNU_RATE", "PRDY_VOL_VRSS_ACML_VOL_RATE", "OPRC_HOUR",
        "OPRC_VRSS_PRPR_SIGN", "OPRC_VRSS_PRPR", "HGPR_HOUR",
        "HGPR_VRSS_PRPR_SIGN", "HGPR_VRSS_PRPR", "LWPR_HOUR",
        "LWPR_VRSS_PRPR_SIGN", "LWPR_VRSS_PRPR", "BSOP_DATE",
        "NEW_MKOP_CLS_CODE", "TRHT_YN", "ASKP_RSQN1", "BIDP_RSQN1",
        "TOTAL_ASKP_RSQN", "TOTAL_BIDP_RSQN", "VOL_TNRT",
        "PRDY_SMNS_HOUR_ACML_VOL", "PRDY_SMNS_HOUR_ACML_VOL_RATE",
        "HOUR_CLS_CODE", "MRKT_TRTM_CLS_CODE", "VI_STND_PRC"
    ]

    return msg, columns
