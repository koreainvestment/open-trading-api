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

##############################################################################################
# [국내주식] 종목정보 > 국내주식 당사 신용가능종목[국내주식-111]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/credit-by-company"

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def credit_by_company(
        fid_rank_sort_cls_code: str,  # 순위 정렬 구분 코드
        fid_slct_yn: str,  # 선택 여부
        fid_input_iscd: str,  # 입력 종목코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    국내주식 당사 신용가능종목[국내주식-111]
    국내주식 당사 신용가능종목 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_rank_sort_cls_code (str): 0:코드순, 1:이름순
        fid_slct_yn (str): 0:신용주문가능, 1: 신용주문불가
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100
        fid_cond_scr_div_code (str): Unique key(20477)
        fid_cond_mrkt_div_code (str): 시장구분코드 (주식 J)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 당사 신용가능종목 데이터
        
    Example:
        >>> df = credit_by_company(
        ...     fid_rank_sort_cls_code="1",
        ...     fid_slct_yn="0",
        ...     fid_input_iscd="0000",
        ...     fid_cond_scr_div_code="20477",
        ...     fid_cond_mrkt_div_code="J"
        ... )
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '1')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '1')")

    if not fid_slct_yn:
        logger.error("fid_slct_yn is required. (e.g. '0')")
        raise ValueError("fid_slct_yn is required. (e.g. '0')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0000')")
        raise ValueError("fid_input_iscd is required. (e.g. '0000')")

    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20477')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20477')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # API 호출 URL 및 ID 설정

    tr_id = "FHPST04770000"

    # 요청 파라미터 설정
    params = {
        "fid_rank_sort_cls_code": fid_rank_sort_cls_code,
        "fid_slct_yn": fid_slct_yn,
        "fid_input_iscd": fid_input_iscd,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
    }

    # API 호출
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    # API 호출 성공 시 데이터 처리
    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        # 기존 데이터프레임과 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        # 다음 페이지 호출
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return credit_by_company(
                fid_rank_sort_cls_code,
                fid_slct_yn,
                fid_input_iscd,
                fid_cond_scr_div_code,
                fid_cond_mrkt_div_code,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 호출 실패 시 에러 로그 출력
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
