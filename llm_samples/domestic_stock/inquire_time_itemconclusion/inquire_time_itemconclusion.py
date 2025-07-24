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
# [국내주식] 기본시세 > 주식현재가 당일시간대별체결[v1_국내주식-023]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-time-itemconclusion"

def inquire_time_itemconclusion(
    env_dv: str,                    # [필수] 실전모의구분 (ex. real:실전, demo:모의)
    fid_cond_mrkt_div_code: str,    # [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
    fid_input_iscd: str,            # [필수] 입력 종목코드
    fid_input_hour_1: str           # [필수] 입력 시간1
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    주식현재가 당일시간대별체결 API입니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (real:실전, demo:모의)
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (J:KRX, NX:NXT, UN:통합)
        fid_input_iscd (str): [필수] 입력 종목코드
        fid_input_hour_1 (str): [필수] 입력 시간1

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> df1, df2 = inquire_time_itemconclusion("real", "U", "0001", "115959")
        >>> print(df1)
        >>> print(df2)
    """

    # 필수 파라미터 검증
    if env_dv == "" or env_dv is None:
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")
    
    if fid_cond_mrkt_div_code == "" or fid_cond_mrkt_div_code is None:
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:KRX, NX:NXT, UN:통합')")
    
    if fid_input_iscd == "" or fid_input_iscd is None:
        raise ValueError("fid_input_iscd is required (e.g. '입력 종목코드')")
    
    if fid_input_hour_1 == "" or fid_input_hour_1 is None:
        raise ValueError("fid_input_hour_1 is required (e.g. '입력 시간1')")

    # tr_id 설정
    if env_dv == "real":
        tr_id = "FHPST01060000"
    elif env_dv == "demo":
        tr_id = "FHPST01060000"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_HOUR_1": fid_input_hour_1
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # output1 처리 (object -> DataFrame)
        output1_data = pd.DataFrame([res.getBody().output1])
        
        # output2 처리 (object -> DataFrame)  
        output2_data = pd.DataFrame(res.getBody().output2)
        
        return output1_data, output2_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 