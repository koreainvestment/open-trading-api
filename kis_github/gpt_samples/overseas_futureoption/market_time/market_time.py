# -*- coding: utf-8 -*-
"""
Created on 2025-07-01

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
# [해외선물옵션] 기본시세 > 해외선물옵션 장운영시간 [해외선물-030]
##############################################################################################

# API 정보
API_URL = "/uapi/overseas-futureoption/v1/quotations/market-time"

def market_time(
    fm_pdgr_cd: str,  # FM상품군코드
    fm_clas_cd: str,  # FM클래스코드
    fm_excg_cd: str,  # FM거래소코드
    opt_yn: str,  # 옵션여부
    ctx_area_nk200: str,  # 연속조회키200
    ctx_area_fk200: str,  # 연속조회검색조건200
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 기본시세 
    해외선물옵션 장운영시간[해외선물-030]
    해외선물옵션 장운영시간 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fm_pdgr_cd (str): FM상품군코드
        fm_clas_cd (str): FM클래스코드
        fm_excg_cd (str): FM거래소코드
        opt_yn (str): 옵션여부
        ctx_area_nk200 (str): 연속조회키200
        ctx_area_fk200 (str): 연속조회검색조건200
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외선물옵션 장운영시간 데이터
        
    Example:
        >>> df = market_time(
        ...     fm_pdgr_cd="001",
        ...     fm_clas_cd="003",
        ...     fm_excg_cd="CME",
        ...     opt_yn="N",
        ...     ctx_area_nk200="",
        ...     ctx_area_fk200=""
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not fm_excg_cd:
        logger.error("fm_excg_cd is required. (e.g. 'CME')")
        raise ValueError("fm_excg_cd is required. (e.g. 'CME')")
    if not opt_yn:
        logger.error("opt_yn is required. (e.g. 'N')")
        raise ValueError("opt_yn is required. (e.g. 'N')")
    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    tr_id = "OTFM2229R"

    params = {
        "FM_PDGR_CD": fm_pdgr_cd,
        "FM_CLAS_CD": fm_clas_cd,
        "FM_EXCG_CD": fm_excg_cd,
        "OPT_YN": opt_yn,
        "CTX_AREA_NK200": ctx_area_nk200,
        "CTX_AREA_FK200": ctx_area_fk200,
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
            
        tr_cont, ctx_area_nk200, ctx_area_fk200 = res.getHeader().tr_cont, res.getBody().ctx_area_nk200, res.getBody().ctx_area_fk200
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return market_time(
                fm_pdgr_cd,
                fm_clas_cd,
                fm_excg_cd,
                opt_yn,
                ctx_area_nk200,
                ctx_area_fk200,
                "N",
                dataframe,
                depth + 1,
                max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
