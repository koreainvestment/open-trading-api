"""
Created on 20250114
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
# [국내주식] 시세분석 > 종목별 일별 대차거래추이 [국내주식-135]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/daily-loan-trans"

def daily_loan_trans(
    mrkt_div_cls_code: str,  # [필수] 조회구분 (ex. 1:코스피,2:코스닥,3:종목)
    mksc_shrn_iscd: str,     # [필수] 종목코드 (ex. 123456)
    start_date: str = "",    # 시작일자
    end_date: str = "",      # 종료일자
    cts: str = ""            # 이전조회KEY
) -> pd.DataFrame:
    """
    종목별 일별 대차거래추이 API입니다.
    한 번의 조회에 최대 100건까지 조회 가능하며, start_date, end_date 를 수정하여 다음 조회가 가능합니다.
    
    Args:
        mrkt_div_cls_code (str): [필수] 조회구분 (ex. 1:코스피,2:코스닥,3:종목)
        mksc_shrn_iscd (str): [필수] 종목코드 (ex. 123456)
        start_date (str): 시작일자
        end_date (str): 종료일자
        cts (str): 이전조회KEY

    Returns:
        pd.DataFrame: 종목별 일별 대차거래추이 데이터
        
    Example:
        >>> df = daily_loan_trans(mrkt_div_cls_code="1", mksc_shrn_iscd="005930")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if mrkt_div_cls_code == "":
        raise ValueError("mrkt_div_cls_code is required (e.g. '1', '2', '3')")
    
    if mksc_shrn_iscd == "":
        raise ValueError("mksc_shrn_iscd is required (e.g. '123456')")

    tr_id = "HHPST074500C0"

    params = {
        "MRKT_DIV_CLS_CODE": mrkt_div_cls_code,
        "MKSC_SHRN_ISCD": mksc_shrn_iscd,
        "START_DATE": start_date,
        "END_DATE": end_date,
        "CTS": cts
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        result_data = pd.DataFrame(res.getBody().output1)
        return result_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 