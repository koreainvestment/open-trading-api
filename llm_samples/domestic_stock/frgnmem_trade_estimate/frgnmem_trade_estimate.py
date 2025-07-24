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
# [국내주식] 시세분석 > 외국계 매매종목 가집계 [국내주식-161]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/frgnmem-trade-estimate"


def frgnmem_trade_estimate(
        fid_cond_mrkt_div_code: str,
        fid_cond_scr_div_code: str,
        fid_input_iscd: str,
        fid_rank_sort_cls_code: str,
        fid_rank_sort_cls_code_2: str
) -> pd.DataFrame:
    """
    외국계 매매종목 가집계 API입니다.
    한국투자 HTS(eFriend Plus) > [0430] 외국계 매매종목 가집계 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건시장분류코드 (ex. J)
        fid_cond_scr_div_code (str): [필수] 조건화면분류코드 (ex. 16441)
        fid_input_iscd (str): [필수] 입력종목코드 (ex. 0000:전체, 1001:코스피, 2001:코스닥)
        fid_rank_sort_cls_code (str): [필수] 순위정렬구분코드 (ex. 0:금액순, 1:수량순)
        fid_rank_sort_cls_code_2 (str): [필수] 순위정렬구분코드2 (ex. 0:매수순, 1:매도순)
        
    Returns:
        pd.DataFrame: 외국계 매매종목 가집계 데이터
        
    Example:
        >>> df = frgnmem_trade_estimate("J", "16441", "0000", "0", "0")
        >>> print(df)
    """

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")

    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '16441')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '0000')")

    if fid_rank_sort_cls_code == "":
        raise ValueError("fid_rank_sort_cls_code is required (e.g. '0')")

    if fid_rank_sort_cls_code_2 == "":
        raise ValueError("fid_rank_sort_cls_code_2 is required (e.g. '0')")

    tr_id = "FHKST644100C0"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_RANK_SORT_CLS_CODE_2": fid_rank_sort_cls_code_2
    }

    res = ka._url_fetch(API_URL, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame()
