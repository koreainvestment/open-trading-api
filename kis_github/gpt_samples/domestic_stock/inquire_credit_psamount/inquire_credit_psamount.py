"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 신용매수가능조회[v1_국내주식-042]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/trading/inquire-credit-psamount"

def inquire_credit_psamount(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    pdno: str,  # 종목코드
    ord_dvsn: str,  # 주문구분
    crdt_type: str,  # 신용유형
    cma_evlu_amt_icld_yn: str,  # CMA평가금액포함여부
    ovrs_icld_yn: str,  # 해외포함여부
    ord_unpr: str = ""  # 주문단가
) -> pd.DataFrame:
    """
    신용매수가능조회 API입니다.
    신용매수주문 시 주문가능수량과 금액을 확인하실 수 있습니다.
    
    Args:
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드
        pdno (str): [필수] 종목코드
        ord_dvsn (str): [필수] 주문구분 (ex. 00 : 지정가, 01 : 시장가, 02 : 조건부지정가, 03 : 최유리지정가, 04 : 최우선지정가, 05 : 장전 시간외, 06 : 장후 시간외, 07 : 시간외 단일가 등)
        crdt_type (str): [필수] 신용유형 (ex. 21 : 자기융자신규, 23 : 유통융자신규, 26 : 유통대주상환, 28 : 자기대주상환, 25 : 자기융자상환, 27 : 유통융자상환, 22 : 유통대주신규, 24 : 자기대주신규)
        cma_evlu_amt_icld_yn (str): [필수] CMA평가금액포함여부
        ovrs_icld_yn (str): [필수] 해외포함여부
        ord_unpr (str): 주문단가 (ex. 1주당 가격. 장전/장후 시간외, 시장가의 경우 "0" 입력 권고)

    Returns:
        pd.DataFrame: 신용매수가능조회 데이터
        
    Example:
        >>> df = inquire_credit_psamount(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, pdno="005930", ord_dvsn="00", crdt_type="21", cma_evlu_amt_icld_yn="N", ovrs_icld_yn="N")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if cano == "" or cano is None:
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "" or acnt_prdt_cd is None:
        raise ValueError("acnt_prdt_cd is required")
    
    if pdno == "" or pdno is None:
        raise ValueError("pdno is required")
    
    if ord_dvsn == "" or ord_dvsn is None:
        raise ValueError("ord_dvsn is required (e.g. '00 : 지정가, 01 : 시장가, 02 : 조건부지정가, 03 : 최유리지정가, 04 : 최우선지정가, 05 : 장전 시간외, 06 : 장후 시간외, 07 : 시간외 단일가 등')")
    
    if crdt_type == "" or crdt_type is None:
        raise ValueError("crdt_type is required (e.g. '21 : 자기융자신규, 23 : 유통융자신규, 26 : 유통대주상환, 28 : 자기대주상환, 25 : 자기융자상환, 27 : 유통융자상환, 22 : 유통대주신규, 24 : 자기대주신규')")
    
    if cma_evlu_amt_icld_yn == "" or cma_evlu_amt_icld_yn is None:
        raise ValueError("cma_evlu_amt_icld_yn is required")
    
    if ovrs_icld_yn == "" or ovrs_icld_yn is None:
        raise ValueError("ovrs_icld_yn is required")

    tr_id = "TTTC8909R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "ORD_DVSN": ord_dvsn,
        "CRDT_TYPE": crdt_type,
        "CMA_EVLU_AMT_ICLD_YN": cma_evlu_amt_icld_yn,
        "OVRS_ICLD_YN": ovrs_icld_yn,
        "ORD_UNPR": ord_unpr
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output, index=[0])
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 