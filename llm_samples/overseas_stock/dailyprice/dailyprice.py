"""
Created on 2025-06-26

@author: LaivData jjlee with cursor
"""

import logging
import time
from typing import Optional, Tuple
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 기본시세 > 해외주식 기간별시세[v1_해외주식-010]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-price/v1/quotations/dailyprice"

def dailyprice(
    auth: str,  # 사용자권한정보
    excd: str,  # 거래소코드
    symb: str,  # 종목코드
    gubn: str,  # 일/주/월구분
    bymd: str,  # 조회기준일자
    modp: str,  # 수정주가반영여부
    env_dv: str = "real",  # 실전모의구분
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 기본시세 
    해외주식 기간별시세[v1_해외주식-010]
    해외주식 기간별시세 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        auth (str): 사용자권한정보 (예: "")
        excd (str): 거래소코드 (예: "NAS")
        symb (str): 종목코드 (예: "TSLA")
        gubn (str): 일/주/월구분 (예: "0")
        bymd (str): 조회기준일자(YYYYMMDD) (예: "20230101")
        modp (str): 수정주가반영여부 (예: "0")
        env_dv (str): 실전모의구분 (real:실전, demo:모의)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식 기간별시세 데이터
        
    Example:
        >>> df1, df2 = dailyprice("auth_token", "NAS", "TSLA", "0", "20230101", "0", "")
        >>> print(df1)
        >>> print(df2)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not excd:
        logger.error("excd is required. (e.g. 'NAS')")
        raise ValueError("excd is required. (e.g. 'NAS')")
    if not symb:
        logger.error("symb is required. (e.g. 'TSLA')")
        raise ValueError("symb is required. (e.g. 'TSLA')")
    if not gubn:
        logger.error("gubn is required. (e.g. '0')")
        raise ValueError("gubn is required. (e.g. '0')")
    if not modp:
        logger.error("modp is required. (e.g. '0')")
        raise ValueError("modp is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real" or env_dv == "demo":
        tr_id = "HHDFS76240000"  # 실전/모의투자 공통 TR ID
    else:
        logger.error("env_dv can only be 'real' or 'demo'")
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "AUTH": auth,
        "EXCD": excd,
        "SYMB": symb,
        "GUBN": gubn,
        "BYMD": bymd,
        "MODP": modp,
    }

    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                # output1은 단일 객체, output2는 배열일 수 있음
                if isinstance(output_data, list):
                    current_data1 = pd.DataFrame(output_data)
                else:
                    # 단일 객체인 경우 리스트로 감싸서 DataFrame 생성
                    current_data1 = pd.DataFrame([output_data])
                
                if dataframe1 is not None:
                    dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
                else:
                    dataframe1 = current_data1
            else:
                if dataframe1 is None:
                    dataframe1 = pd.DataFrame()
        else:
            if dataframe1 is None:
                dataframe1 = pd.DataFrame()
        # output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                # output1은 단일 객체, output2는 배열일 수 있음
                if isinstance(output_data, list):
                    current_data2 = pd.DataFrame(output_data)
                else:
                    # 단일 객체인 경우 리스트로 감싸서 DataFrame 생성
                    current_data2 = pd.DataFrame([output_data])
                
                if dataframe2 is not None:
                    dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
                else:
                    dataframe2 = current_data2
            else:
                if dataframe2 is None:
                    dataframe2 = pd.DataFrame()
        else:
            if dataframe2 is None:
                dataframe2 = pd.DataFrame()
        tr_cont = res.getHeader().tr_cont
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return dailyprice(
                auth,
                excd,
                symb,
                gubn,
                bymd,
                modp,
                env_dv,
                dataframe1,
                dataframe2,
                "N",
                depth + 1,
                max_depth
            )

        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame(), pd.DataFrame()
