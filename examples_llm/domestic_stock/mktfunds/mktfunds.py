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
# [국내주식] 시세분석 > 국내 증시자금 종합 [국내주식-193]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/mktfunds"


def mktfunds(
        fid_input_date_1: str = ""
) -> pd.DataFrame:
    """
    국내 증시자금 종합 API입니다. 
    한국투자 HTS(eFriend Plus) > [0470] 증시자금 종합 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다. (단위: 억원)

    ※ 해당자료는 금융투자협회의 자료를 제공하고 있으며, 오류와 지연이 발생할 수 있습니다.
    ※ 위 정보에 의한 투자판단의 최종책임은 정보이용자에게 있으며, 당사와 한국금융투자협회는 어떠한 법적인 책임도 지지 않사오니 투자에 참고로만 이용하시기 바랍니다.
    
    Args:
        fid_input_date_1 (str): [입력날짜]
        
    Returns:
        pd.DataFrame: 국내 증시자금 종합 데이터
        
    Example:
        >>> df = mktfunds()
        >>> print(df)
    """

    tr_id = "FHKST649100C0"

    params = {
        "FID_INPUT_DATE_1": fid_input_date_1
    }

    res = ka._url_fetch(API_URL, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame()
