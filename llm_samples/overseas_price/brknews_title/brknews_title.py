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
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 시세분석 > 해외속보(제목) [해외주식-055]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-price/v1/quotations/brknews-title"

def brknews_title(
    fid_news_ofer_entp_code: str,     # [필수] 뉴스제공업체코드 (ex. 0:전체조회)
    fid_cond_scr_div_code: str,       # [필수] 조건화면분류코드 (ex. 11801)
    fid_cond_mrkt_cls_code: str = "",  # 조건시장구분코드
    fid_input_iscd: str = "",          # 입력종목코드
    fid_titl_cntt: str = "",           # 제목내용
    fid_input_date_1: str = "",        # 입력날짜1
    fid_input_hour_1: str = "",        # 입력시간1
    fid_rank_sort_cls_code: str = "",  # 순위정렬구분코드
    fid_input_srno: str = ""           # 입력일련번호
) -> pd.DataFrame:
    """
    해외속보(제목) API입니다.
    한국투자 HTS(eFriend Plus) > [7704] 해외속보 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

    최대 100건까지 조회 가능합니다.
    
    Args:
        fid_news_ofer_entp_code (str): [필수] 뉴스제공업체코드 (ex. 0:전체조회)
        fid_cond_scr_div_code (str): [필수] 조건화면분류코드 (ex. 11801)
        fid_cond_mrkt_cls_code (str): 조건시장구분코드
        fid_input_iscd (str): 입력종목코드
        fid_titl_cntt (str): 제목내용
        fid_input_date_1 (str): 입력날짜1
        fid_input_hour_1 (str): 입력시간1
        fid_rank_sort_cls_code (str): 순위정렬구분코드
        fid_input_srno (str): 입력일련번호

    Returns:
        pd.DataFrame: 해외속보(제목) 데이터
        
    Example:
        >>> df = brknews_title("0", "11801")
        >>> print(df)
    """

    if fid_news_ofer_entp_code == "":
        raise ValueError("fid_news_ofer_entp_code is required (e.g. '0')")
    
    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '11801')")

    tr_id = "FHKST01011801"

    params = {
        "FID_NEWS_OFER_ENTP_CODE": fid_news_ofer_entp_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_COND_MRKT_CLS_CODE": fid_cond_mrkt_cls_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_TITL_CNTT": fid_titl_cntt,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_HOUR_1": fid_input_hour_1,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_INPUT_SRNO": fid_input_srno
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        return pd.DataFrame(res.getBody().output)
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 