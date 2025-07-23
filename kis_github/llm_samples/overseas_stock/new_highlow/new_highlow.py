"""
Created on 20250112 
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
# [해외주식] 시세분석 > 해외주식 신고/신저가[해외주식-042]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-stock/v1/ranking/new-highlow"

def new_highlow(
    excd: str,  # [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
    mixn: str,  # [필수] N분전콤보값 (ex. 0:1분전, 1:2분전, 2:3분전, 3:5분전, 4:10분전, 5:15분전, 6:20분전, 7:30분전, 8:60분전, 9:120분전)
    vol_rang: str,  # [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
    gubn: str,  # [필수] 신고/신저 구분 (ex. 0:신저,1:신고)
    gubn2: str,  # [필수] 일시돌파/돌파 구분 (ex. 0:일시돌파0, 1:돌파유지1)
    keyb: str = "",  # NEXT KEY BUFF
    auth: str = "",  # 사용자권한정보
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 output1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 output2
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 시세분석 > 해외주식 신고/신저가[해외주식-042]
    해외주식 신고/신저가 정보를 조회하여 DataFrame으로 반환합니다.
    
    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        mixn (str): [필수] N분전콤보값 (ex. 0:1분전, 1:2분전, 2:3분전, 3:5분전, 4:10분전, 5:15분전, 6:20분전, 7:30분전, 8:60분전, 9:120분전)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        gubn (str): [필수] 신고/신저 구분 (ex. 0:신저,1:신고)
        gubn2 (str): [필수] 일시돌파/돌파 구분 (ex. 0:일시돌파0, 1:돌파유지1)
        keyb (str): NEXT KEY BUFF
        auth (str): 사용자권한정보
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 output1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 output2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> output1, output2 = new_highlow(excd="AMS", mixn="0", vol_rang="0", gubn="1", gubn2="1")
        >>> print(output1)
        >>> print(output2)
    """

    if excd == "":
        raise ValueError("excd is required (e.g. 'NYS')")
    
    if mixn == "":
        raise ValueError("mixn is required (e.g. '0')")
    
    if vol_rang == "":
        raise ValueError("vol_rang is required (e.g. '0')")
        
    if gubn == "":
        raise ValueError("gubn is required (e.g. '1')")
        
    if gubn2 == "":
        raise ValueError("gubn2 is required (e.g. '1')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "HHDFS76300000"  # 해외주식 신고/신저가

    params = {
        "EXCD": excd,
        "MIXN": mixn,
        "VOL_RANG": vol_rang,
        "GUBN": gubn,
        "GUBN2": gubn2,
        "KEYB": keyb,
        "AUTH": auth
    }
    
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 처리 (object 타입)
        current_data1 = pd.DataFrame([res.getBody().output1])
        
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1
            
        # output2 처리 (array 타입)
        current_data2 = pd.DataFrame(res.getBody().output2)
        
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2
            
        tr_cont = res.getHeader().tr_cont
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return new_highlow(
                excd, mixn, vol_rang, gubn, gubn2, keyb, auth, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 