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
# [국내선물옵션] 주문/계좌 > (야간)선물옵션 주문가능 조회 [국내선물-011]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-futureoption/v1/trading/inquire-psbl-ngt-order"

def inquire_psbl_ngt_order(
    cano: str,                 # 종합계좌번호
    acnt_prdt_cd: str,         # 계좌상품코드
    pdno: str,                 # 상품번호
    prdt_type_cd: str,         # 상품유형코드
    sll_buy_dvsn_cd: str,      # 매도매수구분코드
    unit_price: str,           # 주문가격1
    ord_dvsn_cd: str           # 주문구분코드
) -> pd.DataFrame:
    """
    (야간)선물옵션 주문가능 조회 API입니다.
    
    Args:
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드
        pdno (str): [필수] 상품번호
        prdt_type_cd (str): [필수] 상품유형코드 (ex. 301:선물옵션)
        sll_buy_dvsn_cd (str): [필수] 매도매수구분코드 (ex. 01:매도, 02:매수)
        unit_price (str): [필수] 주문가격1
        ord_dvsn_cd (str): [필수] 주문구분코드 (ex. 01:지정가, 02:시장가, 03:조건부, 04:최유리, 10:지정가(IOC), 11:지정가(FOK), 12:시장가(IOC), 13:시장가(FOK), 14:최유리(IOC), 15:최유리(FOK))

    Returns:
        pd.DataFrame: (야간)선물옵션 주문가능 데이터
        
    Example:
        >>> df = inquire_psbl_ngt_order(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, pdno="101W09", prdt_type_cd="301", sll_buy_dvsn_cd="02", unit_price="322", ord_dvsn_cd="01")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if cano == "" or cano is None:
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "" or acnt_prdt_cd is None:
        raise ValueError("acnt_prdt_cd is required")
    
    if pdno == "" or pdno is None:
        raise ValueError("pdno is required")
    
    if prdt_type_cd == "" or prdt_type_cd is None:
        raise ValueError("prdt_type_cd is required (e.g. '301')")
    
    if sll_buy_dvsn_cd == "" or sll_buy_dvsn_cd is None:
        raise ValueError("sll_buy_dvsn_cd is required (e.g. '01', '02')")
    
    if unit_price == "" or unit_price is None:
        raise ValueError("unit_price is required")
    
    if ord_dvsn_cd == "" or ord_dvsn_cd is None:
        raise ValueError("ord_dvsn_cd is required (e.g. '01', '02', '03', '04', '10', '11', '12', '13', '14', '15')")

    tr_id = "STTN5105R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "PRDT_TYPE_CD": prdt_type_cd,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "UNIT_PRICE": unit_price,
        "ORD_DVSN_CD": ord_dvsn_cd
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame([res.getBody().output])
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 