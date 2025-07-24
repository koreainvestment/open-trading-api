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
# [해외주식] 시세분석 > 해외주식 상품기본정보[v1_해외주식-034]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-price/v1/quotations/search-info"


def search_info(
        prdt_type_cd: str,  # 상품유형코드
        pdno: str,  # 상품번호
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외주식] 기본시세 
    해외주식 상품기본정보[v1_해외주식-034]
    해외주식 상품기본정보 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        prdt_type_cd (str): 512  미국 나스닥 / 513  미국 뉴욕 / 529  미국 아멕스  515  일본 501  홍콩 / 543  홍콩CNY / 558  홍콩USD 507  베트남 하노이 / 508  베트남 호치민 551  중국 상해A / 552  중국 심천A
        pdno (str): 예) AAPL (애플)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외주식 상품기본정보 데이터
        
    Example:
        >>> df = search_info(prdt_type_cd="512", pdno="AAPL")
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not prdt_type_cd:
        logger.error("prdt_type_cd is required. (e.g. '512')")
        raise ValueError("prdt_type_cd is required. (e.g. '512')")
    if not pdno:
        logger.error("pdno is required. (e.g. 'AAPL')")
        raise ValueError("pdno is required. (e.g. 'AAPL')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "CTPF1702R"

    params = {
        "PRDT_TYPE_CD": prdt_type_cd,
        "PDNO": pdno,
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
            return search_info(
                prdt_type_cd,
                pdno,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
