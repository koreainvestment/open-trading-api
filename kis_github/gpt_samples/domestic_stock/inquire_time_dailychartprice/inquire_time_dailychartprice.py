"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""


import sys
from typing import Optional, Tuple
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 기본시세 > 주식일별분봉조회 [국내주식-213]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-time-dailychartprice"

def inquire_time_dailychartprice(
    fid_cond_mrkt_div_code: str,  # 시장 분류 코드
    fid_input_iscd: str,         # 종목코드
    fid_input_hour_1: str,       # 입력 시간1
    fid_input_date_1: str,       # 입력 날짜1
    fid_pw_data_incu_yn: str = "N",  # 과거 데이터 포함 여부
    fid_fake_tick_incu_yn: str = ""  # 허봉 포함 여부
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    주식일별분봉조회 API입니다. 

    실전계좌의 경우, 한 번의 호출에 최대 120건까지 확인 가능하며, 
    FID_INPUT_DATE_1, FID_INPUT_HOUR_1 이용하여 과거일자 분봉조회 가능합니다.

    ※ 과거 분봉 조회 시, 당사 서버에서 보관하고 있는 만큼의 데이터만 확인이 가능합니다. (최대 1년 분봉 보관)
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 시장 분류 코드 (ex. J:주식,NX:NXT,UN:통합)
        fid_input_iscd (str): [필수] 종목코드 (ex. 123456)
        fid_input_hour_1 (str): [필수] 입력 시간1 (ex. 130000)
        fid_input_date_1 (str): [필수] 입력 날짜1 (ex. 20241023)
        fid_pw_data_incu_yn (str): 과거 데이터 포함 여부 (기본값: "N")
        fid_fake_tick_incu_yn (str): 허봉 포함 여부 (기본값: "")

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> output1, output2 = inquire_time_dailychartprice("J", "005930", "130000", "20241023")
        >>> print(output1)
        >>> print(output2)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J', 'NX', 'UN')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '123456')")
    
    if fid_input_hour_1 == "":
        raise ValueError("fid_input_hour_1 is required (e.g. '130000')")
    
    if fid_input_date_1 == "":
        raise ValueError("fid_input_date_1 is required (e.g. '20241023')")

    tr_id = "FHKST03010230"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_HOUR_1": fid_input_hour_1,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_PW_DATA_INCU_YN": fid_pw_data_incu_yn,
        "FID_FAKE_TICK_INCU_YN": fid_fake_tick_incu_yn
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # output1 (object) -> DataFrame
        output1 = pd.DataFrame([res.getBody().output1])
        
        # output2 (array) -> DataFrame  
        output2 = pd.DataFrame(res.getBody().output2)
        
        return output1, output2
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 