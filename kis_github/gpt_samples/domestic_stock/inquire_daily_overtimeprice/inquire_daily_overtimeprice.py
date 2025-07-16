"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""


import sys
import logging
from typing import Tuple

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 기본시세 > 주식현재가 시간외일자별주가[v1_국내주식-026]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-daily-overtimeprice"

def inquire_daily_overtimeprice(
    env_dv: str,                          # [필수] 실전모의구분 (ex. real:실전, demo:모의)
    fid_cond_mrkt_div_code: str,         # [필수] 조건 시장 분류 코드 (ex. J)
    fid_input_iscd: str                  # [필수] 입력 종목코드
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    주식현재가 시간외일자별주가 API입니다.  (최근일 30건만 조회 가능)
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J)
        fid_input_iscd (str): [필수] 입력 종목코드

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 데이터프레임 튜플
        
    Example:
        >>> result1, result2 = inquire_daily_overtimeprice("real", "J", "005930")
        >>> print(result1)
        >>> print(result2)
    """

    # 필수 파라미터 검증
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")
    
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required")

    # TR_ID 설정
    if env_dv == "real":
        tr_id = "FHPST02320000"
    elif env_dv == "demo":
        tr_id = "FHPST02320000"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # output1 (object) -> DataFrame
        output1_data = pd.DataFrame(res.getBody().output1, index=[0])
        
        # output2 (array) -> DataFrame  
        output2_data = pd.DataFrame(res.getBody().output2)
        
        return output1_data, output2_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 