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
# [국내주식] ELW시세 - ELW 당일급변종목[국내주식-171]
##############################################################################################

# 상수 정의
API_URL = "/uapi/elw/v1/ranking/quick-change"

def quick_change(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_cond_scr_div_code: str,  # 조건화면분류코드
    fid_unas_input_iscd: str,  # 기초자산입력종목코드
    fid_input_iscd: str,  # 발행사
    fid_mrkt_cls_code: str,  # 시장구분코드
    fid_input_price_1: str,  # 가격(이상)
    fid_input_price_2: str,  # 가격(이하)
    fid_input_vol_1: str,  # 거래량(이상)
    fid_input_vol_2: str,  # 거래량(이하)
    fid_hour_cls_code: str,  # 시간구분코드
    fid_input_hour_1: str,  # 입력 일 또는 분
    fid_input_hour_2: str,  # 기준시간(분 선택 시)
    fid_rank_sort_cls_code: str,  # 순위정렬구분코드
    fid_blng_cls_code: str,  # 결재방법
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 당일급변종목[국내주식-171]
    ELW 당일급변종목 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건시장분류코드 (필수)
        fid_cond_scr_div_code (str): 조건화면분류코드 (필수)
        fid_unas_input_iscd (str): 기초자산입력종목코드 (필수)
        fid_input_iscd (str): 발행사 (필수)
        fid_mrkt_cls_code (str): 시장구분코드 (필수)
        fid_input_price_1 (str): 가격(이상) (필수)
        fid_input_price_2 (str): 가격(이하) (필수)
        fid_input_vol_1 (str): 거래량(이상) (필수)
        fid_input_vol_2 (str): 거래량(이하) (필수)
        fid_hour_cls_code (str): 시간구분코드 (필수)
        fid_input_hour_1 (str): 입력 일 또는 분 (필수)
        fid_input_hour_2 (str): 기준시간(분 선택 시) (필수)
        fid_rank_sort_cls_code (str): 순위정렬구분코드 (필수)
        fid_blng_cls_code (str): 결재방법 (필수)
        tr_cont (str): 연속 거래 여부 (옵션)
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (옵션)
        depth (int): 현재 재귀 깊이 (옵션)
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 당일급변종목 데이터
        
    Example:
        >>> df = quick_change(
        ...     fid_cond_mrkt_div_code='W',
        ...     fid_cond_scr_div_code='20287',
        ...     fid_unas_input_iscd='000000',
        ...     fid_input_iscd='00000',
        ...     fid_mrkt_cls_code='A',
        ...     fid_input_price_1='1000',
        ...     fid_input_price_2='5000',
        ...     fid_input_vol_1='10000',
        ...     fid_input_vol_2='50000',
        ...     fid_hour_cls_code='1',
        ...     fid_input_hour_1='10',
        ...     fid_input_hour_2='30',
        ...     fid_rank_sort_cls_code='1',
        ...     fid_blng_cls_code='0'
        ... )
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20287')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20287')")
    if not fid_unas_input_iscd:
        logger.error("fid_unas_input_iscd is required. (e.g. '000000')")
        raise ValueError("fid_unas_input_iscd is required. (e.g. '000000')")
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '00000')")
        raise ValueError("fid_input_iscd is required. (e.g. '00000')")
    if not fid_mrkt_cls_code:
        logger.error("fid_mrkt_cls_code is required. (e.g. 'A')")
        raise ValueError("fid_mrkt_cls_code is required. (e.g. 'A')")
    if not fid_hour_cls_code:
        logger.error("fid_hour_cls_code is required. (e.g. '1')")
        raise ValueError("fid_hour_cls_code is required. (e.g. '1')")
    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '1')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '1')")
    if not fid_blng_cls_code:
        logger.error("fid_blng_cls_code is required. (e.g. '0')")
        raise ValueError("fid_blng_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHPEW02870000"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_UNAS_INPUT_ISCD": fid_unas_input_iscd,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_MRKT_CLS_CODE": fid_mrkt_cls_code,
        "FID_INPUT_PRICE_1": fid_input_price_1,
        "FID_INPUT_PRICE_2": fid_input_price_2,
        "FID_INPUT_VOL_1": fid_input_vol_1,
        "FID_INPUT_VOL_2": fid_input_vol_2,
        "FID_HOUR_CLS_CODE": fid_hour_cls_code,
        "FID_INPUT_HOUR_1": fid_input_hour_1,
        "FID_INPUT_HOUR_2": fid_input_hour_2,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_BLNG_CLS_CODE": fid_blng_cls_code,
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
            return quick_change(
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_unas_input_iscd,
                fid_input_iscd,
                fid_mrkt_cls_code,
                fid_input_price_1,
                fid_input_price_2,
                fid_input_vol_1,
                fid_input_vol_2,
                fid_hour_cls_code,
                fid_input_hour_1,
                fid_input_hour_2,
                fid_rank_sort_cls_code,
                fid_blng_cls_code,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
