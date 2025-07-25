# [장내채권] 기본시세 - 장내채권 기본조회
# Generated by KIS API Generator (Single API Mode)
# -*- coding: utf-8 -*-
"""
Created on 2025-06-19

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
# [장내채권] 기본시세 > 장내채권 기본조회 [국내주식-129]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-bond/v1/quotations/search-bond-info"

def search_bond_info(
        pdno: str,  # 상품번호
        prdt_type_cd: str,  # 상품유형코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [장내채권] 기본시세 
    장내채권 기본조회[국내주식-129]
    장내채권 기본조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        pdno (str): 상품번호 (필수)
        prdt_type_cd (str): 상품유형코드 (필수)
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 장내채권 기본조회 데이터
        
    Example:
        >>> df = search_bond_info("KR2033022D33", "302")
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not pdno:
        logger.error("pdno is required. (e.g. 'KR2033022D33')")
        raise ValueError("pdno is required. (e.g. 'KR2033022D33')")

    if not prdt_type_cd:
        logger.error("prdt_type_cd is required. (e.g. '302')")
        raise ValueError("prdt_type_cd is required. (e.g. '302')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "CTPF1114R"

    params = {
        "PDNO": pdno,
        "PRDT_TYPE_CD": prdt_type_cd,
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

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return search_bond_info(
                pdno,
                prdt_type_cd,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
