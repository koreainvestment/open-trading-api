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
# [해외주식] 주문/계좌 > 해외주식 예약주문조회[v1_해외주식-013]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-stock/v1/trading/order-resv-list"

def order_resv_list(
    nat_dv: str,  # 국가구분코드
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    inqr_strt_dt: str,  # 조회시작일자
    inqr_end_dt: str,  # 조회종료일자
    inqr_dvsn_cd: str,  # 조회구분코드
    ovrs_excg_cd: str,  # 해외거래소코드
    prdt_type_cd: str = "",  # 상품유형코드
    FK200: str = "",  # 연속조회검색조건200
    NK200: str = "",  # 연속조회키200
    tr_cont: str = "",  # 연속거래여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    해외주식 예약주문 조회 API입니다.
    ※ 모의투자는 사용 불가합니다.

    * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
    https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp
    
    Args:
        nat_dv (str): [필수] 국가구분코드 (ex. us:미국, asia:아시아)
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 01)
        inqr_strt_dt (str): [필수] 조회시작일자 (ex. 20250101)
        inqr_end_dt (str): [필수] 조회종료일자 (ex. 20251231)
        inqr_dvsn_cd (str): [필수] 조회구분코드 (ex. 00:전체, 01:일반해외주식, 02:미니스탁)
        ovrs_excg_cd (str): [필수] 해외거래소코드 (ex. NASD:나스닥, NYSE:뉴욕, AMEX:아멕스, SEHK:홍콩, SHAA:상해, SZAA:심천, TKSE:일본, HASE:하노이, VNSE:호치민)
        prdt_type_cd (str): 상품유형코드
        FK200 (str): 연속조회검색조건200
        NK200 (str): 연속조회키200
        tr_cont (str): 연속거래여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한
        
    Returns:
        pd.DataFrame: 해외주식 예약주문조회 데이터
        
    Example:
        >>> df = order_resv_list(nat_dv="us", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, inqr_strt_dt="20250101", inqr_end_dt="20251231", inqr_dvsn_cd="00", ovrs_excg_cd="NASD")
        >>> print(df)
    """
    
    if nat_dv == "":
        raise ValueError("nat_dv is required (e.g. 'us' or 'asia')")
    
    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '01')")
    
    if inqr_strt_dt == "":
        raise ValueError("inqr_strt_dt is required (e.g. '20250101')")
    
    if inqr_end_dt == "":
        raise ValueError("inqr_end_dt is required (e.g. '20251231')")
    
    if inqr_dvsn_cd == "":
        raise ValueError("inqr_dvsn_cd is required (e.g. '00')")
    
    if ovrs_excg_cd == "":
        raise ValueError("ovrs_excg_cd is required (e.g. 'NASD')")
    
    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    # tr_id 설정
    if nat_dv == "us":
        tr_id = "TTTT3039R"
    elif nat_dv == "asia":
        tr_id = "TTTS3014R"
    else:
        raise ValueError("nat_dv can only be 'us' or 'asia'")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "INQR_STRT_DT": inqr_strt_dt,
        "INQR_END_DT": inqr_end_dt,
        "INQR_DVSN_CD": inqr_dvsn_cd,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "PRDT_TYPE_CD": prdt_type_cd,
        "CTX_AREA_FK200": FK200,
        "CTX_AREA_NK200": NK200
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
            return order_resv_list(
                nat_dv, cano, acnt_prdt_cd, inqr_strt_dt, inqr_end_dt, 
                inqr_dvsn_cd, ovrs_excg_cd, prdt_type_cd, FK200, NK200, 
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 