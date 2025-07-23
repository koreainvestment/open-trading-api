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
# [국내주식] 시세분석 > 종목별 프로그램매매추이(일별) [국내주식-113]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/program-trade-by-stock-daily"

def program_trade_by_stock_daily(
    fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J:KRX,NX:NXT,UN:통합)
    fid_input_iscd: str,         # [필수] 입력 종목코드 (ex. 123456)
    fid_input_date_1: str = ""   # [필수] 입력날짜 (초기값: "")
) -> pd.DataFrame:
    """
    국내주식 종목별 프로그램매매추이(일별) API입니다.
    한국투자 HTS(eFriend Plus) > [0465] 종목별 프로그램 매매추이 화면(혹은 한국투자 MTS > 국내 현재가 > 기타수급 > 프로그램) 의 "일자별" 클릭 시 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX,NX:NXT,UN:통합)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 123456)
        fid_input_date_1 (str): [필수] 입력날짜 (초기값: "")

    Returns:
        pd.DataFrame: 종목별 프로그램매매추이(일별) 데이터
        
    Example:
        >>> df = program_trade_by_stock_daily("J", "005930")
        >>> print(df)
    """

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (ex. J:KRX,NX:NXT,UN:통합)")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (ex. 123456)")

    tr_id = "FHPPG04650201"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_DATE_1": fid_input_date_1
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 