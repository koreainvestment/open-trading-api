"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""


import sys
import time
from typing import Optional
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 국내주식 신용잔고 일별추이[국내주식-110]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/daily-credit-balance"

def daily_credit_balance(
    fid_cond_mrkt_div_code: str,  # [필수] 시장 분류 코드
    fid_cond_scr_div_code: str,   # [필수] 화면 분류 코드  
    fid_input_iscd: str,          # [필수] 종목코드
    fid_input_date_1: str,        # [필수] 결제일자
    tr_cont: str = "",            # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,               # 내부 재귀깊이 (자동관리)
    max_depth: int = 10           # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    국내주식 신용잔고 일별추이 API입니다.
    한국투자 HTS(eFriend Plus) > [0476] 국내주식 신용잔고 일별추이 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    한 번의 호출에 최대 30건 확인 가능하며, fid_input_date_1 을 입력하여 다음 조회가 가능합니다.
    
    ※ 상환수량은 "매도상환수량+현금상환수량"의 합계 수치입니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 시장 분류 코드 (ex. J: 주식)
        fid_cond_scr_div_code (str): [필수] 화면 분류 코드 (ex. 20476)
        fid_input_iscd (str): [필수] 종목코드 (ex. 005930)
        fid_input_date_1 (str): [필수] 결제일자 (ex. 20240313)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        pd.DataFrame: 국내주식 신용잔고 일별추이 데이터
        
    Example:
        >>> df = daily_credit_balance("J", "20476", "005930", "20240313")
        >>> print(df)
    """

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")
    
    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '20476')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '005930')")
    
    if fid_input_date_1 == "":
        raise ValueError("fid_input_date_1 is required (e.g. '20240313')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    tr_id = "FHPST04760000"  # 국내주식 신용잔고 일별추이

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,  # 시장 분류 코드
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,    # 화면 분류 코드
        "FID_INPUT_ISCD": fid_input_iscd,                  # 종목코드
        "FID_INPUT_DATE_1": fid_input_date_1               # 결제일자
    }
    
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
            
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data
            
        tr_cont = res.getHeader().tr_cont
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return daily_credit_balance(
                fid_cond_mrkt_div_code, fid_cond_scr_div_code, fid_input_iscd, fid_input_date_1, "N", dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 