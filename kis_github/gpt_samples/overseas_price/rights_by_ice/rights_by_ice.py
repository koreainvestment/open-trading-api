"""
Created on 20250113 
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
# [해외주식] 시세분석 > 해외주식 권리종합 [해외주식-050]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-price/v1/quotations/rights-by-ice"

def rights_by_ice(
    ncod: str,       # 국가코드 (CN:중국,HK:홍콩,US:미국,JP:일본,VN:베트남)
    symb: str,       # 종목코드
    st_ymd: str = "",   # 일자시작일 (미입력시 3개월전)
    ed_ymd: str = ""    # 일자종료일 (미입력시 3개월후)
) -> pd.DataFrame:
    """
    해외주식 권리종합 API입니다.
    한국투자 HTS(eFriend Plus) > [7833] 해외주식 권리(ICE제공) 화면의 "전체" 탭 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

    ※ 조회기간 기준일 입력시 참고 - 상환: 상환일자, 조기상환: 조기상환일자, 티커변경: 적용일, 그 외: 발표일
    
    Args:
        ncod (str): [필수] 국가코드 (ex. CN:중국,HK:홍콩,US:미국,JP:일본,VN:베트남)
        symb (str): [필수] 종목코드
        st_ymd (str): 일자시작일 (ex. 미입력시 3개월전)
        ed_ymd (str): 일자종료일 (ex. 미입력시 3개월후)

    Returns:
        pd.DataFrame: 해외주식 권리종합 정보
        
    Raises:
        ValueError: 필수 파라미터가 누락되었을 때
        
    Example:
        >>> df = rights_by_ice("US", "NVDL")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if ncod == "":
        raise ValueError("ncod is required (e.g. 'CN:중국,HK:홍콩,US:미국,JP:일본,VN:베트남')")
    
    if symb == "":
        raise ValueError("symb is required")

    tr_id = "HHDFS78330900"

    params = {
        "NCOD": ncod,     # 국가코드
        "SYMB": symb,     # 종목코드
        "ST_YMD": st_ymd, # 일자시작일
        "ED_YMD": ed_ymd  # 일자종료일
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output1)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 