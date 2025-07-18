# -*- coding: utf-8 -*-
"""
Created on 2025-07-02

@author: LaivData jjlee with cursor
"""

import logging
import time
from typing import Optional
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 기간계좌거래내역 [해외선물-014]
##############################################################################################

# API 정보
API_URL = "/uapi/overseas-futureoption/v1/trading/inquire-period-trans"

def inquire_period_trans(
    inqr_term_from_dt: str,  # 조회기간FROM일자
    inqr_term_to_dt: str,  # 조회기간TO일자
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    acnt_tr_type_cd: str,  # 계좌거래유형코드
    crcy_cd: str,  # 통화코드
    ctx_area_fk100: str,  # 연속조회검색조건100
    ctx_area_nk100: str,  # 연속조회키100
    pwd_chk_yn: str,  # 비밀번호체크여부
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 주문/계좌 
    해외선물옵션 기간계좌거래내역[해외선물-014]
    해외선물옵션 기간계좌거래내역 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        inqr_term_from_dt (str): 조회기간FROM일자 (예: '20220101')
        inqr_term_to_dt (str): 조회기간TO일자 (예: '20221214')
        cano (str): 계좌번호 체계(8-2)의 앞 8자리 (예: '80012345')
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리 (예: '08')
        acnt_tr_type_cd (str): 계좌거래유형코드 (1: 전체, 2:입출금 , 3: 결제)
        crcy_cd (str): 통화코드 ('%%%': 전체, 'TUS': TOT_USD, 'TKR': TOT_KRW, 'KRW': 한국, 'USD': 미국, 'EUR': EUR, 'HKD': 홍콩, 'CNY': 중국, 'JPY': 일본, 'VND': 베트남)
        ctx_area_fk100 (str): 연속조회검색조건100
        ctx_area_nk100 (str): 연속조회키100
        pwd_chk_yn (str): 비밀번호체크여부
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외선물옵션 기간계좌거래내역 데이터
        
    Example:
        >>> df = inquire_period_trans(
        ...     inqr_term_from_dt="20220101",
        ...     inqr_term_to_dt="20221214",
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     acnt_tr_type_cd="%%",
        ...     crcy_cd="%%%",
        ...     ctx_area_fk100="",
        ...     ctx_area_nk100="",
        ...     pwd_chk_yn=""
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not inqr_term_from_dt:
        logger.error("inqr_term_from_dt is required. (e.g. '20220101')")
        raise ValueError("inqr_term_from_dt is required. (e.g. '20220101')")
    if not inqr_term_to_dt:
        logger.error("inqr_term_to_dt is required. (e.g. '20221214')")
        raise ValueError("inqr_term_to_dt is required. (e.g. '20221214')")
    if not cano:
        logger.error("cano is required. (e.g. '80012345')")
        raise ValueError("cano is required. (e.g. '80012345')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '08')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '08')")
    if not acnt_tr_type_cd:
        logger.error("acnt_tr_type_cd is required. (e.g. '%%')")
        raise ValueError("acnt_tr_type_cd is required. (e.g. '%%')")
    if not crcy_cd:
        logger.error("crcy_cd is required. (e.g. '%%%')")
        raise ValueError("crcy_cd is required. (e.g. '%%%')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    tr_id = "OTFM3114R"

    params = {
        "INQR_TERM_FROM_DT": inqr_term_from_dt,
        "INQR_TERM_TO_DT": inqr_term_to_dt,
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "ACNT_TR_TYPE_CD": acnt_tr_type_cd,
        "CRCY_CD": crcy_cd,
        "CTX_AREA_FK100": ctx_area_fk100,
        "CTX_AREA_NK100": ctx_area_nk100,
        "PWD_CHK_YN": pwd_chk_yn,
    }

    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()
            
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data
            
        tr_cont = res.getHeader().tr_cont
        
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_period_trans(
                inqr_term_from_dt,
                inqr_term_to_dt,
                cano,
                acnt_prdt_cd,
                acnt_tr_type_cd,
                crcy_cd,
                ctx_area_fk100,
                ctx_area_nk100,
                pwd_chk_yn,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
