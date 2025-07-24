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
# [국내주식] 주문/계좌 > 퇴직연금 매수가능조회[v1_국내주식-034]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/trading/pension/inquire-psbl-order"

def pension_inquire_psbl_order(
    cano: str,                      # [필수] 종합계좌번호 (ex. 12345678)
    acnt_prdt_cd: str,             # [필수] 계좌상품코드 (ex. 29)
    pdno: str,                     # [필수] 상품번호 (ex. 123456)
    acca_dvsn_cd: str,            # [필수] 적립금구분코드 (ex. 00)
    cma_evlu_amt_icld_yn: str,    # [필수] CMA평가금액포함여부 (ex. Y:포함, N:미포함)
    ord_unpr: str,                # [필수] 주문단가
    ord_dvsn: str                 # [필수] 주문구분 (ex. 00: 지정가, 01: 시장가)
) -> pd.DataFrame:
    """
    [국내주식] 주문/계좌 > 퇴직연금 매수가능조회[v1_국내주식-034]
    
    ※ 55번 계좌(DC가입자계좌)의 경우 해당 API 이용이 불가합니다.
    KIS Developers API의 경우 HTS ID에 반드시 연결되어있어야만 API 신청 및 앱정보 발급이 가능한 서비스로 개발되어서 실물계좌가 아닌 55번 계좌는 API 이용이 불가능한 점 양해 부탁드립니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 29)
        pdno (str): [필수] 상품번호 (ex. 123456)
        acca_dvsn_cd (str): [필수] 적립금구분코드 (ex. 00)
        cma_evlu_amt_icld_yn (str): [필수] CMA평가금액포함여부 (ex. Y:포함, N:미포함)
        ord_unpr (str): [필수] 주문단가
        ord_dvsn (str): [필수] 주문구분 (ex. 00: 지정가, 01: 시장가)

    Returns:
        pd.DataFrame: 퇴직연금 매수가능조회 데이터
        
    Example:
        >>> df = pension_inquire_psbl_order(
        ...     cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod,
        ...     pdno="069500",
        ...     acca_dvsn_cd="00",
        ...     cma_evlu_amt_icld_yn="Y",
        ...     ord_unpr="30800",
        ...     ord_dvsn="00"
        ... )
        >>> print(df)
    """

    # 필수 파라미터 검증
    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '29')")
    
    if pdno == "":
        raise ValueError("pdno is required (e.g. '123456')")
    
    if acca_dvsn_cd == "":
        raise ValueError("acca_dvsn_cd is required (e.g. '00')")
    
    if cma_evlu_amt_icld_yn == "":
        raise ValueError("cma_evlu_amt_icld_yn is required (e.g. 'Y:포함, N:미포함')")
    
    if ord_unpr == "":
        raise ValueError("ord_unpr is required")
    
    if ord_dvsn == "":
        raise ValueError("ord_dvsn is required (e.g. '00: 지정가, 01: 시장가')")

    tr_id = "TTTC0503R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "ACCA_DVSN_CD": acca_dvsn_cd,
        "CMA_EVLU_AMT_ICLD_YN": cma_evlu_amt_icld_yn,
        "ORD_UNPR": ord_unpr,
        "ORD_DVSN": ord_dvsn
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output, index=[0])
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 