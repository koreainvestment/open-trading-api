# -*- coding: utf-8 -*-
"""
Created on 2025-07-01

@author: LaivData jjlee with cursor
"""

import logging
from typing import Optional
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 미국주간정정취소 [v1_해외주식-027]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-stock/v1/trading/daytime-order-rvsecncl"

def daytime_order_rvsecncl(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ovrs_excg_cd: str,  # 해외거래소코드
    pdno: str,  # 상품번호
    orgn_odno: str,  # 원주문번호
    rvse_cncl_dvsn_cd: str,  # 정정취소구분코드
    ord_qty: str,  # 주문수량
    ovrs_ord_unpr: str,  # 해외주문단가
    ctac_tlno: str,  # 연락전화번호
    mgco_aptm_odno: str,  # 운용사지정주문번호
    ord_svr_dvsn_cd: str,  # 주문서버구분코드

) -> Optional[pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 미국주간정정취소[v1_해외주식-027]
    해외주식 미국주간정정취소 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ovrs_excg_cd (str): NASD:나스닥 / NYSE:뉴욕 / AMEX:아멕스
        pdno (str): 종목코드
        orgn_odno (str): 정정 또는 취소할 원주문번호
        rvse_cncl_dvsn_cd (str): 01 : 정정, 02 : 취소
        ord_qty (str): 주문수량
        ovrs_ord_unpr (str): 소수점 포함, 1주당 가격
        ctac_tlno (str): 연락전화번호
        mgco_aptm_odno (str): 운용사지정주문번호
        ord_svr_dvsn_cd (str): 주문서버구분코드
        
    Returns:
        Optional[pd.DataFrame]: 해외주식 미국주간정정취소 데이터
        
    Example:
        >>> df = daytime_order_rvsecncl(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ovrs_excg_cd="NASD",
        ...     pdno="AAPL",
        ...     orgn_odno="1234567890",
        ...     rvse_cncl_dvsn_cd="01",
        ...     ord_qty="100",
        ...     ovrs_ord_unpr="150.00",
        ...     ctac_tlno="01012345678",
        ...     mgco_aptm_odno="000000000001",
        ...     ord_svr_dvsn_cd="0"
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '12345678')")
        raise ValueError("cano is required. (e.g. '12345678')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")
    if not ovrs_excg_cd:
        logger.error("ovrs_excg_cd is required. (e.g. 'NASD')")
        raise ValueError("ovrs_excg_cd is required. (e.g. 'NASD')")
    if not pdno:
        logger.error("pdno is required. (e.g. 'AAPL')")
        raise ValueError("pdno is required. (e.g. 'AAPL')")
    if not orgn_odno:
        logger.error("orgn_odno is required. (e.g. '1234567890')")
        raise ValueError("orgn_odno is required. (e.g. '1234567890')")
    if rvse_cncl_dvsn_cd not in ["01", "02"]:
        logger.error("rvse_cncl_dvsn_cd is required. (e.g. '01' or '02')")
        raise ValueError("rvse_cncl_dvsn_cd is required. (e.g. '01' or '02')")
    if not ord_qty:
        logger.error("ord_qty is required. (e.g. '100')")
        raise ValueError("ord_qty is required. (e.g. '100')")
    if not ovrs_ord_unpr:
        logger.error("ovrs_ord_unpr is required. (e.g. '150.00')")
        raise ValueError("ovrs_ord_unpr is required. (e.g. '150.00')")
    if not ord_svr_dvsn_cd:
        logger.error("ord_svr_dvsn_cd is required. (e.g. '0')")
        raise ValueError("ord_svr_dvsn_cd is required. (e.g. '0')")

    tr_id = "TTTS6038U"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "PDNO": pdno,
        "ORGN_ODNO": orgn_odno,
        "RVSE_CNCL_DVSN_CD": rvse_cncl_dvsn_cd,
        "ORD_QTY": ord_qty,
        "OVRS_ORD_UNPR": ovrs_ord_unpr,
        "CTAC_TLNO": ctac_tlno,
        "MGCO_APTM_ODNO": mgco_aptm_odno,
        "ORD_SVR_DVSN_CD": ord_svr_dvsn_cd,
    }

    res = ka._url_fetch(api_url=API_URL,
                         ptr_id=tr_id,
                         tr_cont="",
                         params=params,
                         postFlag=True
                         )

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            dataframe = pd.DataFrame(output_data)
        else:
            dataframe = pd.DataFrame()
                    
        logger.info("Data fetch complete.")
        return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
