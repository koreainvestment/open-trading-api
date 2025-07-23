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
# [국내주식] 기본시세 > 국내주식 장마감 예상체결가[국내주식-120]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/exp-closing-price"

def exp_closing_price(
    fid_cond_mrkt_div_code: str,  # [필수] 조건시장분류코드 (ex. J:주식)
    fid_input_iscd: str,          # [필수] 입력종목코드 (ex. 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100)
    fid_rank_sort_cls_code: str,  # [필수] 순위정렬구분코드 (ex. 0:전체, 1:상한가마감예상, 2:하한가마감예상, 3:직전대비상승률상위, 4:직전대비하락률상위)
    fid_cond_scr_div_code: str,   # [필수] 조건화면분류코드 (ex. 11173)
    fid_blng_cls_code: str        # [필수] 소속구분코드 (ex. 0:전체, 1:종가범위연장)
) -> pd.DataFrame:
    """
    국내주식 장마감 예상체결가 API입니다. 
    한국투자 HTS(eFriend Plus) > [0183] 장마감 예상체결가 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건시장분류코드 (ex. J:주식)
        fid_input_iscd (str): [필수] 입력종목코드 (ex. 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100)
        fid_rank_sort_cls_code (str): [필수] 순위정렬구분코드 (ex. 0:전체, 1:상한가마감예상, 2:하한가마감예상, 3:직전대비상승률상위, 4:직전대비하락률상위)
        fid_cond_scr_div_code (str): [필수] 조건화면분류코드 (ex. 11173)
        fid_blng_cls_code (str): [필수] 소속구분코드 (ex. 0:전체, 1:종가범위연장)

    Returns:
        pd.DataFrame: 국내주식 장마감 예상체결가 데이터
        
    Example:
        >>> df = exp_closing_price("J", "0001", "0", "11173", "0")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '0000', '0001', '1001', '2001', '4001')")
    
    if fid_rank_sort_cls_code == "":
        raise ValueError("fid_rank_sort_cls_code is required (e.g. '0', '1', '2', '3', '4')")
    
    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '11173')")
    
    if fid_blng_cls_code == "":
        raise ValueError("fid_blng_cls_code is required (e.g. '0', '1')")

    tr_id = "FHKST117300C0"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_BLNG_CLS_CODE": fid_blng_cls_code
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        return pd.DataFrame(res.getBody().output)
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 