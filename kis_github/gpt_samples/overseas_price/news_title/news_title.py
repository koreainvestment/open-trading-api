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
# [해외주식] 시세분석 > 해외뉴스종합(제목) [해외주식-053]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-price/v1/quotations/news-title"

def news_title(
    info_gb: str = "",          # [필수] 뉴스구분
    class_cd: str = "",         # [필수] 중분류  
    nation_cd: str = "",        # [필수] 국가코드 (ex. 공백:전체, CN:중국, HK:홍콩, US:미국)
    exchange_cd: str = "",      # [필수] 거래소코드
    symb: str = "",             # [필수] 종목코드
    data_dt: str = "",          # [필수] 조회일자
    data_tm: str = "",          # [필수] 조회시간
    cts: str = "",              # [필수] 다음키
    tr_cont: str = "",          # [필수] 연속거래여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,             # 내부 재귀깊이 (자동관리)
    max_depth: int = 10         # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    해외뉴스종합(제목) API입니다.
    한국투자 HTS(eFriend Plus) > [7702] 해외뉴스종합 화면의 "우측 상단 뉴스목록" 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        info_gb (str): [필수] 뉴스구분
        class_cd (str): [필수] 중분류
        nation_cd (str): [필수] 국가코드 (ex. 공백:전체, CN:중국, HK:홍콩, US:미국)
        exchange_cd (str): [필수] 거래소코드
        symb (str): [필수] 종목코드
        data_dt (str): [필수] 조회일자
        data_tm (str): [필수] 조회시간
        cts (str): [필수] 다음키
        tr_cont (str): [필수] 연속거래여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        pd.DataFrame: 해외뉴스종합(제목) 데이터
        
    Example:
        >>> df = news_title()
        >>> print(df)
    """

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    tr_id = "HHPSTH60100C1"  # 해외뉴스종합(제목)

    params = {
        "INFO_GB": info_gb,           # 뉴스구분
        "CLASS_CD": class_cd,         # 중분류
        "NATION_CD": nation_cd,       # 국가코드
        "EXCHANGE_CD": exchange_cd,   # 거래소코드
        "SYMB": symb,                 # 종목코드
        "DATA_DT": data_dt,           # 조회일자
        "DATA_TM": data_tm,           # 조회시간
        "CTS": cts                    # 다음키
    }
    
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().outblock1)
            
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data
            
        tr_cont = res.getHeader().tr_cont
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return news_title(
                info_gb, class_cd, nation_cd, exchange_cd, symb, data_dt, data_tm, cts, "N", dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 