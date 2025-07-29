"""
Created on 20250601
@author: LaivData SJPark with cursor
"""

import logging
import sys

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 실시간시세 > 지수옵션 실시간체결가[실시간-014]
##############################################################################################

def index_option_realtime_conclusion(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    지수옵션 실시간체결가 API입니다.
    실시간 웹소켓 연결을 통해 지수옵션의 실시간 체결가 정보를 수신할 수 있습니다.
    옵션 현재가, 시고저가, 체결량, 누적거래량, 이론가 등의 기본 정보와 함께
    델타, 감마, 베가, 세타, 로우 등의 그리스 지표와 내재가치, 시간가치, 변동성 정보를 제공합니다.
    옵션 거래에 필수적인 전문 지표들을 포함하는 확장된 체결가 정보입니다.
    실전계좌만 지원되며 모의투자는 미지원됩니다.

    Args:
        tr_type (str): [필수] 구독 등록/해제 여부 (ex. "1": 구독, "2": 해제)
        tr_key (str): [필수] 코드 (ex. 201S11305)

    Returns:
        message (str): 메시지 데이터

    Example:
        >>> msg, columns = index_option_realtime_conclusion("1", "101W09")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0IOCNT0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "optn_shrn_iscd",
        "bsop_hour",
        "optn_prpr",
        "prdy_vrss_sign",
        "optn_prdy_vrss",
        "prdy_ctrt",
        "optn_oprc",
        "optn_hgpr",
        "optn_lwpr",
        "last_cnqn",
        "acml_vol",
        "acml_tr_pbmn",
        "hts_thpr",
        "hts_otst_stpl_qty",
        "otst_stpl_qty_icdc",
        "oprc_hour",
        "oprc_vrss_prpr_sign",
        "oprc_vrss_nmix_prpr",
        "hgpr_hour",
        "hgpr_vrss_prpr_sign",
        "hgpr_vrss_nmix_prpr",
        "lwpr_hour",
        "lwpr_vrss_prpr_sign",
        "lwpr_vrss_nmix_prpr",
        "shnu_rate",
        "prmm_val",
        "invl_val",
        "tmvl_val",
        "delta",
        "gama",
        "vega",
        "theta",
        "rho",
        "hts_ints_vltl",
        "esdg",
        "otst_stpl_rgbf_qty_icdc",
        "thpr_basis",
        "unas_hist_vltl",
        "cttr",
        "dprt",
        "mrkt_basis",
        "optn_askp1",
        "optn_bidp1",
        "askp_rsqn1",
        "bidp_rsqn1",
        "seln_cntg_csnu",
        "shnu_cntg_csnu",
        "ntby_cntg_csnu",
        "seln_cntg_smtn",
        "shnu_cntg_smtn",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "prdy_vol_vrss_acml_vol_rate",
        "avrg_vltl",
        "dscs_lrqn_vol",
        "dynm_mxpr",
        "dynm_llam",
        "dynm_prc_limt_yn"
    ]

    return msg, columns 