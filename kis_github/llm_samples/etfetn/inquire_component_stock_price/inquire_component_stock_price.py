"""
Created on 20250114
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

# 상수 정의
API_URL = "/uapi/etfetn/v1/quotations/inquire-component-stock-price"

##############################################################################################
# [국내주식] 기본시세 > ETF 구성종목시세[국내주식-073]
##############################################################################################

def inquire_component_stock_price(
    fid_cond_mrkt_div_code: str,
    fid_input_iscd: str,
    fid_cond_scr_div_code: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    ETF 구성종목시세 API입니다. 
    한국투자 HTS(eFriend Plus) > [0245] ETF/ETN 구성종목시세 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건시장분류코드 (ex. J: 주식/ETF/ETN)
        fid_input_iscd (str): [필수] 입력종목코드 (ex. 123456)
        fid_cond_scr_div_code (str): [필수] 조건화면분류코드 (ex. 11216)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터프레임, output2 데이터프레임)
        
    Raises:
        ValueError: 필수 파라미터가 누락된 경우
        
    Examples:
        >>> df1, df2 = inquire_component_stock_price("J", "069500", "11216")
        >>> print(df1)  # ETF 기본 정보
        >>> print(df2)  # ETF 구성종목 상세정보
    """
    
    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J: 주식/ETF/ETN')")
        
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '123456')")
        
    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '11216')")
    
    # API 호출 설정
    tr_id = "FHKST121600C0"
    
    # 파라미터 설정
    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code
    }
    
    # API 호출
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # output1 (object) -> DataFrame 변환
        output1_data = res.getBody().output1
        df1 = pd.DataFrame([output1_data]) if output1_data else pd.DataFrame()
        
        # output2 (array) -> DataFrame 변환
        output2_data = res.getBody().output2
        df2 = pd.DataFrame(output2_data) if output2_data else pd.DataFrame()
        
        return df1, df2
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 