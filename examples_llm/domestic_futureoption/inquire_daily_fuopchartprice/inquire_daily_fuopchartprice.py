"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""


import sys
from typing import Tuple
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 기본시세 > 선물옵션기간별시세(일/주/월/년)[v1_국내선물-008]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-futureoption/v1/quotations/inquire-daily-fuopchartprice"

def inquire_daily_fuopchartprice(
    fid_cond_mrkt_div_code: str,  # FID 조건 시장 분류 코드
    fid_input_iscd: str,          # 종목코드
    fid_input_date_1: str,        # 조회 시작일자
    fid_input_date_2: str,        # 조회 종료일자  
    fid_period_div_code: str,     # 기간분류코드
    env_dv: str                   # 실전모의구분
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    (지수)선물옵션 기간별시세 데이터(일/주/월/년) 조회 (최대 100건 조회)
    실전계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다. 
    모의계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] FID 조건 시장 분류 코드 (ex. F: 지수선물, O: 지수옵션)
        fid_input_iscd (str): [필수] 종목코드 (ex. 101W09)
        fid_input_date_1 (str): [필수] 조회 시작일자 (ex. 20220301)
        fid_input_date_2 (str): [필수] 조회 종료일자 (ex. 20220810)
        fid_period_div_code (str): [필수] 기간분류코드 (ex. D: 일봉, W: 주봉)
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (기본정보, 차트데이터) 튜플
        
    Example:
        >>> output1, output2 = inquire_daily_fuopchartprice(
        ...     fid_cond_mrkt_div_code="F",
        ...     fid_input_iscd="101W09",
        ...     fid_input_date_1="20250301",
        ...     fid_input_date_2="20250810",
        ...     fid_period_div_code="D",
        ...     env_dv="real"
        ... )
        >>> print(output1)
        >>> print(output2)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'F: 지수선물, O: 지수옵션')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '101W09')")
    
    if fid_input_date_1 == "":
        raise ValueError("fid_input_date_1 is required (e.g. '20250301')")
    
    if fid_input_date_2 == "":
        raise ValueError("fid_input_date_2 is required (e.g. '20250810')")
    
    if fid_period_div_code == "":
        raise ValueError("fid_period_div_code is required (e.g. 'D: 일봉, W: 주봉')")
    
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")

    # tr_id 설정
    if env_dv == "real":
        tr_id = "FHKIF03020100"
    elif env_dv == "demo":
        tr_id = "FHKIF03020100"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_DATE_2": fid_input_date_2,
        "FID_PERIOD_DIV_CODE": fid_period_div_code
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # output1: object -> DataFrame (1행)
        output1_data = pd.DataFrame([res.getBody().output1])
        
        # output2: array -> DataFrame (여러행)
        output2_data = pd.DataFrame(res.getBody().output2)
        
        return output1_data, output2_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 