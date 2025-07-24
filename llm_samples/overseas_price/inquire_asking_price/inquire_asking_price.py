# -*- coding: utf-8 -*-
"""
Created on 2025-07-03

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
# [해외주식] 기본시세 > 해외주식 현재가 1호가[해외주식-033]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-price/v1/quotations/inquire-asking-price"

def inquire_asking_price(
    auth: str,  # 사용자권한정보
    excd: str,  # 거래소코드
    symb: str,  # 종목코드
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    dataframe3: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output3)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 기본시세 
    해외주식 현재가 1호가[해외주식-033]
    해외주식 현재가 1호가 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        auth (str): 사용자권한정보
        excd (str): 거래소코드 (예: NYS, NAS, AMS, 등)
        symb (str): 종목코드 (예: TSLA)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        dataframe3 (Optional[pd.DataFrame]): 누적 데이터프레임 (output3)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: 해외주식 현재가 1호가 데이터
        
    Example:
        >>> df1, df2, df3 = inquire_asking_price(auth="your_auth_token", excd="NAS", symb="TSLA")
        >>> print(df1)
        >>> print(df2)
        >>> print(df3)
    """
    # [필수 파라미터 검증]
    if not excd:
        logger.error("excd is required. (e.g. 'NAS')")
        raise ValueError("excd is required. (e.g. 'NAS')")
    if not symb:
        logger.error("symb is required. (e.g. 'TSLA')")
        raise ValueError("symb is required. (e.g. 'TSLA')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame(), dataframe3 if dataframe3 is not None else pd.DataFrame()
    
    tr_id = "HHDFS76200100"

    params = {
        "AUTH": auth,
        "EXCD": excd,
        "SYMB": symb,
    }

    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                if isinstance(output_data, list):
                    current_data1 = pd.DataFrame(output_data)
                else:
                    current_data1 = pd.DataFrame([output_data])
                
                if dataframe1 is not None:
                    dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
                else:
                    dataframe1 = current_data1
            else:
                if dataframe1 is None:
                    dataframe1 = pd.DataFrame()
        else:
            if dataframe1 is None:
                dataframe1 = pd.DataFrame()
        
        # output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                if isinstance(output_data, list):
                    current_data2 = pd.DataFrame(output_data)
                else:
                    current_data2 = pd.DataFrame([output_data])
                
                if dataframe2 is not None:
                    dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
                else:
                    dataframe2 = current_data2
            else:
                if dataframe2 is None:
                    dataframe2 = pd.DataFrame()
        else:
            if dataframe2 is None:
                dataframe2 = pd.DataFrame()
        
        # output3 처리
        if hasattr(res.getBody(), 'output3'):
            output_data = res.getBody().output3
            if output_data:
                if isinstance(output_data, list):
                    current_data3 = pd.DataFrame(output_data)
                else:
                    current_data3 = pd.DataFrame([output_data])
                
                if dataframe3 is not None:
                    dataframe3 = pd.concat([dataframe3, current_data3], ignore_index=True)
                else:
                    dataframe3 = current_data3
            else:
                if dataframe3 is None:
                    dataframe3 = pd.DataFrame()
        else:
            if dataframe3 is None:
                dataframe3 = pd.DataFrame()
        
        tr_cont = res.getHeader().tr_cont
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_asking_price(
                auth,
                excd,
                symb,
                "N", dataframe1, dataframe2, dataframe3, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2, dataframe3
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
