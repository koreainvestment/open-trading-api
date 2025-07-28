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
# [국내주식] 시세분석 > 관심종목 그룹조회 [국내주식-204]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/intstock-grouplist"

def intstock_grouplist(
    type: str,                    # [필수] 관심종목구분코드 (ex. 1)
    fid_etc_cls_code: str,        # [필수] FID 기타 구분 코드 (ex. 00)
    user_id: str                  # [필수] 사용자 ID
) -> pd.DataFrame:
    """
    관심종목 그룹조회 API입니다.
    ① 관심종목 그룹조회 → ② 관심종목 그룹별 종목조회 → ③ 관심종목(멀티종목) 시세조회 순서대로 호출하셔서 관심종목 시세 조회 가능합니다.

    ※ 한 번의 호출에 최대 30종목의 시세 확인 가능합니다.

    한국투자증권 Github 에서 관심종목 복수시세조회 파이썬 샘플코드를 참고하실 수 있습니다.
    https://github.com/koreainvestment/open-trading-api/blob/main/rest/interest_stocks_price.py
    
    Args:
        type (str): [필수] 관심종목구분코드 (ex. 1)
        fid_etc_cls_code (str): [필수] FID 기타 구분 코드 (ex. 00)
        user_id (str): [필수] 사용자 ID

    Returns:
        pd.DataFrame: 관심종목 그룹 정보를 담은 DataFrame
        
    Example:
        >>> df = intstock_grouplist(type="1", fid_etc_cls_code="00", user_id=trenv.my_htsid)
        >>> print(df)
    """

    if type == "":
        raise ValueError("type is required (e.g. '1')")
    
    if fid_etc_cls_code == "":
        raise ValueError("fid_etc_cls_code is required (e.g. '00')")
    
    if user_id == "":
        raise ValueError("user_id is required")

    tr_id = "HHKCM113004C7"  # 관심종목 그룹조회

    params = {
        "TYPE": type,                      # 관심종목구분코드
        "FID_ETC_CLS_CODE": fid_etc_cls_code,  # FID 기타 구분 코드
        "USER_ID": user_id                 # 사용자 ID
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output2)
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 