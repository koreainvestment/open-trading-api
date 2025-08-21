"""
Created on 20250126
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
# [국내주식] 시세분석 > 종목별일별매수매도체결량 [v1_국내주식-056]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-daily-trade-volume"

def inquire_daily_trade_volume(
    fid_cond_mrkt_div_code: str,  # FID 조건 시장 분류 코드
    fid_input_iscd: str,          # FID 입력 종목코드
    fid_period_div_code: str,     # FID 기간 분류 코드
    fid_input_date_1: str = "",   # FID 입력 날짜1
    fid_input_date_2: str = ""    # FID 입력 날짜2
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    종목별일별매수매도체결량 API입니다. 실전계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능합니다.
    국내주식 종목의 일별 매수체결량, 매도체결량 데이터를 확인할 수 있습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] FID 조건 시장 분류 코드 (J:KRX, NX:NXT)
        fid_input_iscd (str): [필수] FID 입력 종목코드 (ex. 123456)
        fid_period_div_code (str): [필수] FID 기간 분류 코드 (ex. D)
        fid_input_date_1 (str): FID 입력 날짜1
        fid_input_date_2 (str): FID 입력 날짜2

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터프레임, output2 데이터프레임)
        
    Example:
        >>> df1, df2 = inquire_daily_trade_volume("J", "005930", "D")
        >>> print(df1)
        >>> print(df2)
    """

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '005930')")
    
    if fid_period_div_code == "":
        raise ValueError("fid_period_div_code is required (e.g. 'D')")

    tr_id = "FHKST03010800"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_PERIOD_DIV_CODE": fid_period_div_code,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_DATE_2": fid_input_date_2
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # output1 (object) - 단일 레코드
        output1_data = pd.DataFrame([res.getBody().output1])
        
        # output2 (array) - 배열 데이터
        output2_data = pd.DataFrame(res.getBody().output2)
        
        return output1_data, output2_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 