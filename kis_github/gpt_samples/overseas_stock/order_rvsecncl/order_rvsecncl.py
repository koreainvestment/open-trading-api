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

################################################################################
# [해외주식] 주문/계좌 > 해외주식 정정취소주문[v1_해외주식-003]
################################################################################

API_URL = "/uapi/overseas-stock/v1/trading/order-rvsecncl"

def order_rvsecncl(
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        ovrs_excg_cd: str,  # 해외거래소코드
        pdno: str,  # 상품번호
        orgn_odno: str,  # 원주문번호
        rvse_cncl_dvsn_cd: str,  # 정정취소구분코드
        ord_qty: str,  # 주문수량
        ovrs_ord_unpr: str,  # 해외주문단가
        mgco_aptm_odno: str,  # 운용사지정주문번호
        ord_svr_dvsn_cd: str,  # 주문서버구분코드
        env_dv: str = "real",  # 실전모의구분

) -> Optional[pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 정정취소주문[v1_해외주식-003]
    해외주식 정정취소주문 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ovrs_excg_cd (str): NASD : 나스닥  NYSE : 뉴욕  AMEX : 아멕스 SEHK : 홍콩 SHAA : 중국상해 SZAA : 중국심천 TKSE : 일본 HASE : 베트남 하노이 VNSE : 베트남 호치민
        pdno (str): 상품번호
        orgn_odno (str): 정정 또는 취소할 원주문번호 (해외주식_주문 API ouput ODNO  or 해외주식 미체결내역 API output ODNO 참고)
        rvse_cncl_dvsn_cd (str): 01 : 정정  02 : 취소
        ord_qty (str): 주문수량
        ovrs_ord_unpr (str): 취소주문 시, "0" 입력
        mgco_aptm_odno (str): 운용사지정주문번호
        ord_svr_dvsn_cd (str): "0"(Default)
        env_dv (str): 실전모의구분 (real:실전, demo:모의)
        
    Returns:
        Optional[pd.DataFrame]: 해외주식 정정취소주문 데이터
        
    Example:
        >>> df = order_rvsecncl(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ovrs_excg_cd="NYSE",
        ...     pdno="BA",
        ...     orgn_odno="30135009",
        ...     rvse_cncl_dvsn_cd="01",
        ...     ord_qty="1",
        ...     ovrs_ord_unpr="226.00",
        ...     mgco_aptm_odno="",
        ...     ord_svr_dvsn_cd="0",
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
        logger.error("ovrs_excg_cd is required. (e.g. 'NYSE')")
        raise ValueError("ovrs_excg_cd is required. (e.g. 'NYSE')")
    if not pdno:
        logger.error("pdno is required. (e.g. 'BA')")
        raise ValueError("pdno is required. (e.g. 'BA')")
    if not orgn_odno:
        logger.error("orgn_odno is required. (e.g. '30135009')")
        raise ValueError("orgn_odno is required. (e.g. '30135009')")
    if not rvse_cncl_dvsn_cd:
        logger.error("rvse_cncl_dvsn_cd is required. (e.g. '01')")
        raise ValueError("rvse_cncl_dvsn_cd is required. (e.g. '01')")
    if not ord_qty:
        logger.error("ord_qty is required. (e.g. '1')")
        raise ValueError("ord_qty is required. (e.g. '1')")
    if not ovrs_ord_unpr:
        logger.error("ovrs_ord_unpr is required. (e.g. '226.00')")
        raise ValueError("ovrs_ord_unpr is required. (e.g. '226.00')")
    
    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real":
        tr_id = "TTTT1004U"  # 실전투자용 TR ID
    elif env_dv == "demo":
        tr_id = "VTTT1004U"  # 모의투자용 TR ID
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "PDNO": pdno,
        "ORGN_ODNO": orgn_odno,
        "RVSE_CNCL_DVSN_CD": rvse_cncl_dvsn_cd,
        "ORD_QTY": ord_qty,
        "OVRS_ORD_UNPR": ovrs_ord_unpr,
        "MGCO_APTM_ODNO": mgco_aptm_odno,
        "ORD_SVR_DVSN_CD": ord_svr_dvsn_cd,
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
