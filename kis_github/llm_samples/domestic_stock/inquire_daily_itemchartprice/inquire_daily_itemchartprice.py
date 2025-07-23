"""
Created on 20250101 
@author: LaivData SJPark with cursor
"""


import sys
from typing import Tuple
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 기본시세 > 국내주식기간별시세(일/주/월/년)[v1_국내주식-016]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"

def inquire_daily_itemchartprice(
    env_dv: str,  # 실전모의구분
    fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
    fid_input_iscd: str,  # 입력 종목코드
    fid_input_date_1: str,  # 입력 날짜 1
    fid_input_date_2: str,  # 입력 날짜 2
    fid_period_div_code: str,  # 기간분류코드
    fid_org_adj_prc: str  # 수정주가 원주가 가격 여부
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    국내주식기간별시세(일/주/월/년) API입니다.
    실전계좌/모의계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능합니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 종목코드 (ex 005930 삼성전자))
        fid_input_date_1 (str): [필수] 입력 날짜 1 (ex. 조회 시작일자)
        fid_input_date_2 (str): [필수] 입력 날짜 2 (ex. 조회 종료일자 (최대 100개))
        fid_period_div_code (str): [필수] 기간분류코드 (ex. D:일봉 W:주봉, M:월봉, Y:년봉)
        fid_org_adj_prc (str): [필수] 수정주가 원주가 가격 여부 (ex. 0:수정주가 1:원주가)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> df1, df2 = inquire_daily_itemchartprice("real", "J", "005930", "20220101", "20220809", "D", "1")
        >>> print(df1)
        >>> print(df2)
    """

    # 필수 파라미터 검증
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")
    
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:KRX, NX:NXT, UN:통합')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '종목코드 (ex 005930 삼성전자)')")
    
    if fid_input_date_1 == "":
        raise ValueError("fid_input_date_1 is required (e.g. '조회 시작일자')")
    
    if fid_input_date_2 == "":
        raise ValueError("fid_input_date_2 is required (e.g. '조회 종료일자 (최대 100개)')")
    
    if fid_period_div_code == "":
        raise ValueError("fid_period_div_code is required (e.g. 'D:일봉 W:주봉, M:월봉, Y:년봉')")
    
    if fid_org_adj_prc == "":
        raise ValueError("fid_org_adj_prc is required (e.g. '0:수정주가 1:원주가')")

    # TR_ID 설정
    if env_dv == "real":
        tr_id = "FHKST03010100"
    elif env_dv == "demo":
        tr_id = "FHKST03010100"
    else:
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_DATE_2": fid_input_date_2,
        "FID_PERIOD_DIV_CODE": fid_period_div_code,
        "FID_ORG_ADJ_PRC": fid_org_adj_prc
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # output1 처리 (object 타입이므로 DataFrame)
        output1_data = pd.DataFrame([res.getBody().output1])
        
        # output2 처리 (array 타입이므로 DataFrame)
        output2_data = pd.DataFrame(res.getBody().output2)
        
        return (output1_data, output2_data)
    else:
        res.printError(url=API_URL)
        return (pd.DataFrame(), pd.DataFrame()) 