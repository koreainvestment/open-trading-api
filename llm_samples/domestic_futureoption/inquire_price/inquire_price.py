"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""


import sys
import logging
from typing import  Tuple

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 기본시세 > 선물옵션 시세[v1_국내선물-006]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-futureoption/v1/quotations/inquire-price"

def inquire_price(
    fid_cond_mrkt_div_code: str,  # [필수] FID 조건 시장 분류 코드 (ex. F: 지수선물, O: 지수옵션)
    fid_input_iscd: str,          # [필수] FID 입력 종목코드 (ex. 101S03)
    env_dv: str                   # [필수] 실전모의구분 (ex. real:실전, demo:모의)
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    선물옵션 시세 API입니다.

    ※ 종목코드 마스터파일 정제코드는 한국투자증권 Github 참고:  
      https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

    Args:
        fid_cond_mrkt_div_code (str): [필수] FID 조건 시장 분류 코드 (ex. F: 지수선물, O: 지수옵션)
        fid_input_iscd (str): [필수] FID 입력 종목코드 (ex. 101S03)
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: 선물옵션 시세 데이터 (output1, output2, output3)
        
    Example:
        >>> result1, result2, result3 = inquire_price(
        ...     fid_cond_mrkt_div_code="F",
        ...     fid_input_iscd="101S03",
        ...     env_dv="real"
        ... )
        >>> print(result1)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'F', 'O')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '101S03')")
    
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real', 'demo')")

    # tr_id 설정
    if env_dv == "real":
        tr_id = "FHMIF10000000"
    elif env_dv == "demo":
        tr_id = "FHMIF10000000"
    else:
        raise ValueError("env_dv can only be real or demo")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # output1 처리
        output1 = pd.DataFrame(res.getBody().output1, index=[0])
        
        # output2 처리
        output2 = pd.DataFrame(res.getBody().output2, index=[0])
        
        # output3 처리
        output3 = pd.DataFrame(res.getBody().output3, index=[0])
        
        return output1, output2, output3
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame() 