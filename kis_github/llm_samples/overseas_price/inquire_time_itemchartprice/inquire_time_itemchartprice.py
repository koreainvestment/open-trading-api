# -*- coding: utf-8 -*-
"""
Created on 2025-06-30

@author: LaivData jjlee with cursor
"""

import logging
import time
from typing import Optional, Tuple
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 기본시세 > 해외주식분봉조회[v1_해외주식-030]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-price/v1/quotations/inquire-time-itemchartprice"

def inquire_time_itemchartprice(
    auth: str,  # 사용자권한정보
    excd: str,  # 거래소코드
    symb: str,  # 종목코드
    nmin: str,  # 분갭
    pinc: str,  # 전일포함여부
    next: str,  # 다음여부
    nrec: str,  # 요청갯수
    fill: str,  # 미체결채움구분
    keyb: str,  # NEXT KEY BUFF
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 기본시세 
    해외주식분봉조회[v1_해외주식-030]
    해외주식분봉조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        auth (str): "" 공백으로 입력
        excd (str): NYS : 뉴욕 NAS : 나스닥 AMS : 아멕스  HKS : 홍콩 SHS : 상해  SZS : 심천 HSX : 호치민 HNX : 하노이 TSE : 도쿄   ※ 주간거래는 최대 1일치 분봉만 조회 가능 BAY : 뉴욕(주간) BAQ : 나스닥(주간) BAA : 아멕스(주간)
        symb (str): 종목코드(ex. TSLA)
        nmin (str): 분단위(1: 1분봉, 2: 2분봉, ...)
        pinc (str): 0:당일 1:전일포함 ※ 다음조회 시 반드시 "1"로 입력
        next (str): 처음조회 시, "" 공백 입력 다음조회 시, "1" 입력
        nrec (str): 레코드요청갯수 (최대 120)
        fill (str): "" 공백으로 입력
        keyb (str): 처음 조회 시, "" 공백 입력 다음 조회 시, 이전 조회 결과의 마지막 분봉 데이터를 이용하여, 1분 전 혹은 n분 전의 시간을 입력  (형식: YYYYMMDDHHMMSS, ex. 20241014140100)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식분봉조회 데이터
        
    Example:
        >>> df1, df2 = inquire_time_itemchartprice(
        ...     auth="", excd="NAS", symb="TSLA", nmin="5", pinc="1", next="1", nrec="120", fill="", keyb=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not excd:
        logger.error("excd is required. (e.g. 'NAS')")
        raise ValueError("excd is required. (e.g. 'NAS')")
    if not symb:
        logger.error("symb is required. (e.g. 'TSLA')")
        raise ValueError("symb is required. (e.g. 'TSLA')")
    if not nmin:
        logger.error("nmin is required. (e.g. '5')")
        raise ValueError("nmin is required. (e.g. '5')")
    if not pinc:
        logger.error("pinc is required. (e.g. '1')")
        raise ValueError("pinc is required. (e.g. '1')")
    if not nrec or int(nrec)>120:
        logger.error("nrec is required. (e.g. '120', 최대120개)")
        raise ValueError("nrec is required. (e.g. '120', 최대120개)")
    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    tr_id = "HHDFS76950200"

    params = {
        "AUTH": auth,
        "EXCD": excd,
        "SYMB": symb,
        "NMIN": nmin,
        "PINC": pinc,
        "NEXT": next,
        "NREC": nrec,
        "FILL": fill,
        "KEYB": keyb,
    }

    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        # Output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                if isinstance(output_data, list):
                    current_data1 = pd.DataFrame(output_data)
                else:
                    current_data1 = pd.DataFrame([output_data])
                
                if dataframe1 is not None:
                    dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
                else:
                    dataframe1 = current_data1
            else:
                if dataframe1 is None:
                    dataframe1 = pd.DataFrame()
        else:
            if dataframe1 is None:
                dataframe1 = pd.DataFrame()
        
        # Output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                if isinstance(output_data, list):
                    current_data2 = pd.DataFrame(output_data)
                else:
                    current_data2 = pd.DataFrame([output_data])
                
                if dataframe2 is not None:
                    dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
                else:
                    dataframe2 = current_data2
            else:
                if dataframe2 is None:
                    dataframe2 = pd.DataFrame()
        else:
            if dataframe2 is None:
                dataframe2 = pd.DataFrame()
        
        tr_cont = res.getHeader().tr_cont
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_time_itemchartprice(
                auth,
                excd,
                symb,
                nmin,
                pinc,
                next,
                nrec,
                fill,
                keyb,
                "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame(), pd.DataFrame()
