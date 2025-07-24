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
# [국내주식] 실시간시세 > 국내주식 실시간예상체결 (NXT)
##############################################################################################

def exp_ccnl_nxt(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간예상체결 (NXT)[H0NXANC0]
    국내주식 실시간예상체결 (NXT) API를 통해 실시간 데이터를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 값
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)

    Returns:
        message (dict): 실시간 데이터 메시지
        columns (list[str]): 응답 데이터의 컬럼 정보

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = exp_ccnl_nxt("1", "005930")
        >>> print(msg, columns)

    Note:
        이 함수는 웹소켓을 통해 실시간 데이터를 구독합니다. 구독을 시작하면 실시간으로 데이터가 수신됩니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key is required and cannot be an empty string")

    tr_id = "H0NXANC0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 구독 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터의 컬럼 정보
    columns = [
        "MKSC_SHRN_ISCD",
        "STCK_CNTG_HOUR",
        "STCK_PRPR",
        "PRDY_VRSS_SIGN",
        "PRDY_VRSS",
        "PRDY_CTRT",
        "WGHN_AVRG_STCK_PRC",
        "STCK_OPRC",
        "STCK_HGPR",
        "STCK_LWPR",
        "ASKP1",
        "BIDP1",
        "CNTG_VOL",
        "ACML_VOL",
        "ACML_TR_PBMN",
        "SELN_CNTG_CSNU",
        "SHNU_CNTG_CSNU",
        "NTBY_CNTG_CSNU",
        "CTTR",
        "SELN_CNTG_SMTN",
        "SHNU_CNTG_SMTN",
        "CNTG_CLS_CODE",
        "SHNU_RATE",
        "PRDY_VOL_VRSS_ACML_VOL_RATE",
        "OPRC_HOUR",
        "OPRC_VRSS_PRPR_SIGN",
        "OPRC_VRSS_PRPR",
        "HGPR_HOUR",
        "HGPR_VRSS_PRPR_SIGN",
        "HGPR_VRSS_PRPR",
        "LWPR_HOUR",
        "LWPR_VRSS_PRPR_SIGN",
        "LWPR_VRSS_PRPR",
        "BSOP_DATE",
        "NEW_MKOP_CLS_CODE",
        "TRHT_YN",
        "ASKP_RSQN1",
        "BIDP_RSQN1",
        "TOTAL_ASKP_RSQN",
        "TOTAL_BIDP_RSQN",
        "VOL_TNRT",
        "PRDY_SMNS_HOUR_ACML_VOL",
        "PRDY_SMNS_HOUR_ACML_VOL_RATE",
        "HOUR_CLS_CODE",
        "MRKT_TRTM_CLS_CODE",
        "VI_STND_PRC",
    ]

    return msg, columns
