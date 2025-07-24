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
# [국내주식] 업종/기타 > 국내선물 영업일조회 [국내주식-160]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/market-time"

def market_time() -> pd.DataFrame:
    """
    국내선물 영업일조회 API입니다.
    API호출 시 body 혹은 params로 입력하는 사항이 없습니다.
    
    Returns:
        pd.DataFrame: 국내선물 영업일조회 데이터
        
    Example:
        >>> df = market_time()
        >>> print(df)
    """

    tr_id = "HHMCM000002C0"  # 국내선물 영업일조회

    params = {}
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        result = pd.DataFrame([res.getBody().output1])
        return result
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 