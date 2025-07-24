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
# [해외선물옵션] 주문/계좌 > 해외선물옵션 증거금상세 [해외선물-032]
##############################################################################################

# API 정보
API_URL = "/uapi/overseas-futureoption/v1/trading/margin-detail"

def margin_detail(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    crcy_cd: str,  # 통화코드
    inqr_dt: str,  # 조회일자
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 주문/계좌 
    해외선물옵션 증거금상세[해외선물-032]
    해외선물옵션 증거금상세 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 종합계좌번호 (8자리)
        acnt_prdt_cd (str): 계좌상품코드 (2자리)
        crcy_cd (str): 통화코드 ('TKR', 'TUS', 'USD', 'HKD', 'CNY', 'JPY', 'VND')
        inqr_dt (str): 조회일자 (8자리, YYYYMMDD 형식)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외선물옵션 증거금상세 데이터
        
    Example:
        >>> df = margin_detail(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     crcy_cd="USD",
        ...     inqr_dt="20230701"
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '12345678')")
        raise ValueError("cano is required. (e.g. '12345678')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")
    if not crcy_cd:
        logger.error("crcy_cd is required. (e.g. 'USD')")
        raise ValueError("crcy_cd is required. (e.g. 'USD')")
    if not inqr_dt:
        logger.error("inqr_dt is required. (e.g. '20230701')")
        raise ValueError("inqr_dt is required. (e.g. '20230701')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    tr_id = "OTFM3115R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "CRCY_CD": crcy_cd,
        "INQR_DT": inqr_dt,
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
            return margin_detail(
                cano,
                acnt_prdt_cd,
                crcy_cd,
                inqr_dt,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
