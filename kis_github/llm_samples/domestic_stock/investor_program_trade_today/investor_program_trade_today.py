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
# [국내주식] 시세분석 > 프로그램매매 투자자매매동향(당일) [국내주식-116]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/investor-program-trade-today"

def investor_program_trade_today(
    mrkt_div_cls_code: str  # [필수] 시장 구분 코드 (ex. 1:코스피, 4:코스닥)
) -> pd.DataFrame:
    """
    프로그램매매 투자자매매동향(당일) API입니다.
    한국투자 HTS(eFriend Plus) > [0466] 프로그램매매 투자자별 동향 화면 의 "당일동향" 표의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        mrkt_div_cls_code (str): [필수] 시장 구분 코드 (ex. 1:코스피, 4:코스닥)
        
    Returns:
        pd.DataFrame: 프로그램매매 투자자매매동향 데이터
        
    Example:
        >>> df = investor_program_trade_today(mrkt_div_cls_code="1")
        >>> print(df)
    """

    if mrkt_div_cls_code == "":
        raise ValueError("mrkt_div_cls_code is required (e.g. '1' or '4')")

    tr_id = "HHPPG046600C1"

    params = {
        "MRKT_DIV_CLS_CODE": mrkt_div_cls_code
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output1)
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 