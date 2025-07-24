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
# [국내선물옵션] 기본시세 > 선물옵션 시세호가[v1_국내선물-007]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-futureoption/v1/quotations/inquire-asking-price"

def inquire_asking_price(
    fid_cond_mrkt_div_code: str,  # [필수] FID 조건 시장 분류 코드 (ex. F: 지수선물, JF: 주식선물)
    fid_input_iscd: str,          # [필수] FID 입력 종목코드 (ex. 101S03)
    env_dv: str                   # [필수] 실전모의구분 (ex. real:실전, demo:모의)
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    선물옵션 시세호가 API입니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] FID 조건 시장 분류 코드 (ex. F: 지수선물, JF: 주식선물)
        fid_input_iscd (str): [필수] FID 입력 종목코드 (ex. 101W09)
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> df1, df2 = inquire_asking_price("F", "101W09", "real")
        >>> print(df1)
        >>> print(df2)
    """
    
    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'F', 'JF')")
        
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '101W09')")
        
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real', 'demo')")

    # TR_ID 설정
    if env_dv == "real":
        tr_id = "FHMIF10010000"
    elif env_dv == "demo":
        tr_id = "FHMIF10010000"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # output1 (object) -> DataFrame
        output1_data = pd.DataFrame([res.getBody().output1])
        
        # output2 (object) -> DataFrame
        output2_data = pd.DataFrame([res.getBody().output2])
        
        return output1_data, output2_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 