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
# [국내선물옵션] 주문/계좌 > 선물옵션 정정취소주문[v1_국내선물-002]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-futureoption/v1/trading/order-rvsecncl"

def order_rvsecncl(
    env_dv: str,                    # [필수] 실전모의구분 (ex. real:실전, demo:모의)
    day_dv: str,                    # [필수] 주야간구분 (ex. day:주간, night:야간)
    ord_prcs_dvsn_cd: str,          # [필수] 주문처리구분코드 (ex. 02)
    cano: str,                      # [필수] 종합계좌번호
    acnt_prdt_cd: str,              # [필수] 계좌상품코드
    rvse_cncl_dvsn_cd: str,         # [필수] 정정취소구분코드 (ex. 01:정정, 02:취소)
    orgn_odno: str,                 # [필수] 원주문번호
    ord_qty: str,                   # [필수] 주문수량 (ex. 0:전량, 그 외는 수량)
    unit_price: str,                # [필수] 주문가격1 (ex 0:시장가/최유리, 그 외 가격)
    nmpr_type_cd: str,              # [필수] 호가유형코드 (ex. 01:지정가, 02:시장가, 03:조건부, 04:최유리)
    krx_nmpr_cndt_cd: str,          # [필수] 한국거래소호가조건코드 (ex. 0:취소/없음, 3:IOC, 4:FOK)
    rmn_qty_yn: str,                # [필수] 잔여수량여부 (ex. Y:전량, N:일부)
    ord_dvsn_cd: str,               # [필수] 주문구분코드
    fuop_item_dvsn_cd: str = ""     # 선물옵션종목구분코드
) -> pd.DataFrame:
    """
    선물옵션 주문 건에 대하여 정정 및 취소하는 API입니다. 단, 이미 체결된 건은 정정 및 취소가 불가합니다.

    ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        day_dv (str): [필수] 주야간구분 (ex. day:주간, night:야간)
        ord_prcs_dvsn_cd (str): [필수] 주문처리구분코드 (ex. 02)
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드
        rvse_cncl_dvsn_cd (str): [필수] 정정취소구분코드 (ex. 01:정정, 02:취소)
        orgn_odno (str): [필수] 원주문번호
        ord_qty (str): [필수] 주문수량 (ex. 0:전량, 그 외는 수량)
        unit_price (str): [필수] 주문가격1 (ex 0:시장가/최유리, 그 외 가격)
        nmpr_type_cd (str): [필수] 호가유형코드 (ex. 01:지정가, 02:시장가, 03:조건부, 04:최유리)
        krx_nmpr_cndt_cd (str): [필수] 한국거래소호가조건코드 (ex. 0:취소/없음, 3:IOC, 4:FOK)
        rmn_qty_yn (str): [필수] 잔여수량여부 (ex. Y:전량, N:일부)
        ord_dvsn_cd (str): [필수] 주문구분코드
        fuop_item_dvsn_cd (str): 선물옵션종목구분코드

    Returns:
        pd.DataFrame: 선물옵션 정정취소주문 결과 데이터
        
    Example:
        >>> df = order_rvsecncl(
        ...     env_dv="real", day_dv="day", ord_prcs_dvsn_cd="02",
        ...     cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, rvse_cncl_dvsn_cd="02",
        ...     orgn_odno="0000004018", ord_qty="0", unit_price="0",
        ...     nmpr_type_cd="02", krx_nmpr_cndt_cd="0", rmn_qty_yn="Y",
        ...     ord_dvsn_cd="01"
        ... )
        >>> print(df)
    """
    
    # tr_id 설정
    if env_dv == "real":
        if day_dv == "day":
            tr_id = "TTTO1103U"
        elif day_dv == "night":
            tr_id = "TTTN1103U"
        else:
            raise ValueError("day_dv can only be 'day' or 'night'")
    elif env_dv == "demo":
        if day_dv == "day":
            tr_id = "VTTO1103U"
        else:
            raise ValueError("day_dv can only be 'day' for demo environment")
    else:
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")

    params = {
        "ORD_PRCS_DVSN_CD": ord_prcs_dvsn_cd,
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "RVSE_CNCL_DVSN_CD": rvse_cncl_dvsn_cd,
        "ORGN_ODNO": orgn_odno,
        "ORD_QTY": ord_qty,
        "UNIT_PRICE": unit_price,
        "NMPR_TYPE_CD": nmpr_type_cd,
        "KRX_NMPR_CNDT_CD": krx_nmpr_cndt_cd,
        "RMN_QTY_YN": rmn_qty_yn,
        "ORD_DVSN_CD": ord_dvsn_cd,
        "FUOP_ITEM_DVSN_CD": fuop_item_dvsn_cd
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params, postFlag=True)
    
    if res.isOK():
        return pd.DataFrame(res.getBody().output)
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 