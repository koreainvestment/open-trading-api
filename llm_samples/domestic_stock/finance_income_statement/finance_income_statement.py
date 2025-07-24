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
# [국내주식] 종목정보 > 국내주식 손익계산서 [v1_국내주식-079]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/finance/income-statement"

def finance_income_statement(
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    국내주식 손익계산서 API를 호출하여 DataFrame으로 반환합니다.

    Args:
        fid_div_cls_code (str): 분류 구분 코드 (0: 년, 1: 분기)
        fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (예: 'J')
        fid_input_iscd (str): 입력 종목코드 (예: '000660')
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)

    Returns:
        Optional[pd.DataFrame]: 국내주식 손익계산서 데이터

    Example:
        >>> df = finance_income_statement('1', 'J', '005930')
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0' or '1')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0' or '1')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '000660')")
        raise ValueError("fid_input_iscd is required. (e.g. '000660')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()


    tr_id = "FHKST66430200"

    params = {
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_input_iscd": fid_input_iscd,
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
            return finance_income_statement(
                fid_div_cls_code,
                fid_cond_mrkt_div_code,
                fid_input_iscd,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
