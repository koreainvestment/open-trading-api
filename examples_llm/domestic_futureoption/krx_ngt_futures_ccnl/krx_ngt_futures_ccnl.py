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
# [국내선물옵션] 실시간시세 > KRX야간선물 실시간종목체결 [실시간-064]
##############################################################################################

def krx_ngt_futures_ccnl(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    [참고자료]

    종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = krx_ngt_futures_ccnl("1", "101W9000")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0MFCNT0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "futs_shrn_iscd",
        "bsop_hour",
        "futs_prdy_vrss",
        "prdy_vrss_sign",
        "futs_prdy_ctrt",
        "futs_prpr",
        "futs_oprc",
        "futs_hgpr",
        "futs_lwpr",
        "last_cnqn",
        "acml_vol",
        "acml_tr_pbmn",
        "hts_thpr",
        "mrkt_basis",
        "dprt",
        "nmsc_fctn_stpl_prc",
        "fmsc_fctn_stpl_prc",
        "spead_prc",
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
        "cttr",
        "esdg",
        "otst_stpl_rgbf_qty_icdc",
        "thpr_basis",
        "futs_askp1",
        "futs_bidp1",
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
        "dynm_mxpr",
        "dynm_llam",
        "dynm_prc_limt_yn"
    ]

    return msg, columns 