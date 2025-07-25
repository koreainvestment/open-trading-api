# [장내채권] 주문/계좌 - 장내채권 매수가능조회
# Generated by KIS API Generator (Single API Mode)
# -*- coding: utf-8 -*-
"""
Created on 2025-06-20

@author: LaivData jjlee with cursor
"""

import logging
import sys
import time
from typing import Optional

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [장내채권] 주문/계좌 > 장내채권 매수가능조회 [국내주식-199]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-bond/v1/trading/inquire-psbl-order"

def inquire_psbl_order(
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        pdno: str,  # 상품번호
        bond_ord_unpr: str,  # 채권주문단가
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [장내채권] 주문/계좌 
    장내채권 매수가능조회[국내주식-199]
    장내채권 매수가능조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 종합계좌번호 (필수)
        acnt_prdt_cd (str): 계좌상품코드 (필수)
        pdno (str): 채권종목코드(ex KR2033022D33)
        bond_ord_unpr (str): 채권주문단가 (필수)
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 장내채권 매수가능조회 데이터
        
    Example:
        >>> df = inquire_psbl_order("12345678", "01", "KR2033022D33", "1000")
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not cano:
        logger.error("cano is required. (e.g. '1234567890')")
        raise ValueError("cano is required. (e.g. '1234567890')")

    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")

    if not pdno:
        logger.error("pdno is required. (e.g. 'KR2033022D33')")
        raise ValueError("pdno is required. (e.g. 'KR2033022D33')")

    if not bond_ord_unpr:
        logger.error("bond_ord_unpr is required. (e.g. '1000')")
        raise ValueError("bond_ord_unpr is required. (e.g. '1000')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "TTTC8910R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "BOND_ORD_UNPR": bond_ord_unpr,
    }

    # API 호출
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_psbl_order(
                cano,
                acnt_prdt_cd,
                pdno,
                bond_ord_unpr,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 에러 처리
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
