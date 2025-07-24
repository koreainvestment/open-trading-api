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
# [국내주식] 실시간시세 > 국내주식 실시간예상체결 (KRX)[H0STANC0]
##############################################################################################


def exp_ccnl_krx(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간예상체결 (KRX)[H0STANC0]
    국내주식 실시간예상체결 API를 통해 실시간 데이터를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타냅니다.
        tr_key (str): [필수] 종목코드. 빈 문자열이 아니어야 하며, 유효한 종목코드 형식이어야 합니다.

    Returns:
        message (dict): 실시간 데이터 구독에 대한 메시지 데이터.
        columns (list[str]): 실시간 데이터의 컬럼 정보.

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생합니다.

    Example:
        >>> msg, columns = exp_ccnl_krx("1", "005930")
        >>> print(msg, columns)

    참고자료:
    - 실시간시세(웹소켓) 파이썬 샘플코드는 한국투자증권 Github 참고 부탁드립니다.
      https://github.com/koreainvestment/open-trading-api/blob/main/websocket/python/ws_domestic_overseas_all.py
    - 실시간시세(웹소켓) API 사용방법에 대한 자세한 설명은 한국투자증권 Wikidocs 참고 부탁드립니다.
      https://wikidocs.net/book/7847
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key is required and cannot be an empty string")

    tr_id = "H0STANC0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 구독 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
    columns = [
        "mksc_shrn_iscd",
        "stck_cntg_hour",
        "stck_prpr",
        "prdy_vrss_sign",
        "prdy_vrss",
        "prdy_ctrt",
        "wghn_avrg_stck_prc",
        "stck_oprc",
        "stck_hgpr",
        "stck_lwpr",
        "askp1",
        "bidp1",
        "cntg_vol",
        "acml_vol",
        "acml_tr_pbmn",
        "seln_cntg_csnu",
        "shnu_cntg_csnu",
        "ntby_cntg_csnu",
        "cttr",
        "seln_cntg_smtn",
        "shnu_cntg_smtn",
        "cntg_cls_code",
        "shnu_rate",
        "prdy_vol_vrss_acml_vol_rate",
        "oprc_hour",
        "oprc_vrss_prpr_sign",
        "oprc_vrss_prpr",
        "hgpr_hour",
        "hgpr_vrss_prpr_sign",
        "hgpr_vrss_prpr",
        "lwpr_hour",
        "lwpr_vrss_prpr_sign",
        "lwpr_vrss_prpr",
        "bsop_date",
        "new_mkop_cls_code",
        "trht_yn",
        "askp_rsqn1",
        "bidp_rsqn1",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "vol_tnrt",
        "prdy_smns_hour_acml_vol",
        "prdy_smns_hour_acml_vol_rate",
        "hour_cls_code",
        "mrkt_trtm_cls_code",
    ]

    return msg, columns
