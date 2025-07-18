"""
Created on 20250112 
@author: LaivData SJPark with cursor
"""

import logging
import sys
import time
from typing import Optional

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 퇴직연금 미체결내역[v1_국내주식-033]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/trading/pension/inquire-daily-ccld"

def pension_inquire_daily_ccld(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,     # 계좌상품코드
    user_dvsn_cd: str,      # 사용자구분코드
    sll_buy_dvsn_cd: str,   # 매도매수구분코드
    ccld_nccs_dvsn: str,    # 체결미체결구분
    inqr_dvsn_3: str,       # 조회구분3
    FK100: str = "",        # 연속조회검색조건100
    NK100: str = "",        # 연속조회키100
    tr_cont: str = "",      # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,         # 내부 재귀 깊이 (자동 관리)
    max_depth: int = 10     # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    [국내주식] 주문/계좌 > 퇴직연금 미체결내역[v1_국내주식-033]
    ※ 55번 계좌(DC가입자계좌)의 경우 해당 API 이용이 불가합니다.
    KIS Developers API의 경우 HTS ID에 반드시 연결되어있어야만 API 신청 및 앱정보 발급이 가능한 서비스로 개발되어서 실물계좌가 아닌 55번 계좌는 API 이용이 불가능한 점 양해 부탁드립니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 29)
        user_dvsn_cd (str): [필수] 사용자구분코드 (ex. %%)
        sll_buy_dvsn_cd (str): [필수] 매도매수구분코드 (ex. 00: 전체, 01: 매도, 02: 매수)
        ccld_nccs_dvsn (str): [필수] 체결미체결구분 (ex. %%: 전체, 01: 체결, 02: 미체결)
        inqr_dvsn_3 (str): [필수] 조회구분3 (ex. 00: 전체)
        FK100 (str): 연속조회검색조건100
        NK100 (str): 연속조회키100
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        pd.DataFrame: 퇴직연금 미체결내역 데이터
        
    Example:
        >>> df = pension_inquire_daily_ccld(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, user_dvsn_cd="%%", sll_buy_dvsn_cd="00", ccld_nccs_dvsn="%%", inqr_dvsn_3="00")
        >>> print(df)
    """

    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '29')")
    
    if user_dvsn_cd == "":
        raise ValueError("user_dvsn_cd is required (e.g. '%%')")
        
    if sll_buy_dvsn_cd == "":
        raise ValueError("sll_buy_dvsn_cd is required (e.g. '00: 전체, 01: 매도, 02: 매수')")
        
    if ccld_nccs_dvsn == "":
        raise ValueError("ccld_nccs_dvsn is required (e.g. '%%: 전체, 01: 체결, 02: 미체결')")
        
    if inqr_dvsn_3 == "":
        raise ValueError("inqr_dvsn_3 is required (e.g. '00: 전체')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    tr_id = "TTTC2201R"  # 퇴직연금 미체결내역

    params = {
        "CANO": cano,  # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "USER_DVSN_CD": user_dvsn_cd,  # 사용자구분코드
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,  # 매도매수구분코드
        "CCLD_NCCS_DVSN": ccld_nccs_dvsn,  # 체결미체결구분
        "INQR_DVSN_3": inqr_dvsn_3,  # 조회구분3
        "CTX_AREA_FK100": FK100,
        "CTX_AREA_NK100": NK100
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
            return pension_inquire_daily_ccld(
                cano, acnt_prdt_cd, user_dvsn_cd, sll_buy_dvsn_cd, ccld_nccs_dvsn, inqr_dvsn_3, FK100, NK100, "N", dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 