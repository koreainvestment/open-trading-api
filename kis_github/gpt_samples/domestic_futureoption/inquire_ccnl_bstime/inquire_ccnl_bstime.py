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
# [국내선물옵션] 주문/계좌 > 선물옵션 기준일체결내역[v1_국내선물-016]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-futureoption/v1/trading/inquire-ccnl-bstime"

def inquire_ccnl_bstime(
    cano: str,  # [필수] 종합계좌번호
    acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 03)
    ord_dt: str,  # [필수] 주문일자 (ex. 20250101)
    fuop_tr_strt_tmd: str,  # [필수] 선물옵션거래시작시각 (ex. HHMMSS)
    fuop_tr_end_tmd: str,  # [필수] 선물옵션거래종료시각 (ex. HHMMSS)
    FK200: str = "",  # 연속조회검색조건200
    NK200: str = "",  # 연속조회키200
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    선물옵션 기준일체결내역 API입니다.
    
    Args:
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 03)
        ord_dt (str): [필수] 주문일자 (ex. 20250101)
        fuop_tr_strt_tmd (str): [필수] 선물옵션거래시작시각 (ex. HHMMSS)
        fuop_tr_end_tmd (str): [필수] 선물옵션거래종료시각 (ex. HHMMSS)
        FK200 (str): 연속조회검색조건200
        NK200 (str): 연속조회키200
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 선물옵션 기준일체결내역 데이터 (output1, output2)
        
    Example:
        >>> df1, df2 = inquire_ccnl_bstime(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, ord_dt="20230920", fuop_tr_strt_tmd="000000", fuop_tr_end_tmd="240000")
        >>> print(df1)
        >>> print(df2)
    """

    if cano == "":
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '03')")
    
    if ord_dt == "":
        raise ValueError("ord_dt is required (e.g. '20250101')")
        
    if fuop_tr_strt_tmd == "":
        raise ValueError("fuop_tr_strt_tmd is required (e.g. 'HHMMSS')")
        
    if fuop_tr_end_tmd == "":
        raise ValueError("fuop_tr_end_tmd is required (e.g. 'HHMMSS')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "CTFO5139R"

    params = {
        "CANO": cano,  # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "ORD_DT": ord_dt,  # 주문일자
        "FUOP_TR_STRT_TMD": fuop_tr_strt_tmd,  # 선물옵션거래시작시각
        "FUOP_TR_END_TMD": fuop_tr_end_tmd,  # 선물옵션거래종료시각
        "CTX_AREA_FK200": FK200,  # 연속조회검색조건200
        "CTX_AREA_NK200": NK200  # 연속조회키200
    }
    
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 처리 (array)
        current_data1 = pd.DataFrame(res.getBody().output1)
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1
            
        # output2 처리 (object)
        current_data2 = pd.DataFrame([res.getBody().output2])
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2
            
        tr_cont = res.getHeader().tr_cont
        FK200 = res.getBody().ctx_area_fk200
        NK200 = res.getBody().ctx_area_nk200
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_ccnl_bstime(
                cano, acnt_prdt_cd, ord_dt, fuop_tr_strt_tmd, fuop_tr_end_tmd, 
                FK200, NK200, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 