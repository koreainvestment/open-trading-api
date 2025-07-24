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
# [해외주식] 주문/계좌 > 해외주식 지정가주문번호조회 [해외주식-071]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-stock/v1/trading/algo-ordno"

def algo_ordno(
    cano: str,                    # [필수] 종합계좌번호
    acnt_prdt_cd: str,           # [필수] 계좌상품코드 (ex. 01)
    trad_dt: str,                # [필수] 거래일자
    FK200: str = "",             # 연속조회검색조건200
    NK200: str = "",             # 연속조회키200
    tr_cont: str = "",           # 연속거래여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,              # 내부 재귀깊이 (자동관리)
    max_depth: int = 10          # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    TWAP, VWAP 주문에 대한 주문번호를 조회하는 API
    
    Args:
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 01)
        trad_dt (str): [필수] 거래일자
        FK200 (str): 연속조회검색조건200
        NK200 (str): 연속조회키200
        tr_cont (str): 연속거래여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        pd.DataFrame: 해외주식 지정가주문번호 데이터
        
    Example:
        >>> df = algo_ordno(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, trad_dt="20250619")
        >>> print(df)
    """

    if cano == "":
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '01')")
    
    if trad_dt == "":
        raise ValueError("trad_dt is required")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    tr_id = "TTTS6058R"  # 해외주식 지정가주문번호조회

    params = {
        "CANO": cano,                    # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,   # 계좌상품코드
        "TRAD_DT": trad_dt,             # 거래일자
        "CTX_AREA_FK200": FK200,        # 연속조회검색조건200
        "CTX_AREA_NK200": NK200         # 연속조회키200
    }
    
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
            
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data
            
        tr_cont = res.getHeader().tr_cont
        FK200 = res.getBody().ctx_area_fk200
        NK200 = res.getBody().ctx_area_nk200
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return algo_ordno(
                cano, acnt_prdt_cd, trad_dt, FK200, NK200, "N", dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 