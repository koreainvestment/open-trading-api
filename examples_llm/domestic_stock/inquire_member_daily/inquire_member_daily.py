"""
Created on 20250101 
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
# [국내주식] 시세분석 > 주식현재가 회원사 종목매매동향 [국내주식-197]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-member-daily"

def inquire_member_daily(
    fid_cond_mrkt_div_code: str,  # [필수] 조건시장분류코드 (ex. 주식J)
    fid_input_iscd: str,          # [필수] 입력종목코드 (ex. 123456)
    fid_input_iscd_2: str,        # [필수] 회원사코드 (ex. 회원사코드 FAQ 종목정보 다운로드(국내) > 회원사 참조)
    fid_input_date_1: str,        # [필수] 입력날짜1
    fid_input_date_2: str,        # [필수] 입력날짜2
    fid_sctn_cls_code: str = ""   # 데이터 순위 (초기값: "")
) -> pd.DataFrame:
    """
    주식현재가 회원사 종목매매동향 API입니다.
    한국투자 HTS(eFriend Plus) > [0454] 증권사 종목매매동향 화면을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건시장분류코드 (J:KRX, NX:NXT)
        fid_input_iscd (str): [필수] 입력종목코드 (ex. 123456)  
        fid_input_iscd_2 (str): [필수] 회원사코드 (ex. 회원사코드 FAQ 종목정보 다운로드(국내) > 회원사 참조)
        fid_input_date_1 (str): [필수] 입력날짜1
        fid_input_date_2 (str): [필수] 입력날짜2
        fid_sctn_cls_code (str): 데이터 순위 (초기값: "")

    Returns:
        pd.DataFrame: 주식현재가 회원사 종목매매동향 데이터
        
    Example:
        >>> df = inquire_member_daily(
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_input_iscd="005930", 
        ...     fid_input_iscd_2="00003",
        ...     fid_input_date_1="20240501",
        ...     fid_input_date_2="20240624"
        ... )
        >>> print(df)
    """

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '123456')")
        
    if fid_input_iscd_2 == "":
        raise ValueError("fid_input_iscd_2 is required (e.g. '00003')")
        
    if fid_input_date_1 == "":
        raise ValueError("fid_input_date_1 is required")
        
    if fid_input_date_2 == "":
        raise ValueError("fid_input_date_2 is required")

    tr_id = "FHPST04540000"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_ISCD_2": fid_input_iscd_2,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_DATE_2": fid_input_date_2,
        "FID_SCTN_CLS_CODE": fid_sctn_cls_code
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 