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
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외선물옵션] 기본시세 > 해외옵션 분봉조회 [해외선물-040]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-futureoption/v1/quotations/inquire-time-optchartprice"

def inquire_time_optchartprice(
    srs_cd: str,  # 종목코드
    exch_cd: str,  # 거래소코드
    qry_cnt: str,  # 요청개수
    start_date_time: str = "",  # 조회시작일시
    close_date_time: str = "",  # 조회종료일시
    qry_gap: str = "",  # 묶음개수
    qry_tp: str = "",  # 조회구분
    index_key: str = "",  # 이전조회KEY
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    해외옵션 분봉조회 API입니다. 
    한 번의 호출에 120건까지 확인 가능하며, QRY_TP, INDEX_KEY 를 이용하여 다음조회 가능합니다.

    ※ 다음조회 방법
    (처음조회) "QRY_TP":"Q", "QRY_CNT":"120", "INDEX_KEY":""
    (다음조회) "QRY_TP":"P", "QRY_CNT":"120", "INDEX_KEY":"20240902         5"  ◀ 이전 호출의 "output1 > index_key" 기입

    (중요) 해외옵션시세 출력값을 해석하실 때 focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)에 있는 sCalcDesz(계산 소수점) 값을 활용하셔야 정확한 값을 받아오실 수 있습니다.

    - focode.mst(해외지수옵션 종목마스터파일), (해외주식옵션 종목마스터파일) 다운로드 방법
    1) focode.mst(해외지수옵션 종목마스터파일)
        : 포럼 > FAQ > 종목정보 다운로드(해외) - 해외지수옵션 클릭하여 다운로드 후
        Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외옵션정보.h)를 참고하여 해석
    2) fostkcode.mst(해외주식옵션 종목마스터파일)
        : 포럼 > FAQ > 종목정보 다운로드(해외) - 해외주식옵션 클릭하여 다운로드 후
        Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외주식옵션정보.h)를 참고하여 해석

    - 소수점 계산 시, focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)의 sCalcDesz(계산 소수점) 값 참고
    EX) focode.mst 파일의 sCalcDesz(계산 소수점) 값
        품목코드 OES 계산소수점 -2 → 시세 7525 수신 시 75.25 로 해석
        품목코드 O6E 계산소수점 -4 → 시세 54.0 수신 시 0.0054 로 해석
    
    Args:
        srs_cd (str): [필수] 종목코드 (ex. OESU24 C5500)
        exch_cd (str): [필수] 거래소코드 (ex. CME)
        qry_cnt (str): [필수] 요청개수 (ex. 20)
        start_date_time (str): 조회시작일시
        close_date_time (str): 조회종료일시
        qry_gap (str): 묶음개수
        qry_tp (str): 조회구분
        index_key (str): 이전조회KEY
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 DataFrame, output2 DataFrame)
        
    Example:
        >>> df1, df2 = inquire_time_optchartprice("OESU24 C5500", "CME", "20")
        >>> print(df1)
        >>> print(df2)
    """

    if srs_cd == "":
        raise ValueError("srs_cd is required (e.g. 'OESU24 C5500')")
    
    if exch_cd == "":
        raise ValueError("exch_cd is required (e.g. 'CME')")
    
    if qry_cnt == "":
        raise ValueError("qry_cnt is required (e.g. '20')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None and dataframe2 is None:
            return pd.DataFrame(), pd.DataFrame()
        else:
            return (dataframe1 if dataframe1 is not None else pd.DataFrame(), 
                   dataframe2 if dataframe2 is not None else pd.DataFrame())

    tr_id = "HHDFO55020100"  # 해외옵션 분봉조회

    params = {
        "SRS_CD": srs_cd,  # 종목코드
        "EXCH_CD": exch_cd,  # 거래소코드
        "QRY_CNT": qry_cnt,  # 요청개수
        "START_DATE_TIME": start_date_time,  # 조회시작일시
        "CLOSE_DATE_TIME": close_date_time,  # 조회종료일시
        "QRY_GAP": qry_gap,  # 묶음개수
        "QRY_TP": qry_tp,  # 조회구분
        "INDEX_KEY": index_key  # 이전조회KEY
    }
    
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 처리 (object)
        current_data1 = pd.DataFrame([res.getBody().output1])
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1
            
        # output2 처리 (array)
        current_data2 = pd.DataFrame(res.getBody().output2)  
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2
            
        tr_cont = res.getHeader().tr_cont
        index_key = res.getBody().output1["index_key"]
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_time_optchartprice(
                srs_cd, exch_cd, qry_cnt, start_date_time, close_date_time, 
                qry_gap, qry_tp, index_key, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 