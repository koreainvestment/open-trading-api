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
# [국내주식] 순위분석 > 국내주식 대량체결건수 상위[국내주식-107]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/ranking/bulk-trans-num"

def bulk_trans_num(
    fid_aply_rang_prc_2: str,  # 적용 범위 가격2
    fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
    fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
    fid_input_iscd: str,  # 입력 종목코드
    fid_rank_sort_cls_code: str,  # 순위 정렬 구분 코드
    fid_div_cls_code: str,  # 분류 구분 코드
    fid_input_price_1: str,  # 입력 가격1
    fid_aply_rang_prc_1: str,  # 적용 범위 가격1
    fid_input_iscd_2: str,  # 입력 종목코드2
    fid_trgt_exls_cls_code: str,  # 대상 제외 구분 코드
    fid_trgt_cls_code: str,  # 대상 구분 코드
    fid_vol_cnt: str,  # 거래량 수
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 대량체결건수 상위[국내주식-107]
    국내주식 대량체결건수 상위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_aply_rang_prc_2 (str): ~ 가격
        fid_cond_mrkt_div_code (str): 시장구분코드 (J:KRX, NX:NXT)
        fid_cond_scr_div_code (str): Unique key(11909)
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100
        fid_rank_sort_cls_code (str): 0:매수상위, 1:매도상위
        fid_div_cls_code (str): 0:전체
        fid_input_price_1 (str): 건별금액 ~
        fid_aply_rang_prc_1 (str): 가격 ~
        fid_input_iscd_2 (str): 공백:전체종목, 개별종목 조회시 종목코드 (000660)
        fid_trgt_exls_cls_code (str): 0:전체
        fid_trgt_cls_code (str): 0:전체
        fid_vol_cnt (str): 거래량 ~
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 대량체결건수 상위 데이터
        
    Example:
        >>> df = bulk_trans_num(
                fid_aply_rang_prc_2="100000",
                fid_cond_mrkt_div_code="J",
                fid_cond_scr_div_code="11909",
                fid_input_iscd="0000",
                fid_rank_sort_cls_code="0",
                fid_div_cls_code="0",
                fid_input_price_1="50000",
                fid_aply_rang_prc_1="200000",
                fid_input_iscd_2="",
                fid_trgt_exls_cls_code="0",
                fid_trgt_cls_code="0",
                fid_vol_cnt="1000"
            )
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '11909')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '11909')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0000')")
        raise ValueError("fid_input_iscd is required. (e.g. '0000')")

    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '0')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '0')")

    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")

    if not fid_trgt_exls_cls_code:
        logger.error("fid_trgt_exls_cls_code is required. (e.g. '0')")
        raise ValueError("fid_trgt_exls_cls_code is required. (e.g. '0')")

    if not fid_trgt_cls_code:
        logger.error("fid_trgt_cls_code is required. (e.g. '0')")
        raise ValueError("fid_trgt_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()


    tr_id = "FHKST190900C0"

    params = {
        "fid_aply_rang_prc_2": fid_aply_rang_prc_2,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_input_iscd": fid_input_iscd,
        "fid_rank_sort_cls_code": fid_rank_sort_cls_code,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_input_price_1": fid_input_price_1,
        "fid_aply_rang_prc_1": fid_aply_rang_prc_1,
        "fid_input_iscd_2": fid_input_iscd_2,
        "fid_trgt_exls_cls_code": fid_trgt_exls_cls_code,
        "fid_trgt_cls_code": fid_trgt_cls_code,
        "fid_vol_cnt": fid_vol_cnt,
    }

    # API 호출
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 다음 페이지 여부 확인
        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return bulk_trans_num(
                fid_aply_rang_prc_2,
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_rank_sort_cls_code,
                fid_div_cls_code,
                fid_input_price_1,
                fid_aply_rang_prc_1,
                fid_input_iscd_2,
                fid_trgt_exls_cls_code,
                fid_trgt_cls_code,
                fid_vol_cnt,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 호출 실패 시 에러 로그
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame()
