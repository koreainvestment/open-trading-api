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

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 일별거래내역 [해외주식-063]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-stock/v1/trading/inquire-period-trans"

def inquire_period_trans(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    erlm_strt_dt: str,  # 등록시작일자
    erlm_end_dt: str,  # 등록종료일자
    ovrs_excg_cd: str,  # 해외거래소코드
    pdno: str,  # 상품번호
    sll_buy_dvsn_cd: str,  # 매도매수구분코드
    loan_dvsn_cd: str,  # 대출구분코드
    FK100: str,  # 연속조회검색조건100
    NK100: str,  # 연속조회키100
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 일별거래내역[해외주식-063]
    해외주식 일별거래내역 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 종합계좌번호
        acnt_prdt_cd (str): 계좌상품코드
        erlm_strt_dt (str): 등록시작일자 (예: 20240420)
        erlm_end_dt (str): 등록종료일자 (예: 20240520)
        ovrs_excg_cd (str): 해외거래소코드
        pdno (str): 상품번호
        sll_buy_dvsn_cd (str): 매도매수구분코드 (00: 전체, 01: 매도, 02: 매수)
        loan_dvsn_cd (str): 대출구분코드
        FK100 (str): 연속조회검색조건100
        NK100 (str): 연속조회키100
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식 일별거래내역 데이터
        
    Example:
        >>> df1, df2 = inquire_period_trans(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     erlm_strt_dt="20240420",
        ...     erlm_end_dt="20240520",
        ...     ovrs_excg_cd="NAS",
        ...     pdno="",
        ...     sll_buy_dvsn_cd="00",
        ...     loan_dvsn_cd="",
        ...     FK100="",
        ...     NK100=""
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
    if not erlm_strt_dt:
        logger.error("erlm_strt_dt is required. (e.g. '20240420')")
        raise ValueError("erlm_strt_dt is required. (e.g. '20240420')")
    if not erlm_end_dt:
        logger.error("erlm_end_dt is required. (e.g. '20240520')")
        raise ValueError("erlm_end_dt is required. (e.g. '20240520')")
    if not ovrs_excg_cd:
        logger.error("ovrs_excg_cd is required. (e.g. 'NAS')")
        raise ValueError("ovrs_excg_cd is required. (e.g. 'NAS')")
    if not sll_buy_dvsn_cd:
        logger.error("sll_buy_dvsn_cd is required. (e.g. '00')")
        raise ValueError("sll_buy_dvsn_cd is required. (e.g. '00')")

    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    tr_id = "CTOS4001R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "ERLM_STRT_DT": erlm_strt_dt,
        "ERLM_END_DT": erlm_end_dt,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "PDNO": pdno,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "LOAN_DVSN_CD": loan_dvsn_cd,
        "CTX_AREA_FK100": FK100,
        "CTX_AREA_NK100": NK100,
    }

    res = ka._url_fetch(api_url=API_URL, ptr_id=tr_id, tr_cont=tr_cont, params=params)

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
        
        tr_cont, NK100, FK100 = res.getHeader().tr_cont, res.getBody().ctx_area_nk100, res.getBody().ctx_area_fk100
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_period_trans(
                cano=cano,
                acnt_prdt_cd=acnt_prdt_cd,
                erlm_strt_dt=erlm_strt_dt,
                erlm_end_dt=erlm_end_dt,
                ovrs_excg_cd=ovrs_excg_cd,
                pdno=pdno,
                sll_buy_dvsn_cd=sll_buy_dvsn_cd,
                loan_dvsn_cd=loan_dvsn_cd,
                FK100=FK100,
                NK100=NK100,
                dataframe1=dataframe1,
                dataframe2=dataframe2,
                tr_cont="N",
                depth=depth + 1,
                max_depth=max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        # 이미 수집된 데이터가 있으면 그것을 반환, 없으면 빈 DataFrame 반환
        if dataframe1 is not None and not dataframe1.empty:
            logger.info("Returning already collected data due to API error.")
            return dataframe1, dataframe2 if dataframe2 is not None else pd.DataFrame()
        else:
            return pd.DataFrame(), pd.DataFrame()
