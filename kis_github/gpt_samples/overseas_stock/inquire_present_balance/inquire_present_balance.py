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
# [해외주식] 주문/계좌 > 해외주식 체결기준현재잔고 [v1_해외주식-008]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-stock/v1/trading/inquire-present-balance"

def inquire_present_balance(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    wcrc_frcr_dvsn_cd: str,  # 원화외화구분코드
    natn_cd: str,  # 국가코드
    tr_mket_cd: str,  # 거래시장코드
    inqr_dvsn_cd: str,  # 조회구분코드
    env_dv: str = "real",  # 실전모의구분
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    dataframe3: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output3)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 체결기준현재잔고[v1_해외주식-008]
    해외주식 체결기준현재잔고 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        wcrc_frcr_dvsn_cd (str): 01 : 원화  02 : 외화
        natn_cd (str): 000 전체 840 미국 344 홍콩 156 중국 392 일본 704 베트남
        tr_mket_cd (str): [Request body NATN_CD 000 설정] 00 : 전체  [Request body NATN_CD 840 설정] 00 : 전체 01 : 나스닥(NASD) 02 : 뉴욕거래소(NYSE) 03 : 미국(PINK SHEETS) 04 : 미국(OTCBB) 05 : 아멕스(AMEX)  [Request body NATN_CD 156 설정] 00 : 전체 01 : 상해B 02 : 심천B 03 : 상해A 04 : 심천A  [Request body NATN_CD 392 설정] 01 : 일본  [Request body NATN_CD 704 설정] 01 : 하노이거래 02 : 호치민거래소  [Request body NATN_CD 344 설정] 01 : 홍콩 02 : 홍콩CNY 03 : 홍콩USD
        inqr_dvsn_cd (str): 00 : 전체  01 : 일반해외주식  02 : 미니스탁
        env_dv (str): 실전모의구분 (real:실전, demo:모의)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        dataframe3 (Optional[pd.DataFrame]): 누적 데이터프레임 (output3)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: 해외주식 체결기준현재잔고 데이터
        
    Example:
        >>> df1, df2, df3 = inquire_present_balance(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     wcrc_frcr_dvsn_cd="01",
        ...     natn_cd="000",
        ...     tr_mket_cd="00",
        ...     inqr_dvsn_cd="00"
        ... )
        >>> print(df1)
        >>> print(df2)
        >>> print(df3)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '810XXXXX')")
        raise ValueError("cano is required. (e.g. '810XXXXX')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")
    if not wcrc_frcr_dvsn_cd:
        logger.error("wcrc_frcr_dvsn_cd is required. (e.g. '01')")
        raise ValueError("wcrc_frcr_dvsn_cd is required. (e.g. '01')")
    if not natn_cd:
        logger.error("natn_cd is required. (e.g. '000')")
        raise ValueError("natn_cd is required. (e.g. '000')")
    if not tr_mket_cd:
        logger.error("tr_mket_cd is required. (e.g. '00')")
        raise ValueError("tr_mket_cd is required. (e.g. '00')")
    if not inqr_dvsn_cd:
        logger.error("inqr_dvsn_cd is required. (e.g. '00')")
        raise ValueError("inqr_dvsn_cd is required. (e.g. '00')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame(), dataframe3 if dataframe3 is not None else pd.DataFrame()
    
    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real":
        tr_id = "CTRP6504R"  # 실전투자용 TR ID
    elif env_dv == "demo":
        tr_id = "VTRP6504R"  # 모의투자용 TR ID
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "WCRC_FRCR_DVSN_CD": wcrc_frcr_dvsn_cd,
        "NATN_CD": natn_cd,
        "TR_MKET_CD": tr_mket_cd,
        "INQR_DVSN_CD": inqr_dvsn_cd,
    }

    res = ka._url_fetch(api_url=API_URL, ptr_id=tr_id, tr_cont=tr_cont, params=params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                if isinstance(output_data, list):
                    current_data1 = pd.DataFrame(output_data)
                else:
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
                if isinstance(output_data, list):
                    current_data2 = pd.DataFrame(output_data)
                else:
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
        
        # output3 처리
        if hasattr(res.getBody(), 'output3'):
            output_data = res.getBody().output3
            if output_data:
                if isinstance(output_data, list):
                    current_data3 = pd.DataFrame(output_data)
                else:
                    current_data3 = pd.DataFrame([output_data])
                
                if dataframe3 is not None:
                    dataframe3 = pd.concat([dataframe3, current_data3], ignore_index=True)
                else:
                    dataframe3 = current_data3
            else:
                if dataframe3 is None:
                    dataframe3 = pd.DataFrame()
        else:
            if dataframe3 is None:
                dataframe3 = pd.DataFrame()
        
        tr_cont = res.getHeader().tr_cont
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_present_balance(
                cano=cano,
                acnt_prdt_cd=acnt_prdt_cd,
                wcrc_frcr_dvsn_cd=wcrc_frcr_dvsn_cd,
                natn_cd=natn_cd,
                tr_mket_cd=tr_mket_cd,
                inqr_dvsn_cd=inqr_dvsn_cd,
                env_dv=env_dv,
                dataframe1=dataframe1,
                dataframe2=dataframe2,
                dataframe3=dataframe3,
                tr_cont="N",
                depth=depth + 1,
                max_depth=max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2, dataframe3
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        # 이미 수집된 데이터가 있으면 그것을 반환, 없으면 빈 DataFrame 반환
        if dataframe1 is not None and not dataframe1.empty:
            logger.info("Returning already collected data due to API error.")
            return dataframe1, dataframe2 if dataframe2 is not None else pd.DataFrame(), dataframe3 if dataframe3 is not None else pd.DataFrame()
        else:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
