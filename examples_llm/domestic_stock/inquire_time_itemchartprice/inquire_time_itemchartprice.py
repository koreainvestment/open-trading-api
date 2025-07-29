"""
Created on 20250601 
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
# [국내주식] 기본시세 > 주식당일분봉조회[v1_국내주식-022]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"

def inquire_time_itemchartprice(
    env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
    fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
    fid_input_iscd: str,  # [필수] 입력 종목코드 (ex. 123456)
    fid_input_hour_1: str,  # [필수] 입력 시간1 (ex. 입력시간)
    fid_pw_data_incu_yn: str,  # [필수] 과거 데이터 포함 여부
    fid_etc_cls_code: str = ""  # [필수] 기타 구분 코드
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    주식당일분봉조회 API입니다. 
    실전계좌/모의계좌의 경우, 한 번의 호출에 최대 30건까지 확인 가능합니다.

    ※ 당일 분봉 데이터만 제공됩니다. (전일자 분봉 미제공)

    ※ input > FID_INPUT_HOUR_1 에 미래일시 입력 시에 현재가로 조회됩니다.
    ex) 오전 10시에 113000 입력 시에 오전 10시~11시30분 사이의 데이터가 오전 10시 값으로 조회됨

    ※ output2의 첫번째 배열의 체결량(cntg_vol)은 첫체결이 발생되기 전까지는 이전 분봉의 체결량이 해당 위치에 표시됩니다. 
    해당 분봉의 첫 체결이 발생되면 해당 이전분 체결량이 두번째 배열로 이동되면서 새로운 체결량으로 업데이트됩니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 123456)
        fid_input_hour_1 (str): [필수] 입력 시간1 (ex. 입력시간)
        fid_pw_data_incu_yn (str): [필수] 과거 데이터 포함 여부
        fid_etc_cls_code (str): [필수] 기타 구분 코드

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> output1, output2 = inquire_time_itemchartprice(env_dv="real", fid_cond_mrkt_div_code="J", fid_input_iscd="005930", fid_input_hour_1="093000", fid_pw_data_incu_yn="Y")
        >>> print(output1)
        >>> print(output2)
    """

    # 필수 파라미터 검증
    if env_dv == "" or env_dv is None:
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")
    
    if fid_cond_mrkt_div_code == "" or fid_cond_mrkt_div_code is None:
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:KRX, NX:NXT, UN:통합')")
    
    if fid_input_iscd == "" or fid_input_iscd is None:
        raise ValueError("fid_input_iscd is required (e.g. '123456')")
    
    if fid_input_hour_1 == "" or fid_input_hour_1 is None:
        raise ValueError("fid_input_hour_1 is required (e.g. '입력시간')")
    
    if fid_pw_data_incu_yn == "" or fid_pw_data_incu_yn is None:
        raise ValueError("fid_pw_data_incu_yn is required")

    # tr_id 설정 (실전/모의 동일)
    if env_dv == "real" or env_dv == "demo":
        tr_id = "FHKST03010200"
    else:
        raise ValueError("env_dv can only be real or demo")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_HOUR_1": fid_input_hour_1,
        "FID_PW_DATA_INCU_YN": fid_pw_data_incu_yn,
        "FID_ETC_CLS_CODE": fid_etc_cls_code
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # output1 (object) -> DataFrame (1행)
        output1_data = pd.DataFrame(res.getBody().output1, index=[0])
        
        # output2 (array) -> DataFrame (여러행)
        output2_data = pd.DataFrame(res.getBody().output2)
        
        return output1_data, output2_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 