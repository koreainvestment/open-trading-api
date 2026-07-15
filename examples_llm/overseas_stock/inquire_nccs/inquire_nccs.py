# -*- coding: utf-8 -*-
"""
Created on 2025-07-01

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
# [해외주식] 주문/계좌 > 해외주식 미체결내역 [v1_해외주식-005]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-stock/v1/trading/inquire-nccs"

def inquire_nccs(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ovrs_excg_cd: str,  # 해외거래소코드
    sort_sqn: str,  # 정렬순서
    FK200: str,  # 연속조회검색조건200
    NK200: str,  # 연속조회키200
    env_dv: str = "real",  # 실전모의구분
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 미체결내역[v1_해외주식-005]
    해외주식 미체결내역 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ovrs_excg_cd (str): 해외거래소코드(필수).
            기존 설명은 NASD를 "나스닥"과 "미국전체"로 동시에 표기합니다.
            따라서 이 문서에서는 확인 전까지 NASD의 조회 범위를 확정하지 않습니다.
            NYSE : 뉴욕, AMEX : 아멕스, SEHK : 홍콩, SHAA : 중국상해,
            SZAA : 중국심천, TKSE : 일본, HASE : 베트남 하노이,
            VNSE : 베트남 호치민
        sort_sqn (str): DS : 정순 그외 : 역순  [header tr_id: TTTS3018R] ""(공란)
        FK200 (str): 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK200값 : 다음페이지 조회시(2번째부터)
        NK200 (str): 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK200값 : 다음페이지 조회시(2번째부터)
        env_dv (str): 실전모의구분 (real:실전, demo:모의).
            현재 구현은 이 값으로 TR ID를 분기하지 않고 TTTS3018R을 사용합니다.
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외주식 미체결내역 데이터.
            반환값에는 전체 조회 완료, 부분 조회, 실패를 구분하는 상태가 없습니다.

    Notes:
        현재 샘플 구현은 응답 헤더 tr_cont가 M 또는 F이면 응답의
        ctx_area_fk200과 ctx_area_nk200을 다음 요청에 전달하고
        tr_cont="N"으로 다시 호출합니다. 이는 현재 코드의 동작 설명이며,
        API 연속조회 계약을 확정하는 문구가 아닙니다.

        max_depth 도달 또는 후속 API 호출 실패 시 이미 수집한 DataFrame을
        반환합니다. 따라서 빈 DataFrame은 정상 0건과 첫 호출 실패를
        구분하지 않으며, 비어 있지 않은 DataFrame도 전체 페이지 완료를
        보장하지 않습니다.
        
    Example:
        >>> df = inquire_nccs(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ovrs_excg_cd="NYSE",
        ...     sort_sqn="DS",
        ...     FK200="",
        ...     NK200=""
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '810XXXXX')")
        raise ValueError("cano is required. (e.g. '810XXXXX')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")
    if not ovrs_excg_cd:
        logger.error("ovrs_excg_cd is required. (e.g. 'NYSE')")
        raise ValueError("ovrs_excg_cd is required. (e.g. 'NYSE')")
    if not sort_sqn:
        logger.error("sort_sqn is required. (e.g. 'DS')")
        raise ValueError("sort_sqn is required. (e.g. 'DS')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    tr_id = "TTTS3018R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "SORT_SQN": sort_sqn,
        "CTX_AREA_FK200": FK200,
        "CTX_AREA_NK200": NK200,
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
            
        tr_cont, NK200, FK200 = res.getHeader().tr_cont, res.getBody().ctx_area_nk200, res.getBody().ctx_area_fk200
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_nccs(
                cano=cano,
                acnt_prdt_cd=acnt_prdt_cd,
                ovrs_excg_cd=ovrs_excg_cd,
                sort_sqn=sort_sqn,
                FK200=FK200,
                NK200=NK200,
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
        # 이미 수집된 데이터가 있으면 그것을 반환, 없으면 빈 DataFrame 반환
        if dataframe is not None and not dataframe.empty:
            logger.info("Returning already collected data due to API error.")
            return dataframe
        else:
            return pd.DataFrame()
