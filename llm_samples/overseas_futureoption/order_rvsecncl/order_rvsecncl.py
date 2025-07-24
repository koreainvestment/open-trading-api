# -*- coding: utf-8 -*-
"""
Created on 2025-07-03

@author: LaivData jjlee with cursor
"""

import logging
from typing import Optional
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 상수 정의
API_URL = "/uapi/overseas-futureoption/v1/trading/order-rvsecncl"

##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 정정취소주문[v1_해외선물-002, 003]
##############################################################################################

def order_rvsecncl(
    cano: str,  # 종합계좌번호
    ord_dv: str, # 주문구분
    acnt_prdt_cd: str,  # 계좌상품코드
    orgn_ord_dt: str,  # 원주문일자
    orgn_odno: str,  # 원주문번호
    fm_limit_ord_pric: str,  # FMLIMIT주문가격
    fm_stop_ord_pric: str,  # FMSTOP주문가격
    fm_lqd_lmt_ord_pric: str,  # FM청산LIMIT주문가격
    fm_lqd_stop_ord_pric: str,  # FM청산STOP주문가격
    fm_hdge_ord_scrn_yn: str,  # FM_HEDGE주문화면여부
    fm_mkpr_cvsn_yn: str,  # FM시장가전환여부

) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 주문/계좌 
    해외선물옵션 정정취소주문[v1_해외선물-002, 003]
    해외선물옵션 정정취소주문 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        ord_dv (str): 주문구분 (0:정정, 1:취소)
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        orgn_ord_dt (str): 원 주문 시 출력되는 ORD_DT 값을 입력 (현지거래일)
        orgn_odno (str): 정정/취소시 주문번호(ODNO) 8자리를 문자열처럼 "0"을 포함해서 전송 (원 주문 시 출력된 ODNO 값 활용) (ex. ORGN_ODNO : 00360686)
        fm_limit_ord_pric (str): OTFM3002U(해외선물옵션주문정정)만 사용
        fm_stop_ord_pric (str): OTFM3002U(해외선물옵션주문정정)만 사용
        fm_lqd_lmt_ord_pric (str): OTFM3002U(해외선물옵션주문정정)만 사용
        fm_lqd_stop_ord_pric (str): OTFM3002U(해외선물옵션주문정정)만 사용
        fm_hdge_ord_scrn_yn (str): N
        fm_mkpr_cvsn_yn (str): OTFM3003U(해외선물옵션주문취소)만 사용  ※ FM_MKPR_CVSN_YN 항목에 'Y'로 설정하여 취소주문을 접수할 경우, 주문 취소확인이 들어오면 원장에서 시장가주문을 하나 또 내줌
        
    Returns:
        Optional[pd.DataFrame]: 해외선물옵션 정정취소주문 데이터
        
    Example:
        >>> df = order_rvsecncl(
        ...     cano=trenv.my_acct,
        ...     ord_dv="0",
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     orgn_ord_dt="20250630",
        ...     orgn_odno="00360686",
        ...     fm_limit_ord_pric="",
        ...     fm_stop_ord_pric="",
        ...     fm_lqd_lmt_ord_pric="",
        ...     fm_lqd_stop_ord_pric="",
        ...     fm_hdge_ord_scrn_yn="N",
        ...     fm_mkpr_cvsn_yn="N"
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '81012345')")
        raise ValueError("cano is required. (e.g. '81012345')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '08')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '08')")
    if not orgn_ord_dt:
        logger.error("orgn_ord_dt is required. (e.g. '20250630')")
        raise ValueError("orgn_ord_dt is required. (e.g. '20250630')")
    if not orgn_odno:
        logger.error("orgn_odno is required. (e.g. '00360686')")
        raise ValueError("orgn_odno is required. (e.g. '00360686')")

    if ord_dv == "0":
        tr_id = "OTFM3002U"
    elif ord_dv == "1":
        tr_id = "OTFM3003U"
    else:
        logger.error("ord_dv is required. (e.g. '0' or '1')")
        raise ValueError("ord_dv is required. (e.g. '0' or '1')")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "ORGN_ORD_DT": orgn_ord_dt,
        "ORGN_ODNO": orgn_odno,
        "FM_LIMIT_ORD_PRIC": fm_limit_ord_pric,
        "FM_STOP_ORD_PRIC": fm_stop_ord_pric,
        "FM_LQD_LMT_ORD_PRIC": fm_lqd_lmt_ord_pric,
        "FM_LQD_STOP_ORD_PRIC": fm_lqd_stop_ord_pric,
        "FM_HDGE_ORD_SCRN_YN": fm_hdge_ord_scrn_yn,
        "FM_MKPR_CVSN_YN": fm_mkpr_cvsn_yn,
    }

    logger.info("Calling API with parameters: %s", params)

    res = ka._url_fetch(api_url=API_URL,
                         ptr_id=tr_id,
                         tr_cont="",
                         params=params,
                         postFlag=True)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            dataframe = pd.DataFrame(output_data)
        else:
            dataframe = pd.DataFrame()
                    
        logger.info("Data fetch complete.")
        return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
