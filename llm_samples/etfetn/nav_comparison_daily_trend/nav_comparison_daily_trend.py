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
# [국내주식] 기본시세 > NAV 비교추이(일)[v1_국내주식-071]
##############################################################################################

# 상수 정의
API_URL = "/uapi/etfetn/v1/quotations/nav-comparison-daily-trend"

def nav_comparison_daily_trend(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_input_iscd: str,          # 입력종목코드
    fid_input_date_1: str,        # 조회시작일자
    fid_input_date_2: str         # 조회종료일자
) -> pd.DataFrame:
    """
    NAV 비교추이(일) API입니다.
    한국투자 HTS(eFriend Plus) > [0244] ETF/ETN 비교추이(NAV/IIV) 좌측 화면 "일별" 비교추이 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    실전계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건시장분류코드 (ex. J:주식)
        fid_input_iscd (str): [필수] 입력종목코드 (ex. 123456)
        fid_input_date_1 (str): [필수] 조회시작일자 (ex. 20240101)
        fid_input_date_2 (str): [필수] 조회종료일자 (ex. 20240220)

    Returns:
        pd.DataFrame: NAV 비교추이(일) 데이터
        
    Example:
        >>> df = nav_comparison_daily_trend("J", "069500", "20240101", "20240220")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:주식')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '123456')")
    
    if fid_input_date_1 == "":
        raise ValueError("fid_input_date_1 is required (e.g. '20240101')")
    
    if fid_input_date_2 == "":
        raise ValueError("fid_input_date_2 is required (e.g. '20240220')")

    tr_id = "FHPST02440200"  # NAV 비교추이(일)

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,  # 조건시장분류코드
        "FID_INPUT_ISCD": fid_input_iscd,                  # 입력종목코드
        "FID_INPUT_DATE_1": fid_input_date_1,              # 조회시작일자
        "FID_INPUT_DATE_2": fid_input_date_2               # 조회종료일자
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 