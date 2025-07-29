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
# [해외주식] 주문/계좌 > 해외주식 주문체결내역 [v1_해외주식-007]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-stock/v1/trading/inquire-ccnl"


def inquire_ccnl(
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        pdno: str,  # 상품번호
        ord_strt_dt: str,  # 주문시작일자
        ord_end_dt: str,  # 주문종료일자
        sll_buy_dvsn: str,  # 매도매수구분
        ccld_nccs_dvsn: str,  # 체결미체결구분
        sort_sqn: str,  # 정렬순서
        ord_dt: str,  # 주문일자
        ord_gno_brno: str,  # 주문채번지점번호
        odno: str,  # 주문번호
        ovrs_excg_cd: str = "",  # 해외거래소코드
        NK200: str = "",  # 연속조회키200
        FK200: str = "",  # 연속조회검색조건200
        env_dv: str = "real",  # 실전모의구분
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 주문체결내역[v1_해외주식-007]
    해외주식 주문체결내역 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        pdno (str): 전종목일 경우 "%" 입력 ※ 모의투자계좌의 경우 ""(전체 조회)만 가능
        ord_strt_dt (str): YYYYMMDD 형식 (현지시각 기준)
        ord_end_dt (str): YYYYMMDD 형식 (현지시각 기준)
        sll_buy_dvsn (str): 00 : 전체  01 : 매도  02 : 매수 ※ 모의투자계좌의 경우 "00"(전체 조회)만 가능
        ccld_nccs_dvsn (str): 00 : 전체  01 : 체결  02 : 미체결 ※ 모의투자계좌의 경우 "00"(전체 조회)만 가능
        ovrs_excg_cd (str): 전종목일 경우 "%" 입력 NASD : 미국시장 전체(나스닥, 뉴욕, 아멕스) NYSE : 뉴욕 AMEX : 아멕스 SEHK : 홍콩  SHAA : 중국상해 SZAA : 중국심천 TKSE : 일본 HASE : 베트남 하노이 VNSE : 베트남 호치민 ※ 모의투자계좌의 경우 ""(전체 조회)만 가능
        sort_sqn (str): DS : 정순 AS : 역순  ※ 모의투자계좌의 경우 정렬순서 사용불가(Default : DS(정순))
        ord_dt (str): "" (Null 값 설정)
        ord_gno_brno (str): "" (Null 값 설정)
        odno (str): "" (Null 값 설정) ※ 주문번호로 검색 불가능합니다. 반드시 ""(Null 값 설정) 바랍니다.
        NK200 (str): 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK200값 : 다음페이지 조회시(2번째부터)
        FK200 (str): 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK200값 : 다음페이지 조회시(2번째부터)
        env_dv (str): 실전모의구분 (real:실전, demo:모의)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외주식 주문체결내역 데이터
        
    Example:
        >>> df = inquire_ccnl(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     pdno="",
        ...     ord_strt_dt="20250601",
        ...     ord_end_dt="20250630",
        ...     sll_buy_dvsn="00",
        ...     ccld_nccs_dvsn="00",
        ...     ovrs_excg_cd="%",
        ...     sort_sqn="DS",
        ...     ord_dt="",
        ...     ord_gno_brno="02111",
        ...     odno="",
        ...     NK200="",
        ...     FK200=""
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
    if not ord_strt_dt:
        logger.error("ord_strt_dt is required. (e.g. '20211027')")
        raise ValueError("ord_strt_dt is required. (e.g. '20211027')")
    if not ord_end_dt:
        logger.error("ord_end_dt is required. (e.g. '20211027')")
        raise ValueError("ord_end_dt is required. (e.g. '20211027')")
    if not sll_buy_dvsn:
        logger.error("sll_buy_dvsn is required. (e.g. '00')")
        raise ValueError("sll_buy_dvsn is required. (e.g. '00')")
    if not ccld_nccs_dvsn:
        logger.error("ccld_nccs_dvsn is required. (e.g. '00')")
        raise ValueError("ccld_nccs_dvsn is required. (e.g. '00')")
    if not sort_sqn:
        logger.error("sort_sqn is required. (e.g. 'DS')")
        raise ValueError("sort_sqn is required. (e.g. 'DS')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real":
        tr_id = "TTTS3035R"  # 실전투자용 TR ID
    elif env_dv == "demo":
        tr_id = "VTTS3035R"  # 모의투자용 TR ID
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "ORD_STRT_DT": ord_strt_dt,
        "ORD_END_DT": ord_end_dt,
        "SLL_BUY_DVSN": sll_buy_dvsn,
        "CCLD_NCCS_DVSN": ccld_nccs_dvsn,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "SORT_SQN": sort_sqn,
        "ORD_DT": ord_dt,
        "ORD_GNO_BRNO": ord_gno_brno,
        "ODNO": odno,
        "CTX_AREA_NK200": NK200,
        "CTX_AREA_FK200": FK200,
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
            return inquire_ccnl(
                cano=cano,
                acnt_prdt_cd=acnt_prdt_cd,
                pdno=pdno,
                ord_strt_dt=ord_strt_dt,
                ord_end_dt=ord_end_dt,
                sll_buy_dvsn=sll_buy_dvsn,
                ccld_nccs_dvsn=ccld_nccs_dvsn,
                ovrs_excg_cd=ovrs_excg_cd,
                sort_sqn=sort_sqn,
                ord_dt=ord_dt,
                ord_gno_brno=ord_gno_brno,
                odno=odno,
                NK200=NK200,
                FK200=FK200,
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
        return pd.DataFrame()
