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
# [국내주식] 주문/계좌 > 주식예약주문조회[v1_국내주식-020]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/trading/order-resv-ccnl"

def order_resv_ccnl(
    rsvn_ord_ord_dt: str,       # [필수] 예약주문시작일자
    rsvn_ord_end_dt: str,       # [필수] 예약주문종료일자
    tmnl_mdia_kind_cd: str,     # [필수] 단말매체종류코드 (ex. 00)
    cano: str,                  # [필수] 종합계좌번호
    acnt_prdt_cd: str,          # [필수] 계좌상품코드 (ex. 01)
    prcs_dvsn_cd: str,          # [필수] 처리구분코드 (ex. 0)
    cncl_yn: str,               # [필수] 취소여부 (ex. Y)
    rsvn_ord_seq: str = "",     # 예약주문순번
    pdno: str = "",             # 상품번호 (ex. 005930)
    sll_buy_dvsn_cd: str = "",  # 매도매수구분코드 (ex. 01)
    FK200: str = "",            # 연속조회검색조건200
    NK200: str = "",            # 연속조회키200
    tr_cont: str = "",          # 연속거래여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,             # 내부 재귀깊이 (자동관리)
    max_depth: int = 10         # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    국내예약주문 처리내역 조회 API 입니다.
    실전계좌/모의계좌의 경우, 한 번의 호출에 최대 20건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.
    
    Args:
        rsvn_ord_ord_dt (str): [필수] 예약주문시작일자
        rsvn_ord_end_dt (str): [필수] 예약주문종료일자 
        tmnl_mdia_kind_cd (str): [필수] 단말매체종류코드 (ex. 00)
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 01)
        prcs_dvsn_cd (str): [필수] 처리구분코드 (ex. 0)
        cncl_yn (str): [필수] 취소여부 (ex. Y)
        rsvn_ord_seq (str): 예약주문순번
        pdno (str): 상품번호 (ex. 005930)
        sll_buy_dvsn_cd (str): 매도매수구분코드 (ex. 01)
        FK200 (str): 연속조회검색조건200
        NK200 (str): 연속조회키200
        tr_cont (str): 연속거래여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        pd.DataFrame: 주식예약주문조회 데이터
        
    Example:
        >>> df = order_resv_ccnl(
        ...     rsvn_ord_ord_dt="20220729",
        ...     rsvn_ord_end_dt="20220810", 
        ...     tmnl_mdia_kind_cd="00",
        ...     cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod,
        ...     prcs_dvsn_cd="0",
        ...     cncl_yn="Y"
        ... )
        >>> print(df)
    """

    # 필수 파라미터 검증
    if rsvn_ord_ord_dt == "":
        raise ValueError("rsvn_ord_ord_dt is required")
    
    if rsvn_ord_end_dt == "":
        raise ValueError("rsvn_ord_end_dt is required")
    
    if tmnl_mdia_kind_cd == "":
        raise ValueError("tmnl_mdia_kind_cd is required (e.g. '00')")
    
    if cano == "":
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '01')")
    
    if prcs_dvsn_cd == "":
        raise ValueError("prcs_dvsn_cd is required (e.g. '0')")
    
    if cncl_yn == "":
        raise ValueError("cncl_yn is required (e.g. 'Y')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    tr_id = "CTSC0004R"  # 주식예약주문조회

    params = {
        "RSVN_ORD_ORD_DT": rsvn_ord_ord_dt,         # 예약주문시작일자
        "RSVN_ORD_END_DT": rsvn_ord_end_dt,         # 예약주문종료일자
        "TMNL_MDIA_KIND_CD": tmnl_mdia_kind_cd,     # 단말매체종류코드
        "CANO": cano,                               # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,               # 계좌상품코드
        "PRCS_DVSN_CD": prcs_dvsn_cd,               # 처리구분코드
        "CNCL_YN": cncl_yn,                         # 취소여부
        "RSVN_ORD_SEQ": rsvn_ord_seq,               # 예약주문순번
        "PDNO": pdno,                               # 상품번호
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,         # 매도매수구분코드
        "CTX_AREA_FK200": FK200,                    # 연속조회검색조건200
        "CTX_AREA_NK200": NK200                     # 연속조회키200
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
            return order_resv_ccnl(
                rsvn_ord_ord_dt, rsvn_ord_end_dt, tmnl_mdia_kind_cd, cano, acnt_prdt_cd, 
                prcs_dvsn_cd, cncl_yn, rsvn_ord_seq, pdno, sll_buy_dvsn_cd,
                FK200, NK200, "N", dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 