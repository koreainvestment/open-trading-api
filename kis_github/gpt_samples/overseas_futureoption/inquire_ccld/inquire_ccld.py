# -*- coding: utf-8 -*-
"""
Created on 2025-07-02

@author: LaivData jjlee with cursor
"""

import logging
import time
from typing import Optional
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 당일주문내역조회 [v1_해외선물-004]
##############################################################################################

# API 정보
API_URL = "/uapi/overseas-futureoption/v1/trading/inquire-ccld"

def inquire_ccld(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ccld_nccs_dvsn: str,  # 체결미체결구분
    sll_buy_dvsn_cd: str,  # 매도매수구분코드
    fuop_dvsn: str,  # 선물옵션구분
    ctx_area_fk200: str,  # 연속조회검색조건200
    ctx_area_nk200: str,  # 연속조회키200
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 주문/계좌 
    해외선물옵션 당일주문내역조회[v1_해외선물-004]
    해외선물옵션 당일주문내역조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ccld_nccs_dvsn (str): 01:전체 / 02:체결 / 03:미체결
        sll_buy_dvsn_cd (str): %%:전체 / 01:매도 / 02:매수
        fuop_dvsn (str): 00:전체 / 01:선물 / 02:옵션
        ctx_area_fk200 (str): 연속조회검색조건200
        ctx_area_nk200 (str): 연속조회키200
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외선물옵션 당일주문내역조회 데이터
        
    Example:
        >>> df = inquire_ccld(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ccld_nccs_dvsn="01",
        ...     sll_buy_dvsn_cd="01",
        ...     fuop_dvsn="00",
        ...     ctx_area_fk200="",
        ...     ctx_area_nk200=""
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '80012345')")
        raise ValueError("cano is required. (e.g. '80012345')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '08')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '08')")
    if not ccld_nccs_dvsn:
        logger.error("ccld_nccs_dvsn is required. (e.g. '01')")
        raise ValueError("ccld_nccs_dvsn is required. (e.g. '01')")
    if not sll_buy_dvsn_cd:
        logger.error("sll_buy_dvsn_cd is required. (e.g. '01')")
        raise ValueError("sll_buy_dvsn_cd is required. (e.g. '01')")
    if not fuop_dvsn:
        logger.error("fuop_dvsn is required. (e.g. '00')")
        raise ValueError("fuop_dvsn is required. (e.g. '00')")
    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    tr_id = "OTFM3116R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "CCLD_NCCS_DVSN": ccld_nccs_dvsn,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "FUOP_DVSN": fuop_dvsn,
        "CTX_AREA_FK200": ctx_area_fk200,
        "CTX_AREA_NK200": ctx_area_nk200,
    }

    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()
            
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data
            
        tr_cont = res.getHeader().tr_cont
        
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_ccld(
                cano,
                acnt_prdt_cd,
                ccld_nccs_dvsn,
                sll_buy_dvsn_cd,
                fuop_dvsn,
                ctx_area_fk200,
                ctx_area_nk200,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
