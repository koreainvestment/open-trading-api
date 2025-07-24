"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 종목별 외국계 순매수추이 [국내주식-164]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/frgnmem-pchs-trend"

def frgnmem_pchs_trend(
    fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드 (ex. J)
    fid_input_iscd: str,         # 입력 종목코드 (ex. 123456)
    fid_input_iscd_2: str        # 입력 종목코드 (ex. 99999)
) -> pd.DataFrame:
    """
    종목별 외국계 순매수추이 API입니다.
    한국투자 HTS(eFriend Plus) > [0433] 종목별 외국계 순매수추이 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 123456)
        fid_input_iscd_2 (str): [필수] 입력 종목코드 (ex. 99999)

    Returns:
        pd.DataFrame: 종목별 외국계 순매수추이 데이터

    Example:
        >>> df = frgnmem_pchs_trend("J", "005930", "99999")
        >>> print(df)
    """

    if not fid_cond_mrkt_div_code:
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")
    
    if not fid_input_iscd:
        raise ValueError("fid_input_iscd is required (e.g. '123456')")
    
    if not fid_input_iscd_2:
        raise ValueError("fid_input_iscd_2 is required (e.g. '99999')")

    tr_id = "FHKST644400C0"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_ISCD_2": fid_input_iscd_2,
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        output_data = pd.DataFrame(res.getBody().output)
        
        logging.info("Data fetch complete.")
        return output_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 