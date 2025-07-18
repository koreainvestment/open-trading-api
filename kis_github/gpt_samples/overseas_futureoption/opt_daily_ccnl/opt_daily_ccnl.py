"""
Created on 20250129 
@author: LaivData SJPark with cursor
"""

import logging
import sys
import time
from typing import Optional, Tuple

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외선물옵션] 기본시세 > 해외옵션 체결추이(일간) [해외선물-037]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-futureoption/v1/quotations/opt-daily-ccnl"

def opt_daily_ccnl(
    srs_cd: str,                              # [필수] 종목코드 (ex. OESU24 C5500)  
    exch_cd: str,                             # [필수] 거래소코드 (ex. CME)
    qry_cnt: str,                             # [필수] 요청개수 (ex. 20)
    start_date_time: str = "",                # 조회시작일시
    close_date_time: str = "",                # 조회종료일시
    qry_gap: str = "",                        # 묶음개수
    qry_tp: str = "",                         # 조회구분
    index_key: str = "",                      # 이전조회KEY
    tr_cont: str = "",                        # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None, # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None, # 누적 데이터프레임 (output2)
    depth: int = 0,                           # 내부 재귀깊이 (자동관리)
    max_depth: int = 10                       # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    해외옵션 체결추이(일간) API입니다.
    최근 120건까지 데이터 확인이 가능합니다. ("QRY_CNT: 119 입력", START_DATE_TIME, CLOSE_DATE_TIME은 공란)

    ※ 호출 시 유의사항
    : START_DATE_TIME, CLOSE_DATE_TIME은 공란 입력, QRY_CNT는 확인 데이터 개수의 -1 개 입력
    ex) "START_DATE_TIME":"","CLOSE_DATE_TIME":"","QRY_CNT":"119" → 최근 120건 데이터 조회

    (중요) 해외옵션시세 출력값을 해석하실 때 focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)에 있는 sCalcDesz(계산 소수점) 값을 활용하셔야 정확한 값을 받아오실 수 있습니다.

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
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> result1, result2 = opt_daily_ccnl("OESU24 C5500", "CME", "20")
        >>> print(result1)
        >>> print(result2)
    """

    # 필수 파라미터 검증
    if srs_cd == "" or srs_cd is None:
        raise ValueError("srs_cd is required (e.g. 'OESU24 C5500')")
    
    if exch_cd == "" or exch_cd is None:
        raise ValueError("exch_cd is required (e.g. 'CME')")
    
    if qry_cnt == "" or qry_cnt is None:
        raise ValueError("qry_cnt is required (e.g. '20')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "HHDFO55020100"

    params = {
        "SRS_CD": srs_cd,
        "EXCH_CD": exch_cd,
        "QRY_CNT": qry_cnt,
        "START_DATE_TIME": start_date_time,
        "CLOSE_DATE_TIME": close_date_time,
        "QRY_GAP": qry_gap,
        "QRY_TP": qry_tp,
        "INDEX_KEY": index_key
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
            return opt_daily_ccnl(
                srs_cd, exch_cd, qry_cnt, start_date_time, close_date_time, 
                qry_gap, qry_tp, index_key, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 