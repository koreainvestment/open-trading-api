"""
Created on 2025-06-16

@author: LaivData jjlee with cursor
"""

import logging
import time
from typing import Optional
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 순위분석 > 국내주식 이격도 순위 [v1_국내주식-095]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/ranking/disparity"

def disparity(
        fid_input_price_2: str,  # 입력 가격2
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_rank_sort_cls_code: str,  # 순위 정렬 구분 코드
        fid_hour_cls_code: str,  # 시간 구분 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_trgt_cls_code: str,  # 대상 구분 코드
        fid_trgt_exls_cls_code: str,  # 대상 제외 구분 코드
        fid_input_price_1: str,  # 입력 가격1
        fid_vol_cnt: str,  # 거래량 수
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 이격도 순위[v1_국내주식-095]
    국내주식 이격도 순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_input_price_2 (str): 입력값 없을때 전체 (~ 가격)
        fid_cond_mrkt_div_code (str): 시장구분코드 (J:KRX, NX:NXT)
        fid_cond_scr_div_code (str): Unique key( 20178 )
        fid_div_cls_code (str): 0: 전체, 1:관리종목, 2:투자주의, 3:투자경고, 4:투자위험예고, 5:투자위험, 6:보톧주, 7:우선주
        fid_rank_sort_cls_code (str): 0: 이격도상위순, 1:이격도하위순
        fid_hour_cls_code (str): 5:이격도5, 10:이격도10, 20:이격도20, 60:이격도60, 120:이격도120
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200
        fid_trgt_cls_code (str): 0 : 전체
        fid_trgt_exls_cls_code (str): 0 : 전체
        fid_input_price_1 (str): 입력값 없을때 전체 (가격 ~)
        fid_vol_cnt (str): 입력값 없을때 전체 (거래량 ~)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 이격도 순위 데이터
        
    Example:
        >>> df = disparity(
        ...     fid_input_price_2="",
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_cond_scr_div_code="20178",
        ...     fid_div_cls_code="0",
        ...     fid_rank_sort_cls_code="0",
        ...     fid_hour_cls_code="5",
        ...     fid_input_iscd="0000",
        ...     fid_trgt_cls_code="0",
        ...     fid_trgt_exls_cls_code="0",
        ...     fid_input_price_1="",
        ...     fid_vol_cnt=""
        ... )
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20178')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20178')")

    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")

    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '0')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '0')")

    if not fid_hour_cls_code:
        logger.error("fid_hour_cls_code is required. (e.g. '5')")
        raise ValueError("fid_hour_cls_code is required. (e.g. '5')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0000')")
        raise ValueError("fid_input_iscd is required. (e.g. '0000')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHPST01780000"

    params = {
        "fid_input_price_2": fid_input_price_2,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_rank_sort_cls_code": fid_rank_sort_cls_code,
        "fid_hour_cls_code": fid_hour_cls_code,
        "fid_input_iscd": fid_input_iscd,
        "fid_trgt_cls_code": fid_trgt_cls_code,
        "fid_trgt_exls_cls_code": fid_trgt_exls_cls_code,
        "fid_input_price_1": fid_input_price_1,
        "fid_vol_cnt": fid_vol_cnt,
    }

    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return disparity(
                fid_input_price_2,
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_div_cls_code,
                fid_rank_sort_cls_code,
                fid_hour_cls_code,
                fid_input_iscd,
                fid_trgt_cls_code,
                fid_trgt_exls_cls_code,
                fid_input_price_1,
                fid_vol_cnt,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
