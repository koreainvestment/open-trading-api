"""
Created on 20250112
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
# [국내선물옵션] 기본시세 > 국내옵션전광판_선물[국내선물-023]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-futureoption/v1/quotations/display-board-futures"

def display_board_futures(
    fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
    fid_cond_scr_div_code: str,   # 조건 화면 분류 코드
    fid_cond_mrkt_cls_code: str   # 조건 시장 구분 코드
) -> pd.DataFrame:
    """
    국내옵션전광판_선물 API입니다.
    한국투자 HTS(eFriend Plus) > [0503] 선물옵션 종합시세(Ⅰ) 화면의 "하단" 기능을 API로 개발한 사항입니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. F)
        fid_cond_scr_div_code (str): [필수] 조건 화면 분류 코드 (ex. 20503)
        fid_cond_mrkt_cls_code (str): [필수] 조건 시장 구분 코드 (ex. MKI)

    Returns:
        pd.DataFrame: 국내선물옵션 선물전광판 데이터
        
    Example:
        >>> df = display_board_futures("F", "20503", "MKI")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'F')")
    
    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '20503')")
    
    if fid_cond_mrkt_cls_code == "":
        raise ValueError("fid_cond_mrkt_cls_code is required (e.g. 'MKI')")

    tr_id = "FHPIF05030200"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_COND_MRKT_CLS_CODE": fid_cond_mrkt_cls_code
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        return pd.DataFrame(res.getBody().output)
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 