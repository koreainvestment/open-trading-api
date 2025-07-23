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
# [국내주식] 시세분석 > 시장별 투자자매매동향(시세)[v1_국내주식-074]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-investor-time-by-market"

def inquire_investor_time_by_market(
    fid_input_iscd: str,    # [필수] 시장구분
    fid_input_iscd_2: str   # [필수] 업종구분
) -> pd.DataFrame:
    """
    시장별 투자자매매동향(시세성) API입니다.
    한국투자 HTS(eFriend Plus) > [0403] 시장별 시간동향 의 상단 표 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_input_iscd (str): [필수] 시장구분
        fid_input_iscd_2 (str): [필수] 업종구분
        
    Returns:
        pd.DataFrame: 시장별 투자자매매동향 데이터
        
    Example:
        >>> df = inquire_investor_time_by_market(fid_input_iscd="999", fid_input_iscd_2="S001")
        >>> print(df)
    """

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required")
    
    if fid_input_iscd_2 == "":
        raise ValueError("fid_input_iscd_2 is required")

    tr_id = "FHPTJ04030000"

    params = {
        "FID_INPUT_ISCD": fid_input_iscd,      # 시장구분
        "FID_INPUT_ISCD_2": fid_input_iscd_2   # 업종구분
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 