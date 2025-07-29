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
# [국내주식] 주문/계좌 > 기간별매매손익현황조회[v1_국내주식-060]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/trading/inquire-period-trade-profit"

def inquire_period_trade_profit(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    sort_dvsn: str,  # 정렬구분 (00: 최근, 01:과거, 02:최근)
    inqr_strt_dt: str,  # 조회시작일자
    inqr_end_dt: str,  # 조회종료일자
    cblc_dvsn: str,  # 잔고구분 (00: 전체)
    pdno: str = "",  # 상품번호
    NK100: str = "",  # 연속조회키100
    FK100: str = "",  # 연속조회검색조건100
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    기간별매매손익현황조회 API입니다.
    한국투자 HTS(eFriend Plus) > [0856] 기간별 매매손익 화면 에서 "종목별" 클릭 시의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드
        sort_dvsn (str): [필수] 정렬구분 (ex. 00: 최근, 01:과거, 02:최근)
        inqr_strt_dt (str): [필수] 조회시작일자
        inqr_end_dt (str): [필수] 조회종료일자
        cblc_dvsn (str): [필수] 잔고구분 (ex. 00: 전체)
        pdno (str): 상품번호
        NK100 (str): 연속조회키100
        FK100 (str): 연속조회검색조건100
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 기간별매매손익현황 데이터 (output1, output2)
        
    Example:
        >>> df1, df2 = inquire_period_trade_profit(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, sort_dvsn="02", inqr_strt_dt="20230216", inqr_end_dt="20240301", cblc_dvsn="00")
        >>> print(df1)
        >>> print(df2)
    """

    if cano == "":
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required")
    
    if sort_dvsn == "":
        raise ValueError("sort_dvsn is required (e.g. '00', '01', '02')")
    
    if inqr_strt_dt == "":
        raise ValueError("inqr_strt_dt is required")
    
    if inqr_end_dt == "":
        raise ValueError("inqr_end_dt is required")
    
    if cblc_dvsn == "":
        raise ValueError("cblc_dvsn is required (e.g. '00')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "TTTC8715R"  # 기간별매매손익현황조회

    params = {
        "CANO": cano,  # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "SORT_DVSN": sort_dvsn,  # 정렬구분
        "INQR_STRT_DT": inqr_strt_dt,  # 조회시작일자
        "INQR_END_DT": inqr_end_dt,  # 조회종료일자
        "CBLC_DVSN": cblc_dvsn,  # 잔고구분
        "PDNO": pdno,  # 상품번호
        "CTX_AREA_FK100": FK100,  # 연속조회검색조건100
        "CTX_AREA_NK100": NK100  # 연속조회키100
    }
    
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)
    
    if res.isOK():
        current_data1 = pd.DataFrame(res.getBody().output1)
        current_data2 = pd.DataFrame(res.getBody().output2, index=[0])
            
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1
            
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2
            
        tr_cont = res.getHeader().tr_cont
        FK100 = res.getBody().ctx_area_fk100
        NK100 = res.getBody().ctx_area_nk100
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_period_trade_profit(
                cano, acnt_prdt_cd, sort_dvsn, inqr_strt_dt, inqr_end_dt, cblc_dvsn, 
                pdno, NK100, FK100, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 