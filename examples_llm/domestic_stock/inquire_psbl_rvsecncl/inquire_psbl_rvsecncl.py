"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""


import sys
import time
from typing import Optional
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 주식정정취소가능주문조회[v1_국내주식-004]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/trading/inquire-psbl-rvsecncl"

def inquire_psbl_rvsecncl(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    inqr_dvsn_1: str,  # 조회구분1
    inqr_dvsn_2: str,  # 조회구분2
    FK100: str = "",  # 연속조회검색조건100
    NK100: str = "",  # 연속조회키100
    tr_cont: str = "",  # 연속거래여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    주식정정취소가능주문조회 API입니다. 한 번의 호출에 최대 50건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.

    ※ 주식주문(정정취소) 호출 전에 반드시 주식정정취소가능주문조회 호출을 통해 정정취소가능수량(output > psbl_qty)을 확인하신 후 정정취소주문 내시기 바랍니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. 계좌번호 체계(8-2)의 앞 8자리)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 계좌번호 체계(8-2)의 뒤 2자리)
        inqr_dvsn_1 (str): [필수] 조회구분1 (ex. 0: 주문, 1: 종목)
        inqr_dvsn_2 (str): [필수] 조회구분2 (ex. 0: 전체, 1: 매도, 2: 매수)
        FK100 (str): 연속조회검색조건100
        NK100 (str): 연속조회키100
        tr_cont (str): 연속거래여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        pd.DataFrame: 주식정정취소가능주문조회 데이터
        
    Example:
        >>> df = inquire_psbl_rvsecncl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, inqr_dvsn_1="1", inqr_dvsn_2="0")
        >>> print(df)
    """

    if cano == "":
        raise ValueError("cano is required (e.g. '계좌번호 체계(8-2)의 앞 8자리')")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '계좌번호 체계(8-2)의 뒤 2자리')")
    
    if inqr_dvsn_1 == "":
        raise ValueError("inqr_dvsn_1 is required (e.g. '0: 주문, 1: 종목')")
    
    if inqr_dvsn_2 == "":
        raise ValueError("inqr_dvsn_2 is required (e.g. '0: 전체, 1: 매도, 2: 매수')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    tr_id = "TTTC0084R"  # 주식정정취소가능주문조회

    params = {
        "CANO": cano,  # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "INQR_DVSN_1": inqr_dvsn_1,  # 조회구분1
        "INQR_DVSN_2": inqr_dvsn_2,  # 조회구분2
        "CTX_AREA_FK100": FK100,  # 연속조회검색조건100
        "CTX_AREA_NK100": NK100  # 연속조회키100
    }
    
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
            
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data
            
        tr_cont = res.getHeader().tr_cont
        FK100 = res.getBody().ctx_area_fk100
        NK100 = res.getBody().ctx_area_nk100
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_psbl_rvsecncl(
                cano, acnt_prdt_cd, inqr_dvsn_1, inqr_dvsn_2, FK100, NK100, "N", dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 