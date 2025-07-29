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
# [국내선물옵션] 기본시세 > 국내선물 기초자산 시세[국내선물-021]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-futureoption/v1/quotations/display-board-top"

def display_board_top(
    fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. F)
    fid_input_iscd: str,          # [필수] 입력 종목코드 (ex. 101V06)
    fid_cond_mrkt_div_code1: str = "",  # 조건 시장 분류 코드
    fid_cond_scr_div_code: str = "",    # 조건 화면 분류 코드
    fid_mtrt_cnt: str = "",             # 만기 수
    fid_cond_mrkt_cls_code: str = ""    # 조건 시장 구분 코드
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    국내선물 기초자산 시세 API입니다.
    한국투자 HTS(eFriend Plus) > [0503] 선물옵션 종합시세(Ⅰ) 화면의 "상단 바" 기능을 API로 개발한 사항입니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. F)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 101V06)
        fid_cond_mrkt_div_code1 (str): 조건 시장 분류 코드
        fid_cond_scr_div_code (str): 조건 화면 분류 코드
        fid_mtrt_cnt (str): 만기 수
        fid_cond_mrkt_cls_code (str): 조건 시장 구분 코드

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 데이터프레임 튜플
        
    Example:
        >>> output1, output2 = display_board_top(fid_cond_mrkt_div_code="F", fid_input_iscd="101W09")
        >>> print(output1)
        >>> print(output2)
    """

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'F')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '101W09')")

    tr_id = "FHPIF05030000"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_COND_MRKT_DIV_CODE1": fid_cond_mrkt_div_code1,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_MTRT_CNT": fid_mtrt_cnt,
        "FID_COND_MRKT_CLS_CODE": fid_cond_mrkt_cls_code
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        output1 = pd.DataFrame(res.getBody().output1, index=[0])
        output2 = pd.DataFrame(res.getBody().output2)
        
        return output1, output2
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 