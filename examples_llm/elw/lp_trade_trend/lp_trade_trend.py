# -*- coding: utf-8 -*-
"""
Created on 2025-06-18

@author: LaivData jjlee with cursor
"""

import logging
import time
from typing import Optional, Tuple
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] ELW시세 - ELW LP매매추이[국내주식-182]
##############################################################################################

# 상수 정의
API_URL = "/uapi/elw/v1/quotations/lp-trade-trend"

def lp_trade_trend(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_input_iscd: str,  # 입력종목코드
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    [국내주식] ELW시세 
    ELW LP매매추이[국내주식-182]
    ELW LP매매추이 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 시장구분(W)
        fid_input_iscd (str): 입력종목코드(ex 52K577(미래 K577KOSDAQ150콜)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: ELW LP매매추이 데이터
        
    Example:
        >>> df1, df2 = lp_trade_trend("W", "52K577")
        >>> print(df1)
        >>> print(df2)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")
    
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '52K577')")
        raise ValueError("fid_input_iscd is required. (e.g. '52K577')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    tr_id = "FHPEW03760000"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
    }

    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                current_data1 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True) if dataframe1 is not None else current_data1
            else:
                dataframe1 = dataframe1 if dataframe1 is not None else pd.DataFrame()
        else:
            dataframe1 = dataframe1 if dataframe1 is not None else pd.DataFrame()

        # output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                current_data2 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True) if dataframe2 is not None else current_data2
            else:
                dataframe2 = dataframe2 if dataframe2 is not None else pd.DataFrame()
        else:
            dataframe2 = dataframe2 if dataframe2 is not None else pd.DataFrame()

        tr_cont = res.getHeader().tr_cont
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return lp_trade_trend(
                fid_cond_mrkt_div_code,
                fid_input_iscd,
                "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame(), pd.DataFrame()
