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
# [국내주식] 순위분석 > HTS조회상위20종목[국내주식-214]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/ranking/hts-top-view"


def hts_top_view(
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    HTS조회상위20종목[국내주식-214]
    HTS조회상위20종목 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        tr_cont (str): 연속 거래 여부 ("공백": 초기 조회, "N": 다음 데이터 조회)
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: HTS조회상위20종목 데이터
        
    Example:
        >>> df = hts_top_view(tr_cont="", dataframe=None, depth=0, max_depth=10)
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()


    tr_id = "HHMCM000100C0"

    # Request Query Parameter가 없으므로 빈 딕셔너리로 유지
    params = {}

    # API 호출
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
        if hasattr(res.getBody(), 'output1'):
            current_data = pd.DataFrame(res.getBody().output1)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 다음 페이지 호출 여부 결정
        tr_cont = res.getHeader().tr_cont
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return hts_top_view(
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 호출 실패 시 에러 로그 출력
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
