# -*- coding: utf-8 -*-
"""
Created on 2025-06-30

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
# [해외주식] 주문/계좌 > 해외주식 매수가능금액조회 [v1_해외주식-014]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-stock/v1/trading/inquire-psamount"

def inquire_psamount(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ovrs_excg_cd: str,  # 해외거래소코드
    ovrs_ord_unpr: str,  # 해외주문단가
    item_cd: str,  # 종목코드
    env_dv: str = "real",  # 실전모의구분
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 매수가능금액조회[v1_해외주식-014]
    해외주식 매수가능금액조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ovrs_excg_cd (str): NASD : 나스닥 / NYSE : 뉴욕 / AMEX : 아멕스 SEHK : 홍콩 / SHAA : 중국상해 / SZAA : 중국심천 TKSE : 일본 / HASE : 하노이거래소 / VNSE : 호치민거래소
        ovrs_ord_unpr (str): 해외주문단가 (23.8) 정수부분 23자리, 소수부분 8자리
        item_cd (str): 종목코드
        env_dv (str): 실전모의구분 (real:실전, demo:모의)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외주식 매수가능금액조회 데이터
        
    Example:
        >>> df = inquire_psamount(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ovrs_excg_cd="NASD",
        ...     ovrs_ord_unpr="1.4",
        ...     item_cd="QQQ"
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '81019777')")
        raise ValueError("cano is required. (e.g. '81019777')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")
    if not ovrs_excg_cd:
        logger.error("ovrs_excg_cd is required. (e.g. 'NASD')")
        raise ValueError("ovrs_excg_cd is required. (e.g. 'NASD')")
    if not ovrs_ord_unpr:
        logger.error("ovrs_ord_unpr is required. (e.g. '1.4')")
        raise ValueError("ovrs_ord_unpr is required. (e.g. '1.4')")
    if not item_cd:
        logger.error("item_cd is required. (e.g. 'QQQ')")
        raise ValueError("item_cd is required. (e.g. 'QQQ')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real":
        tr_id = "TTTS3007R"  # 실전투자용 TR ID
    elif env_dv == "demo":
        tr_id = "VTTS3007R"  # 모의투자용 TR ID
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "OVRS_ORD_UNPR": ovrs_ord_unpr,
        "ITEM_CD": item_cd,
    }

    res = ka._url_fetch(api_url=API_URL, ptr_id=tr_id, tr_cont=tr_cont, params=params)

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
            return inquire_psamount(
                cano=cano,
                acnt_prdt_cd=acnt_prdt_cd,
                ovrs_excg_cd=ovrs_excg_cd,
                ovrs_ord_unpr=ovrs_ord_unpr,
                item_cd=item_cd,
                env_dv=env_dv,
                tr_cont="N",
                dataframe=dataframe,
                depth=depth + 1,
                max_depth=max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
