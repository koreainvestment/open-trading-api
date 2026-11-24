"""
Created on 20250115 
"""

import sys
from typing import Optional, Tuple
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 퇴직연금 체결기준잔고[v1_국내주식-032]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/trading/pension/inquire-present-balance"


def _has_next_page(tr_cont: str) -> bool:
    """연속조회 여부: "M"(다음 있음)·"F"(다음 있음)면 True."""
    return tr_cont in ("M", "F")

def pension_inquire_present_balance(
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        user_dvsn_cd: str,  # 상품번호
        FK100: str = "",  # 연속조회검색조건100
        NK100: str = "",  # 연속조회키100
        tr_cont: str = "",  # 연속 거래 여부
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
        depth: int = 0,  # 내부 재귀깊이 (자동관리)
        max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 주문/계좌 > 퇴직연금 체결기준잔고[v1_국내주식-032]
    
    ※ 55번 계좌(DC가입자계좌)의 경우 해당 API 이용이 불가합니다.
    KIS Developers API의 경우 HTS ID에 반드시 연결되어있어야만 API 신청 및 앱정보 발급이 가능한 서비스로 개발되어서 실물계좌가 아닌 55번 계좌는 API 이용이 불가능한 점 양해 부탁드립니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. '12345678')
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. '29')
        user_dvsn_cd (str): [필수] 상품번호 (ex. '00')
        FK100 (str): 연속조회검색조건100
        NK100 (str): 연속조회키100
        tr_cont (str): 연속 거래 여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 데이터프레임 튜플
        
    Example:
        >>> df1, df2 = pension_inquire_present_balance(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, user_dvsn_cd="00")
        >>> print(df1)
        >>> print(df2)
    """

    # 필수 파라미터 검증
    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '29')")

    if user_dvsn_cd == "":
        raise ValueError("user_dvsn_cd is required (e.g. '00')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached (results may be truncated).")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "TTTC2202R"  # 퇴직연금 체결기준잔고

    params = {
        "CANO": cano,  # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "USER_DVSN_CD": user_dvsn_cd,  # 상품번호
        "CTX_AREA_FK100": FK100,  # 연속조회검색조건100
        "CTX_AREA_NK100": NK100  # 연속조회키100
    }

    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        # output1 (array) - 보유종목 정보
        current_data1 = pd.DataFrame(res.getBody().output1)
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1

        # output2 (array) - 계좌 요약 정보
        current_data2 = pd.DataFrame(res.getBody().output2)
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2

        tr_cont = res.getHeader().tr_cont
        FK100 = getattr(res.getBody(), "ctx_area_fk100", "") or ""
        NK100 = getattr(res.getBody(), "ctx_area_nk100", "") or ""

        if _has_next_page(tr_cont):  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return pension_inquire_present_balance(
                cano, acnt_prdt_cd, user_dvsn_cd, FK100, NK100, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame()
