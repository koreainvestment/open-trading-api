"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""


import sys
import time
from typing import Optional, Tuple
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 지정가체결내역조회 [해외주식-070]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-stock/v1/trading/inquire-algo-ccnl"

def inquire_algo_ccnl(
    cano: str,  # [필수] 계좌번호
    acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 01)
    ord_dt: str = "",  # 주문일자
    ord_gno_brno: str = "",  # 주문채번지점번호
    odno: str = "",  # 주문번호 (ex. 지정가주문번호 TTTC6058R에서 조회된 주문번호 입력)
    ttlz_icld_yn: str = "",  # 집계포함여부
    NK200: str = "",  # 연속조회키200
    FK200: str = "",  # 연속조회조건200
    tr_cont: str = "",  # 연속거래여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    dataframe3: Optional[pd.DataFrame] = None,  # 누적 데이터프레임3
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    해외주식 TWAP, VWAP 주문에 대한 체결내역 조회 API로 지정가 주문번호조회 API를 수행 후 조회해야합니다
    
    Args:
        cano (str): [필수] 계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 01)
        ord_dt (str): 주문일자
        ord_gno_brno (str): 주문채번지점번호
        odno (str): 주문번호 (ex. 지정가주문번호 TTTC6058R에서 조회된 주문번호 입력)
        ttlz_icld_yn (str): 집계포함여부
        NK200 (str): 연속조회키200
        FK200 (str): 연속조회조건200
        tr_cont (str): 연속거래여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        dataframe3 (Optional[pd.DataFrame]): 누적 데이터프레임3
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output, output3) 체결내역 데이터
        
    Example:
        >>> result, result3 = inquire_algo_ccnl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod)
        >>> print(result)
        >>> print(result3)
    """

    if cano == "":
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            dataframe = pd.DataFrame()
        if dataframe3 is None:
            dataframe3 = pd.DataFrame()
        return dataframe, dataframe3

    tr_id = "TTTS6059R"  # 해외주식 지정가체결내역조회

    params = {
        "CANO": cano,  # 계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "ORD_DT": ord_dt,  # 주문일자
        "ORD_GNO_BRNO": ord_gno_brno,  # 주문채번지점번호
        "ODNO": odno,  # 주문번호
        "TTLZ_ICLD_YN": ttlz_icld_yn,  # 집계포함여부
        "CTX_AREA_NK200": NK200,  # 연속조회키200
        "CTX_AREA_FK200": FK200  # 연속조회조건200
    }
    
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        current_data3 = pd.DataFrame(res.getBody().output3)
            
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data
            
        if dataframe3 is not None:
            dataframe3 = pd.concat([dataframe3, current_data3], ignore_index=True)
        else:
            dataframe3 = current_data3
            
        tr_cont = res.getHeader().tr_cont
        NK200 = res.getBody().ctx_area_nk200
        FK200 = res.getBody().ctx_area_fk200
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_algo_ccnl(
                cano, acnt_prdt_cd, ord_dt, ord_gno_brno, odno, ttlz_icld_yn, 
                NK200, FK200, "N", dataframe, dataframe3, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe, dataframe3
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 