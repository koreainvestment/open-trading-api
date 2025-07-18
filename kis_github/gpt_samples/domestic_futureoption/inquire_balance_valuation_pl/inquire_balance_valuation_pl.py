"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import time
from typing import Optional, Tuple
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 잔고평가손익내역[v1_국내선물-015]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-futureoption/v1/trading/inquire-balance-valuation-pl"


def inquire_balance_valuation_pl(
        cano: str,  # [필수] 종합계좌번호 (ex. 계좌번호 체계(8-2)의 앞 8자리)
        acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 계좌번호 체계(8-2)의 뒤 2자리)
        mgna_dvsn: str,  # [필수] 증거금구분 (ex. 01:개시, 02:유지)
        excc_stat_cd: str,  # [필수] 정산상태코드 (ex. 1:정산, 2:본정산)
        FK200: str = "",  # 연속조회검색조건200 (ex. 연속조회검색조건200)
        NK200: str = "",  # 연속조회키200 (ex. 연속조회키200)
        tr_cont: str = "",  # 연속거래여부
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        depth: int = 0,  # 내부 재귀깊이 (자동관리)
        max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    시장별 투자자매매동향(일별) API입니다.
    한국투자 HTS(eFriend Plus) > [0404] 시장별 일별동향 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. 계좌번호 체계(8-2)의 앞 8자리)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 계좌번호 체계(8-2)의 뒤 2자리)
        mgna_dvsn (str): [필수] 증거금구분 (ex. 01:개시, 02:유지)
        excc_stat_cd (str): [필수] 정산상태코드 (ex. 1:정산, 2:본정산)
        FK200 (str): 연속조회검색조건200 (ex. 연속조회검색조건200)
        NK200 (str): 연속조회키200 (ex. 연속조회키200)
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터프레임, output2 데이터프레임)
        
    Example:
        >>> df1, df2 = inquire_balance_valuation_pl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, mgna_dvsn="01", excc_stat_cd="1")
        >>> print(df1)
        >>> print(df2)
    """

    if cano == "":
        raise ValueError("cano is required (e.g. '계좌번호 체계(8-2)의 앞 8자리')")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '계좌번호 체계(8-2)의 뒤 2자리')")

    if mgna_dvsn == "":
        raise ValueError("mgna_dvsn is required (e.g. '01:개시, 02:유지')")

    if excc_stat_cd == "":
        raise ValueError("excc_stat_cd is required (e.g. '1:정산, 2:본정산')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "CTFO6159R"  # 선물옵션 잔고평가손익내역

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "MGNA_DVSN": mgna_dvsn,
        "EXCC_STAT_CD": excc_stat_cd,
        "CTX_AREA_FK200": FK200,
        "CTX_AREA_NK200": NK200
    }

    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리 (array)
        current_data1 = pd.DataFrame(res.getBody().output1)
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1

        # output2 처리 (object)
        current_data2 = pd.DataFrame([res.getBody().output2])
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2

        tr_cont = res.getHeader().tr_cont
        FK200 = res.getBody().ctx_area_fk200
        NK200 = res.getBody().ctx_area_nk200

        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_balance_valuation_pl(
                cano, acnt_prdt_cd, mgna_dvsn, excc_stat_cd, FK200, NK200, "N", dataframe1, dataframe2, depth + 1,
                max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame()
