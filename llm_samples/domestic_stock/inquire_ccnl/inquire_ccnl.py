"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""


import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 기본시세 > 주식현재가 체결[v1_국내주식-009]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-ccnl"

def inquire_ccnl(
    env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
    fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
    fid_input_iscd: str  # [필수] 입력 종목코드 (ex. 123456)
) -> pd.DataFrame:
    """
    국내현재가 체결 API 입니다. 종목의 체결 정보를 확인할 수 있습니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 123456)

    Returns:
        pd.DataFrame: 주식현재가 체결 데이터
        
    Example:
        >>> df = inquire_ccnl("real", "J", "005930")
        >>> print(df)
    """
    
    # 필수 파라미터 검증
    if env_dv == "" or env_dv is None:
        raise ValueError("env_dv is required (e.g. 'real:실전', 'demo:모의')")
    
    if fid_cond_mrkt_div_code == "" or fid_cond_mrkt_div_code is None:
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:KRX', 'NX:NXT', 'UN:통합')")
    
    if fid_input_iscd == "" or fid_input_iscd is None:
        raise ValueError("fid_input_iscd is required (e.g. '123456')")

    # tr_id 설정
    if env_dv == "real":
        tr_id = "FHKST01010300"
    elif env_dv == "demo":
        tr_id = "FHKST01010300"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 