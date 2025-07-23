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
# [국내주식] ELW시세 - ELW 상승률순위[국내주식-167]
##############################################################################################

# 상수 정의
API_URL = "/uapi/elw/v1/ranking/updown-rate"

def updown_rate(
    fid_cond_mrkt_div_code: str,  # 사용자권한정보
    fid_cond_scr_div_code: str,  # 거래소코드
    fid_unas_input_iscd: str,  # 상승율/하락율 구분
    fid_input_iscd: str,  # N일자값
    fid_input_rmnn_dynu_1: str,  # 거래량조건
    fid_div_cls_code: str,  # NEXT KEY BUFF
    fid_input_price_1: str,  # 사용자권한정보
    fid_input_price_2: str,  # 거래소코드
    fid_input_vol_1: str,  # 상승율/하락율 구분
    fid_input_vol_2: str,  # N일자값
    fid_input_date_1: str,  # 거래량조건
    fid_rank_sort_cls_code: str,  # NEXT KEY BUFF
    fid_blng_cls_code: str,  # 사용자권한정보
    fid_input_date_2: str,  # 거래소코드
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 상승률순위[국내주식-167]
    ELW 상승률순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 시장구분코드 (W)
        fid_cond_scr_div_code (str): Unique key(20277)
        fid_unas_input_iscd (str): '000000(전체), 2001(코스피200) , 3003(코스닥150), 005930(삼성전자) '
        fid_input_iscd (str): '00000(전체), 00003(한국투자증권) , 00017(KB증권), 00005(미래에셋주식회사)'
        fid_input_rmnn_dynu_1 (str): '0(전체), 1(1개월이하), 2(1개월~2개월),  3(2개월~3개월), 4(3개월~6개월), 5(6개월~9개월),6(9개월~12개월), 7(12개월이상)'
        fid_div_cls_code (str): 0(전체), 1(콜), 2(풋)
        fid_input_price_1 (str): 
        fid_input_price_2 (str): 
        fid_input_vol_1 (str): 
        fid_input_vol_2 (str): 
        fid_input_date_1 (str): 
        fid_rank_sort_cls_code (str): '0(상승율), 1(하락율), 2(시가대비상승율) , 3(시가대비하락율), 4(변동율)'
        fid_blng_cls_code (str): 0(전체)
        fid_input_date_2 (str): 
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 상승률순위 데이터
        
    Example:
        >>> df = updown_rate(
        ...     fid_cond_mrkt_div_code='W',
        ...     fid_cond_scr_div_code='20277',
        ...     fid_unas_input_iscd='000000',
        ...     fid_input_iscd='00000',
        ...     fid_input_rmnn_dynu_1='0',
        ...     fid_div_cls_code='0',
        ...     fid_input_price_1='',
        ...     fid_input_price_2='',
        ...     fid_input_vol_1='',
        ...     fid_input_vol_2='',
        ...     fid_input_date_1='1',
        ...     fid_rank_sort_cls_code='0',
        ...     fid_blng_cls_code='0',
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
        logger.error("fid_cond_scr_div_code is required. (e.g. '20277')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20277')")

    if not fid_unas_input_iscd:
        logger.error("fid_unas_input_iscd is required. (e.g. '000000')")
        raise ValueError("fid_unas_input_iscd is required. (e.g. '000000')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '00000')")
        raise ValueError("fid_input_iscd is required. (e.g. '00000')")

    if not fid_input_rmnn_dynu_1:
        logger.error("fid_input_rmnn_dynu_1 is required. (e.g. '0')")
        raise ValueError("fid_input_rmnn_dynu_1 is required. (e.g. '0')")

    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")

    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '0')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '0')")

    if not fid_blng_cls_code:
        logger.error("fid_blng_cls_code is required. (e.g. '0')")
        raise ValueError("fid_blng_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHPEW02770000"

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
        "FID_INPUT_DATE_2": fid_input_date_2,
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
            return updown_rate(
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
                fid_input_date_2,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
