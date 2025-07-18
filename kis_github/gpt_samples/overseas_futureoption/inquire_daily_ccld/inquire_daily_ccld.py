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
# [해외선물옵션] 주문/계좌 > 해외선물옵션 일별체결내역[해외선물-011]
##############################################################################################

# API 정보
API_URL = "/uapi/overseas-futureoption/v1/trading/inquire-daily-ccld"

def inquire_daily_ccld(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    strt_dt: str,  # 시작일자
    end_dt: str,  # 종료일자
    fuop_dvsn_cd: str,  # 선물옵션구분코드
    fm_pdgr_cd: str,  # FM상품군코드
    crcy_cd: str,  # 통화코드
    fm_item_ftng_yn: str,  # FM종목합산여부
    sll_buy_dvsn_cd: str,  # 매도매수구분코드
    ctx_area_fk200: str,  # 연속조회검색조건200
    ctx_area_nk200: str,  # 연속조회키200
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외선물옵션] 주문/계좌 
    해외선물옵션 일별 체결내역[해외선물-011]
    해외선물옵션 일별 체결내역 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        strt_dt (str): 시작일자(YYYYMMDD)
        end_dt (str): 종료일자(YYYYMMDD)
        fuop_dvsn_cd (str): 00:전체 / 01:선물 / 02:옵션
        fm_pdgr_cd (str): 공란(Default)
        crcy_cd (str): %%% : 전체 TUS: TOT_USD  / TKR: TOT_KRW KRW: 한국  / USD: 미국 EUR: EUR   / HKD: 홍콩 CNY: 중국  / JPY: 일본 VND: 베트남
        fm_item_ftng_yn (str): "N"(Default)
        sll_buy_dvsn_cd (str): %%: 전체 / 01 : 매도 / 02 : 매수
        ctx_area_fk200 (str): 연속조회검색조건200
        ctx_area_nk200 (str): 연속조회키200
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외선물옵션 일별 체결내역 데이터
        
    Example:
        >>> df1, df2 = inquire_daily_ccld(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     strt_dt="20221010",
        ...     end_dt="20221216",
        ...     fuop_dvsn_cd="00",
        ...     fm_pdgr_cd="",
        ...     crcy_cd="%%%",
        ...     fm_item_ftng_yn="N",
        ...     sll_buy_dvsn_cd="%%",
        ...     ctx_area_fk200="",
        ...     ctx_area_nk200=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '80012345')")
        raise ValueError("cano is required. (e.g. '80012345')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '08')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '08')")
    if not strt_dt:
        logger.error("strt_dt is required. (e.g. '20221010')")
        raise ValueError("strt_dt is required. (e.g. '20221010')")
    if not end_dt:
        logger.error("end_dt is required. (e.g. '20221216')")
        raise ValueError("end_dt is required. (e.g. '20221216')")
    if fuop_dvsn_cd not in ['00', '01', '02']:
        logger.error("fuop_dvsn_cd is required. (e.g. '00', '01', '02')")
        raise ValueError("fuop_dvsn_cd is required. (e.g. '00', '01', '02')")
    if not crcy_cd:
        logger.error("crcy_cd is required. (e.g. '%%%',KRW, USD, EUR..)")
        raise ValueError("crcy_cd is required. (e.g. '%%%',KRW, USD, EUR..)")
    if not fm_item_ftng_yn:
        logger.error("fm_item_ftng_yn is required. (e.g. 'N')")
        raise ValueError("fm_item_ftng_yn is required. (e.g. 'N')")
    if not sll_buy_dvsn_cd:
        logger.error("sll_buy_dvsn_cd is required. (e.g. '%%')")
        raise ValueError("sll_buy_dvsn_cd is required. (e.g. '%%')")
    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    tr_id = "OTFM3122R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "STRT_DT": strt_dt,
        "END_DT": end_dt,
        "FUOP_DVSN_CD": fuop_dvsn_cd,
        "FM_PDGR_CD": fm_pdgr_cd,
        "CRCY_CD": crcy_cd,
        "FM_ITEM_FTNG_YN": fm_item_ftng_yn,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "CTX_AREA_FK200": ctx_area_fk200,
        "CTX_AREA_NK200": ctx_area_nk200,
    }

    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        # output 처리
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
        # output1 처리
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
        tr_cont, ctx_area_fk200, ctx_area_nk200 = res.getHeader().tr_cont, res.getBody().ctx_area_fk200, res.getBody().ctx_area_fk200
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_daily_ccld(
                cano,
                acnt_prdt_cd,
                strt_dt,
                end_dt,
                fuop_dvsn_cd,
                fm_pdgr_cd,
                crcy_cd,
                fm_item_ftng_yn,
                sll_buy_dvsn_cd,
                ctx_area_fk200,
                ctx_area_nk200,
                dataframe1, dataframe2, "N", depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame(), pd.DataFrame()
