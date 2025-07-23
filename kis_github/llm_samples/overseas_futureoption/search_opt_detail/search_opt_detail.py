"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""


import sys
import logging
from typing import Optional

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외선물옵션] 기본시세 > 해외옵션 상품기본정보 [해외선물-041]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-futureoption/v1/quotations/search-opt-detail"

def search_opt_detail(
    qry_cnt: str,  # [필수] 요청개수 (SRS_CD_N 개수)
    srs_cd_01: str,  # [필수] 종목코드1
    srs_cd_02: Optional[str] = "",  # 종목코드2
    srs_cd_03: Optional[str] = "",  # 종목코드3
    srs_cd_04: Optional[str] = "",  # 종목코드4
    srs_cd_05: Optional[str] = "",  # 종목코드5
    srs_cd_06: Optional[str] = "",  # 종목코드6
    srs_cd_07: Optional[str] = "",  # 종목코드7
    srs_cd_08: Optional[str] = "",  # 종목코드8
    srs_cd_09: Optional[str] = "",  # 종목코드9
    srs_cd_10: Optional[str] = "",  # 종목코드10
    srs_cd_11: Optional[str] = "",  # 종목코드11
    srs_cd_12: Optional[str] = "",  # 종목코드12
    srs_cd_13: Optional[str] = "",  # 종목코드13
    srs_cd_14: Optional[str] = "",  # 종목코드14
    srs_cd_15: Optional[str] = "",  # 종목코드15
    srs_cd_16: Optional[str] = "",  # 종목코드16
    srs_cd_17: Optional[str] = "",  # 종목코드17
    srs_cd_18: Optional[str] = "",  # 종목코드18
    srs_cd_19: Optional[str] = "",  # 종목코드19
    srs_cd_20: Optional[str] = "",  # 종목코드20
    srs_cd_21: Optional[str] = "",  # 종목코드21
    srs_cd_22: Optional[str] = "",  # 종목코드22
    srs_cd_23: Optional[str] = "",  # 종목코드23
    srs_cd_24: Optional[str] = "",  # 종목코드24
    srs_cd_25: Optional[str] = "",  # 종목코드25
    srs_cd_26: Optional[str] = "",  # 종목코드26
    srs_cd_27: Optional[str] = "",  # 종목코드27
    srs_cd_28: Optional[str] = "",  # 종목코드28
    srs_cd_29: Optional[str] = "",  # 종목코드29
    srs_cd_30: Optional[str] = ""   # 종목코드30
) -> pd.DataFrame:
    """
    해외옵션 상품기본정보 API입니다.

    (중요) 해외옵션시세 출력값을 해석하실 때 focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)에 있는 sCalcDesz(계산 소수점) 값을 활용하셔야 정확한 값을 받아오실 수 있습니다.

    - focode.mst(해외지수옵션 종목마스터파일), (해외주식옵션 종목마스터파일) 다운로드 방법
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
        qry_cnt (str): [필수] 요청개수 (ex. SRS_CD_N 개수)
        srs_cd_01 (str): [필수] 종목코드1
        srs_cd_02 (Optional[str]): 종목코드2
        srs_cd_03 (Optional[str]): 종목코드3
        srs_cd_04 (Optional[str]): 종목코드4
        srs_cd_05 (Optional[str]): 종목코드5
        srs_cd_06 (Optional[str]): 종목코드6
        srs_cd_07 (Optional[str]): 종목코드7
        srs_cd_08 (Optional[str]): 종목코드8
        srs_cd_09 (Optional[str]): 종목코드9
        srs_cd_10 (Optional[str]): 종목코드10
        srs_cd_11 (Optional[str]): 종목코드11
        srs_cd_12 (Optional[str]): 종목코드12
        srs_cd_13 (Optional[str]): 종목코드13
        srs_cd_14 (Optional[str]): 종목코드14
        srs_cd_15 (Optional[str]): 종목코드15
        srs_cd_16 (Optional[str]): 종목코드16
        srs_cd_17 (Optional[str]): 종목코드17
        srs_cd_18 (Optional[str]): 종목코드18
        srs_cd_19 (Optional[str]): 종목코드19
        srs_cd_20 (Optional[str]): 종목코드20
        srs_cd_21 (Optional[str]): 종목코드21
        srs_cd_22 (Optional[str]): 종목코드22
        srs_cd_23 (Optional[str]): 종목코드23
        srs_cd_24 (Optional[str]): 종목코드24
        srs_cd_25 (Optional[str]): 종목코드25
        srs_cd_26 (Optional[str]): 종목코드26
        srs_cd_27 (Optional[str]): 종목코드27
        srs_cd_28 (Optional[str]): 종목코드28
        srs_cd_29 (Optional[str]): 종목코드29
        srs_cd_30 (Optional[str]): 종목코드30

    Returns:
        pd.DataFrame: 해외옵션 상품기본정보 데이터
        
    Example:
        >>> df = search_opt_detail(qry_cnt="1", srs_cd_01="6AM24")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if qry_cnt == "":
        raise ValueError("qry_cnt is required (e.g. 'SRS_CD_N 개수')")
    
    if srs_cd_01 == "":
        raise ValueError("srs_cd_01 is required")

    tr_id = "HHDFO55200000"  # 해외옵션 상품기본정보

    params = {
        "QRY_CNT": qry_cnt,
        "SRS_CD_01": srs_cd_01
    }
    
    # 옵션 파라미터 추가
    if srs_cd_02:
        params["SRS_CD_02"] = srs_cd_02
    if srs_cd_03:
        params["SRS_CD_03"] = srs_cd_03
    if srs_cd_04:
        params["SRS_CD_04"] = srs_cd_04
    if srs_cd_05:
        params["SRS_CD_05"] = srs_cd_05
    if srs_cd_06:
        params["SRS_CD_06"] = srs_cd_06
    if srs_cd_07:
        params["SRS_CD_07"] = srs_cd_07
    if srs_cd_08:
        params["SRS_CD_08"] = srs_cd_08
    if srs_cd_09:
        params["SRS_CD_09"] = srs_cd_09
    if srs_cd_10:
        params["SRS_CD_10"] = srs_cd_10
    if srs_cd_11:
        params["SRS_CD_11"] = srs_cd_11
    if srs_cd_12:
        params["SRS_CD_12"] = srs_cd_12
    if srs_cd_13:
        params["SRS_CD_13"] = srs_cd_13
    if srs_cd_14:
        params["SRS_CD_14"] = srs_cd_14
    if srs_cd_15:
        params["SRS_CD_15"] = srs_cd_15
    if srs_cd_16:
        params["SRS_CD_16"] = srs_cd_16
    if srs_cd_17:
        params["SRS_CD_17"] = srs_cd_17
    if srs_cd_18:
        params["SRS_CD_18"] = srs_cd_18
    if srs_cd_19:
        params["SRS_CD_19"] = srs_cd_19
    if srs_cd_20:
        params["SRS_CD_20"] = srs_cd_20
    if srs_cd_21:
        params["SRS_CD_21"] = srs_cd_21
    if srs_cd_22:
        params["SRS_CD_22"] = srs_cd_22
    if srs_cd_23:
        params["SRS_CD_23"] = srs_cd_23
    if srs_cd_24:
        params["SRS_CD_24"] = srs_cd_24
    if srs_cd_25:
        params["SRS_CD_25"] = srs_cd_25
    if srs_cd_26:
        params["SRS_CD_26"] = srs_cd_26
    if srs_cd_27:
        params["SRS_CD_27"] = srs_cd_27
    if srs_cd_28:
        params["SRS_CD_28"] = srs_cd_28
    if srs_cd_29:
        params["SRS_CD_29"] = srs_cd_29
    if srs_cd_30:
        params["SRS_CD_30"] = srs_cd_30
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # 메타데이터에 따라 output2 (array)를 pd.DataFrame으로 반환
        return pd.DataFrame(res.getBody().output2)
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 