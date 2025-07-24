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
# [국내선물옵션] 주문/계좌 > 선물옵션 주문체결내역조회[v1_국내선물-003]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-futureoption/v1/trading/inquire-ccnl"

def inquire_ccnl(
    env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
    cano: str,    # [필수] 종합계좌번호
    acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 03)
    strt_ord_dt: str,   # [필수] 시작주문일자 (ex. 주문내역 조회 시작 일자, YYYYMMDD)
    end_ord_dt: str,    # [필수] 종료주문일자 (ex. 주문내역 조회 마지막 일자, YYYYMMDD)
    sll_buy_dvsn_cd: str,  # [필수] 매도매수구분코드 (ex. 00:전체, 01:매도, 02:매수)
    ccld_nccs_dvsn: str,   # [필수] 체결미체결구분 (ex. 00:전체, 01:체결, 02:미체결)
    sort_sqn: str,      # [필수] 정렬순서 (ex. AS:정순, DS:역순)
    pdno: str = "",     # 상품번호
    strt_odno: str = "",  # 시작주문번호
    mket_id_cd: str = "",  # 시장ID코드
    FK200: str = "",    # 연속조회검색조건200
    NK200: str = "",    # 연속조회키200
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
    depth: int = 0,     # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    선물옵션 주문체결내역조회 API입니다. 한 번의 호출에 최대 100건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 03)
        strt_ord_dt (str): [필수] 시작주문일자 (ex. 주문내역 조회 시작 일자, YYYYMMDD)
        end_ord_dt (str): [필수] 종료주문일자 (ex. 주문내역 조회 마지막 일자, YYYYMMDD)
        sll_buy_dvsn_cd (str): [필수] 매도매수구분코드 (ex. 00:전체, 01:매도, 02:매수)
        ccld_nccs_dvsn (str): [필수] 체결미체결구분 (ex. 00:전체, 01:체결, 02:미체결)
        sort_sqn (str): [필수] 정렬순서 (ex. AS:정순, DS:역순)
        pdno (str, optional): 상품번호. Defaults to "".
        strt_odno (str, optional): 시작주문번호. Defaults to "".
        mket_id_cd (str, optional): 시장ID코드. Defaults to "".
        FK200 (str, optional): 연속조회검색조건200. Defaults to "".
        NK200 (str, optional): 연속조회키200. Defaults to "".
        tr_cont (str, optional): 연속거래여부. Defaults to "".
        dataframe1 (Optional[pd.DataFrame], optional): 누적 데이터프레임1. Defaults to None.
        dataframe2 (Optional[pd.DataFrame], optional): 누적 데이터프레임2. Defaults to None.
        depth (int, optional): 내부 재귀깊이 (자동관리). Defaults to 0.
        max_depth (int, optional): 최대 재귀 횟수 제한. Defaults to 10.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 주문체결내역 데이터 (output1, output2)
        
    Example:
        >>> df1, df2 = inquire_ccnl(env_dv="real", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, strt_ord_dt="20220730", end_ord_dt="20220830", sll_buy_dvsn_cd="00", ccld_nccs_dvsn="00", sort_sqn="DS")
        >>> print(df1)
        >>> print(df2)
    """

    # 필수 파라미터 검증
    if not env_dv:
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")
    
    if not cano:
        raise ValueError("cano is required")
    
    if not acnt_prdt_cd:
        raise ValueError("acnt_prdt_cd is required (e.g. '03')")
    
    if not strt_ord_dt:
        raise ValueError("strt_ord_dt is required (e.g. '20220730')")
    
    if not end_ord_dt:
        raise ValueError("end_ord_dt is required (e.g. '20220830')")
    
    if not sll_buy_dvsn_cd:
        raise ValueError("sll_buy_dvsn_cd is required (e.g. '00')")
    
    if not ccld_nccs_dvsn:
        raise ValueError("ccld_nccs_dvsn is required (e.g. '00')")
    
    if not sort_sqn:
        raise ValueError("sort_sqn is required (e.g. 'AS' or 'DS')")

    # 재귀 깊이 제한 확인
    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    # tr_id 설정
    if env_dv == "real":
        tr_id = "TTTO5201R"
    elif env_dv == "demo":
        tr_id = "VTTO5201R"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    # 파라미터 설정
    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "STRT_ORD_DT": strt_ord_dt,
        "END_ORD_DT": end_ord_dt,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "CCLD_NCCS_DVSN": ccld_nccs_dvsn,
        "SORT_SQN": sort_sqn,
        "PDNO": pdno,
        "STRT_ODNO": strt_odno,
        "MKET_ID_CD": mket_id_cd,
        "CTX_AREA_FK200": FK200,
        "CTX_AREA_NK200": NK200
    }
    
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 데이터 처리
        current_data1 = pd.DataFrame(res.getBody().output1)
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1
            
        # output2 데이터 처리 (단일 객체)
        current_data2 = pd.DataFrame(res.getBody().output2, index=[0])
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2
            
        # 연속조회 정보 업데이트
        tr_cont = res.getHeader().tr_cont
        FK200 = res.getBody().ctx_area_fk200
        NK200 = res.getBody().ctx_area_nk200
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_ccnl(
                env_dv, cano, acnt_prdt_cd, strt_ord_dt, end_ord_dt, 
                sll_buy_dvsn_cd, ccld_nccs_dvsn, sort_sqn, pdno, strt_odno, 
                mket_id_cd, FK200, NK200, "N", dataframe1, dataframe2, 
                depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 