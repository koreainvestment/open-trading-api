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
# [국내주식] 주문/계좌 > 주식예약주문[v1_국내주식-017]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/trading/order-resv"

def order_resv(
    cano: str,
    acnt_prdt_cd: str,
    pdno: str,
    ord_qty: str,
    ord_unpr: str,
    sll_buy_dvsn_cd: str,
    ord_dvsn_cd: str,
    ord_objt_cblc_dvsn_cd: str,
    loan_dt: Optional[str] = "",
    rsvn_ord_end_dt: Optional[str] = "",
    ldng_dt: Optional[str] = ""
) -> pd.DataFrame:
    """
    국내주식 예약주문 매수/매도 API 입니다.

    ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)

    ※ 유의사항
    1. 예약주문 가능시간 : 15시 40분 ~ 다음 영업일 7시 30분 
        (단, 서버 초기화 작업 시 예약주문 불가 : 23시 40분 ~ 00시 10분)
        ※ 예약주문 처리내역은 통보되지 않으므로 주문처리일 장 시작전에 반드시 주문처리 결과를 확인하시기 바랍니다.

    2. 예약주문 안내
    - 예약종료일 미입력 시 일반예약주문으로 최초 도래하는 영업일에 주문 전송됩니다.
    - 예약종료일 입력 시 기간예약주문으로 최초 예약주문수량 중 미체결 된 수량에 대해 예약종료일까지 매 영업일 주문이
        실행됩니다. (예약종료일은 익영업일부터 달력일 기준으로 공휴일 포함하여 최대 30일이 되는 일자까지 입력가능)
    - 예약주문 접수 처리순서는 일반/기간예약주문 중 신청일자가 빠른 주문이 우선합니다.
        단, 기간예약주문 자동배치시간(약 15시35분 ~ 15시55분)사이 접수되는 주문의 경우 당일에 한해 순서와 상관없이
        처리될 수 있습니다.
    - 기간예약주문 자동배치시간(약 15시35분 ~ 15시55분)에는 예약주문 조회가 제한 될 수 있습니다.
    - 기간예약주문은 계좌 당 주문건수 최대 1,000건으로 제한됩니다.

    3. 예약주문 접수내역 중 아래의 사유 등으로 인해 주문이 거부될 수 있사오니, 주문처리일 장 시작전에 반드시
        주문처리 결과를 확인하시기 바랍니다.
        * 주문처리일 기준 : 매수가능금액 부족, 매도가능수량 부족, 주문수량/호가단위 오류, 대주 호가제한, 
                                신용/대주가능종목 변경, 상/하한폭 변경, 시가형성 종목(신규상장 등)의 시장가, 거래서비스 미신청 등

    4. 익일 예상 상/하한가는 조회시점의 현재가로 계산되며 익일의 유/무상증자, 배당, 감자, 합병, 액면변경 등에 의해
        변동될 수 있으며 이로 인해 상/하한가를 벗어나 주문이 거부되는 경우가 발생할 수 있사오니, 주문처리일 장 시작전에
        반드시 주문처리결과를 확인하시기 바랍니다.

    5. 정리매매종목, ELW, 신주인수권증권, 신주인수권증서 등은 가격제한폭(상/하한가) 적용 제외됩니다.

    6. 영업일 장 시작 후 [기간예약주문] 내역 취소는 해당시점 이후의 예약주문이 취소되는 것으로, 
        일반주문으로 이미 전환된 주문에는 영향을 미치지 않습니다. 반드시 장 시작전 주문처리결과를 확인하시기 바랍니다. 
    
    Args:
        cano (str): [필수] 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        pdno (str): [필수] 종목코드(6자리)
        ord_qty (str): [필수] 주문수량 (주0문주식수)
        ord_unpr (str): [필수] 주문단가 (1주당 가격, 시장가/장전 시간외는 0 입력)
        sll_buy_dvsn_cd (str): [필수] 매도매수구분코드 (01 : 매도, 02 : 매수)
        ord_dvsn_cd (str): [필수] 주문구분코드 (00 : 지정가, 01 : 시장가, 02 : 조건부지정가, 05 : 장전 시간외)
        ord_objt_cblc_dvsn_cd (str): [필수] 주문대상잔고구분코드 (10: 현금, 12~28: 각종 대출/상환코드)
        loan_dt (Optional[str]): 대출일자
        rsvn_ord_end_dt (Optional[str]): 예약주문종료일자 (YYYYMMDD, 익영업일부터 최대 30일 이내)
        ldng_dt (Optional[str]): 대여일자

    Returns:
        pd.DataFrame: 예약주문 결과 데이터
        
    Example:
        >>> df = order_resv(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, pdno="005930", ord_qty="1", ord_unpr="55000", sll_buy_dvsn_cd="02", ord_dvsn_cd="00", ord_objt_cblc_dvsn_cd="10")
        >>> print(df)
    """

    if cano == "" or cano is None:
        raise ValueError("cano is required (e.g. '계좌번호 체계(8-2)의 앞 8자리')")
    
    if acnt_prdt_cd == "" or acnt_prdt_cd is None:
        raise ValueError("acnt_prdt_cd is required (e.g. '계좌번호 체계(8-2)의 뒤 2자리')")
    
    if pdno == "" or pdno is None:
        raise ValueError("pdno is required (e.g. '종목코드(6자리)')")
    
    if ord_qty == "" or ord_qty is None:
        raise ValueError("ord_qty is required (e.g. '주0문주식수')")
    
    if ord_unpr == "" or ord_unpr is None:
        raise ValueError("ord_unpr is required (e.g. '1주당 가격, 시장가/장전 시간외는 0 입력')")
    
    if sll_buy_dvsn_cd == "" or sll_buy_dvsn_cd is None:
        raise ValueError("sll_buy_dvsn_cd is required (e.g. '01 : 매도, 02 : 매수')")
    
    if ord_dvsn_cd == "" or ord_dvsn_cd is None:
        raise ValueError("ord_dvsn_cd is required (e.g. '00 : 지정가, 01 : 시장가, 02 : 조건부지정가, 05 : 장전 시간외')")
    
    if ord_objt_cblc_dvsn_cd == "" or ord_objt_cblc_dvsn_cd is None:
        raise ValueError("ord_objt_cblc_dvsn_cd is required (e.g. '10: 현금, 12~28: 각종 대출/상환코드')")

    tr_id = "CTSC0008U"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "ORD_QTY": ord_qty,
        "ORD_UNPR": ord_unpr,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "ORD_DVSN_CD": ord_dvsn_cd,
        "ORD_OBJT_CBLC_DVSN_CD": ord_objt_cblc_dvsn_cd
    }
    
    if loan_dt:
        params["LOAN_DT"] = loan_dt
    if rsvn_ord_end_dt:
        params["RSVN_ORD_END_DT"] = rsvn_ord_end_dt
    if ldng_dt:
        params["LDNG_DT"] = ldng_dt
    
    res = ka._url_fetch(API_URL, tr_id, "", params, postFlag=True)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output, index=[0])
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 