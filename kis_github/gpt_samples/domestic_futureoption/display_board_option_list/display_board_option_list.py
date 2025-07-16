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
# [국내선물옵션] 기본시세 > 국내옵션전광판_옵션월물리스트[국내선물-020]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-futureoption/v1/quotations/display-board-option-list"

def display_board_option_list(
    fid_cond_scr_div_code: str,
    fid_cond_mrkt_div_code: str = "",
    fid_cond_mrkt_cls_code: str = ""
) -> pd.DataFrame:
    """
    국내옵션전광판_옵션월물리스트 API입니다.
    한국투자 HTS(eFriend Plus) > [0503] 선물옵션 종합시세(Ⅰ) 화면의 "월물리스트 목록 확인" 기능을 API로 개발한 사항입니다.
    
    Args:
        fid_cond_scr_div_code (str): [필수] 조건 화면 분류 코드 (ex. 509)
        fid_cond_mrkt_div_code (str): 조건 시장 분류 코드
        fid_cond_mrkt_cls_code (str): 조건 시장 구분 코드

    Returns:
        pd.DataFrame: 국내옵션전광판_옵션월물리스트 데이터
        
    Example:
        >>> df = display_board_option_list(fid_cond_scr_div_code="509")
        >>> print(df)
    """

    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '509')")

    tr_id = "FHPIO056104C0"

    params = {
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_MRKT_CLS_CODE": fid_cond_mrkt_cls_code
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 