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
# [국내주식] 종목정보 > 예탁원정보(합병_분할일정)[국내주식-147]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/ksdinfo/merger-split"

def ksdinfo_merger_split(
        cts: str,  # CTS
        f_dt: str,  # 조회일자From
        t_dt: str,  # 조회일자To
        sht_cd: str,  # 종목코드
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    예탁원정보(합병_분할일정)[국내주식-147]
    예탁원정보(합병_분할일정) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cts (str): 공백
        f_dt (str): 일자 ~
        t_dt (str): ~ 일자
        sht_cd (str): 공백: 전체, 특정종목 조회시 : 종목코드
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 예탁원정보(합병_분할일정) 데이터
        
    Example:
        >>> df = ksdinfo_merger_split(" ", "20230101", "20231231", "005930")
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not f_dt:
        logger.error("f_dt is required. (e.g. '20230101')")
        raise ValueError("f_dt is required. (e.g. '20230101')")

    if not t_dt:
        logger.error("t_dt is required. (e.g. '20231231')")
        raise ValueError("t_dt is required. (e.g. '20231231')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()


    tr_id = "HHKDB669104C0"

    params = {
        "CTS": cts,
        "F_DT": f_dt,
        "T_DT": t_dt,
        "SHT_CD": sht_cd,
    }

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

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return ksdinfo_merger_split(
                cts,
                f_dt,
                t_dt,
                sht_cd,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 호출 실패 시 에러 로그
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
