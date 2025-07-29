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
# [국내주식] 기본시세 > 주식현재가 일자별[v1_국내주식-010]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-daily-price"

def inquire_daily_price(
    env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
    fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
    fid_input_iscd: str,  # [필수] 입력 종목코드 (ex. 종목코드 (ex 005930 삼성전자))
    fid_period_div_code: str,  # [필수] 기간 분류 코드 (ex. D:(일)최근 30거래일, W:(주)최근 30주, M:(월)최근 30개월)
    fid_org_adj_prc: str  # [필수] 수정주가 원주가 가격 (ex. 0:수정주가미반영, 1:수정주가반영, *수정주가는 액면분할/액면병합 등 권리 발생 시 과거 시세를 현재 주가에 맞게 보정한 가격)
) -> pd.DataFrame:
    """
    주식현재가 일자별 API입니다. 일/주/월별 주가를 확인할 수 있으며 최근 30일(주,별)로 제한되어 있습니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)  
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 종목코드 (ex 005930 삼성전자))
        fid_period_div_code (str): [필수] 기간 분류 코드 (ex. D:(일)최근 30거래일, W:(주)최근 30주, M:(월)최근 30개월)
        fid_org_adj_prc (str): [필수] 수정주가 원주가 가격 (ex. 0:수정주가미반영, 1:수정주가반영, *수정주가는 액면분할/액면병합 등 권리 발생 시 과거 시세를 현재 주가에 맞게 보정한 가격)

    Returns:
        pd.DataFrame: 주식현재가 일자별 데이터
        
    Raises:
        ValueError: 필수 파라미터가 누락된 경우
        
    Example:
        >>> df = inquire_daily_price("real", "J", "005930", "D", "1")
        >>> print(df)
    """
    
    # 필수 파라미터 검증
    if env_dv == "" or env_dv is None:
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")
    
    if fid_cond_mrkt_div_code == "" or fid_cond_mrkt_div_code is None:
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:KRX, NX:NXT, UN:통합')")
    
    if fid_input_iscd == "" or fid_input_iscd is None:
        raise ValueError("fid_input_iscd is required (e.g. '종목코드 (ex 005930 삼성전자)')")
    
    if fid_period_div_code == "" or fid_period_div_code is None:
        raise ValueError("fid_period_div_code is required (e.g. 'D:(일)최근 30거래일, W:(주)최근 30주, M:(월)최근 30개월')")
    
    if fid_org_adj_prc == "" or fid_org_adj_prc is None:
        raise ValueError("fid_org_adj_prc is required (e.g. '0:수정주가미반영, 1:수정주가반영, *수정주가는 액면분할/액면병합 등 권리 발생 시 과거 시세를 현재 주가에 맞게 보정한 가격')")

    # tr_id 설정 (실전/모의 모두 동일)
    if env_dv == "real":
        tr_id = "FHKST01010400"
    elif env_dv == "demo":
        tr_id = "FHKST01010400"
    else:
        raise ValueError("env_dv can only be real or demo")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_PERIOD_DIV_CODE": fid_period_div_code,
        "FID_ORG_ADJ_PRC": fid_org_adj_prc
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # output은 array 자료형이므로 DataFrame으로 변환
        current_data = pd.DataFrame(res.getBody().output)
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 