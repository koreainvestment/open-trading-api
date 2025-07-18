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
# [국내주식] 업종/기타 > 국내업종 시간별지수(분)[국내주식-119]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-index-timeprice"

def inquire_index_timeprice(
        fid_input_hour_1: str,  # ?입력 시간1
        fid_input_iscd: str,  # 입력 종목코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 업종/기타 
    국내업종 시간별지수(분)[국내주식-119]
    국내업종 시간별지수(분) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_input_hour_1 (str): 초단위, 60(1분), 300(5분), 600(10분)
        fid_input_iscd (str): 0001:거래소, 1001:코스닥, 2001:코스피200, 3003:KSQ150
        fid_cond_mrkt_div_code (str): 시장구분코드 (업종 U)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내업종 시간별지수(분) 데이터
        
    Example:
        >>> df = inquire_index_timeprice("60", "0001", "U")
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not fid_input_hour_1:
        logger.error("fid_input_hour_1 is required. (e.g. '60')")
        raise ValueError("fid_input_hour_1 is required. (e.g. '60')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0001')")
        raise ValueError("fid_input_iscd is required. (e.g. '0001')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'U')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'U')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()


    tr_id = "FHPUP02110200"

    params = {
        "FID_INPUT_HOUR_1": fid_input_hour_1,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
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
            return inquire_index_timeprice(
                fid_input_hour_1,
                fid_input_iscd,
                fid_cond_mrkt_div_code,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
