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

def inquire_balance(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ovrs_excg_cd: str,  # 해외거래소코드
    tr_crcy_cd: str,  # 거래통화코드
    ctx_area_fk200: str,  # 연속조회검색조건200
    ctx_area_nk200: str,  # 연속조회키200
    env_dv: str = "real",  # 실전모의구분
    FK200: str = "",  # 연속조회검색조건
    NK200: str = "",  # 연속조회검색조건
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 잔고[v1_해외주식-006]
    해외주식 잔고 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ovrs_excg_cd (str): [모의] NASD : 나스닥 NYSE : 뉴욕  AMEX : 아멕스  [실전] NASD : 미국전체 NAS : 나스닥 NYSE : 뉴욕  AMEX : 아멕스  [모의/실전 공통] SEHK : 홍콩 SHAA : 중국상해 SZAA : 중국심천 TKSE : 일본 HASE : 베트남 하노이 VNSE : 베트남 호치민
        tr_crcy_cd (str): USD : 미국달러 HKD : 홍콩달러 CNY : 중국위안화 JPY : 일본엔화 VND : 베트남동
        ctx_area_fk200 (str): 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK200값 : 다음페이지 조회시(2번째부터)
        ctx_area_nk200 (str): 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK200값 : 다음페이지 조회시(2번째부터)
        env_dv (str): 실전모의구분 (real:실전, demo:모의)
        FK200 (str): 연속조회검색조건
        NK200 (str): 연속조회검색조건
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식 잔고 데이터
        
    Example:
        >>> df1, df2 = inquire_balance(
        ...     cano="810XXXXX",
        ...     acnt_prdt_cd="01",
        ...     ovrs_excg_cd="NASD",
        ...     tr_crcy_cd="USD",
        ...     ctx_area_fk200="",
        ...     ctx_area_nk200=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '810XXXXX')")
        raise ValueError("cano is required. (e.g. '810XXXXX')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")
    if not ovrs_excg_cd:
        logger.error("ovrs_excg_cd is required. (e.g. 'NASD')")
        raise ValueError("ovrs_excg_cd is required. (e.g. 'NASD')")
    if not tr_crcy_cd:
        logger.error("tr_crcy_cd is required. (e.g. 'USD')")
        raise ValueError("tr_crcy_cd is required. (e.g. 'USD')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    url = "/uapi/overseas-stock/v1/trading/inquire-balance"
    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real":
        tr_id = "TTTS3012R"  # 실전투자용 TR ID
    elif env_dv == "demo":
        tr_id = "VTTS3012R"  # 모의투자용 TR ID
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "TR_CRCY_CD": tr_crcy_cd,
        "CTX_AREA_FK200": ctx_area_fk200,
        "CTX_AREA_NK200": ctx_area_nk200,
        "ctx_area_fk200": FK200,
        "ctx_area_nk200": NK200,
    }

    res = ka._url_fetch(url, tr_id, tr_cont, params)

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
        FK200 = res.getBody().ctx_area_fk200 if hasattr(res.getBody(), 'ctx_area_fk200') else ""
        NK200 = res.getBody().ctx_area_nk200 if hasattr(res.getBody(), 'ctx_area_nk200') else ""
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            time.sleep(0.1)
            return inquire_balance(
                cano,
                acnt_prdt_cd,
                ovrs_excg_cd,
                tr_crcy_cd,
                ctx_area_fk200,
                ctx_area_nk200,
                env_dv,
                "N", FK200, NK200, dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(url)
        return pd.DataFrame(), pd.DataFrame()
