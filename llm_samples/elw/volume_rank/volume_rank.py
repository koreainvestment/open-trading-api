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
# [국내주식] ELW시세 - ELW 거래량순위[국내주식-168]
##############################################################################################

# 상수 정의
API_URL = "/uapi/elw/v1/ranking/volume-rank"

def volume_rank(
        fid_cond_mrkt_div_code: str,  # 조건시장분류코드
        fid_cond_scr_div_code: str,  # 조건화면분류코드
        fid_unas_input_iscd: str,  # 기초자산입력종목코드
        fid_input_iscd: str,  # 발행사
        fid_input_rmnn_dynu_1: str,  # 입력잔존일수
        fid_div_cls_code: str,  # 콜풋구분코드
        fid_input_price_1: str,  # 가격(이상)
        fid_input_price_2: str,  # 가격(이하)
        fid_input_vol_1: str,  # 거래량(이상)
        fid_input_vol_2: str,  # 거래량(이하)
        fid_input_date_1: str,  # 조회기준일
        fid_rank_sort_cls_code: str,  # 순위정렬구분코드
        fid_blng_cls_code: str,  # 소속구분코드
        fid_input_iscd_2: str,  # LP발행사
        fid_input_date_2: str,  # 만기일-최종거래일조회
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 거래량순위[국내주식-168]
    ELW 거래량순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건시장분류코드 (예: 'W')
        fid_cond_scr_div_code (str): 조건화면분류코드 (예: '20278')
        fid_unas_input_iscd (str): 기초자산입력종목코드 (예: '000000')
        fid_input_iscd (str): 발행사 (예: '00000')
        fid_input_rmnn_dynu_1 (str): 입력잔존일수
        fid_div_cls_code (str): 콜풋구분코드 (예: '0')
        fid_input_price_1 (str): 가격(이상)
        fid_input_price_2 (str): 가격(이하)
        fid_input_vol_1 (str): 거래량(이상)
        fid_input_vol_2 (str): 거래량(이하)
        fid_input_date_1 (str): 조회기준일
        fid_rank_sort_cls_code (str): 순위정렬구분코드 (예: '0')
        fid_blng_cls_code (str): 소속구분코드 (예: '0')
        fid_input_iscd_2 (str): LP발행사 (예: '0000')
        fid_input_date_2 (str): 만기일-최종거래일조회
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 거래량순위 데이터
        
    Example:
        >>> df = volume_rank(
        ...     fid_cond_mrkt_div_code='W',
        ...     fid_cond_scr_div_code='20278',
        ...     fid_unas_input_iscd='000000',
        ...     fid_input_iscd='00000',
        ...     fid_input_rmnn_dynu_1='',
        ...     fid_div_cls_code='0',
        ...     fid_input_price_1='1000',
        ...     fid_input_price_2='5000',
        ...     fid_input_vol_1='100',
        ...     fid_input_vol_2='1000',
        ...     fid_input_date_1='20230101',
        ...     fid_rank_sort_cls_code='0',
        ...     fid_blng_cls_code='0',
        ...     fid_input_iscd_2='0000',
        ...     fid_input_date_2=''
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
        logger.error("fid_cond_scr_div_code is required. (e.g. '20278')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20278')")
    if not fid_unas_input_iscd:
        logger.error("fid_unas_input_iscd is required. (e.g. '000000')")
        raise ValueError("fid_unas_input_iscd is required. (e.g. '000000')")
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '00000')")
        raise ValueError("fid_input_iscd is required. (e.g. '00000')")
    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")
    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '0')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '0')")
    if not fid_blng_cls_code:
        logger.error("fid_blng_cls_code is required. (e.g. '0')")
        raise ValueError("fid_blng_cls_code is required. (e.g. '0')")
    if not fid_input_iscd_2:
        logger.error("fid_input_iscd_2 is required. (e.g. '0000')")
        raise ValueError("fid_input_iscd_2 is required. (e.g. '0000')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    url = API_URL
    tr_id = "FHPEW02780000"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_UNAS_INPUT_ISCD": fid_unas_input_iscd,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_RMNN_DYNU_1": fid_input_rmnn_dynu_1,
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_INPUT_PRICE_1": fid_input_price_1,
        "FID_INPUT_PRICE_2": fid_input_price_2,
        "FID_INPUT_VOL_1": fid_input_vol_1,
        "FID_INPUT_VOL_2": fid_input_vol_2,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_BLNG_CLS_CODE": fid_blng_cls_code,
        "FID_INPUT_ISCD_2": fid_input_iscd_2,
        "FID_INPUT_DATE_2": fid_input_date_2,
    }

    # API 호출
    res = ka._url_fetch(url, tr_id, tr_cont, params)

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
            return volume_rank(
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_unas_input_iscd,
                fid_input_iscd,
                fid_input_rmnn_dynu_1,
                fid_div_cls_code,
                fid_input_price_1,
                fid_input_price_2,
                fid_input_vol_1,
                fid_input_vol_2,
                fid_input_date_1,
                fid_rank_sort_cls_code,
                fid_blng_cls_code,
                fid_input_iscd_2,
                fid_input_date_2,
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
