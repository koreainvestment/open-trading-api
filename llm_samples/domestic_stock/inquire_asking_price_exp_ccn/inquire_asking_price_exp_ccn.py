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
# [국내주식] 기본시세 > 주식현재가 호가/예상체결[v1_국내주식-011]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn"

def inquire_asking_price_exp_ccn(
    env_dv: str,  # 실전모의구분 (real:실전, demo:모의)
    fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드 (J:KRX, NX:NXT, UN:통합)
    fid_input_iscd: str  # 입력 종목코드 (123456)
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    주식현재가 호가 예상체결 API입니다. 매수 매도 호가를 확인하실 수 있습니다. 실시간 데이터를 원하신다면 웹소켓 API를 활용하세요.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 123456)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (호가정보, 예상체결정보) 데이터
        
    Example:
        >>> result1, result2 = inquire_asking_price_exp_ccn(env_dv="real", fid_cond_mrkt_div_code="J", fid_input_iscd="005930")
        >>> print(result1)  # 호가정보
        >>> print(result2)  # 예상체결정보
    """
    
    # 필수 파라미터 검증
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")
    
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:KRX, NX:NXT, UN:통합')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '123456')")

    # TR_ID 설정
    if env_dv == "real":
        tr_id = "FHKST01010200"
    elif env_dv == "demo":
        tr_id = "FHKST01010200"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,  # 조건 시장 분류 코드
        "FID_INPUT_ISCD": fid_input_iscd  # 입력 종목코드
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # output1 (object) -> 호가정보
        output1_data = pd.DataFrame([res.getBody().output1])
        
        # output2 (array) -> 예상체결정보
        output2_data = pd.DataFrame([res.getBody().output2])
        
        return output1_data, output2_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 