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
# [해외선물옵션] 주문/계좌 > 해외선물옵션 미결제내역조회(잔고) [v1_해외선물-005]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-futureoption/v1/trading/inquire-unpd"

def inquire_unpd(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    fuop_dvsn: str,  # 선물옵션구분
    ctx_area_fk100: str,  # 연속조회검색조건100
    ctx_area_nk100: str,  # 연속조회키100
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 주문/계좌 
    해외선물옵션 미결제내역조회(잔고)[v1_해외선물-005]
    해외선물옵션 미결제내역조회(잔고) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        fuop_dvsn (str): 00: 전체 / 01:선물 / 02: 옵션
        ctx_area_fk100 (str): 연속조회검색조건100
        ctx_area_nk100 (str): 연속조회키100
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외선물옵션 미결제내역조회(잔고) 데이터
        
    Example:
        >>> df = inquire_unpd(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     fuop_dvsn="00",
        ...     ctx_area_fk100="",
        ...     ctx_area_nk100=""
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '80012345')")
        raise ValueError("cano is required. (e.g. '80012345')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '08')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '08')")
    if fuop_dvsn not in ['00', '01', '02']:
        logger.error("fuop_dvsn is required. (e.g. '00')")
        raise ValueError("fuop_dvsn is required. (e.g. '00')")
    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    tr_id = "OTFM1412R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "FUOP_DVSN": fuop_dvsn,
        "CTX_AREA_FK100": ctx_area_fk100,
        "CTX_AREA_NK100": ctx_area_nk100,
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
            return inquire_unpd(
                cano,
                acnt_prdt_cd,
                fuop_dvsn,
                ctx_area_fk100,
                ctx_area_nk100,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
