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
# [국내선물옵션] 주문/계좌 > 선물옵션 주문가능[v1_국내선물-005]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-futureoption/v1/trading/inquire-psbl-order"

def inquire_psbl_order(
    env_dv: str,         # [필수] 실전모의구분 (ex. real:실전, demo:모의)
    cano: str,           # [필수] 종합계좌번호
    acnt_prdt_cd: str,   # [필수] 계좌상품코드 (ex. 03)
    pdno: str,           # [필수] 상품번호 (ex. 선물 6자리, 옵션 9자리)
    sll_buy_dvsn_cd: str, # [필수] 매도매수구분코드 (ex. 01:매도,02:매수)
    unit_price: str,     # [필수] 주문가격1
    ord_dvsn_cd: str     # [필수] 주문구분코드
) -> pd.DataFrame:
    """
    선물옵션 주문가능 API입니다. 주문가능 내역과 수량을 확인하실 수 있습니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 03)
        pdno (str): [필수] 상품번호 (ex. 선물 6자리, 옵션 9자리)
        sll_buy_dvsn_cd (str): [필수] 매도매수구분코드 (ex. 01:매도,02:매수)
        unit_price (str): [필수] 주문가격1
        ord_dvsn_cd (str): [필수] 주문구분코드

    Returns:
        pd.DataFrame: 선물옵션 주문가능 데이터
        
    Example:
        >>> df = inquire_psbl_order(env_dv="real", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod,
        ...                                    pdno="101W09", sll_buy_dvsn_cd="02", unit_price="1", ord_dvsn_cd="01")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")
    
    if cano == "":
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '03')")
    
    if pdno == "":
        raise ValueError("pdno is required (e.g. '101W09')")
    
    if sll_buy_dvsn_cd == "":
        raise ValueError("sll_buy_dvsn_cd is required (e.g. '01' or '02')")
    
    if unit_price == "":
        raise ValueError("unit_price is required")
    
    if ord_dvsn_cd == "":
        raise ValueError("ord_dvsn_cd is required")

    # tr_id 설정
    if env_dv == "real":
        tr_id = "TTTO5105R"
    elif env_dv == "demo":
        tr_id = "VTTO5105R"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "UNIT_PRICE": unit_price,
        "ORD_DVSN_CD": ord_dvsn_cd
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame([res.getBody().output])
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 