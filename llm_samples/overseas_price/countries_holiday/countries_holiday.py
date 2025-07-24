# -*- coding: utf-8 -*-
"""
Created on 2025-06-26

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
# [해외주식] 기본시세 > 해외결제일자조회[해외주식-017]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-stock/v1/quotations/countries-holiday"

def countries_holiday(
    trad_dt: str,  # 기준일자
    NK: str = "",  # 연속조회키
    FK: str = "",  # 연속조회검색조건
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [해외주식] 기본시세 
    해외결제일자조회[해외주식-017]
    해외결제일자조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        trad_dt (str): 기준일자(YYYYMMDD)
        ctx_area_nk (str): 공백으로 입력
        ctx_area_fk (str): 공백으로 입력
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외결제일자조회 데이터
        
    Example:
        >>> df = countries_holiday("20250131", "", "")
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not trad_dt:
        logger.error("trad_dt is required. (e.g. '20250131')")
        raise ValueError("trad_dt is required. (e.g. '20250131')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    tr_id = "CTOS5011R"

    params = {
        "TRAD_DT": trad_dt,
        "CTX_AREA_NK": NK,
        "CTX_AREA_FK": FK,
    }

    # API 호출
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()
        
        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data
        
        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont
        NK = res.getBody().ctx_area_nk
        FK = res.getBody().ctx_area_fk
        
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return countries_holiday(
                trad_dt,
                NK,
                FK,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
