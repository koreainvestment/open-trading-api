# -*- coding: utf-8 -*-
"""
Created on 2025-06-27

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
# [해외주식] 시세분석 > 해외주식조건검색[v1_해외주식-015]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-price/v1/quotations/inquire-search"

def inquire_search(
    auth: str,  # 사용자권한정보
    excd: str,  # 거래소코드
    co_yn_pricecur: str,  # 현재가선택조건
    co_st_pricecur: str,  # 현재가시작범위가
    co_en_pricecur: str,  # 현재가끝범위가
    co_yn_rate: str,  # 등락율선택조건
    co_st_rate: str,  # 등락율시작율
    co_en_rate: str,  # 등락율끝율
    co_yn_valx: str,  # 시가총액선택조건
    co_st_valx: str,  # 시가총액시작액
    co_en_valx: str,  # 시가총액끝액
    co_yn_shar: str,  # 발행주식수선택조건
    co_st_shar: str,  # 발행주식시작수
    co_en_shar: str,  # 발행주식끝수
    co_yn_volume: str,  # 거래량선택조건
    co_st_volume: str,  # 거래량시작량
    co_en_volume: str,  # 거래량끝량
    co_yn_amt: str,  # 거래대금선택조건
    co_st_amt: str,  # 거래대금시작금
    co_en_amt: str,  # 거래대금끝금
    co_yn_eps: str,  # EPS선택조건
    co_st_eps: str,  # EPS시작
    co_en_eps: str,  # EPS끝
    co_yn_per: str,  # PER선택조건
    co_st_per: str,  # PER시작
    co_en_per: str,  # PER끝
    keyb: str,  # NEXT KEY BUFF
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 기본시세 
    해외주식조건검색[v1_해외주식-015]
    해외주식조건검색 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        auth (str): "" (Null 값 설정)
        excd (str): NYS : 뉴욕, NAS : 나스닥,  AMS : 아멕스  HKS : 홍콩, SHS : 상해 , SZS : 심천 HSX : 호치민, HNX : 하노이 TSE : 도쿄
        co_yn_pricecur (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_pricecur (str): 단위: 각국통화(JPY, USD, HKD, CNY, VND)
        co_en_pricecur (str): 단위: 각국통화(JPY, USD, HKD, CNY, VND)
        co_yn_rate (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_rate (str): %
        co_en_rate (str): %
        co_yn_valx (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_valx (str): 단위: 천
        co_en_valx (str): 단위: 천
        co_yn_shar (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_shar (str): 단위: 천
        co_en_shar (str): 단위: 천
        co_yn_volume (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_volume (str): 단위: 주
        co_en_volume (str): 단위: 주
        co_yn_amt (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_amt (str): 단위: 천
        co_en_amt (str): 단위: 천
        co_yn_eps (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_eps (str): 
        co_en_eps (str): 
        co_yn_per (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_per (str): 
        co_en_per (str): 
        keyb (str): "" 공백 입력
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식조건검색 데이터
        
    Example:
        >>> df1, df2 = inquire_search(
        ...     auth="", excd="NAS", co_yn_pricecur="1", co_st_pricecur="160", co_en_pricecur="161",
        ...     co_yn_rate="", co_st_rate="", co_en_rate="", co_yn_valx="", co_st_valx="", co_en_valx="",
        ...     co_yn_shar="", co_st_shar="", co_en_shar="", co_yn_volume="", co_st_volume="", co_en_volume="",
        ...     co_yn_amt="", co_st_amt="", co_en_amt="", co_yn_eps="", co_st_eps="", co_en_eps="",
        ...     co_yn_per="", co_st_per="", co_en_per="", keyb=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not excd:
        logger.error("excd is required. (e.g. 'NAS')")
        raise ValueError("excd is required. (e.g. 'NAS')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    tr_id = "HHDFS76410000"

    params = {
        "AUTH": auth,
        "EXCD": excd,
        "CO_YN_PRICECUR": co_yn_pricecur,
        "CO_ST_PRICECUR": co_st_pricecur,
        "CO_EN_PRICECUR": co_en_pricecur,
        "CO_YN_RATE": co_yn_rate,
        "CO_ST_RATE": co_st_rate,
        "CO_EN_RATE": co_en_rate,
        "CO_YN_VALX": co_yn_valx,
        "CO_ST_VALX": co_st_valx,
        "CO_EN_VALX": co_en_valx,
        "CO_YN_SHAR": co_yn_shar,
        "CO_ST_SHAR": co_st_shar,
        "CO_EN_SHAR": co_en_shar,
        "CO_YN_VOLUME": co_yn_volume,
        "CO_ST_VOLUME": co_st_volume,
        "CO_EN_VOLUME": co_en_volume,
        "CO_YN_AMT": co_yn_amt,
        "CO_ST_AMT": co_st_amt,
        "CO_EN_AMT": co_en_amt,
        "CO_YN_EPS": co_yn_eps,
        "CO_ST_EPS": co_st_eps,
        "CO_EN_EPS": co_en_eps,
        "CO_YN_PER": co_yn_per,
        "CO_ST_PER": co_st_per,
        "CO_EN_PER": co_en_per,
        "KEYB": keyb,
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
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_search(
                auth,
                excd,
                co_yn_pricecur,
                co_st_pricecur,
                co_en_pricecur,
                co_yn_rate,
                co_st_rate,
                co_en_rate,
                co_yn_valx,
                co_st_valx,
                co_en_valx,
                co_yn_shar,
                co_st_shar,
                co_en_shar,
                co_yn_volume,
                co_st_volume,
                co_en_volume,
                co_yn_amt,
                co_st_amt,
                co_en_amt,
                co_yn_eps,
                co_st_eps,
                co_en_eps,
                co_yn_per,
                co_st_per,
                co_en_per,
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
