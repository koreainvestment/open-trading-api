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
# [국내주식] 주문/계좌 > 퇴직연금 예수금조회[v1_국내주식-035]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/trading/pension/inquire-deposit"

def pension_inquire_deposit(
    cano: str,              # 종합계좌번호 (12345678)
    acnt_prdt_cd: str,      # 계좌상품코드 (29)
    acca_dvsn_cd: str       # 적립금구분코드 (00)
) -> pd.DataFrame:
    """
    ​※ 55번 계좌(DC가입자계좌)의 경우 해당 API 이용이 불가합니다.
    KIS Developers API의 경우 HTS ID에 반드시 연결되어있어야만 API 신청 및 앱정보 발급이 가능한 서비스로 개발되어서 실물계좌가 아닌 55번 계좌는 API 이용이 불가능한 점 양해 부탁드립니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 29)
        acca_dvsn_cd (str): [필수] 적립금구분코드 (ex. 00)

    Returns:
        pd.DataFrame: 퇴직연금 예수금 데이터
        
    Example:
        >>> df = pension_inquire_deposit(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, acca_dvsn_cd="00")
        >>> print(df)
    """

    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '29')")
    
    if acca_dvsn_cd == "":
        raise ValueError("acca_dvsn_cd is required (e.g. '00')")

    tr_id = "TTTC0506R"  # 퇴직연금 예수금조회

    params = {
        "CANO": cano,                    # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,    # 계좌상품코드
        "ACCA_DVSN_CD": acca_dvsn_cd     # 적립금구분코드
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame([res.getBody().output])
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 