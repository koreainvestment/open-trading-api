"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""


import sys
import time
from typing import Optional, Tuple
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외주식] 시세분석 > 해외주식 거래량순위[해외주식-043]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-stock/v1/ranking/trade-vol"

def trade_vol(
    excd: str,  # 거래소명
    nday: str,  # N분전콤보값
    vol_rang: str,  # 거래량조건
    keyb: str = "",  # NEXT KEY BUFF
    auth: str = "",  # 사용자권한정보
    prc1: str = "",  # 가격 필터 시작
    prc2: str = "",  # 가격 필터 종료
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 시세분석 > 해외주식 거래량순위[해외주식-043]
    해외주식 거래량순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        nday (str): [필수] N분전콤보값 (ex. 0:당일, 1:2일전, 2:3일전, 3:5일전, 4:10일전, 5:20일전, 6:30일전, 7:60일전, 8:120일전, 9:1년전)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        keyb (str): NEXT KEY BUFF (ex. "")
        auth (str): 사용자권한정보 (ex. "")
        prc1 (str): 가격 필터 시작 (ex. "")
        prc2 (str): 가격 필터 종료 (ex. "")
        tr_cont (str): 연속거래여부 (ex. "")
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식 거래량순위 데이터 (output1, output2)
        
    Example:
        >>> df1, df2 = trade_vol(excd="NYS", nday="0", vol_rang="0")
        >>> print(df1)
        >>> print(df2)
    """

    # 필수 파라미터 검증
    if excd == "":
        raise ValueError("excd is required (e.g. 'NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄')")
    
    if nday == "":
        raise ValueError("nday is required (e.g. '0:당일, 1:2일전, 2:3일전, 3:5일전, 4:10일전, 5:20일전, 6:30일전, 7:60일전, 8:120일전, 9:1년전')")
    
    if vol_rang == "":
        raise ValueError("vol_rang is required (e.g. '0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "HHDFS76310010"  # 해외주식 거래량순위

    params = {
        "EXCD": excd,
        "NDAY": nday,
        "VOL_RANG": vol_rang,
        "KEYB": keyb,
        "AUTH": auth,
        "PRC1": prc1,
        "PRC2": prc2
    }
    
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 처리
        current_data1 = pd.DataFrame(res.getBody().output1, index=[0])
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1
            
        # output2 처리
        current_data2 = pd.DataFrame(res.getBody().output2)
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2
            
        tr_cont = res.getHeader().tr_cont
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return trade_vol(
                excd, nday, vol_rang, keyb, auth, prc1, prc2, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 