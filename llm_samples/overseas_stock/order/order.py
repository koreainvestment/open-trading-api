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
# [해외주식] 주문/계좌 > 해외주식 주문 [v1_해외주식-001]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-stock/v1/trading/order"

def order(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ovrs_excg_cd: str,  # 해외거래소코드
    pdno: str,  # 상품번호
    ord_qty: str,  # 주문수량
    ovrs_ord_unpr: str,  # 해외주문단가
    ord_dv: str,  # 주문구분 (buy: 매수, sell: 매도)
    ctac_tlno: str,  # 연락전화번호
    mgco_aptm_odno: str,  # 운용사지정주문번호
    ord_svr_dvsn_cd: str,  # 주문서버구분코드
    ord_dvsn: str,  # 주문구분
    env_dv: str = "real",  # 실전모의구분

) -> Optional[pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 주문[v1_해외주식-001]
    해외주식 주문 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ovrs_excg_cd (str): NASD : 나스닥 NYSE : 뉴욕 AMEX : 아멕스 SEHK : 홍콩 SHAA : 중국상해 SZAA : 중국심천 TKSE : 일본 HASE : 베트남 하노이 VNSE : 베트남 호치민
        pdno (str): 종목코드
        ord_qty (str): 주문수량 (해외거래소 별 최소 주문수량 및 주문단위 확인 필요)
        ovrs_ord_unpr (str): 1주당 가격 * 시장가의 경우 1주당 가격을 공란으로 비우지 않음 "0"으로 입력
        ord_dv (str): 주문구분 (buy: 매수, sell: 매도)
        ctac_tlno (str): 
        mgco_aptm_odno (str): 
        ord_svr_dvsn_cd (str): "0"(Default)
        ord_dvsn (str): [Header tr_id TTTT1002U(미국 매수 주문)] 00 : 지정가 32 : LOO(장개시지정가) 34 : LOC(장마감지정가) * 모의투자 VTTT1002U(미국 매수 주문)로는 00:지정가만 가능  [Header tr_id TTTT1006U(미국 매도 주문)] 00 : 지정가 31 : MOO(장개시시장가) 32 : LOO(장개시지정가) 33 : MOC(장마감시장가) 34 : LOC(장마감지정가) * 모의투자 VTTT1006U(미국 매도 주문)로는 00:지정가만 가능  [Header tr_id TTTS1001U(홍콩 매도 주문)] 00 : 지정가 50 : 단주지정가 * 모의투자 VTTS1001U(홍콩 매도 주문)로는 00:지정가만 가능  [그외 tr_id] 제거
        env_dv (str): 실전모의구분 (real:실전, demo:모의)
        
    Returns:
        Optional[pd.DataFrame]: 해외주식 주문 데이터
        
    Example:
        >>> df = order(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ovrs_excg_cd="NASD",
        ...     pdno="AAPL",
        ...     ord_qty="1",
        ...     ovrs_ord_unpr="145.00",
        ...     ord_dv="buy",
        ...     ctac_tlno="",
        ...     mgco_aptm_odno="",
        ...     ord_svr_dvsn_cd="0",
        ...     ord_dvsn="00",
        ...     env_dv="real"
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
        logger.error("ovrs_excg_cd is required. (e.g. 'NASD')")
        raise ValueError("ovrs_excg_cd is required. (e.g. 'NASD')")
    if not pdno:
        logger.error("pdno is required. (e.g. 'AAPL')")
        raise ValueError("pdno is required. (e.g. 'AAPL')")
    if not ord_qty:
        logger.error("ord_qty is required. (e.g. '1')")
        raise ValueError("ord_qty is required. (e.g. '1')")
    if not ovrs_ord_unpr:
        logger.error("ovrs_ord_unpr is required. (e.g. '145.00')")
        raise ValueError("ovrs_ord_unpr is required. (e.g. '145.00')")
    if not ord_dv:
        logger.error("ord_dv is required. (e.g. 'buy' or 'sell')")
        raise ValueError("ord_dv is required. (e.g. 'buy' or 'sell')")
    if not ord_svr_dvsn_cd:
        logger.error("ord_svr_dvsn_cd is required. (e.g. '0')")
        raise ValueError("ord_svr_dvsn_cd is required. (e.g. '0')")
    if not ord_dvsn:
        logger.error("ord_dvsn is required. (e.g. '00')")
        raise ValueError("ord_dvsn is required. (e.g. '00')")

    # TR ID 설정 (매수/매도 및 거래소별)
    if ord_dv == "buy":
        if ovrs_excg_cd in ("NASD", "NYSE", "AMEX"):
            tr_id = "TTTT1002U"  # 미국 매수 주문 [모의투자] VTTT1002U
        elif ovrs_excg_cd == "SEHK":
            tr_id = "TTTS1002U"  # 홍콩 매수 주문 [모의투자] VTTS1002U
        elif ovrs_excg_cd == "SHAA":
            tr_id = "TTTS0202U"  # 중국상해 매수 주문 [모의투자] VTTS0202U
        elif ovrs_excg_cd == "SZAA":
            tr_id = "TTTS0305U"  # 중국심천 매수 주문 [모의투자] VTTS0305U
        elif ovrs_excg_cd == "TKSE":
            tr_id = "TTTS0308U"  # 일본 매수 주문 [모의투자] VTTS0308U
        elif ovrs_excg_cd in ("HASE", "VNSE"):
            tr_id = "TTTS0311U"  # 베트남(하노이,호치민) 매수 주문 [모의투자] VTTS0311U
        else:
            logger.error("ovrs_excg_cd is required. (e.g. 'NASD', 'NYSE', 'AMEX', 'SEHK', 'SHAA', 'SZAA', 'TKSE', 'HASE', 'VNSE')")
            raise ValueError("ovrs_excg_cd is required. (e.g. 'NASD', 'NYSE', 'AMEX', 'SEHK', 'SHAA', 'SZAA', 'TKSE', 'HASE', 'VNSE')")
        sll_type = ""
    elif ord_dv == "sell":
        if ovrs_excg_cd in ("NASD", "NYSE", "AMEX"):
            tr_id = "TTTT1006U"  # 미국 매도 주문 [모의투자] VTTT1006U
        elif ovrs_excg_cd == "SEHK":
            tr_id = "TTTS1001U"  # 홍콩 매도 주문 [모의투자] VTTS1001U
        elif ovrs_excg_cd == "SHAA":
            tr_id = "TTTS1005U"  # 중국상해 매도 주문 [모의투자] VTTS1005U
        elif ovrs_excg_cd == "SZAA":
            tr_id = "TTTS0304U"  # 중국심천 매도 주문 [모의투자] VTTS0304U
        elif ovrs_excg_cd == "TKSE":
            tr_id = "TTTS0307U"  # 일본 매도 주문 [모의투자] VTTS0307U
        elif ovrs_excg_cd in ("HASE", "VNSE"):
            tr_id = "TTTS0310U"  # 베트남(하노이,호치민) 매도 주문 [모의투자] VTTS0310U
        else:
            logger.error("ovrs_excg_cd is required. (e.g. 'NASD', 'NYSE', 'AMEX', 'SEHK', 'SHAA', 'SZAA', 'TKSE', 'HASE', 'VNSE')")
            raise ValueError("ovrs_excg_cd is required. (e.g. 'NASD', 'NYSE', 'AMEX', 'SEHK', 'SHAA', 'SZAA', 'TKSE', 'HASE', 'VNSE')")
        sll_type = "00"
    else:
        logger.error("ord_dv is required. (e.g. 'buy' or 'sell')")
        raise ValueError("ord_dv is required. (e.g. 'buy' or 'sell')")

    # 모의투자인 경우 TR ID 앞에 V 붙이기
    if env_dv == "demo":
        tr_id = "V" + tr_id[1:]
    elif env_dv != "real":
        logger.error("env_dv can only be 'real' or 'demo'")
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "PDNO": pdno,
        "ORD_QTY": ord_qty,
        "OVRS_ORD_UNPR": ovrs_ord_unpr,
        "CTAC_TLNO": ctac_tlno,
        "MGCO_APTM_ODNO": mgco_aptm_odno,
        "SLL_TYPE": sll_type,
        "ORD_SVR_DVSN_CD": ord_svr_dvsn_cd,
        "ORD_DVSN": ord_dvsn,
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
