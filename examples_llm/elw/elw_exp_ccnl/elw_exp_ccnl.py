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
# [국내주식] 실시간시세 - ELW 실시간예상체결[실시간-063]
##############################################################################################

def elw_exp_ccnl(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    ELW 실시간예상체결[H0EWANC0]
    ELW 실시간예상체결 API입니다. 이 함수는 웹소켓을 통해 실시간 데이터를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타냅니다.
        tr_key (str): [필수] 종목코드. 빈 문자열일 수 없습니다.

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 응답 데이터의 컬럼 정보

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생합니다.

    Example:
        >>> msg, columns = elw_exp_ccnl("1", "005930")
        >>> print(msg, columns)

    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key is required and cannot be an empty string")

    tr_id = "H0EWANC0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 구독 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터의 컬럼 정보
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
        "tmvl_val",
        "prit",
        "prmm_val",
        "gear",
        "prls_qryr_rate",
        "invl_val",
        "prmm_rate",
        "cfp",
        "lvrg_val",
        "delta",
        "gama",
        "vega",
        "theta",
        "rho",
        "hts_ints_vltl",
        "hts_thpr",
        "vol_tnrt",
        "lp_hvol",
        "lp_hldn_rate",
    ]

    return msg, columns
