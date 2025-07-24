"""
Created on 2025-06-16

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
# [국내주식] 순위분석 > 국내주식 배당률 상위[국내주식-106]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/ranking/dividend-rate"

def dividend_rate(
        cts_area: str,  # CTS_AREA
        gb1: str,  # KOSPI
        upjong: str,  # 업종구분
        gb2: str,  # 종목선택
        gb3: str,  # 배당구분
        f_dt: str,  # 기준일From
        t_dt: str,  # 기준일To
        gb4: str,  # 결산/중간배당
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 배당률 상위[국내주식-106]
    국내주식 배당률 상위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cts_area (str): 공백
        gb1 (str): 0:전체, 1:코스피,  2: 코스피200, 3: 코스닥,
        upjong (str): '코스피(0001:종합, 0002:대형주.…0027:제조업 ),  코스닥(1001:종합, …. 1041:IT부품 코스피200 (2001:KOSPI200, 2007:KOSPI100, 2008:KOSPI50)'
        gb2 (str): 0:전체, 6:보통주, 7:우선주
        gb3 (str): 1:주식배당, 2: 현금배당
        f_dt (str): 기준일 시작
        t_dt (str): 기준일 종료
        gb4 (str): 0:전체, 1:결산배당, 2:중간배당
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 배당률 상위 데이터
        
    Example:
        >>> df = dividend_rate(
        ...     cts_area=" ",
        ...     gb1="1",
        ...     upjong="0001",
        ...     gb2="0",
        ...     gb3="1",
        ...     f_dt="20230101",
        ...     t_dt="20231231",
        ...     gb4="0"
        ... )
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not gb1:
        logger.error("gb1 is required. (e.g. '1')")
        raise ValueError("gb1 is required. (e.g. '1')")

    if not upjong:
        logger.error("upjong is required. (e.g. '0001')")
        raise ValueError("upjong is required. (e.g. '0001')")

    if not gb2:
        logger.error("gb2 is required. (e.g. '0')")
        raise ValueError("gb2 is required. (e.g. '0')")

    if not gb3:
        logger.error("gb3 is required. (e.g. '1')")
        raise ValueError("gb3 is required. (e.g. '1')")

    if not f_dt:
        logger.error("f_dt is required. (e.g. '20230101')")
        raise ValueError("f_dt is required. (e.g. '20230101')")

    if not t_dt:
        logger.error("t_dt is required. (e.g. '20231231')")
        raise ValueError("t_dt is required. (e.g. '20231231')")

    if not gb4:
        logger.error("gb4 is required. (e.g. '0')")
        raise ValueError("gb4 is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()


    tr_id = "HHKDB13470100"

    params = {
        "CTS_AREA": cts_area,
        "GB1": gb1,
        "UPJONG": upjong,
        "GB2": gb2,
        "GB3": gb3,
        "F_DT": f_dt,
        "T_DT": t_dt,
        "GB4": gb4,
    }

    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
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
            return dividend_rate(
                cts_area,
                gb1,
                upjong,
                gb2,
                gb3,
                f_dt,
                t_dt,
                gb4,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
