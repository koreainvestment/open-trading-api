"""
Created on 20250131
@author: LaivData SJPark with cursor
"""

import logging
import sys
from typing import Tuple

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 투자계좌자산현황조회[v1_국내주식-048]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/trading/inquire-account-balance"

def inquire_account_balance(
    cano: str,  # [필수] 종합계좌번호 (ex. 12345678)
    acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 19 or 21)
    inqr_dvsn_1: str = "",  # 조회구분1
    bspr_bf_dt_aply_yn: str = ""  # 기준가이전일자적용여부
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    투자계좌자산현황조회 API입니다.

    output1은 한국투자 HTS(eFriend Plus) > [0891] 계좌 자산비중(결제기준) 화면 아래 테이블의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 19 or 21)
        inqr_dvsn_1 (str): 조회구분1
        bspr_bf_dt_aply_yn (str): 기준가이전일자적용여부
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터프레임, output2 데이터프레임)
        
    Example:
        >>> df1, df2 = inquire_account_balance("12345678", "21")
        >>> print(df1)
        >>> print(df2)
    """

    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '19' or '21')")

    tr_id = "CTRP6548R"  # 투자계좌자산현황조회

    params = {
        "CANO": cano,  # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "INQR_DVSN_1": inqr_dvsn_1,  # 조회구분1
        "BSPR_BF_DT_APLY_YN": bspr_bf_dt_aply_yn  # 기준가이전일자적용여부
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # output1 - array 타입
        df1 = pd.DataFrame(res.getBody().output1)
        
        # output2 - object 타입 (단일 객체를 DataFrame으로 변환)
        df2 = pd.DataFrame([res.getBody().output2])
            
        logging.info("Data fetch complete.")
        return df1, df2
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 