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
# [국내주식] 시세분석 > 국내주식 시간외예상체결등락률 [국내주식-140]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/ranking/overtime-exp-trans-fluct"

def overtime_exp_trans_fluct(
    fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J:주식)
    fid_cond_scr_div_code: str,   # [필수] 조건 화면 분류 코드 (ex. 11186)
    fid_input_iscd: str,          # [필수] 입력 종목코드 (ex. 0000:전체, 0001:코스피, 1001:코스닥)
    fid_rank_sort_cls_code: str,  # [필수] 순위 정렬 구분 코드 (ex. 0:상승률, 1:상승폭, 2:보합, 3:하락률, 4:하락폭)
    fid_div_cls_code: str,        # [필수] 분류 구분 코드 (ex. 0:전체, 1:관리종목, 2:투자주의, 3:투자경고, 4:투자위험예고, 5:투자위험, 6:보통주, 7:우선주)
    fid_input_price_1: str = "",  # 입력 가격1
    fid_input_price_2: str = "",  # 입력 가격2
    fid_input_vol_1: str = ""     # 입력 거래량
) -> pd.DataFrame:
    """
    국내주식 시간외예상체결등락률 API입니다. 
    한국투자 HTS(eFriend Plus) > [0236] 시간외 예상체결등락률 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:주식)
        fid_cond_scr_div_code (str): [필수] 조건 화면 분류 코드 (ex. 11186)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 0000:전체, 0001:코스피, 1001:코스닥)
        fid_rank_sort_cls_code (str): [필수] 순위 정렬 구분 코드 (ex. 0:상승률, 1:상승폭, 2:보합, 3:하락률, 4:하락폭)
        fid_div_cls_code (str): [필수] 분류 구분 코드 (ex. 0:전체, 1:관리종목, 2:투자주의, 3:투자경고, 4:투자위험예고, 5:투자위험, 6:보통주, 7:우선주)
        fid_input_price_1 (str): 입력 가격1
        fid_input_price_2 (str): 입력 가격2
        fid_input_vol_1 (str): 입력 거래량

    Returns:
        pd.DataFrame: 국내주식 시간외예상체결등락률 데이터
        
    Example:
        >>> df = overtime_exp_trans_fluct("J", "11186", "0000", "0", "0")
        >>> print(df)
    """

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")
    
    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '11186')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '0000')")
        
    if fid_rank_sort_cls_code == "":
        raise ValueError("fid_rank_sort_cls_code is required (e.g. '0')")
        
    if fid_div_cls_code == "":
        raise ValueError("fid_div_cls_code is required (e.g. '0')")

    tr_id = "FHKST11860000"  # 국내주식 시간외예상체결등락률

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_INPUT_PRICE_1": fid_input_price_1,
        "FID_INPUT_PRICE_2": fid_input_price_2,
        "FID_INPUT_VOL_1": fid_input_vol_1
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 