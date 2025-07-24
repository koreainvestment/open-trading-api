"""
Created on 20250116
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
# [국내선물옵션] 주문/계좌 > 선물옵션 주문[v1_국내선물-001]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-futureoption/v1/trading/order"

def order(
    env_dv: str,  # 실전모의구분
    ord_dv: str,  # 매도매수구분  
    ord_prcs_dvsn_cd: str,  # 주문처리구분코드
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    sll_buy_dvsn_cd: str,  # 매도매수구분코드
    shtn_pdno: str,  # 단축상품번호
    ord_qty: str,  # 주문수량
    unit_price: str,  # 주문가격1
    nmpr_type_cd: str,  # 호가유형코드
    krx_nmpr_cndt_cd: str,  # 한국거래소호가조건코드
    ord_dvsn_cd: str,  # 주문구분코드
    ctac_tlno: str = "",  # 연락전화번호
    fuop_item_dvsn_cd: str = ""  # 선물옵션종목구분코드
) -> pd.DataFrame:
    """
    [국내선물옵션] 주문/계좌 > 선물옵션 주문[v1_국내선물-001]
    선물옵션 주문 API입니다.
    * 선물옵션 운영시간 외 API 호출 시 애러가 발생하오니 운영시간을 확인해주세요.

    ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)

    ※ 종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        ord_dv (str): [필수] 매도매수구분 (ex. day:주간, night:야간)
        ord_prcs_dvsn_cd (str): [필수] 주문처리구분코드 (ex. 02:주문전송)
        cano (str): [필수] 종합계좌번호 (ex. 계좌번호 체계(8-2)의 앞 8자리)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 계좌번호 체계(8-2)의 뒤 2자리)
        sll_buy_dvsn_cd (str): [필수] 매도매수구분코드 (ex. 01:매도, 02:매수)
        shtn_pdno (str): [필수] 단축상품번호 (ex. 종목번호, 선물 6자리 (예: 101W09), 옵션 9자리 (예: 201S03370))
        ord_qty (str): [필수] 주문수량
        unit_price (str): [필수] 주문가격1 (ex. 시장가나 최유리 지정가인 경우 0으로 입력)
        nmpr_type_cd (str): [필수] 호가유형코드 (ex. 01:지정가, 02:시장가, 03:조건부, 04:최유리)
        krx_nmpr_cndt_cd (str): [필수] 한국거래소호가조건코드 (ex. 0:없음, 3:IOC, 4:FOK)
        ord_dvsn_cd (str): [필수] 주문구분코드 (ex. 01:지정가, 02:시장가, 03:조건부, 04:최유리, 10:지정가(IOC), 11:지정가(FOK), 12:시장가(IOC), 13:시장가(FOK), 14:최유리(IOC), 15:최유리(FOK))
        ctac_tlno (str): 연락전화번호 (ex. 고객의 연락 가능한 전화번호)
        fuop_item_dvsn_cd (str): 선물옵션종목구분코드 (ex. 공란(Default))

    Returns:
        pd.DataFrame: 선물옵션 주문 결과 데이터
        
    Example:
        >>> df = order(env_dv="real", ord_dv="day", ord_prcs_dvsn_cd="02", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, sll_buy_dvsn_cd="02", shtn_pdno="101W09", ord_qty="1", unit_price="0", nmpr_type_cd="02", krx_nmpr_cndt_cd="0", ord_dvsn_cd="02")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real', 'demo')")
    
    if ord_dv == "":
        raise ValueError("ord_dv is required (e.g. 'day', 'night')")
        
    if ord_prcs_dvsn_cd == "":
        raise ValueError("ord_prcs_dvsn_cd is required (e.g. '02')")
        
    if cano == "":
        raise ValueError("cano is required (e.g. '계좌번호 체계(8-2)의 앞 8자리')")
        
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '계좌번호 체계(8-2)의 뒤 2자리')")
        
    if sll_buy_dvsn_cd == "":
        raise ValueError("sll_buy_dvsn_cd is required (e.g. '01', '02')")
        
    if shtn_pdno == "":
        raise ValueError("shtn_pdno is required (e.g. '101W09', '201S03370')")
        
    if ord_qty == "":
        raise ValueError("ord_qty is required")
        
    if unit_price == "":
        raise ValueError("unit_price is required (e.g. '0')")
        
    if nmpr_type_cd == "":
        raise ValueError("nmpr_type_cd is required (e.g. '01', '02', '03', '04')")
        
    if krx_nmpr_cndt_cd == "":
        raise ValueError("krx_nmpr_cndt_cd is required (e.g. '0', '3', '4')")
        
    if ord_dvsn_cd == "":
        raise ValueError("ord_dvsn_cd is required (e.g. '01', '02', '03', '04', '10', '11', '12', '13', '14', '15')")

    # tr_id 설정
    if env_dv == "real":
        if ord_dv == "day":
            tr_id = "TTTO1101U"
        elif ord_dv == "night":
            tr_id = "STTN1101U"
        else:
            raise ValueError("ord_dv can only be 'day' or 'night'")
    elif env_dv == "demo":
        if ord_dv == "day":
            tr_id = "VTTO1101U" 
        else:
            raise ValueError("ord_dv can only be 'day' for demo environment")
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "ORD_PRCS_DVSN_CD": ord_prcs_dvsn_cd,
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "SHTN_PDNO": shtn_pdno,
        "ORD_QTY": ord_qty,
        "UNIT_PRICE": unit_price,
        "NMPR_TYPE_CD": nmpr_type_cd,
        "KRX_NMPR_CNDT_CD": krx_nmpr_cndt_cd,
        "ORD_DVSN_CD": ord_dvsn_cd,
        "CTAC_TLNO": ctac_tlno,
        "FUOP_ITEM_DVSN_CD": fuop_item_dvsn_cd
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params, postFlag=True)
    
    if res.isOK():
        return pd.DataFrame(res.getBody().output, index=[0])
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 