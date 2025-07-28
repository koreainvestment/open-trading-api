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
# [국내주식] 시세분석 > 종목조건검색 목록조회[국내주식-038]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/psearch-title"

def psearch_title(
    user_id: str  # [필수] 사용자 HTS ID (ex. U:업종)
) -> pd.DataFrame:
    """
    [국내주식] 시세분석 > 종목조건검색 목록조회[국내주식-038]
    HTS(efriend Plus) [0110] 조건검색에서 등록 및 서버저장한 나의 조건 목록을 확인할 수 있는 API입니다.
    종목조건검색 목록조회 API(/uapi/domestic-stock/v1/quotations/psearch-title)의 output인 'seq'을 종목조건검색조회 API(/uapi/domestic-stock/v1/quotations/psearch-result)의 input으로 사용하시면 됩니다.

    ※ 시스템 안정성을 위해 API로 제공되는 조건검색 결과의 경우 조건당 100건으로 제한을 둔 점 양해 부탁드립니다.

    ※ [0110] 화면의 '대상변경' 설정사항은 HTS [0110] 사용자 조건검색 화면에만 적용됨에 유의 부탁드립니다.

    ※ '조회가 계속 됩니다. (다음을 누르십시오.)' 오류 발생 시 해결방법
    → HTS(efriend Plus) [0110] 조건검색 화면에서 조건을 등록하신 후, 왼쪽 하단의 "사용자조건 서버저장" 클릭하셔서 등록한 조건들을 서버로 보낸 후 다시 API 호출 시도 부탁드립니다.
    
    Args:
        user_id (str): [필수] 사용자 HTS ID (ex. U:업종)

    Returns:
        pd.DataFrame: 종목조건검색 목록 데이터
        
    Example:
        >>> df = psearch_title(user_id=trenv.my_htsid)
        >>> print(df)
    """

    if user_id == "":
        raise ValueError("user_id is required (e.g. 'U:업종')")

    tr_id = "HHKST03900300"  # 종목조건검색 목록조회

    params = {
        "user_id": user_id  # 사용자 HTS ID
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output2)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 