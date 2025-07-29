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
# [국내주식] 시세분석 > 시장별 투자자매매동향(일별) [국내주식-075]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/inquire-investor-daily-by-market"


def inquire_investor_daily_by_market(
        fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. U:업종)
        fid_input_iscd: str,  # [필수] 입력 종목코드 (ex. 0001)
        fid_input_date_1: str,  # [필수] 입력 날짜1 (ex. 20250701)
        fid_input_iscd_1: str,  # [필수] 입력 종목코드 (ex. KSP:코스피, KSQ:코스닥)
        fid_input_date_2: str,  # [필수] 입력 날짜1과 동일날짜 입력
        fid_input_iscd_2: str,  # [필수] 입력 종목코드 (ex. 업종분류코드)

) -> pd.DataFrame:
    """
    시장별 투자자매매동향(일별) API입니다.
    한국투자 HTS(eFriend Plus) > [0404] 시장별 일별동향 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. U:업종)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 0001)
        fid_input_date_1 (str): [필수] 입력 날짜1 (ex. 20250701)
        fid_input_iscd_1 (str): [필수] 입력 종목코드 (ex. KSP:코스피, KSQ:코스닥)
        fid_input_date_2 (str): [필수] 입력 날짜1과 동일날짜 입력
        fid_input_iscd_2 (str): [필수] 입력 종목코드 (ex. 업종분류코드)

    Returns:
        pd.DataFrame: 시장별 투자자매매동향(일별) 데이터
        
    Example:
        >>> df = inquire_investor_daily_by_market("U", "0001", "20250701", "KSP", "20250701", "0001")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'U')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '0001')")

    if fid_input_date_1 == "":
        raise ValueError("fid_input_date_1 is required (e.g. '20250701')")

    if fid_input_iscd_1 == "":
        raise ValueError("fid_input_iscd_1 is required (e.g. 'KSP')")

    if fid_input_date_2 == "":
        raise ValueError("fid_input_date_2 is required (e.g. '20250701')")

    if fid_input_iscd_2 == "":
        raise ValueError("fid_input_iscd_2 is required (e.g. 업종분류코드')")

    tr_id = "FHPTJ04040000"  # 시장별 투자자매매동향(일별)

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,  # 조건 시장 분류 코드
        "FID_INPUT_ISCD": fid_input_iscd,  # 입력 종목코드
        "FID_INPUT_DATE_1": fid_input_date_1,  # 입력 날짜1
        "FID_INPUT_ISCD_1": fid_input_iscd_1,  # 입력 종목코드
        "FID_INPUT_DATE_2": fid_input_date_2,  # 입력 날짜2
        "FID_INPUT_ISCD_2": fid_input_iscd_2,  # 입력 종목코드
    }

    res = ka._url_fetch(API_URL, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame()
