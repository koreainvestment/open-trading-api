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
# [국내주식] 기본시세 > 변동성완화장치(VI) 현황[v1_국내주식-055]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-vi-status"

def inquire_vi_status(
        fid_div_cls_code: str,  # FID 분류 구분 코드
        fid_cond_scr_div_code: str,  # FID 조건 화면 분류 코드
        fid_mrkt_cls_code: str,  # FID 시장 구분 코드
        fid_input_iscd: str,  # FID 입력 종목코드
        fid_rank_sort_cls_code: str,  # FID 순위 정렬 구분 코드
        fid_input_date_1: str,  # FID 입력 날짜1
        fid_trgt_cls_code: str,  # FID 대상 구분 코드
        fid_trgt_exls_cls_code: str,  # FID 대상 제외 구분 코드
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 업종/기타 
    변동성완화장치(VI) 현황[v1_국내주식-055]
    변동성완화장치(VI) 현황 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_div_cls_code (str): 0:전체 1:상승 2:하락
        fid_cond_scr_div_code (str): 20139
        fid_mrkt_cls_code (str): 0:전체 K:거래소 Q:코스닥
        fid_input_iscd (str): 종목코드
        fid_rank_sort_cls_code (str): 0:전체 1:정적 2:동적 3:정적&동적
        fid_input_date_1 (str): 영업일
        fid_trgt_cls_code (str): 대상 구분 코드
        fid_trgt_exls_cls_code (str): 대상 제외 구분 코드
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 변동성완화장치(VI) 현황 데이터
        
    Example:
        >>> df = inquire_vi_status(
        ...     fid_div_cls_code="0",
        ...     fid_cond_scr_div_code="20139",
        ...     fid_mrkt_cls_code="0",
        ...     fid_input_iscd="005930",
        ...     fid_rank_sort_cls_code="0",
        ...     fid_input_date_1="20240126",
        ...     fid_trgt_cls_code="",
        ...     fid_trgt_exls_cls_code=""
        ... )
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증 (첨부된 사진 기준, 비어있으면 빼고 체크)
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20139')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20139')")

    if not fid_mrkt_cls_code:
        logger.error("fid_mrkt_cls_code is required. (e.g. '0')")
        raise ValueError("fid_mrkt_cls_code is required. (e.g. '0')")

    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '0')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '0')")

    if not fid_input_date_1:
        logger.error("fid_input_date_1 is required. (e.g. '20200420')")
        raise ValueError("fid_input_date_1 is required. (e.g. '20200420')")

    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()


    tr_id = "FHPST01390000"

    params = {
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_MRKT_CLS_CODE": fid_mrkt_cls_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_TRGT_CLS_CODE": fid_trgt_cls_code,
        "FID_TRGT_EXLS_CLS_CODE": fid_trgt_exls_cls_code,
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
            return inquire_vi_status(
                fid_div_cls_code,
                fid_cond_scr_div_code,
                fid_mrkt_cls_code,
                fid_input_iscd,
                fid_rank_sort_cls_code,
                fid_input_date_1,
                fid_trgt_cls_code,
                fid_trgt_exls_cls_code,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
