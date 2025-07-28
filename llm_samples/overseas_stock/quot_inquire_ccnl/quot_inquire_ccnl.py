"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""


import sys
import time
from typing import Optional
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 기본시세 > 해외주식 체결추이[해외주식-037]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-price/v1/quotations/inquire-ccnl"

def quot_inquire_ccnl(
    excd: str,         # [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
    tday: str,         # [필수] 당일전일구분 (ex. 0:전일, 1:당일)
    symb: str,         # [필수] 종목코드 (ex. 해외종목코드)
    auth: str = "",    # 사용자권한정보
    keyb: str = "",    # NEXT KEY BUFF
    tr_cont: str = "", # 연속거래여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,         # 내부 재귀깊이 (자동관리)
    max_depth: int = 10     # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    해외주식 체결추이 API입니다.
    
    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        tday (str): [필수] 당일전일구분 (ex. 0:전일, 1:당일)
        symb (str): [필수] 종목코드 (ex. 해외종목코드)
        auth (str): 사용자권한정보
        keyb (str): NEXT KEY BUFF
        tr_cont (str): 연속거래여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        pd.DataFrame: 해외주식 체결추이 데이터
        
    Example:
        >>> df = quot_inquire_ccnl(excd="NAS", tday="0", symb="TSLA")
        >>> print(df)
    """

    if excd == "":
        raise ValueError("excd is required (e.g. 'NAS')")
    
    if tday == "":
        raise ValueError("tday is required (e.g. '0' or '1')")
    
    if symb == "":
        raise ValueError("symb is required (e.g. 'TSLA')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    tr_id = "HHDFS76200300"

    params = {
        "EXCD": excd,
        "TDAY": tday,
        "SYMB": symb,
        "AUTH": auth,
        "KEYB": keyb
    }
    
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output1)
            
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data
            
        tr_cont = res.getHeader().tr_cont
        keyb = res.getBody().keyb if hasattr(res.getBody(), 'keyb') else ""
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return quot_inquire_ccnl(
                excd, tday, symb, auth, keyb, "N", dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 