"""
Created on 20250113 
@author: LaivData SJPark with cursor
"""


import sys
from typing import Optional

import pandas as pd
import logging

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 주식예약주문정정취소[v1_국내주식-018,019]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/trading/order-resv-rvsecncl"

def order_resv_rvsecncl(
    cano: str,  # [필수] 종합계좌번호
    acnt_prdt_cd: str,  # [필수] 계좌상품코드
    rsvn_ord_seq: str,  # [필수] 예약주문순번
    rsvn_ord_orgno: str,  # [필수] 예약주문조직번호
    rsvn_ord_ord_dt: str,  # [필수] 예약주문주문일자
    ord_type: str,  # [필수] 주문구분 (ex. cancel:취소, modify:정정)
    pdno: Optional[str] = "",  # 종목코드
    ord_qty: Optional[str] = "",  # 주문수량
    ord_unpr: Optional[str] = "",  # 주문단가
    sll_buy_dvsn_cd: Optional[str] = "",  # 매도매수구분코드 (ex. 01:매도, 02:매수)
    ord_dvsn_cd: Optional[str] = "",  # 주문구분코드 (ex. 00:지정가, 01:시장가, 02:조건부지정가, 05:장전 시간외)
    ord_objt_cblc_dvsn_cd: Optional[str] = "",  # 주문대상잔고구분코드 (ex. 10 : 현금, 12 : 주식담보대출, ... 28 : 자기대주상환)
    loan_dt: Optional[str] = "",  # 대출일자
    rsvn_ord_end_dt: Optional[str] = "",  # 예약주문종료일자
    ctal_tlno: Optional[str] = ""  # 연락전화번호
) -> pd.DataFrame:
    """
    국내주식 예약주문 정정/취소 API 입니다.
    *  정정주문은 취소주문에 비해 필수 입력값이 추가 됩니다. 
    하단의 입력값을 참조하시기 바랍니다.

    ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)
    
    Args:
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드
        rsvn_ord_seq (str): [필수] 예약주문순번
        rsvn_ord_orgno (str): [필수] 예약주문조직번호
        rsvn_ord_ord_dt (str): [필수] 예약주문주문일자
        ord_type (str): [필수] 주문구분 (ex. cancel:취소, modify:정정)
        pdno (Optional[str]): 종목코드
        ord_qty (Optional[str]): 주문수량
        ord_unpr (Optional[str]): 주문단가
        sll_buy_dvsn_cd (Optional[str]): 매도매수구분코드 (ex. 01:매도, 02:매수)
        ord_dvsn_cd (Optional[str]): 주문구분코드 (ex. 00:지정가, 01:시장가, 02:조건부지정가, 05:장전 시간외)
        ord_objt_cblc_dvsn_cd (Optional[str]): 주문대상잔고구분코드 (ex. 10 : 현금, 12 : 주식담보대출, ... 28 : 자기대주상환)
        loan_dt (Optional[str]): 대출일자
        rsvn_ord_end_dt (Optional[str]): 예약주문종료일자
        ctal_tlno (Optional[str]): 연락전화번호

    Returns:
        pd.DataFrame: 주식예약주문정정취소 결과 데이터
        
    Example:
        >>> df = order_resv_rvsecncl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, rsvn_ord_seq="88793", rsvn_ord_orgno="123", rsvn_ord_ord_dt="20250113", ord_type="cancel")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if cano == "" or cano is None:
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "" or acnt_prdt_cd is None:
        raise ValueError("acnt_prdt_cd is required")
    
    if rsvn_ord_seq == "" or rsvn_ord_seq is None:
        raise ValueError("rsvn_ord_seq is required")
    
    if rsvn_ord_orgno == "" or rsvn_ord_orgno is None:
        raise ValueError("rsvn_ord_orgno is required")
    
    if rsvn_ord_ord_dt == "" or rsvn_ord_ord_dt is None:
        raise ValueError("rsvn_ord_ord_dt is required")
    
    if ord_type == "" or ord_type is None:
        raise ValueError("ord_type is required")

    # tr_id 설정
    if ord_type == "cancel":
        tr_id = "CTSC0009U"
    elif ord_type == "modify":
        tr_id = "CTSC0013U"
    else:
        raise ValueError("ord_type can only be cancel or modify")
    
    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "RSVN_ORD_SEQ": rsvn_ord_seq,
        "RSVN_ORD_ORGNO": rsvn_ord_orgno,
        "RSVN_ORD_ORD_DT": rsvn_ord_ord_dt
    }
    
    # 옵션 파라미터 추가
    if pdno:
        params["PDNO"] = pdno
    if ord_qty:
        params["ORD_QTY"] = ord_qty
    if ord_unpr:
        params["ORD_UNPR"] = ord_unpr
    if sll_buy_dvsn_cd:
        params["SLL_BUY_DVSN_CD"] = sll_buy_dvsn_cd
    if ord_dvsn_cd:
        params["ORD_DVSN_CD"] = ord_dvsn_cd
    if ord_objt_cblc_dvsn_cd:
        params["ORD_OBJT_CBLC_DVSN_CD"] = ord_objt_cblc_dvsn_cd
    if loan_dt:
        params["LOAN_DT"] = loan_dt
    if rsvn_ord_end_dt:
        params["RSVN_ORD_END_DT"] = rsvn_ord_end_dt
    if ctal_tlno:
        params["CTAL_TLNO"] = ctal_tlno
    
    res = ka._url_fetch(API_URL, tr_id, "", params, postFlag=True)
    
    if res.isOK():
        current_data = pd.DataFrame([res.getBody().output])
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 