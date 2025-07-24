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
# [국내선물옵션] 주문/계좌 > 선물옵션 잔고현황[v1_국내선물-004]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-futureoption/v1/trading/inquire-balance"

def inquire_balance(
    env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
    cano: str,    # [필수] 종합계좌번호
    acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 03)
    mgna_dvsn: str,     # [필수] 증거금 구분 (ex. 01:게시,02:유지)
    excc_stat_cd: str,  # [필수] 정산상태코드 (ex. 1:정산,2:본정산)
    FK200: str = "",    # 연속조회검색조건200
    NK200: str = "",    # 연속조회키200
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
    depth: int = 0,         # 내부 재귀 깊이 (자동 관리)
    max_depth: int = 10     # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    선물옵션 잔고현황 API입니다. 한 번의 호출에 최대 20건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 03)
        mgna_dvsn (str): [필수] 증거금 구분 (ex. 01:게시,02:유지)
        excc_stat_cd (str): [필수] 정산상태코드 (ex. 1:정산,2:본정산)
        FK200 (str): 연속조회검색조건200
        NK200 (str): 연속조회키200
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀 깊이 (자동 관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 선물옵션 잔고현황 데이터
        
    Example:
        >>> df1, df2 = inquire_balance(env_dv="real", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, mgna_dvsn="01", excc_stat_cd="1")
        >>> print(df1)
        >>> print(df2)
    """

    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")
    
    if cano == "":
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '03')")
    
    if mgna_dvsn == "":
        raise ValueError("mgna_dvsn is required (e.g. '01' or '02')")
    
    if excc_stat_cd == "":
        raise ValueError("excc_stat_cd is required (e.g. '1' or '2')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    # tr_id 설정
    if env_dv == "real":
        tr_id = "CTFO6118R"
    elif env_dv == "demo":
        tr_id = "VTFO6118R"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "MGNA_DVSN": mgna_dvsn,
        "EXCC_STAT_CD": excc_stat_cd,
        "CTX_AREA_FK200": FK200,
        "CTX_AREA_NK200": NK200
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
        current_data2 = pd.DataFrame(res.getBody().output2, index=[0])
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
            return inquire_balance(
                env_dv, cano, acnt_prdt_cd, mgna_dvsn, excc_stat_cd,
                FK200, NK200, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 