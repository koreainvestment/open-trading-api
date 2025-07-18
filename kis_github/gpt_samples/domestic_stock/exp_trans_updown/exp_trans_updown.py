"""
Created on 2025-06-17

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
# [국내주식] 순위분석 > 국내주식 예상체결 상승_하락상위[v1_국내주식-103]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/ranking/exp-trans-updown"

def exp_trans_updown(
        fid_rank_sort_cls_code: str,  # 순위 정렬 구분 코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_aply_rang_prc_1: str,  # 적용 범위 가격1
        fid_vol_cnt: str,  # 거래량 수
        fid_pbmn: str,  # 거래대금
        fid_blng_cls_code: str,  # 소속 구분 코드
        fid_mkop_cls_code: str,  # 장운영 구분 코드
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 예상체결 상승_하락상위[v1_국내주식-103]
    국내주식 예상체결 상승_하락상위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_rank_sort_cls_code (str): 0:상승률1:상승폭2:보합3:하락율4:하락폭5:체결량6:거래대금
        fid_cond_mrkt_div_code (str): 시장구분코드 (주식 J)
        fid_cond_scr_div_code (str): Unique key(20182)
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100
        fid_div_cls_code (str): 0:전체 1:보통주 2:우선주
        fid_aply_rang_prc_1 (str): 입력값 없을때 전체 (가격 ~)
        fid_vol_cnt (str): 입력값 없을때 전체 (거래량 ~)
        fid_pbmn (str): 입력값 없을때 전체 (거래대금 ~) 천원단위
        fid_blng_cls_code (str): 0: 전체
        fid_mkop_cls_code (str): 0:장전예상1:장마감예상
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 예상체결 상승_하락상위 데이터
        
    Example:
        >>> df = exp_trans_updown(
        ...     fid_rank_sort_cls_code="0",
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_cond_scr_div_code="20182",
        ...     fid_input_iscd="0000",
        ...     fid_div_cls_code="0",
        ...     fid_aply_rang_prc_1="",
        ...     fid_vol_cnt="",
        ...     fid_pbmn="",
        ...     fid_blng_cls_code="0",
        ...     fid_mkop_cls_code="0"
        ... )
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '0')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '0')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20182')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20182')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0000')")
        raise ValueError("fid_input_iscd is required. (e.g. '0000')")

    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")

    if not fid_blng_cls_code:
        logger.error("fid_blng_cls_code is required. (e.g. '0')")
        raise ValueError("fid_blng_cls_code is required. (e.g. '0')")

    if not fid_mkop_cls_code:
        logger.error("fid_mkop_cls_code is required. (e.g. '0')")
        raise ValueError("fid_mkop_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()


    tr_id = "FHPST01820000"

    params = {
        "fid_rank_sort_cls_code": fid_rank_sort_cls_code,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_input_iscd": fid_input_iscd,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_aply_rang_prc_1": fid_aply_rang_prc_1,
        "fid_vol_cnt": fid_vol_cnt,
        "fid_pbmn": fid_pbmn,
        "fid_blng_cls_code": fid_blng_cls_code,
        "fid_mkop_cls_code": fid_mkop_cls_code,
    }

    # API 호출
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
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
            return exp_trans_updown(
                fid_rank_sort_cls_code,
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_div_cls_code,
                fid_aply_rang_prc_1,
                fid_vol_cnt,
                fid_pbmn,
                fid_blng_cls_code,
                fid_mkop_cls_code,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
