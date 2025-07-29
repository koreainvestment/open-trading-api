# -*- coding: utf-8 -*-
"""
Created on 2025-06-30

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
# [해외주식] 주문/계좌 > 해외주식 미국주간주문 [v1_해외주식-026]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-stock/v1/trading/daytime-order"

def daytime_order(
    order_dv: str, # 주문구분 buy(매수) / sell(매도)
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ovrs_excg_cd: str,  # 해외거래소코드
    pdno: str,  # 상품번호
    ord_qty: str,  # 주문수량
    ovrs_ord_unpr: str,  # 해외주문단가
    ctac_tlno: str,  # 연락전화번호
    mgco_aptm_odno: str,  # 운용사지정주문번호
    ord_svr_dvsn_cd: str,  # 주문서버구분코드
    ord_dvsn: str,  # 주문구분

) -> Optional[pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 미국주간주문[v1_해외주식-026]
    해외주식 미국주간주문 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        order_dv (str): 주문구분 buy(매수) / sell(매도)
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ovrs_excg_cd (str): NASD:나스닥 / NYSE:뉴욕 / AMEX:아멕스
        pdno (str): 종목코드
        ord_qty (str): 해외거래소 별 최소 주문수량 및 주문단위 확인 필요
        ovrs_ord_unpr (str): 소수점 포함, 1주당 가격 * 시장가의 경우 1주당 가격을 공란으로 비우지 않음 "0"으로 입력
        ctac_tlno (str): " "
        mgco_aptm_odno (str): " "
        ord_svr_dvsn_cd (str): "0"
        ord_dvsn (str): [미국 매수/매도 주문]  00 : 지정가  * 주간거래는 지정가만 가능
        
    Returns:
        Optional[pd.DataFrame]: 해외주식 미국주간주문 데이터
        
    Example:
        >>> df = daytime_order(
        ...     order_dv="buy",
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ovrs_excg_cd="NASD",
        ...     pdno="AAPL",
        ...     ord_qty="10",
        ...     ovrs_ord_unpr="150.00",
        ...     ctac_tlno="01012345678",
        ...     mgco_aptm_odno="",
        ...     ord_svr_dvsn_cd="0",
        ...     ord_dvsn="00"
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
    if not ord_qty:
        logger.error("ord_qty is required. (e.g. '10')")
        raise ValueError("ord_qty is required. (e.g. '10')")
    if not ovrs_ord_unpr:
        logger.error("ovrs_ord_unpr is required. (e.g. '150.00')")
        raise ValueError("ovrs_ord_unpr is required. (e.g. '150.00')")
    if not ord_svr_dvsn_cd:
        logger.error("ord_svr_dvsn_cd is required. (e.g. '0')")
        raise ValueError("ord_svr_dvsn_cd is required. (e.g. '0')")
    if not ord_dvsn:
        logger.error("ord_dvsn is required. (e.g. '00')")
        raise ValueError("ord_dvsn is required. (e.g. '00')")

    if order_dv == "buy":
        tr_id = "TTTS6036U"
    elif order_dv == "sell":
        tr_id = "TTTS6037U"
    else:
        logger.error("Invalid order_dv. (e.g. 'buy' or 'sell')")
        raise ValueError("Invalid order_dv. (e.g. 'buy' or 'sell')")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "PDNO": pdno,
        "ORD_QTY": ord_qty,
        "OVRS_ORD_UNPR": ovrs_ord_unpr,
        "CTAC_TLNO": ctac_tlno,
        "MGCO_APTM_ODNO": mgco_aptm_odno,
        "ORD_SVR_DVSN_CD": ord_svr_dvsn_cd,
        "ORD_DVSN": ord_dvsn,
    }

    res = ka._url_fetch(api_url=API_URL,
                         ptr_id=tr_id,
                         tr_cont="",
                         params=params,
                         postFlag=True)

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
