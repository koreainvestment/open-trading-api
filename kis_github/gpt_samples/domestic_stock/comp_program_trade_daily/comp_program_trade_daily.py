"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 프로그램매매 종합현황(일별)[국내주식-115]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/comp-program-trade-daily"


def comp_program_trade_daily(
        fid_cond_mrkt_div_code: str,  # [필수] 조건시장분류코드 (ex. J:주식,NX:NXT,UN:통합)
        fid_mrkt_cls_code: str,  # [필수] 시장구분코드 (ex. K:코스피,Q:코스닥)
        fid_input_date_1: str = "",  # 검색시작일
        fid_input_date_2: str = ""  # 검색종료일
) -> pd.DataFrame:
    """
    프로그램매매 종합현황(일별) API입니다. 
    한국투자 HTS(eFriend Plus) > [0460] 프로그램매매 종합현황 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건시장분류코드 (ex. J:주식,NX:NXT,UN:통합)
        fid_mrkt_cls_code (str): [필수] 시장구분코드 (ex. K:코스피,Q:코스닥)
        fid_input_date_1 (str): 검색시작일
        fid_input_date_2 (str): 검색종료일

    Returns:
        pd.DataFrame: 프로그램매매 종합현황(일별) 데이터
        
    Example:
        >>> df = comp_program_trade_daily("J", "K", "20250101", "20250617")
        >>> print(df)
    """

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:주식,NX:NXT,UN:통합')")

    if fid_mrkt_cls_code == "":
        raise ValueError("fid_mrkt_cls_code is required (e.g. 'K:코스피,Q:코스닥')")

    tr_id = "FHPPG04600001"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_MRKT_CLS_CODE": fid_mrkt_cls_code,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_DATE_2": fid_input_date_2
    }

    res = ka._url_fetch(API_URL, tr_id, "", params)

    if res.isOK():
        return pd.DataFrame(res.getBody().output)
    else:
        res.printError(url=API_URL)
        return pd.DataFrame()
