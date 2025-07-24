"""
Created on 20250112 
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
# [국내주식] 기본시세 > NAV 비교추이(종목)[v1_국내주식-069]
##############################################################################################

# 상수 정의
API_URL = "/uapi/etfetn/v1/quotations/nav-comparison-trend"

def nav_comparison_trend(
    fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J)
    fid_input_iscd: str,          # [필수] 입력 종목코드
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    NAV 비교추이(종목) API입니다.
    한국투자 HTS(eFriend Plus) > [0244] ETF/ETN 비교추이(NAV/IIV) 좌측 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J)
        fid_input_iscd (str): [필수] 입력 종목코드
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: output1, output2 데이터프레임
        
    Example:
        >>> output1, output2 = nav_comparison_trend("J", "069500")
        >>> print(output1)
        >>> print(output2)
    """
    
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")
        
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required")

    tr_id = "FHPST02440000"  # NAV 비교추이(종목)

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,  # 조건 시장 분류 코드
        "FID_INPUT_ISCD": fid_input_iscd,                  # 입력 종목코드
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        output1_data = pd.DataFrame(res.getBody().output1, index=[0])
        output2_data = pd.DataFrame(res.getBody().output2, index=[0])
        
        logging.info("Data fetch complete.")
        return output1_data, output2_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 