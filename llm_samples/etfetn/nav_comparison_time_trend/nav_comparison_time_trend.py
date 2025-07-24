"""
Created on 20250115 
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
# [국내주식] 기본시세 > NAV 비교추이(분)[v1_국내주식-070]
##############################################################################################

# 상수 정의
API_URL = "/uapi/etfetn/v1/quotations/nav-comparison-time-trend"

def nav_comparison_time_trend(
    fid_cond_mrkt_div_code: str,  # [필수] 조건시장분류코드 (ex. E)
    fid_input_iscd: str,          # [필수] 입력종목코드 (ex. 123456)
    fid_hour_cls_code: str        # [필수] 시간구분코드 (ex. 60:1분,180:3분,...,7200:120분)
) -> pd.DataFrame:
    """
    NAV 비교추이(분) API입니다.
    한국투자 HTS(eFriend Plus) > [0244] ETF/ETN 비교추이(NAV/IIV) 좌측 화면 "분별" 비교추이 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    실전계좌의 경우, 한 번의 호출에 최근 30건까지 확인 가능합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건시장분류코드 (ex. E)
        fid_input_iscd (str): [필수] 입력종목코드 (ex. 123456)
        fid_hour_cls_code (str): [필수] 시간구분코드 (ex. 60:1분,180:3분,...,7200:120분)

    Returns:
        pd.DataFrame: NAV 비교추이(분) 데이터
        
    Example:
        >>> df = nav_comparison_time_trend("E", "069500", "60")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "" or fid_cond_mrkt_div_code is None:
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'E')")
    
    if fid_input_iscd == "" or fid_input_iscd is None:
        raise ValueError("fid_input_iscd is required (e.g. '123456')")
    
    if fid_hour_cls_code == "" or fid_hour_cls_code is None:
        raise ValueError("fid_hour_cls_code is required (e.g. '60:1분,180:3분,...,7200:120분')")

    tr_id = "FHPST02440100"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_HOUR_CLS_CODE": fid_hour_cls_code
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # output (array) -> pd.DataFrame
        current_data = pd.DataFrame(res.getBody().output)
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 