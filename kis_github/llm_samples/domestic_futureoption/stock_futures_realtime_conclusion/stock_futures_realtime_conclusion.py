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
# [국내선물옵션] 실시간시세 > 주식선물 실시간체결가 [실시간-029]
##############################################################################################

def stock_futures_realtime_conclusion(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    주식선물 실시간체결가 API입니다.
    실시간 웹소켓 연결을 통해 주식선물의 실시간 체결가 정보를 수신할 수 있습니다.
    주식 현재가, 시고저가, 체결량, 누적거래량, 이론가, 베이시스, 괴리율 등의 상세 정보를 제공합니다.
    매도/매수 호가, 체결 건수, 미결제 약정 수량 등의 선물거래 필수 정보를 포함합니다.
    실전계좌만 지원되며 모의투자는 미지원됩니다.

    Args:
        tr_type (str): [필수] 구독 등록/해제 여부 (ex. "1": 구독, "2": 해제)
        tr_key (str): [필수] 종목코드 (ex. 101S12)

    Returns:
        message (str): 메시지 데이터

    Example:
        >>> msg, columns = stock_futures_realtime_conclusion("1", "101S12")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0ZFCNT0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "futs_shrn_iscd",
        "bsop_hour",
        "stck_prpr",
        "prdy_vrss_sign",
        "prdy_vrss",
        "futs_prdy_ctrt",
        "stck_oprc",
        "stck_hgpr",
        "stck_lwpr",
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
        "oprc_vrss_prpr",
        "hgpr_hour",
        "hgpr_vrss_prpr_sign",
        "hgpr_vrss_prpr",
        "lwpr_hour",
        "lwpr_vrss_prpr_sign",
        "lwpr_vrss_prpr",
        "shnu_rate",
        "cttr",
        "esdg",
        "otst_stpl_rgbf_qty_icdc",
        "thpr_basis",
        "askp1",
        "bidp1",
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