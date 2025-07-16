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

def inquire_period_profit(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ovrs_excg_cd: str,  # 해외거래소코드
    natn_cd: str,  # 국가코드
    crcy_cd: str,  # 통화코드
    pdno: str,  # 상품번호
    inqr_strt_dt: str,  # 조회시작일자
    inqr_end_dt: str,  # 조회종료일자
    wcrc_frcr_dvsn_cd: str,  # 원화외화구분코드
    ctx_area_fk200: str,  # 연속조회검색조건200
    ctx_area_nk200: str,  # 연속조회키200
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 기간손익[v1_해외주식-032]
    해외주식 기간손익 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ovrs_excg_cd (str): 공란 : 전체,  NASD : 미국, SEHK : 홍콩, SHAA : 중국, TKSE : 일본, HASE : 베트남
        natn_cd (str): 공란(Default)
        crcy_cd (str): 공란 : 전체 USD : 미국달러, HKD : 홍콩달러, CNY : 중국위안화,  JPY : 일본엔화, VND : 베트남동
        pdno (str): 공란 : 전체
        inqr_strt_dt (str): YYYYMMDD
        inqr_end_dt (str): YYYYMMDD
        wcrc_frcr_dvsn_cd (str): 01 : 외화, 02 : 원화
        ctx_area_fk200 (str): 
        ctx_area_nk200 (str): 
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식 기간손익 데이터
        
    Example:
        >>> df1, df2 = inquire_period_profit(
        ...     cano="12345678",
        ...     acnt_prdt_cd="01",
        ...     ovrs_excg_cd="NASD",
        ...     natn_cd="",
        ...     crcy_cd="USD",
        ...     pdno="",
        ...     inqr_strt_dt="20230101",
        ...     inqr_end_dt="20231231",
        ...     wcrc_frcr_dvsn_cd="01",
        ...     ctx_area_fk200="",
        ...     ctx_area_nk200=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '12345678')")
        raise ValueError("cano is required. (e.g. '12345678')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")
    if not ovrs_excg_cd:
        logger.error("ovrs_excg_cd is required. (e.g. 'NASD')")
        raise ValueError("ovrs_excg_cd is required. (e.g. 'NASD')")
    if not crcy_cd:
        logger.error("crcy_cd is required. (e.g. 'USD')")
        raise ValueError("crcy_cd is required. (e.g. 'USD')")
    if not inqr_strt_dt:
        logger.error("inqr_strt_dt is required. (e.g. '20230101')")
        raise ValueError("inqr_strt_dt is required. (e.g. '20230101')")
    if not inqr_end_dt:
        logger.error("inqr_end_dt is required. (e.g. '20231231')")
        raise ValueError("inqr_end_dt is required. (e.g. '20231231')")
    if not wcrc_frcr_dvsn_cd:
        logger.error("wcrc_frcr_dvsn_cd is required. (e.g. '01')")
        raise ValueError("wcrc_frcr_dvsn_cd is required. (e.g. '01')")


    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    url = "/uapi/overseas-stock/v1/trading/inquire-period-profit"
    tr_id = "TTTS3039R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "NATN_CD": natn_cd,
        "CRCY_CD": crcy_cd,
        "PDNO": pdno,
        "INQR_STRT_DT": inqr_strt_dt,
        "INQR_END_DT": inqr_end_dt,
        "WCRC_FRCR_DVSN_CD": wcrc_frcr_dvsn_cd,
        "CTX_AREA_FK200": ctx_area_fk200,
        "CTX_AREA_NK200": ctx_area_nk200,
    }

    res = ka._url_fetch(url, tr_id, tr_cont, params)

    if res.isOK():
        # Output1 처리
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
        # Output2 처리
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
            time.sleep(0.1)
            return inquire_period_profit(
                cano,
                acnt_prdt_cd,
                ovrs_excg_cd,
                natn_cd,
                crcy_cd,
                pdno,
                inqr_strt_dt,
                inqr_end_dt,
                wcrc_frcr_dvsn_cd,
                ctx_area_fk200,
                ctx_area_nk200,
                dataframe1, dataframe2, "N", depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(url)
        return pd.DataFrame(), pd.DataFrame()
