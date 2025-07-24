"""
Created on 2025-06-19

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
# [국내주식] ELW시세 - ELW 만기예정/만기종목[국내주식-184]
##############################################################################################

# 상수 정의
API_URL = "/uapi/elw/v1/quotations/expiration-stocks"

def expiration_stocks(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_cond_scr_div_code: str,  # 조건화면분류코드
    fid_input_date_1: str,  # 입력날짜1
    fid_input_date_2: str,  # 입력날짜2
    fid_div_cls_code: str,  # 분류구분코드
    fid_etc_cls_code: str,  # 기타구분코드
    fid_unas_input_iscd: str,  # 기초자산입력종목코드
    fid_input_iscd_2: str,  # 발행회사코드
    fid_blng_cls_code: str,  # 결제방법
    fid_input_option_1: str,  # 입력옵션1
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 만기예정_만기종목[국내주식-184]
    ELW 만기예정_만기종목 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): W 입력
        fid_cond_scr_div_code (str): 11547 입력
        fid_input_date_1 (str): 입력날짜 ~ (ex) 20240402)
        fid_input_date_2 (str): ~입력날짜 (ex) 20240408)
        fid_div_cls_code (str): 0(콜),1(풋),2(전체)
        fid_etc_cls_code (str): 공백 입력
        fid_unas_input_iscd (str): 000000(전체), 2001(KOSPI 200), 기초자산코드(종목코드 ex. 삼성전자-005930)
        fid_input_iscd_2 (str): 00000(전체), 00003(한국투자증권), 00017(KB증권), 00005(미래에셋증권)
        fid_blng_cls_code (str): 0(전체),1(일반),2(조기종료)
        fid_input_option_1 (str): 공백 입력
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 만기예정_만기종목 데이터
        
    Example:
        >>> df = expiration_stocks(
        ...     fid_cond_mrkt_div_code='W',
        ...     fid_cond_scr_div_code='11547',
        ...     fid_input_date_1='20240402',
        ...     fid_input_date_2='20240408',
        ...     fid_div_cls_code='0',
        ...     fid_etc_cls_code='',
        ...     fid_unas_input_iscd='000000',
        ...     fid_input_iscd_2='00000',
        ...     fid_blng_cls_code='0',
        ...     fid_input_option_1='',
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
        logger.error("fid_cond_scr_div_code is required. (e.g. '11547')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '11547')")
    
    if not fid_input_date_1:
        logger.error("fid_input_date_1 is required. (e.g. '20240402')")
        raise ValueError("fid_input_date_1 is required. (e.g. '20240402')")
    
    if not fid_input_date_2:
        logger.error("fid_input_date_2 is required. (e.g. '20240408')")
        raise ValueError("fid_input_date_2 is required. (e.g. '20240408')")
    
    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")
    
    if not fid_unas_input_iscd:
        logger.error("fid_unas_input_iscd is required. (e.g. '000000')")
        raise ValueError("fid_unas_input_iscd is required. (e.g. '000000')")
    
    if not fid_input_iscd_2:
        logger.error("fid_input_iscd_2 is required. (e.g. '00000')")
        raise ValueError("fid_input_iscd_2 is required. (e.g. '00000')")
    
    if not fid_blng_cls_code:
        logger.error("fid_blng_cls_code is required. (e.g. '0')")
        raise ValueError("fid_blng_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    tr_id = "FHKEW154700C0"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_DATE_2": fid_input_date_2,
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_ETC_CLS_CODE": fid_etc_cls_code,
        "FID_UNAS_INPUT_ISCD": fid_unas_input_iscd,
        "FID_INPUT_ISCD_2": fid_input_iscd_2,
        "FID_BLNG_CLS_CODE": fid_blng_cls_code,
        "FID_INPUT_OPTION_1": fid_input_option_1,
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
            return expiration_stocks(
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_input_date_1,
                fid_input_date_2,
                fid_div_cls_code,
                fid_etc_cls_code,
                fid_unas_input_iscd,
                fid_input_iscd_2,
                fid_blng_cls_code,
                fid_input_option_1,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
