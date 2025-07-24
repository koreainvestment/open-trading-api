"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import logging
import sys
from typing import Tuple

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 국내주식 예상체결가 추이[국내주식-118]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/exp-price-trend"

def exp_price_trend(
    fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드 (ex. J)
    fid_input_iscd: str,         # 입력 종목코드 (ex. 123456)
    fid_mkop_cls_code: str       # (ex. 0:전체, 4:체결량 0 제외)
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    국내주식 예상체결가 추이 API입니다.
    한국투자 HTS(eFriend Plus) > [0184] 예상체결지수 추이 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    최대 30건 확인 가능하며, 다음 조회가 불가합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 123456)
        fid_mkop_cls_code (str): [필수]  (ex. 0:전체, 4:체결량 0 제외)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 데이터

    Example:
        >>> output1, output2 = exp_price_trend("J", "005930", "0")
        >>> print(output1)
        >>> print(output2)
    """

    if not fid_cond_mrkt_div_code:
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")
    
    if not fid_input_iscd:
        raise ValueError("fid_input_iscd is required (e.g. '123456')")
    
    if not fid_mkop_cls_code:
        raise ValueError("fid_mkop_cls_code is required (e.g. '0')")

    tr_id = "FHPST01810000"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_MKOP_CLS_CODE": fid_mkop_cls_code,
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        output1_data = pd.DataFrame([res.getBody().output1])
        output2_data = pd.DataFrame(res.getBody().output2)
        
        logging.info("Data fetch complete.")
        return output1_data, output2_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 