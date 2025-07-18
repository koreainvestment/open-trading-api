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
# [국내선물옵션] 주문/계좌 > (야간)선물옵션 주문체결 내역조회 [국내선물-009]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-futureoption/v1/trading/inquire-ngt-ccnl"

def inquire_ngt_ccnl(
    cano: str,                                           # 종합계좌번호
    acnt_prdt_cd: str,                                   # 계좌상품코드
    strt_ord_dt: str,                                    # 시작주문일자
    end_ord_dt: str,                                     # 종료주문일자
    sll_buy_dvsn_cd: str,                               # 매도매수구분코드
    ccld_nccs_dvsn: str,                                # 체결미체결구분
    sort_sqn: str = "",                                 # 정렬순서
    strt_odno: str = "",                                # 시작주문번호
    pdno: str = "",                                     # 상품번호
    mket_id_cd: str = "",                               # 시장ID코드
    fuop_dvsn_cd: str = "",                             # 선물옵션구분코드
    scrn_dvsn: str = "",                                # 화면구분
    FK200: str = "",                                    # 연속조회검색조건200
    NK200: str = "",                                    # 연속조회키200
    tr_cont: str = "",                                  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,          # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,          # 누적 데이터프레임2
    depth: int = 0,                                     # 내부 재귀깊이 (자동관리)
    max_depth: int = 10                                 # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    (야간)선물옵션 주문체결 내역조회 API입니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. 계좌번호 체계(8-2)의 앞 8자리)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 계좌번호 체계(8-2)의 뒤 2자리)
        strt_ord_dt (str): [필수] 시작주문일자
        end_ord_dt (str): [필수] 종료주문일자 (ex. 조회하려는 마지막 일자 다음일자로 조회 (ex. 20221011 까지의 내역을 조회하고자 할 경우, 20221012로 종료주문일자 설정))
        sll_buy_dvsn_cd (str): [필수] 매도매수구분코드 (ex. 공란:default, 00:전체, 01:매도, 02:매수)
        ccld_nccs_dvsn (str): [필수] 체결미체결구분 (ex. 00:전체, 01:체결, 02:미체결)
        sort_sqn (str): 정렬순서 (ex. 공란:default(DS:정순, 그외:역순))
        strt_odno (str): 시작주문번호 (ex. 공란:default)
        pdno (str): 상품번호 (ex. 공란:default)
        mket_id_cd (str): 시장ID코드 (ex. 공란:default)
        fuop_dvsn_cd (str): 선물옵션구분코드 (ex. 공란:전체, 01:선물, 02:옵션)
        scrn_dvsn (str): 화면구분 (ex. 02(Default))
        FK200 (str): 연속조회검색조건200 (ex. 공란:최초 조회시, 이전 조회 Output CTX_AREA_FK200값:다음페이지 조회시(2번째부터))
        NK200 (str): 연속조회키200 (ex. 공란:최초 조회시, 이전 조회 Output CTX_AREA_NK200값:다음페이지 조회시(2번째부터))
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> df1, df2 = inquire_ngt_ccnl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, strt_ord_dt="20231201", end_ord_dt="20231214", sll_buy_dvsn_cd="00", ccld_nccs_dvsn="00")
        >>> print(df1)
        >>> print(df2)
    """

    # 필수 파라미터 검증
    if cano == "" or cano is None:
        raise ValueError("cano is required (e.g. '계좌번호 체계(8-2)의 앞 8자리')")
    
    if acnt_prdt_cd == "" or acnt_prdt_cd is None:
        raise ValueError("acnt_prdt_cd is required (e.g. '계좌번호 체계(8-2)의 뒤 2자리')")
    
    if strt_ord_dt == "" or strt_ord_dt is None:
        raise ValueError("strt_ord_dt is required")
    
    if end_ord_dt == "" or end_ord_dt is None:
        raise ValueError("end_ord_dt is required (e.g. '조회하려는 마지막 일자 다음일자로 조회 (ex. 20221011 까지의 내역을 조회하고자 할 경우, 20221012로 종료주문일자 설정)')")
    
    if sll_buy_dvsn_cd == "" or sll_buy_dvsn_cd is None:
        raise ValueError("sll_buy_dvsn_cd is required (e.g. '공란:default, 00:전체, 01:매도, 02:매수')")
    
    if ccld_nccs_dvsn == "" or ccld_nccs_dvsn is None:
        raise ValueError("ccld_nccs_dvsn is required (e.g. '00:전체, 01:체결, 02:미체결')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "STTN5201R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "STRT_ORD_DT": strt_ord_dt,
        "END_ORD_DT": end_ord_dt,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "CCLD_NCCS_DVSN": ccld_nccs_dvsn,
        "SORT_SQN": sort_sqn,
        "STRT_ODNO": strt_odno,
        "PDNO": pdno,
        "MKET_ID_CD": mket_id_cd,
        "FUOP_DVSN_CD": fuop_dvsn_cd,
        "SCRN_DVSN": scrn_dvsn,
        "CTX_AREA_FK200": FK200,
        "CTX_AREA_NK200": NK200
    }
    
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)
    
    print(res.getBody())

    if res.isOK():
        # output1 (array) 처리
        current_data1 = pd.DataFrame(res.getBody().output1)
        
        # output2 (object) 처리
        current_data2 = pd.DataFrame([res.getBody().output2])
        
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1
            
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
            return inquire_ngt_ccnl(
                cano, acnt_prdt_cd, strt_ord_dt, end_ord_dt, sll_buy_dvsn_cd, ccld_nccs_dvsn,
                sort_sqn, strt_odno, pdno, mket_id_cd, fuop_dvsn_cd, scrn_dvsn,
                FK200, NK200, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 