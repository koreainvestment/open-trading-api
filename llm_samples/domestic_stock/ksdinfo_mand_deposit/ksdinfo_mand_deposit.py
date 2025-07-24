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
# [국내주식] 종목정보 > 예탁원정보(의무예치일정) [국내주식-153]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/ksdinfo/mand-deposit"

def ksdinfo_mand_deposit(
        t_dt: str,  # 조회일자To
        sht_cd: str,  # 종목코드
        f_dt: str,  # 조회일자From
        cts: str,  # CTS
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    예탁원정보(의무예치일정)[국내주식-153]
    예탁원정보(의무예치일정) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        t_dt (str): 조회 종료 일자 (예: '20230301')
        sht_cd (str): 종목코드 (공백: 전체, 특정종목 조회시 : 종목코드)
        f_dt (str): 조회 시작 일자 (예: '20230101')
        cts (str): CTS (공백)
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 예탁원정보(의무예치일정) 데이터
        
    Example:
        >>> df = ksdinfo_mand_deposit('20230301', '005930', '20230101', '')
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not t_dt:
        logger.error("t_dt is required. (e.g. '20230301')")
        raise ValueError("t_dt is required. (e.g. '20230301')")

    if not f_dt:
        logger.error("f_dt is required. (e.g. '20230101')")
        raise ValueError("f_dt is required. (e.g. '20230101')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # API 호출 URL 및 거래 ID 설정

    tr_id = "HHKDB669110C0"

    # 요청 파라미터 설정
    params = {
        "T_DT": t_dt,
        "SHT_CD": sht_cd,
        "F_DT": f_dt,
        "CTS": cts,
    }

    # API 호출
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    # API 호출 성공 시 데이터 처리
    if res.isOK():
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        # 기존 데이터프레임과 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        # 다음 페이지 호출
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return ksdinfo_mand_deposit(
                t_dt,
                sht_cd,
                f_dt,
                cts,
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
