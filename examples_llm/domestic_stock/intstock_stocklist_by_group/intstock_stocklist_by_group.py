"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""


import sys
import logging
from typing import Tuple

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 관심종목 그룹별 종목조회 [국내주식-203]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/intstock-stocklist-by-group"

def intstock_stocklist_by_group(
    type: str,                    # 관심종목구분코드 (ex. 1)
    user_id: str,                 # 사용자 ID
    inter_grp_code: str,          # 관심 그룹 코드 (ex. 001)
    fid_etc_cls_code: str,        # 기타 구분 코드 (ex. 4)
    data_rank: str = "",          # 데이터 순위
    inter_grp_name: str = "",     # 관심 그룹 명
    hts_kor_isnm: str = "",       # HTS 한글 종목명
    cntg_cls_code: str = ""       # 체결 구분 코드
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    관심종목 그룹별 종목조회 API입니다.
    ① 관심종목 그룹조회 → ② 관심종목 그룹별 종목조회 → ③ 관심종목(멀티종목) 시세조회 순서대로 호출하셔서 관심종목 시세 조회 가능합니다.

    ※ 한 번의 호출에 최대 30종목의 시세 확인 가능합니다.

    한국투자증권 Github 에서 관심종목 복수시세조회 파이썬 샘플코드를 참고하실 수 있습니다.
    https://github.com/koreainvestment/open-trading-api/blob/main/rest/interest_stocks_price.py
    
    Args:
        type (str): [필수] 관심종목구분코드 (ex. 1)
        user_id (str): [필수] 사용자 ID
        inter_grp_code (str): [필수] 관심 그룹 코드 (ex. 001)
        fid_etc_cls_code (str): [필수] 기타 구분 코드 (ex. 4)
        data_rank (str): 데이터 순위
        inter_grp_name (str): 관심 그룹 명
        hts_kor_isnm (str): HTS 한글 종목명
        cntg_cls_code (str): 체결 구분 코드

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터프레임, output2 데이터프레임)
        
    Example:
        >>> df1, df2 = intstock_stocklist_by_group(
        ...     type="1", user_id=trenv.my_htsid, inter_grp_code="001", fid_etc_cls_code="4"
        ... )
        >>> print(df1)
        >>> print(df2)
    """

    if type == "":
        raise ValueError("type is required (e.g. '1')")
    
    if user_id == "":
        raise ValueError("user_id is required")
    
    if inter_grp_code == "":
        raise ValueError("inter_grp_code is required (e.g. '001')")
    
    if fid_etc_cls_code == "":
        raise ValueError("fid_etc_cls_code is required (e.g. '4')")

    tr_id = "HHKCM113004C6"  # 관심종목 그룹별 종목조회

    params = {
        "TYPE": type,                           # 관심종목구분코드
        "USER_ID": user_id,                     # 사용자 ID
        "INTER_GRP_CODE": inter_grp_code,       # 관심 그룹 코드
        "FID_ETC_CLS_CODE": fid_etc_cls_code,   # 기타 구분 코드
        "DATA_RANK": data_rank,                 # 데이터 순위
        "INTER_GRP_NAME": inter_grp_name,       # 관심 그룹 명
        "HTS_KOR_ISNM": hts_kor_isnm,          # HTS 한글 종목명
        "CNTG_CLS_CODE": cntg_cls_code          # 체결 구분 코드
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # output1 데이터프레임 생성
        output1_data = pd.DataFrame([res.getBody().output1])
        
        # output2 데이터프레임 생성
        output2_data = pd.DataFrame(res.getBody().output2)
        
        logging.info("Data fetch complete.")
        return output1_data, output2_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 