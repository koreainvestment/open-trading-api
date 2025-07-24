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

# 상수 정의
API_URL = "/uapi/overseas-futureoption/v1/quotations/search-contract-detail"

##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물 상품기본정보[해외선물-023]
##############################################################################################

def search_contract_detail(
    qry_cnt: str,  # 요청개수
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10,
    **kwargs  # srs_cd_01, srs_cd_02, ... srs_cd_32 등을 받음
) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 기본시세 
    해외선물 상품기본정보[해외선물-023]
    해외선물 상품기본정보 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        qry_cnt (str): 입력한 코드 개수
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        **kwargs: srs_cd_01, srs_cd_02, ... srs_cd_32 품목종류 코드들
        
    Returns:
        Optional[pd.DataFrame]: 해외선물 상품기본정보 데이터
        
    Example:
        >>> df = search_contract_detail(
        ...     qry_cnt="3",
        ...     srs_cd_01="SRS001",
        ...     srs_cd_02="SRS002",
        ...     srs_cd_03="SRS003"
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not 1 <= int(qry_cnt) <= 32:
        logger.error("qry_cnt is required. (e.g. '1' ~ '32')")
        raise ValueError("qry_cnt is required. (e.g. '1' ~ '32')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    tr_id = "HHDFC55200000"

    # 기본 파라미터
    params = {
        "QRY_CNT": qry_cnt,
    }
    
    # SRS_CD_01 ~ SRS_CD_32 파라미터 동적 생성
    for i in range(1, 33):
        srs_key = f"srs_cd_{i:02d}"
        api_key = f"SRS_CD_{i:02d}"
        params[api_key] = kwargs.get(srs_key, "")

    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
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
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return search_contract_detail(
                qry_cnt, "N", dataframe, depth + 1, max_depth, **kwargs
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
