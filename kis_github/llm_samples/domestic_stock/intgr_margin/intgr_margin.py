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
# [국내주식] 주문/계좌 > 주식통합증거금 현황 [국내주식-191]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/trading/intgr-margin"

def intgr_margin(
    cano: str,  # [필수] 종합계좌번호 (ex. 12345678)
    acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 01)
    cma_evlu_amt_icld_yn: str,  # [필수] CMA평가금액포함여부 (ex. Y: 포함, N: 미포함)
    wcrc_frcr_dvsn_cd: str,  # [필수] 원화외화구분코드 (ex. 01: 외화기준, 02: 원화기준)
    fwex_ctrt_frcr_dvsn_cd: str  # [필수] 선도환계약외화구분코드 (ex. 01: 외화기준, 02: 원화기준)
) -> pd.DataFrame:
    """
    주식통합증거금 현황 API입니다.
    한국투자 HTS(eFriend Plus) > [0867] 통합증거금조회 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

    ※ 해당 화면은 일반계좌와 통합증거금 신청계좌에 대해서 국내 및 해외 주문가능금액을 간단하게 조회하는 화면입니다.
    ※ 해외 국가별 상세한 증거금현황을 원하시면 [해외주식] 주문/계좌 > 해외증거금 통화별조회 API를 이용하여 주시기 바랍니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 01)
        cma_evlu_amt_icld_yn (str): [필수] CMA평가금액포함여부 (ex. Y: 포함, N: 미포함)
        wcrc_frcr_dvsn_cd (str): [필수] 원화외화구분코드 (ex. 01: 외화기준, 02: 원화기준)
        fwex_ctrt_frcr_dvsn_cd (str): [필수] 선도환계약외화구분코드 (ex. 01: 외화기준, 02: 원화기준)

    Returns:
        pd.DataFrame: 주식통합증거금 현황 데이터
        
    Example:
        >>> df = intgr_margin(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, cma_evlu_amt_icld_yn="N", wcrc_frcr_dvsn_cd="01", fwex_ctrt_frcr_dvsn_cd="01")
        >>> print(df)
    """

    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '01')")
    
    if cma_evlu_amt_icld_yn == "":
        raise ValueError("cma_evlu_amt_icld_yn is required (e.g. 'Y' or 'N')")
    
    if wcrc_frcr_dvsn_cd == "":
        raise ValueError("wcrc_frcr_dvsn_cd is required (e.g. '01' or '02')")
    
    if fwex_ctrt_frcr_dvsn_cd == "":
        raise ValueError("fwex_ctrt_frcr_dvsn_cd is required (e.g. '01' or '02')")

    tr_id = "TTTC0869R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "CMA_EVLU_AMT_ICLD_YN": cma_evlu_amt_icld_yn,
        "WCRC_FRCR_DVSN_CD": wcrc_frcr_dvsn_cd,
        "FWEX_CTRT_FRCR_DVSN_CD": fwex_ctrt_frcr_dvsn_cd
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame([res.getBody().output])
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 