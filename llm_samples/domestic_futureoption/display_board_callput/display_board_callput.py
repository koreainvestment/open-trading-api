"""
Created on 20250601 
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
# [국내선물옵션] 기본시세 > 국내옵션전광판_콜풋[국내선물-022]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-futureoption/v1/quotations/display-board-callput"

def display_board_callput(
    fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. O: 옵션)
    fid_cond_scr_div_code: str,   # [필수] 조건 화면 분류 코드 (ex. 20503)
    fid_mrkt_cls_code: str,       # [필수] 시장 구분 코드 (ex. CO: 콜옵션)
    fid_mtrt_cnt: str,            # [필수] 만기 수 (ex. 202508)
    fid_mrkt_cls_code1: str,      # [필수] 시장 구분 코드 (ex. PO: 풋옵션)
    fid_cond_mrkt_cls_code: str = ""  # 조건 시장 구분 코드
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    국내옵션전광판_콜풋 API입니다.
    한국투자 HTS(eFriend Plus) > [0503] 선물옵션 종합시세(Ⅰ) 화면의 "중앙" 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

    ※ output1, output2 각각 100건까지만 확인이 가능합니다. (FY25년도 서비스 개선 예정)
    ※ 조회시간이 긴 API인 점 참고 부탁드리며, 잦은 호출을 삼가해주시기 바랍니다. (1초당 최대 1건 권장)
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. O: 옵션)
        fid_cond_scr_div_code (str): [필수] 조건 화면 분류 코드 (ex. 20503)
        fid_mrkt_cls_code (str): [필수] 시장 구분 코드 (ex. CO: 콜옵션)
        fid_mtrt_cnt (str): [필수] 만기 수 (ex. 202508)
        fid_mrkt_cls_code1 (str): [필수] 시장 구분 코드 (ex. PO: 풋옵션)
        fid_cond_mrkt_cls_code (str): 조건 시장 구분 코드

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 DataFrame, output2 DataFrame)
        
    Example:
        >>> df1, df2 = display_board_callput("O", "20503", "CO", "202508", "PO")
        >>> print(df1)
        >>> print(df2)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'O')")
        
    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '20503')")
        
    if fid_mrkt_cls_code == "":
        raise ValueError("fid_mrkt_cls_code is required (e.g. 'CO')")
        
    if fid_mtrt_cnt == "":
        raise ValueError("fid_mtrt_cnt is required (e.g. '202508')")
        
    if fid_mrkt_cls_code1 == "":
        raise ValueError("fid_mrkt_cls_code1 is required (e.g. 'PO')")

    tr_id = "FHPIF05030100"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_MRKT_CLS_CODE": fid_mrkt_cls_code,
        "FID_MTRT_CNT": fid_mtrt_cnt,
        "FID_MRKT_CLS_CODE1": fid_mrkt_cls_code1,
        "FID_COND_MRKT_CLS_CODE": fid_cond_mrkt_cls_code
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        output1_df = pd.DataFrame(res.getBody().output1)
        output2_df = pd.DataFrame(res.getBody().output2)
        return output1_df, output2_df
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 