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
# [국내주식] 시세분석 > 국내주식 공매도 일별추이[국내주식-134]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/daily-short-sale"

def daily_short_sale(
    fid_cond_mrkt_div_code: str,  # [필수] 시장분류코드 (ex. J:주식)
    fid_input_iscd: str,          # [필수] 종목코드 (ex. 123456)
    fid_input_date_1: str = "",   # 시작일자
    fid_input_date_2: str = ""    # 종료일자
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    국내주식 공매도 일별추이를 조회합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 시장분류코드 (ex. J:주식)
        fid_input_iscd (str): [필수] 종목코드 (ex. 123456)
        fid_input_date_1 (str): 시작일자
        fid_input_date_2 (str): 종료일자

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 데이터프레임 쌍
        
    Example:
        >>> df1, df2 = daily_short_sale("J", "005930", "20240301", "20240328")
        >>> print(df1)
        >>> print(df2)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:주식')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '123456')")

    tr_id = "FHPST04830000"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_DATE_2": fid_input_date_2
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # output1 처리 (object 타입 -> DataFrame)
        output1_data = pd.DataFrame(res.getBody().output1, index=[0])
        
        # output2 처리 (array 타입 -> DataFrame)
        output2_data = pd.DataFrame(res.getBody().output2)
        
        return output1_data, output2_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 