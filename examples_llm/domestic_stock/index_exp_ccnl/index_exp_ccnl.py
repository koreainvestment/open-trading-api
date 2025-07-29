"""
Created on 2025-07-08
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
# [국내주식] 실시간시세 > 국내지수 실시간예상체결 [실시간-027]
##############################################################################################

def index_exp_ccnl(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내지수 실시간예상체결[H0UPANC0] 구독 함수

    이 함수는 한국투자증권 웹소켓 API를 통해 국내지수의 실시간 데이터를 구독합니다.
    실시간 데이터는 웹소켓을 통해 지속적으로 업데이트되며, 구독 등록/해제 여부와 종목코드를 통해 데이터를 필터링합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 문자열
        tr_key (str): [필수] 종목코드를 나타내는 문자열. 빈 문자열일 수 없습니다.

    Returns:
        message (dict): 실시간 데이터 구독에 대한 응답 메시지
        columns (list[str]): 실시간 데이터의 컬럼 정보 리스트

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = index_exp_ccnl("1", "005930")
        >>> print(msg, columns)

    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key is required and cannot be an empty string")

    tr_id = "H0UPANC0"

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
        "stnr_issu_cnt", "down_issu_cnt", "lslm_issu_cnt",
        "qtqt_ascn_issu_cnt", "qtqt_down_issu_cnt", "tick_vrss"
    ]

    return msg, columns
