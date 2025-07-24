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
# [국내주식] 업종/기타 > 국내주식 예상체결 전체지수[국내주식-122]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/exp-total-index"


def exp_total_index(
        fid_mrkt_cls_code: str,  # 시장 구분 코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_mkop_cls_code: str,  # 장운영 구분 코드
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        tr_cont: str = "",
        depth: int = 0,
        max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 업종/기타 
    국내주식 예상체결 전체지수[국내주식-122]
    국내주식 예상체결 전체지수 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_mrkt_cls_code (str): 0:전체 K:거래소 Q:코스닥
        fid_cond_mrkt_div_code (str): 시장구분코드 (업종 U)
        fid_cond_scr_div_code (str): Unique key(11175)
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100
        fid_mkop_cls_code (str): 1:장시작전, 2:장마감
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 국내주식 예상체결 전체지수 데이터
        
    Example:
        >>> df1, df2 = exp_total_index(
        ...     fid_mrkt_cls_code="K",
        ...     fid_cond_mrkt_div_code="U",
        ...     fid_cond_scr_div_code="11175",
        ...     fid_input_iscd="1001",
        ...     fid_mkop_cls_code="1"
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_mrkt_cls_code:
        logger.error("fid_mrkt_cls_code is required. (e.g. 'K')")
        raise ValueError("fid_mrkt_cls_code is required. (e.g. 'K')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'U')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'U')")

    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '11175')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '11175')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '1001')")
        raise ValueError("fid_input_iscd is required. (e.g. '1001')")

    if not fid_mkop_cls_code:
        logger.error("fid_mkop_cls_code is required. (e.g. '1')")
        raise ValueError("fid_mkop_cls_code is required. (e.g. '1')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()


    tr_id = "FHKUP11750000"

    params = {
        "fid_mrkt_cls_code": fid_mrkt_cls_code,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_input_iscd": fid_input_iscd,
        "fid_mkop_cls_code": fid_mkop_cls_code,
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
                dataframe1 = pd.DataFrame() if dataframe1 is None else dataframe1
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
        else:
            dataframe2 = pd.DataFrame() if dataframe2 is None else dataframe2

        tr_cont = res.getHeader().tr_cont

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return exp_total_index(
                fid_mrkt_cls_code,
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_mkop_cls_code,
                "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame(), pd.DataFrame()
