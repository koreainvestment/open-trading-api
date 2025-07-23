"""
Created on 2025-06-17

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
# [국내주식] 종목정보 > 예탁원정보(실권주일정)[국내주식-152]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/ksdinfo/forfeit"

def ksdinfo_forfeit(
    sht_cd: str,  # 종목코드
    t_dt: str,  # 조회일자To
    f_dt: str,  # 조회일자From
    cts: str,  # CTS
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    예탁원정보(실권주일정)[국내주식-152]
    예탁원정보(실권주일정) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        sht_cd (str): 공백: 전체, 특정종목 조회시 : 종목코드
        t_dt (str): ~ 일자
        f_dt (str): 일자 ~
        cts (str): 공백
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 예탁원정보(실권주일정) 데이터
        
    Example:
        >>> df = ksdinfo_forfeit("001440", "20240315", "20240314", " ")
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not t_dt:
        logger.error("t_dt is required. (e.g. '20240315')")
        raise ValueError("t_dt is required. (e.g. '20240315')")
    
    if not f_dt:
        logger.error("f_dt is required. (e.g. '20240314')")
        raise ValueError("f_dt is required. (e.g. '20240314')")
    

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    

    tr_id = "HHKDB669109C0"

    params = {
        "SHT_CD": sht_cd,
        "T_DT": t_dt,
        "F_DT": f_dt,
        "CTS": cts,
    }

    # API 호출
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
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
            return ksdinfo_forfeit(
                sht_cd,
                t_dt,
                f_dt,
                cts,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
