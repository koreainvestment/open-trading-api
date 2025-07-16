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
# [국내주식] 시세분석 > 종목별 외인기관 추정가집계[v1_국내주식-046]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/investor-trend-estimate"

def investor_trend_estimate(
    mksc_shrn_iscd: str  # [필수] 종목코드 (ex. 123456)
) -> pd.DataFrame:
    """
    국내주식 종목별 외국인, 기관 추정가집계 API입니다.

    한국투자 MTS > 국내 현재가 > 투자자 > 투자자동향 탭 > 왼쪽구분을 '추정(주)'로 선택 시 확인 가능한 데이터를 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

    증권사 직원이 장중에 집계/입력한 자료를 단순 누계한 수치로서,
    입력시간은 외국인 09:30, 11:20, 13:20, 14:30 / 기관종합 10:00, 11:20, 13:20, 14:30 이며, 사정에 따라 변동될 수 있습니다.
    
    Args:
        mksc_shrn_iscd (str): [필수] 종목코드 (ex. 123456)

    Returns:
        pd.DataFrame: 종목별 외인기관 추정가집계 데이터
        
    Example:
        >>> df = investor_trend_estimate(mksc_shrn_iscd="005930")
        >>> print(df)
    """

    if mksc_shrn_iscd == "":
        raise ValueError("mksc_shrn_iscd is required (ex. '123456')")

    tr_id = "HHPTJ04160200"

    params = {
        "MKSC_SHRN_ISCD": mksc_shrn_iscd
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output2)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 