# -*- coding: utf-8 -*-
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
# [국내주식] ELW시세 - ELW 투자지표추이(분별)[국내주식-174]
##############################################################################################

# 상수 정의
API_URL = "/uapi/elw/v1/quotations/indicator-trend-minute"

def indicator_trend_minute(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_input_iscd: str,  # 입력종목코드
    fid_hour_cls_code: str,  # 시간구분코드
    fid_pw_data_incu_yn: str,  # 과거데이터 포함 여부
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 투자지표추이(분별)[국내주식-174]
    ELW 투자지표추이(분별) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 시장구분코드 (W)
        fid_input_iscd (str): 입력종목코드 예시: 58J297(KBJ297삼성전자콜)
        fid_hour_cls_code (str): 시간구분코드 예시: '60(1분), 180(3분), 300(5분), 600(10분), 1800(30분), 3600(60분), 7200(60분)'
        fid_pw_data_incu_yn (str): 과거데이터 포함 여부 예시: N(과거데이터포함X), Y(과거데이터포함O)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 투자지표추이(분별) 데이터
        
    Example:
        >>> df = indicator_trend_minute(
        ...     fid_cond_mrkt_div_code='W',
        ...     fid_input_iscd='58J297',
        ...     fid_hour_cls_code='60',
        ...     fid_pw_data_incu_yn='N'
        ... )
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '58J297')")
        raise ValueError("fid_input_iscd is required. (e.g. '58J297')")

    if not fid_hour_cls_code:
        logger.error("fid_hour_cls_code is required. (e.g. '60')")
        raise ValueError("fid_hour_cls_code is required. (e.g. '60')")

    if not fid_pw_data_incu_yn:
        logger.error("fid_pw_data_incu_yn is required. (e.g. 'N')")
        raise ValueError("fid_pw_data_incu_yn is required. (e.g. 'N')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # API 호출 URL 및 거래 ID 설정
    url = API_URL
    tr_id = "FHPEW02740300"

    # 요청 파라미터 설정
    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_HOUR_CLS_CODE": fid_hour_cls_code,
        "FID_PW_DATA_INCU_YN": fid_pw_data_incu_yn,
    }

    # API 호출
    res = ka._url_fetch(url, tr_id, tr_cont, params)

    # API 호출 성공 여부 확인
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
            return indicator_trend_minute(
                fid_cond_mrkt_div_code,
                fid_input_iscd,
                fid_hour_cls_code,
                fid_pw_data_incu_yn,
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
