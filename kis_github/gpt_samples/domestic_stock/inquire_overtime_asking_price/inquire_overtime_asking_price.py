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
# [국내주식] 기본시세 > 국내주식 시간외호가[국내주식-077]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-overtime-asking-price"

def inquire_overtime_asking_price(
    fid_cond_mrkt_div_code: str,  # [필수] 시장 분류 코드 (ex. J:주식)
    fid_input_iscd: str,         # [필수] 종목코드 (ex. 123456)
) -> pd.DataFrame:
    """
    국내주식 시간외호가 API입니다. 
    한국투자 HTS(eFriend Plus) > [0230] 시간외 현재가 화면의 '호가' 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 시장 분류 코드 (ex. J:주식)
        fid_input_iscd (str): [필수] 종목코드 (ex. 123456)

    Returns:
        pd.DataFrame: 국내주식 시간외호가 데이터
        
    Example:
        >>> df = inquire_overtime_asking_price("J", "005930")
        >>> print(df)
    """

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '123456')")

    tr_id = "FHPST02300400"  # 국내주식 시간외호가

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,  # 시장 분류 코드
        "FID_INPUT_ISCD": fid_input_iscd,                  # 종목코드
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame([res.getBody().output])
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 