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
# [국내주식] 기본시세 > 주식현재가 시간외시간별체결[v1_국내주식-025]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-time-overtimeconclusion"

def inquire_time_overtimeconclusion(
    env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의) 
    fid_cond_mrkt_div_code: str,  # [필수] 조건시장분류코드 (ex. J:주식/ETF/ETN)
    fid_input_iscd: str,  # [필수] 입력종목코드 (ex. 123456(ETN의 경우 Q로 시작 Q500001))
    fid_hour_cls_code: str  # [필수] 적립금구분코드 (ex. 1: 시간외)
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    주식현재가 시간외시간별체결 API입니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code (str): [필수] 조건시장분류코드 (ex. J:주식/ETF/ETN)
        fid_input_iscd (str): [필수] 입력종목코드 (ex. 123456(ETN의 경우 Q로 시작 Q500001))
        fid_hour_cls_code (str): [필수] 적립금구분코드 (ex. 1: 시간외)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> output1, output2 = inquire_time_overtimeconclusion("real", "J", "005930", "1")
        >>> print(output1)
        >>> print(output2)
    """

    # 필수 파라미터 검증
    if env_dv == "" or env_dv is None:
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")
    
    if fid_cond_mrkt_div_code == "" or fid_cond_mrkt_div_code is None:
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:주식/ETF/ETN')")
    
    if fid_input_iscd == "" or fid_input_iscd is None:
        raise ValueError("fid_input_iscd is required (e.g. '123456(ETN의 경우 Q로 시작 Q500001)')")
    
    if fid_hour_cls_code == "" or fid_hour_cls_code is None:
        raise ValueError("fid_hour_cls_code is required (e.g. '1: 시간외')")

    # TR_ID 설정
    if env_dv == "real":
        tr_id = "FHPST02310000"
    elif env_dv == "demo":
        tr_id = "FHPST02310000"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_HOUR_CLS_CODE": fid_hour_cls_code
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