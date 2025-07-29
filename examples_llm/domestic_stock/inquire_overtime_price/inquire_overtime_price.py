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
# [국내주식] 기본시세 > 국내주식 시간외현재가[국내주식-076]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-overtime-price"

def inquire_overtime_price(
    fid_cond_mrkt_div_code: str,  # [필수] 시장 분류 코드 (ex. J: 주식)
    fid_input_iscd: str           # [필수] 종목코드 (ex. 005930)
) -> pd.DataFrame:
    """
    국내주식 시간외현재가 API입니다. 
    한국투자 HTS(eFriend Plus) > [0230] 시간외 현재가 화면의 좌측 상단기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 시장 분류 코드 (ex. J: 주식)
        fid_input_iscd (str): [필수] 종목코드 (ex. 005930)

    Returns:
        pd.DataFrame: 시간외현재가 데이터
        
    Example:
        >>> df = inquire_overtime_price("J", "005930")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '005930')")

    tr_id = "FHPST02300000"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output, index=[0])
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 