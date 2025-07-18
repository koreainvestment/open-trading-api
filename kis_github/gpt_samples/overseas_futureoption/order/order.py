# -*- coding: utf-8 -*-
"""
Created on 2025-07-01

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
API_URL = "/uapi/overseas-futureoption/v1/trading/order"

##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 주문[v1_해외선물-001]
##############################################################################################

def order(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ovrs_futr_fx_pdno: str,  # 해외선물FX상품번호
    sll_buy_dvsn_cd: str,  # 매도매수구분코드
    fm_lqd_ustl_ccld_dt: str,  # FM청산미결제체결일자
    fm_lqd_ustl_ccno: str,  # FM청산미결제체결번호
    pric_dvsn_cd: str,  # 가격구분코드
    fm_limit_ord_pric: str,  # FMLIMIT주문가격
    fm_stop_ord_pric: str,  # FMSTOP주문가격
    fm_ord_qty: str,  # FM주문수량
    fm_lqd_lmt_ord_pric: str,  # FM청산LIMIT주문가격
    fm_lqd_stop_ord_pric: str,  # FM청산STOP주문가격
    ccld_cndt_cd: str,  # 체결조건코드
    cplx_ord_dvsn_cd: str,  # 복합주문구분코드
    ecis_rsvn_ord_yn: str,  # 행사예약주문여부
    fm_hdge_ord_scrn_yn: str,  # FM_HEDGE주문화면여부

) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 주문/계좌 
    해외선물옵션 주문[v1_해외선물-001]
    해외선물옵션 주문 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ovrs_futr_fx_pdno (str): 해외선물FX상품번호
        sll_buy_dvsn_cd (str): 01 : 매도 02 : 매수
        fm_lqd_ustl_ccld_dt (str): 빈칸 (hedge청산만 이용)
        fm_lqd_ustl_ccno (str): 빈칸 (hedge청산만 이용)
        pric_dvsn_cd (str): 1.지정, 2. 시장, 3. STOP, 4 S/L
        fm_limit_ord_pric (str): 지정가인 경우 가격 입력 * 시장가, STOP주문인 경우, 빈칸("") 입력
        fm_stop_ord_pric (str): STOP 주문 가격 입력 * 시장가, 지정가인 경우, 빈칸("") 입력
        fm_ord_qty (str): FM주문수량
        fm_lqd_lmt_ord_pric (str): 빈칸 (hedge청산만 이용)
        fm_lqd_stop_ord_pric (str): 빈칸 (hedge청산만 이용)
        ccld_cndt_cd (str): 일반적으로 6 (EOD, 지정가)  GTD인 경우 5, 시장가인 경우만 2
        cplx_ord_dvsn_cd (str): 0 (hedge청산만 이용)
        ecis_rsvn_ord_yn (str): N
        fm_hdge_ord_scrn_yn (str): N
        
    Returns:
        Optional[pd.DataFrame]: 해외선물옵션 주문 데이터
        
    Example:
        >>> df = order(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ovrs_futr_fx_pdno="6BZ22",
        ...     sll_buy_dvsn_cd="02",
        ...     fm_lqd_ustl_ccld_dt="",
        ...     fm_lqd_ustl_ccno="",
        ...     pric_dvsn_cd="1",
        ...     fm_limit_ord_pric="1.17",
        ...     fm_stop_ord_pric="",
        ...     fm_ord_qty="1",
        ...     fm_lqd_lmt_ord_pric="",
        ...     fm_lqd_stop_ord_pric="",
        ...     ccld_cndt_cd="6",
        ...     cplx_ord_dvsn_cd="0",
        ...     ecis_rsvn_ord_yn="N",
        ...     fm_hdge_ord_scrn_yn="N"
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
    if not ovrs_futr_fx_pdno:
        logger.error("ovrs_futr_fx_pdno is required. (e.g. '1AALN25 C10.0')")
        raise ValueError("ovrs_futr_fx_pdno is required. (e.g. '1AALN25 C10.0')")
    if not sll_buy_dvsn_cd:
        logger.error("sll_buy_dvsn_cd is required. (e.g. '02')")
        raise ValueError("sll_buy_dvsn_cd is required. (e.g. '02')")
    if not pric_dvsn_cd:
        logger.error("pric_dvsn_cd is required. (e.g. '1')")
        raise ValueError("pric_dvsn_cd is required. (e.g. '1')")
    if not fm_ord_qty:
        logger.error("fm_ord_qty is required. (e.g. '1')")
        raise ValueError("fm_ord_qty is required. (e.g. '1')")
    if not ccld_cndt_cd:
        logger.error("ccld_cndt_cd is required. (e.g. '6')")
        raise ValueError("ccld_cndt_cd is required. (e.g. '6')")

    url = API_URL
    tr_id = "OTFM3001U"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "OVRS_FUTR_FX_PDNO": ovrs_futr_fx_pdno,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "FM_LQD_USTL_CCLD_DT": fm_lqd_ustl_ccld_dt,
        "FM_LQD_USTL_CCNO": fm_lqd_ustl_ccno,
        "PRIC_DVSN_CD": pric_dvsn_cd,
        "FM_LIMIT_ORD_PRIC": fm_limit_ord_pric,
        "FM_STOP_ORD_PRIC": fm_stop_ord_pric,
        "FM_ORD_QTY": fm_ord_qty,
        "FM_LQD_LMT_ORD_PRIC": fm_lqd_lmt_ord_pric,
        "FM_LQD_STOP_ORD_PRIC": fm_lqd_stop_ord_pric,
        "CCLD_CNDT_CD": ccld_cndt_cd,
        "CPLX_ORD_DVSN_CD": cplx_ord_dvsn_cd,
        "ECIS_RSVN_ORD_YN": ecis_rsvn_ord_yn,
        "FM_HDGE_ORD_SCRN_YN": fm_hdge_ord_scrn_yn,
    }

    res = ka._url_fetch(api_url=API_URL,
                        ptr_id=tr_id,
                        tr_cont="",
                        params=params,
                        postFlag=True
            )

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
