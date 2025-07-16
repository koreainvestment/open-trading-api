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
# [국내선물옵션] 실시간시세 > 주식옵션 실시간체결가 [실시간-044]
##############################################################################################

def stock_option_ccnl(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    주식옵션 실시간체결가 API입니다.

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = stock_option_ccnl("1", "101W9000")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0ZOCNT0"

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
        "prdy_vol_vrss_acml_vol_rate"
    ]

    return msg, columns
