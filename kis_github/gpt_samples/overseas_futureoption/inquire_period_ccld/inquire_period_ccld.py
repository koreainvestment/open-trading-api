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
# [해외선물옵션] 주문/계좌 > 해외선물옵션 기간계좌손익 일별 [해외선물-010]
##############################################################################################

# API 정보
API_URL = "/uapi/overseas-futureoption/v1/trading/inquire-period-ccld"

def inquire_period_ccld(
    inqr_term_from_dt: str,  # 조회기간FROM일자
    inqr_term_to_dt: str,  # 조회기간TO일자
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    crcy_cd: str,  # 통화코드
    whol_trsl_yn: str,  # 전체환산여부
    fuop_dvsn: str,  # 선물옵션구분
    ctx_area_fk200: str,  # 연속조회검색조건200
    ctx_area_nk200: str,  # 연속조회키200
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외선물옵션] 주문/계좌 
    해외선물옵션 기간계좌손익 일별[해외선물-010]
    해외선물옵션 기간계좌손익 일별 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        inqr_term_from_dt (str): 조회기간FROM일자
        inqr_term_to_dt (str): 조회기간TO일자
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        crcy_cd (str): '%%% : 전체 TUS: TOT_USD  / TKR: TOT_KRW KRW: 한국  / USD: 미국 EUR: EUR   / HKD: 홍콩 CNY: 중국  / JPY: 일본'
        whol_trsl_yn (str): 전체환산여부
        fuop_dvsn (str): 00:전체 / 01:선물 / 02:옵션
        ctx_area_fk200 (str): 연속조회검색조건200
        ctx_area_nk200 (str): 연속조회키200
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외선물옵션 기간계좌손익 일별 데이터
        
    Example:
        >>> df1, df2 = inquire_period_ccld(
        ...     inqr_term_from_dt="20250601",
        ...     inqr_term_to_dt="20250630",
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     crcy_cd="%%%",
        ...     whol_trsl_yn="N",
        ...     fuop_dvsn="00",
        ...     ctx_area_fk200="",
        ...     ctx_area_nk200=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not inqr_term_from_dt:
        logger.error("inqr_term_from_dt is required. (e.g. '20250601')")
        raise ValueError("inqr_term_from_dt is required. (e.g. '20250601')")
    if not inqr_term_to_dt:
        logger.error("inqr_term_to_dt is required. (e.g. '20250630')")
        raise ValueError("inqr_term_to_dt is required. (e.g. '20250630')")
    if not cano:
        logger.error("cano is required. (e.g. '80012345')")
        raise ValueError("cano is required. (e.g. '80012345')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '08')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '08')")
    if not crcy_cd:
        logger.error("crcy_cd is required. (e.g. '%%%')")
        raise ValueError("crcy_cd is required. (e.g. '%%%')")
    if not whol_trsl_yn:
        logger.error("whol_trsl_yn is required. (e.g. 'N')")
        raise ValueError("whol_trsl_yn is required. (e.g. 'N')")
    if not fuop_dvsn:
        logger.error("fuop_dvsn is required. (e.g. '00')")
        raise ValueError("fuop_dvsn is required. (e.g. '00')")
    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    tr_id = "OTFM3118R"

    params = {
        "INQR_TERM_FROM_DT": inqr_term_from_dt,
        "INQR_TERM_TO_DT": inqr_term_to_dt,
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "CRCY_CD": crcy_cd,
        "WHOL_TRSL_YN": whol_trsl_yn,
        "FUOP_DVSN": fuop_dvsn,
        "CTX_AREA_FK200": ctx_area_fk200,
        "CTX_AREA_NK200": ctx_area_nk200,
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
            return inquire_period_ccld(
                inqr_term_from_dt,
                inqr_term_to_dt,
                cano,
                acnt_prdt_cd,
                crcy_cd,
                whol_trsl_yn,
                fuop_dvsn,
                ctx_area_fk200,
                ctx_area_nk200,
                "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame(), pd.DataFrame()
