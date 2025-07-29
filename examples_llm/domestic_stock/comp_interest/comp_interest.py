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
# [국내주식] 업종/기타 > 금리 종합(국내채권_금리)[국내주식-155]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/comp-interest"

def comp_interest(
        fid_cond_mrkt_div_code: str,  # 조건시장분류코드
        fid_cond_scr_div_code: str,  # 조건화면분류코드
        fid_div_cls_code: str,  # 분류구분코드
        fid_div_cls_code1: str,  # 분류구분코드
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        tr_cont: str = "",
        depth: int = 0,
        max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 업종/기타 
    금리 종합(국내채권_금리)[국내주식-155]
    금리 종합(국내채권_금리) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건시장분류코드 (필수)
        fid_cond_scr_div_code (str): 조건화면분류코드 (필수)
        fid_div_cls_code (str): 분류구분코드 (필수)
        fid_div_cls_code1 (str): 분류구분코드 (공백 허용)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 금리 종합(국내채권_금리) 데이터
        
    Example:
        >>> df1, df2 = comp_interest('01', '20702', '1', '')
        >>> print(df1)
        >>> print(df2)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. '01')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. '01')")

    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20702')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20702')")

    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '1')")
        raise ValueError("fid_div_cls_code is required. (e.g. '1')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()


    tr_id = "FHPST07020000"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_DIV_CLS_CODE1": fid_div_cls_code1,
    }

    # API 호출
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
                dataframe1 = dataframe1 if dataframe1 is not None else pd.DataFrame()

        # output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                current_data2 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe2 = pd.concat([dataframe2, current_data2],
                                       ignore_index=True) if dataframe2 is not None else current_data2
            else:
                dataframe2 = dataframe2 if dataframe2 is not None else pd.DataFrame()

        tr_cont = res.getHeader().tr_cont

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return comp_interest(
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_div_cls_code,
                fid_div_cls_code1,
                "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame(), pd.DataFrame()
