"""
Created on 20250115 
@author: LaivData SJPark with cursor
"""

import sys
from typing import Tuple
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


def pension_inquire_present_balance(
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        user_dvsn_cd: str,  # 상품번호
        FK100: str = "",  # 연속조회검색조건100
        NK100: str = ""  # 연속조회키100
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

    tr_id = "TTTC2202R"  # 퇴직연금 체결기준잔고

    params = {
        "CANO": cano,  # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "USER_DVSN_CD": user_dvsn_cd,  # 상품번호
        "CTX_AREA_FK100": FK100,  # 연속조회검색조건100
        "CTX_AREA_NK100": NK100  # 연속조회키100
    }

    res = ka._url_fetch(API_URL, tr_id, "", params)

    if res.isOK():
        # output1 (array) - 보유종목 정보
        output1_data = pd.DataFrame(res.getBody().output1)

        # output2 (array) - 계좌 요약 정보
        output2_data = pd.DataFrame(res.getBody().output2)

        return output1_data, output2_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame()
