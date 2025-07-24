"""
Created on 2025-06-17

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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 순위분석 > 국내주식 신용잔고 상위 [국내주식-109]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/ranking/credit-balance"

def credit_balance(
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_option: str,  # 증가율기간
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_rank_sort_cls_code: str,  # 순위 정렬 구분 코드
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        tr_cont: str = "",
        depth: int = 0,
        max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 신용잔고 상위[국내주식-109]
    국내주식 신용잔고 상위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_scr_div_code (str): Unique key(11701)
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200,
        fid_option (str): 2~999
        fid_cond_mrkt_div_code (str): 시장구분코드 (주식 J)
        fid_rank_sort_cls_code (str): '(융자)0:잔고비율 상위, 1: 잔고수량 상위, 2: 잔고금액 상위, 3: 잔고비율 증가상위, 4: 잔고비율 감소상위  (대주)5:잔고비율 상위, 6: 잔고수량 상위, 7: 잔고금액 상위, 8: 잔고비율 증가상위, 9: 잔고비율 감소상위 '
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 국내주식 신용잔고 상위 데이터
        
    Example:
        >>> df1, df2 = credit_balance('11701', '0000', '2', 'J', '0')
        >>> print(df1)
        >>> print(df2)
    """
    # 필수 파라미터 검증
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '11701')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '11701')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0000')")
        raise ValueError("fid_input_iscd is required. (e.g. '0000')")

    if not fid_option:
        logger.error("fid_option is required. (e.g. '2')")
        raise ValueError("fid_option is required. (e.g. '2')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    if fid_rank_sort_cls_code not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '0')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()

    tr_id = "FHKST17010000"

    params = {
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_OPTION": fid_option,
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
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
            return credit_balance(
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_option,
                fid_cond_mrkt_div_code,
                fid_rank_sort_cls_code,
                "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame(), pd.DataFrame()
