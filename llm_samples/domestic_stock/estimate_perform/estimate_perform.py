"""
Created on 2025-06-17

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
# [국내주식] 종목정보 > 국내주식 종목추정실적[국내주식-187]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/estimate-perform"

def estimate_perform(
        sht_cd: str,  # 종목코드
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        dataframe3: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output3)
        dataframe4: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output4)
        tr_cont: str = "",
        depth: int = 0,
        max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 종목정보 
    국내주식 종목추정실적[국내주식-187]
    국내주식 종목추정실적 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        sht_cd (str): 종목코드 (예: 265520)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        dataframe3 (Optional[pd.DataFrame]): 누적 데이터프레임 (output3)
        dataframe4 (Optional[pd.DataFrame]): 누적 데이터프레임 (output4)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]: 국내주식 종목추정실적 데이터
        
    Example:
        >>> df1, df2, df3, df4 = estimate_perform("265520")
        >>> print(df1)
        >>> print(df2)
    """
    # 필수 파라미터 검증
    if not sht_cd:
        logger.error("sht_cd is required. (e.g. '265520')")
        raise ValueError("sht_cd is required. (e.g. '265520')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return (
            dataframe1 if dataframe1 is not None else pd.DataFrame(),
            dataframe2 if dataframe2 is not None else pd.DataFrame(),
            dataframe3 if dataframe3 is not None else pd.DataFrame(),
            dataframe4 if dataframe4 is not None else pd.DataFrame()
        )

    tr_id = "HHKST668300C0"

    params = {
        "SHT_CD": sht_cd,
    }

    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                current_data1 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe1 = pd.concat([dataframe1, current_data1],
                                       ignore_index=True) if dataframe1 is not None else current_data1
            else:
                dataframe1 = pd.DataFrame() if dataframe1 is None else dataframe1

        # output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                current_data2 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe2 = pd.concat([dataframe2, current_data2],
                                       ignore_index=True) if dataframe2 is not None else current_data2
            else:
                dataframe2 = pd.DataFrame() if dataframe2 is None else dataframe2

        # output3 처리
        if hasattr(res.getBody(), 'output3'):
            output_data = res.getBody().output3
            if output_data:
                current_data3 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe3 = pd.concat([dataframe3, current_data3],
                                       ignore_index=True) if dataframe3 is not None else current_data3
            else:
                dataframe3 = pd.DataFrame() if dataframe3 is None else dataframe3

        # output4 처리
        if hasattr(res.getBody(), 'output4'):
            output_data = res.getBody().output4
            if output_data:
                current_data4 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe4 = pd.concat([dataframe4, current_data4],
                                       ignore_index=True) if dataframe4 is not None else current_data4
            else:
                dataframe4 = pd.DataFrame() if dataframe4 is None else dataframe4

        tr_cont = res.getHeader().tr_cont

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return estimate_perform(
                sht_cd, dataframe1, dataframe2, dataframe3, dataframe4, "N", depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2, dataframe3, dataframe4
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
