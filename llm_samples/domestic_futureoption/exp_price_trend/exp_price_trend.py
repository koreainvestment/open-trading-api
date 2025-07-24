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
# [국내선물옵션] 기본시세 > 선물옵션 일중예상체결추이[국내선물-018]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-futureoption/v1/quotations/exp-price-trend"

def exp_price_trend(
    fid_input_iscd: str,  # [필수] 입력 종목코드 (ex. 101V06)
    fid_cond_mrkt_div_code: str  # [필수] 조건 시장 분류 코드 (ex. F)
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    선물옵션 일중예상체결추이 API입니다.
    한국투자 HTS(eFriend Plus) > [0548] 선물옵션 예상체결추이 화면의 기능을 API로 개발한 사항입니다.
    
    Args:
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 101V06)
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. F)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 데이터프레임 튜플
        
    Example:
        >>> df1, df2 = exp_price_trend(fid_input_iscd="101W09", fid_cond_mrkt_div_code="F")
        >>> print(df1)
        >>> print(df2)
    """

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '101W09')")
    
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'F')")

    tr_id = "FHPIF05110100"  # 선물옵션 일중예상체결추이

    params = {
        "FID_INPUT_ISCD": fid_input_iscd,  # 입력 종목코드
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code  # 조건 시장 분류 코드
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # output1은 object 타입이므로 단일 행 DataFrame
        output1_data = pd.DataFrame([res.getBody().output1])
        
        # output2는 array 타입이므로 여러 행 DataFrame
        output2_data = pd.DataFrame(res.getBody().output2)
        
        return output1_data, output2_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 