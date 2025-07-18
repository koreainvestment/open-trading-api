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
# [국내주식] ELW시세 > ELW 현재가 시세 [v1_국내주식-014]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-elw-price"

def inquire_elw_price(
        fid_cond_mrkt_div_code: str,  # FID 조건 시장 분류 코드
        fid_input_iscd: str,  # FID 입력 종목코드
        env_dv: str = "real",  # 실전모의구분 (real:실전, demo:모의)
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 현재가 시세[v1_국내주식-014]
    ELW 현재가 시세 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): FID 조건 시장 분류 코드 (예: 'W')
        fid_input_iscd (str): FID 입력 종목코드 (예: '000660')
        env_dv (str): [추가] 실전모의구분 (real:실전, demo:모의, 기본값: 'real')
        tr_cont (str): 연속 거래 여부 (기본값: '')
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (기본값: None)
        depth (int): 현재 재귀 깊이 (기본값: 0)
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 현재가 시세 데이터
        
    Example:
        >>> df = inquire_elw_price('W', '000660', env_dv='real')  # 실전투자
        >>> df = inquire_elw_price('W', '000660', env_dv='demo')  # 모의투자
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '000660')")
        raise ValueError("fid_input_iscd is required. (e.g. '000660')")

    # env_dv 파라미터 검증 (모의투자 지원 로직)
    if env_dv not in ["real", "demo"]:
        logger.error("env_dv must be 'real' or 'demo'")
        raise ValueError("env_dv must be 'real' or 'demo'")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # API 호출 URL 설정


    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real" or env_dv == "demo":
        tr_id = "FHKEW15010000"  # 실전투자용 TR ID

    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    # 요청 파라미터 설정
    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
    }

    # API 호출
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    # API 응답 처리
    if res.isOK():
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

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_elw_price(
                fid_cond_mrkt_div_code,
                fid_input_iscd,
                env_dv,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
