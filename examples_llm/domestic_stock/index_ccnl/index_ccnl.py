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
# [국내주식] 실시간시세 > 국내지수 실시간체결 [실시간-026]
##############################################################################################

def index_ccnl(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내지수 실시간체결[H0UPCNT0] 구독 함수

    이 함수는 한국투자증권의 웹소켓 API를 통해 국내지수의 실시간 데이터를 구독합니다.
    실시간 데이터는 웹소켓을 통해 지속적으로 업데이트되며, 구독을 통해 실시간으로 데이터를 수신할 수 있습니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 값
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 응답 데이터의 컬럼 정보

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = subscribe_realtime_index("1", "005930")
        >>> print(msg, columns)

    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 필수 입력값입니다.")

    tr_id = "H0UPCNT0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 구독 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
    columns = [
        "bstp_cls_code", "bsop_hour", "prpr_nmix", "prdy_vrss_sign",
        "bstp_nmix_prdy_vrss", "acml_vol", "acml_tr_pbmn", "pcas_vol",
        "pcas_tr_pbmn", "prdy_ctrt", "oprc_nmix", "nmix_hgpr", "nmix_lwpr",
        "oprc_vrss_nmix_prpr", "oprc_vrss_nmix_sign", "hgpr_vrss_nmix_prpr",
        "hgpr_vrss_nmix_sign", "lwpr_vrss_nmix_prpr", "lwpr_vrss_nmix_sign",
        "prdy_clpr_vrss_oprc_rate", "prdy_clpr_vrss_hgpr_rate",
        "prdy_clpr_vrss_lwpr_rate", "uplm_issu_cnt", "ascn_issu_cnt",
        "stnr_issu_cnt", "down_issu_cnt", "lslm_issu_cnt", "qtqt_ascn_issu_cnt",
        "qtqt_down_issu_cnt", "tick_vrss"
    ]

    return msg, columns
