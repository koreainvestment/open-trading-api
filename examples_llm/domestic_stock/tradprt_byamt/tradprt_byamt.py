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
# [국내주식] 시세분석 > 국내주식 체결금액별 매매비중 [국내주식-192]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/tradprt-byamt"

def tradprt_byamt(
    fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J)
    fid_cond_scr_div_code: str,   # [필수] 조건화면분류코드 (ex. 11119)
    fid_input_iscd: str           # [필수] 입력 종목코드 (ex. 123456)
) -> pd.DataFrame:
    """
    국내주식 체결금액별 매매비중 API입니다.
    한국투자 HTS(eFriend Plus) > [0135] 체결금액별 매매비중 화면의 "상단 표" 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (J:KRX, NX:NXT)
        fid_cond_scr_div_code (str): [필수] 조건화면분류코드 (ex. 11119)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 123456)

    Returns:
        pd.DataFrame: 국내주식 체결금액별 매매비중 데이터
        
    Example:
        >>> df = tradprt_byamt("J", "11119", "005930")
        >>> print(df)
    """

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")
    
    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '11119')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '123456')")

    tr_id = "FHKST111900C0"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_INPUT_ISCD": fid_input_iscd
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 