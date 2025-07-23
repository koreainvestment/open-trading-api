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
# [국내주식] 업종/기타 > 국내업종 시간별지수(초)[국내주식-064]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-index-tickprice"

def inquire_index_tickprice(
        fid_input_iscd: str,  # 입력 종목코드
        fid_cond_mrkt_div_code: str,  # 시장 분류 코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 업종/기타 
    국내업종 시간별지수(초)[국내주식-064]
    국내업종 시간별지수(초) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_input_iscd (str): 0001:거래소, 1001:코스닥, 2001:코스피200, 3003:KSQ150
        fid_cond_mrkt_div_code (str): 시장구분코드 (업종 U)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내업종 시간별지수(초) 데이터
        
    Example:
        >>> df = inquire_index_tickprice('0001', 'U')
        >>> print(df)
    """
    # 필수 파라미터 검증
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


    tr_id = "FHPUP02110100"

    params = {
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
    }

    # API 호출
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
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
            return inquire_index_tickprice(
                fid_input_iscd,
                fid_cond_mrkt_div_code,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 에러 처리
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
