"""
Created on 2025-06-18

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
# [국내주식] ELW시세 - ELW 비교대상종목조회[국내주식-183]
##############################################################################################

# 상수 정의
API_URL = "/uapi/elw/v1/quotations/compare-stocks"

def compare_stocks(
    fid_cond_scr_div_code: str,  # 조건화면분류코드
    fid_input_iscd: str,  # 입력종목코드
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 비교대상종목조회[국내주식-183]
    ELW 비교대상종목조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_scr_div_code (str): 조건화면분류코드 (예: '11517')
        fid_input_iscd (str): 입력종목코드 (예: '005930')
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (기본값: None)
        depth (int): 현재 재귀 깊이 (기본값: 0)
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 비교대상종목조회 데이터
        
    Example:
        >>> df = compare_stocks('11517', '005930')
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '11517')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '11517')")
    
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '005930')")
        raise ValueError("fid_input_iscd is required. (e.g. '005930')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHKEW151701C0"

    params = {
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
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
        
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return compare_stocks(
                fid_cond_scr_div_code,
                fid_input_iscd,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
