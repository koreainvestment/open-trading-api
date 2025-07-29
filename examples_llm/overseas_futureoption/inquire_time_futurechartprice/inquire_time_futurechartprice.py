# -*- coding: utf-8 -*-
"""
Created on 2025-07-02

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
# [해외선물옵션] 기본시세 > 해외선물 분봉조회[해외선물-016]
##############################################################################################

# API 정보
API_URL = "/uapi/overseas-futureoption/v1/quotations/inquire-time-futurechartprice"

def inquire_time_futurechartprice(
    srs_cd: str,  # 종목코드
    exch_cd: str,  # 거래소코드
    start_date_time: str,  # 조회시작일시
    close_date_time: str,  # 조회종료일시
    qry_tp: str,  # 조회구분
    qry_cnt: str,  # 요청개수
    qry_gap: str,  # 묶음개수
    index_key: str,  # 이전조회KEY
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외선물옵션] 기본시세 
    해외선물 분봉조회[해외선물-016]
    해외선물 분봉조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        srs_cd (str): ex) CNHU24 ※ 종목코드 "포럼 > FAQ > 종목정보 다운로드(해외) - 해외지수선물" 참고
        exch_cd (str): CME
        start_date_time (str): 공백
        close_date_time (str): ex) 20230823
        qry_tp (str): Q : 최초조회시 , P : 다음키(INDEX_KEY) 입력하여 조회시
        qry_cnt (str): 120 (조회갯수)
        qry_gap (str): 5 (분간격)
        index_key (str): 다음조회(QRY_TP를 P로 입력) 시, 이전 호출의 "output1 > index_key" 기입하여 조회
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외선물 분봉조회 데이터
        
    Example:
        >>> df1, df2 = inquire_time_futurechartprice(
        ...     srs_cd="BONU25",
        ...     exch_cd="EUREX",
        ...     start_date_time="20250101",
        ...     close_date_time="20250702",
        ...     qry_tp="Q",
        ...     qry_cnt="120",
        ...     qry_gap="1",
        ...     index_key=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not srs_cd:
        logger.error("srs_cd is required. (e.g. 'BONU25')")
        raise ValueError("srs_cd is required. (e.g. 'BONU25')")
    if not exch_cd:
        logger.error("exch_cd is required. (e.g. 'EUREX')")
        raise ValueError("exch_cd is required. (e.g. 'EUREX')")
    if not close_date_time:
        logger.error("close_date_time is required. (e.g. '20250702')")
        raise ValueError("close_date_time is required. (e.g. '20250702')")
    if not qry_cnt:
        logger.error("qry_cnt is required. (e.g. '120')")
        raise ValueError("qry_cnt is required. (e.g. '120')")
    if not qry_gap:
        logger.error("qry_gap is required. (e.g. '1', '5', '10', '15', '30', '60')")
        raise ValueError("qry_gap is required. (e.g. '1', '5', '10', '15', '30', '60')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    tr_id = "HHDFC55020400"

    params = {
        "SRS_CD": srs_cd,
        "EXCH_CD": exch_cd,
        "START_DATE_TIME": start_date_time,
        "CLOSE_DATE_TIME": close_date_time,
        "QRY_TP": qry_tp,
        "QRY_CNT": qry_cnt,
        "QRY_GAP": qry_gap,
        "INDEX_KEY": index_key,
    }

    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                # output1은 단일 객체, output2는 배열일 수 있음
                if isinstance(output_data, list):
                    current_data1 = pd.DataFrame(output_data)
                else:
                    # 단일 객체인 경우 리스트로 감싸서 DataFrame 생성
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
        # output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                # output1은 단일 객체, output2는 배열일 수 있음
                if isinstance(output_data, list):
                    current_data2 = pd.DataFrame(output_data)
                else:
                    # 단일 객체인 경우 리스트로 감싸서 DataFrame 생성
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
        index_key = res.getBody().output2["index_key"]
        qry_tp = "P"

        print("index _key", index_key, "//" )

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_time_futurechartprice(
                srs_cd,
                exch_cd,
                start_date_time,
                close_date_time,
                qry_tp,
                qry_cnt,
                qry_gap,
                index_key,
                dataframe1, dataframe2, "N", depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame(), pd.DataFrame()
