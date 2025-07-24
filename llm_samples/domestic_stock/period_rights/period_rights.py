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
# [국내주식] 주문/계좌 > 기간별계좌권리현황조회 [국내주식-211]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/trading/period-rights"

def period_rights(
    inqr_dvsn: str,  # [필수] 조회구분 (ex. 03)
    cano: str,       # [필수] 종합계좌번호 (ex. 12345678)
    acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 01 or 22)
    inqr_strt_dt: str,  # [필수] 조회시작일자 (ex. 20250101)
    inqr_end_dt: str,   # [필수] 조회종료일자 (ex. 20250103)
    cust_rncno25: str = "",  # 고객실명확인번호25
    hmid: str = "",          # 홈넷ID
    rght_type_cd: str = "",  # 권리유형코드
    pdno: str = "",          # 상품번호
    prdt_type_cd: str = "",  # 상품유형코드
    NK100: str = "",         # 연속조회키100
    FK100: str = "",         # 연속조회검색조건100
    tr_cont: str = "",       # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,          # 내부 재귀깊이 (자동관리)
    max_depth: int = 10      # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    기간별계좌권리현황조회 API입니다.
    한국투자 HTS(eFriend Plus) > [7344] 권리유형별 현황조회 화면을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        inqr_dvsn (str): [필수] 조회구분 (ex. 03)
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 01 or 22)
        inqr_strt_dt (str): [필수] 조회시작일자 (ex. 20250101)
        inqr_end_dt (str): [필수] 조회종료일자 (ex. 20250103)
        cust_rncno25 (str): 고객실명확인번호25
        hmid (str): 홈넷ID
        rght_type_cd (str): 권리유형코드
        pdno (str): 상품번호
        prdt_type_cd (str): 상품유형코드
        NK100 (str): 연속조회키100
        FK100 (str): 연속조회검색조건100
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        pd.DataFrame: 기간별계좌권리현황 데이터
        
    Example:
        >>> df = period_rights(inqr_dvsn="03", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, inqr_strt_dt="20250101", inqr_end_dt="20250103")
        >>> print(df)
    """

    if inqr_dvsn == "":
        raise ValueError("inqr_dvsn is required (e.g. '03')")
    
    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '01' or '22')")
    
    if inqr_strt_dt == "":
        raise ValueError("inqr_strt_dt is required (e.g. '20250101')")
    
    if inqr_end_dt == "":
        raise ValueError("inqr_end_dt is required (e.g. '20250103')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    tr_id = "CTRGA011R"  # 기간별계좌권리현황조회

    params = {
        "INQR_DVSN": inqr_dvsn,
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "INQR_STRT_DT": inqr_strt_dt,
        "INQR_END_DT": inqr_end_dt,
        "CUST_RNCNO25": cust_rncno25,
        "HMID": hmid,
        "RGHT_TYPE_CD": rght_type_cd,
        "PDNO": pdno,
        "PRDT_TYPE_CD": prdt_type_cd,
        "CTX_AREA_NK100": NK100,
        "CTX_AREA_FK100": FK100
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
            return period_rights(
                inqr_dvsn, cano, acnt_prdt_cd, inqr_strt_dt, inqr_end_dt,
                cust_rncno25, hmid, rght_type_cd, pdno, prdt_type_cd,
                NK100, FK100, "N", dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 