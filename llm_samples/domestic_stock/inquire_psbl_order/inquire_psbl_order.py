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
# [국내주식] 주문/계좌 > 매수가능조회[v1_국내주식-007]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/trading/inquire-psbl-order"

def inquire_psbl_order(
    env_dv: str,  # 실전모의구분
    cano: str,    # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    pdno: str,    # 상품번호
    ord_unpr: str,  # 주문단가
    ord_dvsn: str,  # 주문구분
    cma_evlu_amt_icld_yn: str,  # CMA평가금액포함여부
    ovrs_icld_yn: str  # 해외포함여부
) -> pd.DataFrame:
    """
    매수가능 조회 API입니다. 
    실전계좌/모의계좌의 경우, 한 번의 호출에 최대 1건까지 확인 가능합니다.

    1) 매수가능금액 확인
    . 미수 사용 X: nrcvb_buy_amt(미수없는매수금액) 확인
    . 미수 사용 O: max_buy_amt(최대매수금액) 확인

    2) 매수가능수량 확인
    . 특정 종목 전량매수 시 가능수량을 확인하실 경우 ORD_DVSN:00(지정가)는 종목증거금율이 반영되지 않습니다. 
    따라서 "반드시" ORD_DVSN:01(시장가)로 지정하여 종목증거금율이 반영된 가능수량을 확인하시기 바랍니다. 

    (다만, 조건부지정가 등 특정 주문구분(ex.IOC)으로 주문 시 가능수량을 확인할 경우 주문 시와 동일한 주문구분(ex.IOC) 입력하여 가능수량 확인)

    . 미수 사용 X: ORD_DVSN:01(시장가) or 특정 주문구분(ex.IOC)로 지정하여 nrcvb_buy_qty(미수없는매수수량) 확인
    . 미수 사용 O: ORD_DVSN:01(시장가) or 특정 주문구분(ex.IOC)로 지정하여 max_buy_qty(최대매수수량) 확인
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        cano (str): [필수] 종합계좌번호 (ex. 계좌번호 체계(8-2)의 앞 8자리)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 계좌번호 체계(8-2)의 뒤 2자리)
        pdno (str): [필수] 상품번호 (ex. 종목번호(6자리))
        ord_unpr (str): [필수] 주문단가 (ex. 1주당 가격)
        ord_dvsn (str): [필수] 주문구분 (ex. 01 : 시장가)
        cma_evlu_amt_icld_yn (str): [필수] CMA평가금액포함여부 (ex. Y)
        ovrs_icld_yn (str): [필수] 해외포함여부 (ex. N)

    Returns:
        pd.DataFrame: 매수가능조회 데이터
        
    Example:
        >>> df = inquire_psbl_order(env_dv="real", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, pdno="005930", ord_unpr="55000", ord_dvsn="01", cma_evlu_amt_icld_yn="N", ovrs_icld_yn="N")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")
    
    if cano == "":
        raise ValueError("cano is required (e.g. '계좌번호 체계(8-2)의 앞 8자리')")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '계좌번호 체계(8-2)의 뒤 2자리')")
    
    if pdno == "":
        raise ValueError("pdno is required (e.g. '종목번호(6자리)')")
    
    if ord_unpr == "":
        raise ValueError("ord_unpr is required (e.g. '1주당 가격')")
    
    if ord_dvsn == "":
        raise ValueError("ord_dvsn is required (e.g. '01 : 시장가')")
    
    if cma_evlu_amt_icld_yn == "":
        raise ValueError("cma_evlu_amt_icld_yn is required (e.g. 'Y')")
    
    if ovrs_icld_yn == "":
        raise ValueError("ovrs_icld_yn is required (e.g. 'N')")

    # tr_id 설정
    if env_dv == "real":
        tr_id = "TTTC8908R"
    elif env_dv == "demo":
        tr_id = "VTTC8908R"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "ORD_UNPR": ord_unpr,
        "ORD_DVSN": ord_dvsn,
        "CMA_EVLU_AMT_ICLD_YN": cma_evlu_amt_icld_yn,
        "OVRS_ICLD_YN": ovrs_icld_yn
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        return pd.DataFrame(res.getBody().output, index=[0])
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 