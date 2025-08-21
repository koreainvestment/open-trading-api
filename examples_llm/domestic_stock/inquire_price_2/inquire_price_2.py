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
# [국내주식] 기본시세 > 주식현재가 시세2[v1_국내주식-054]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-price-2"

def inquire_price_2(
    fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
    fid_input_iscd: str,          # 입력 종목코드
) -> pd.DataFrame:
    """
    주식현재가 시세2 API입니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
        fid_input_iscd (str): [필수] 입력 종목코드
        
    Returns:
        pd.DataFrame: 주식현재가 시세2 데이터
        
    Example:
        >>> df = inquire_price_2("J", "005930")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required")

    tr_id = "FHPST01010000"  # 주식현재가 시세2

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,  # 조건 시장 분류 코드
        "FID_INPUT_ISCD": fid_input_iscd,                  # 입력 종목코드
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        return pd.DataFrame(res.getBody().output, index=[0])
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 