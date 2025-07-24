"""
Created on 20250112 
@author: LaivData SJPark with cursor
"""


import sys
from typing import Optional
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 주식주문(정정취소)[v1_국내주식-003]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/trading/order-rvsecncl"

def order_rvsecncl(
    env_dv: str,                    # [필수] 실전모의구분 (ex. real:실전, demo:모의)
    cano: str,                      # [필수] 종합계좌번호
    acnt_prdt_cd: str,              # [필수] 계좌상품코드
    krx_fwdg_ord_orgno: str,        # [필수] 한국거래소전송주문조직번호
    orgn_odno: str,                 # [필수] 원주문번호
    ord_dvsn: str,                  # [필수] 주문구분
    rvse_cncl_dvsn_cd: str,         # [필수] 정정취소구분코드 (ex. 01:정정,02:취소)
    ord_qty: str,                   # [필수] 주문수량
    ord_unpr: str,                  # [필수] 주문단가
    qty_all_ord_yn: str,            # [필수] 잔량전부주문여부 (ex. Y:전량, N:일부)
    excg_id_dvsn_cd: str,           # [필수] 거래소ID구분코드 (ex. KRX: 한국거래소, NXT:대체거래소,SOR:SOR)
    cndt_pric: Optional[str] = ""   # 조건가격
) -> pd.DataFrame:
    """
    주문 건에 대하여 정정 및 취소하는 API입니다. 단, 이미 체결된 건은 정정 및 취소가 불가합니다.

    ※ 정정은 원주문에 대한 주문단가 혹은 주문구분을 변경하는 사항으로, 정정이 가능한 수량은 원주문수량을 초과 할 수 없습니다.

    ※ 주식주문(정정취소) 호출 전에 반드시 주식정정취소가능주문조회 호출을 통해 정정취소가능수량(output > psbl_qty)을 확인하신 후 정정취소주문 내시기 바랍니다.

    ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드
        krx_fwdg_ord_orgno (str): [필수] 한국거래소전송주문조직번호
        orgn_odno (str): [필수] 원주문번호
        ord_dvsn (str): [필수] 주문구분
        rvse_cncl_dvsn_cd (str): [필수] 정정취소구분코드 (ex. 01:정정,02:취소)
        ord_qty (str): [필수] 주문수량
        ord_unpr (str): [필수] 주문단가
        qty_all_ord_yn (str): [필수] 잔량전부주문여부 (ex. Y:전량, N:일부)
        excg_id_dvsn_cd (str): [필수] 거래소ID구분코드 (ex. KRX: 한국거래소, NXT:대체거래소,SOR:SOR)
        cndt_pric (Optional[str]): 조건가격

    Returns:
        pd.DataFrame: 주식주문(정정취소) 결과 데이터
        
    Example:
        >>> df = order_rvsecncl(env_dv="real", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, ...)
        >>> print(df)
    """

    # 필수 파라미터 검증
    if env_dv == "" or env_dv is None:
        raise ValueError("env_dv is required (e.g. 'real', 'demo')")
    
    if cano == "" or cano is None:
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "" or acnt_prdt_cd is None:
        raise ValueError("acnt_prdt_cd is required")
    
    if krx_fwdg_ord_orgno == "" or krx_fwdg_ord_orgno is None:
        raise ValueError("krx_fwdg_ord_orgno is required")
    
    if orgn_odno == "" or orgn_odno is None:
        raise ValueError("orgn_odno is required")
    
    if ord_dvsn == "" or ord_dvsn is None:
        raise ValueError("ord_dvsn is required")
    
    if rvse_cncl_dvsn_cd == "" or rvse_cncl_dvsn_cd is None:
        raise ValueError("rvse_cncl_dvsn_cd is required (e.g. '01', '02')")
    
    if ord_qty == "" or ord_qty is None:
        raise ValueError("ord_qty is required")
    
    if ord_unpr == "" or ord_unpr is None:
        raise ValueError("ord_unpr is required")
    
    if qty_all_ord_yn == "" or qty_all_ord_yn is None:
        raise ValueError("qty_all_ord_yn is required (e.g. 'Y', 'N')")
    
    if excg_id_dvsn_cd == "" or excg_id_dvsn_cd is None:
        raise ValueError("excg_id_dvsn_cd is required (e.g. 'KRX', 'NXT', 'SOR')")

    # tr_id 설정
    if env_dv == "real":
        tr_id = "TTTC0013U"
    elif env_dv == "demo":
        tr_id = "VTTC0013U"
    else:
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "KRX_FWDG_ORD_ORGNO": krx_fwdg_ord_orgno,
        "ORGN_ODNO": orgn_odno,
        "ORD_DVSN": ord_dvsn,
        "RVSE_CNCL_DVSN_CD": rvse_cncl_dvsn_cd,
        "ORD_QTY": ord_qty,
        "ORD_UNPR": ord_unpr,
        "QTY_ALL_ORD_YN": qty_all_ord_yn,
        "EXCG_ID_DVSN_CD": excg_id_dvsn_cd
    }
    
    # 옵션 파라미터 추가
    if cndt_pric:
        params["CNDT_PRIC"] = cndt_pric
    
    res = ka._url_fetch(API_URL, tr_id, "", params, postFlag=True)
    
    if res.isOK():
        return pd.DataFrame([res.getBody().output])
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 