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
# [해외선물옵션] 기본시세 > 해외옵션종목상세 [해외선물-034]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-futureoption/v1/quotations/opt-detail"

def opt_detail(
    srs_cd: str  # [필수] 종목명
) -> pd.DataFrame:
    """
    해외옵션종목상세 API입니다.

    (주의) sstl_price 자리에 정산가 X 전일종가 O 가 수신되는 점 유의 부탁드립니다.

    (중요) 해외옵션시세 출력값을 해석하실 때 focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)에 있는 sCalcDesz(계산 소수점) 값을 활용하셔야 정확한 값을 받아오실 수 있습니다.

    - focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일) 다운로드 방법
    1) focode.mst(해외지수옵션 종목마스터파일)
        : 포럼 > FAQ > 종목정보 다운로드(해외) - 해외지수옵션 클릭하여 다운로드 후
        Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외옵션정보.h)를 참고하여 해석
    2) fostkcode.mst(해외주식옵션 종목마스터파일)
        : 포럼 > FAQ > 종목정보 다운로드(해외) - 해외주식옵션 클릭하여 다운로드 후
        Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외주식옵션정보.h)를 참고하여 해석

    - 소수점 계산 시, focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)의 sCalcDesz(계산 소수점) 값 참고
    EX) focode.mst 파일의 sCalcDesz(계산 소수점) 값
        품목코드 OES 계산소수점 -2 → 시세 7525 수신 시 75.25 로 해석
        품목코드 O6E 계산소수점 -4 → 시세 54.0 수신 시 0.0054 로 해석
    
    Args:
        srs_cd (str): [필수] 종목명
        
    Returns:
        pd.DataFrame: 해외옵션종목상세 데이터
        
    Raises:
        ValueError: 필수 파라미터 누락 시
        
    Examples:
        >>> df = opt_detail("C5500")
        >>> print(df)
    """

    if srs_cd == "":
        raise ValueError("srs_cd is required (e.g. 'C5500')")

    tr_id = "HHDFO55010100"

    params = {
        "SRS_CD": srs_cd
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output1, index=[0])
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 