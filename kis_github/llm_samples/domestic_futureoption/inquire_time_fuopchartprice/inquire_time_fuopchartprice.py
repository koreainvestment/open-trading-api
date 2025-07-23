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
# [국내선물옵션] 기본시세 > 선물옵션 분봉조회[v1_국내선물-012]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-futureoption/v1/quotations/inquire-time-fuopchartprice"

def inquire_time_fuopchartprice(
    fid_cond_mrkt_div_code: str,     # FID 조건 시장 분류 코드 (F: 지수선물, O: 지수옵션)
    fid_input_iscd: str,             # FID 입력 종목코드 (101T12)
    fid_hour_cls_code: str,          # FID 시간 구분 코드 (30: 30초, 60: 1분)
    fid_pw_data_incu_yn: str,        # FID 과거 데이터 포함 여부 (Y:과거, N: 당일)
    fid_fake_tick_incu_yn: str,      # FID 허봉 포함 여부 (N)
    fid_input_date_1: str,           # FID 입력 날짜1 (20230901)
    fid_input_hour_1: str            # FID 입력 시간1 (100000)
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    선물옵션 분봉조회 API입니다.
    실전계좌의 경우, 한 번의 호출에 최대 102건까지 확인 가능하며,  
    FID_INPUT_DATE_1(입력날짜), FID_INPUT_HOUR_1(입력시간)을 이용하여 다음 조회 가능합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] FID 조건 시장 분류 코드 (ex. F: 지수선물, O: 지수옵션)
        fid_input_iscd (str): [필수] FID 입력 종목코드 (ex. 101T12)
        fid_hour_cls_code (str): [필수] FID 시간 구분 코드 (ex. 30: 30초, 60: 1분)
        fid_pw_data_incu_yn (str): [필수] FID 과거 데이터 포함 여부 (ex. Y:과거, N: 당일)
        fid_fake_tick_incu_yn (str): [필수] FID 허봉 포함 여부 (ex. N)
        fid_input_date_1 (str): [필수] FID 입력 날짜1 (ex. 20230901)
        fid_input_hour_1 (str): [필수] FID 입력 시간1 (ex. 100000)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 선물옵션 분봉 데이터 (output1, output2)
        
    Example:
        >>> df1, df2 = inquire_time_fuopchartprice("F", "101T12", "60", "Y", "N", "20230901", "100000")
        >>> print(df1)
        >>> print(df2)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'F: 지수선물, O: 지수옵션')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '101T12')")
    
    if fid_hour_cls_code == "":
        raise ValueError("fid_hour_cls_code is required (e.g. '30: 30초, 60: 1분')")
    
    if fid_pw_data_incu_yn == "":
        raise ValueError("fid_pw_data_incu_yn is required (e.g. 'Y:과거, N: 당일')")
    
    if fid_fake_tick_incu_yn == "":
        raise ValueError("fid_fake_tick_incu_yn is required (e.g. 'N')")
    
    if fid_input_date_1 == "":
        raise ValueError("fid_input_date_1 is required (e.g. '20230901')")
    
    if fid_input_hour_1 == "":
        raise ValueError("fid_input_hour_1 is required (e.g. '100000')")

    tr_id = "FHKIF03020200"  # 선물옵션 분봉조회

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_HOUR_CLS_CODE": fid_hour_cls_code,
        "FID_PW_DATA_INCU_YN": fid_pw_data_incu_yn,
        "FID_FAKE_TICK_INCU_YN": fid_fake_tick_incu_yn,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_HOUR_1": fid_input_hour_1
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # output1: object array -> DataFrame
        output1_data = pd.DataFrame(res.getBody().output1, index=[0])
        
        # output2: array -> DataFrame
        output2_data = pd.DataFrame(res.getBody().output2)
            
        logging.info("Data fetch complete.")
        return output1_data, output2_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 