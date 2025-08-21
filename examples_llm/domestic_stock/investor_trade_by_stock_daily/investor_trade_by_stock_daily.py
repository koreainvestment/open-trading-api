"""
Created on 2025-08-21

@author: LaivData jjlee with cursor
"""

import logging
import sys
from typing import Optional, Tuple

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

########################################################################################
# [국내주식] 시세분석  > 종목별 투자자매매동향(일별)[종목별 투자자매매동향(일별)]
########################################################################################

API_URL = "/uapi/domestic-stock/v1/quotations/investor-trade-by-stock-daily"

def investor_trade_by_stock_daily(
    fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
    fid_input_iscd: str,  # 입력 종목코드
    fid_input_date_1: str,  # 입력 날짜1
    fid_org_adj_prc: str,  # 수정주가 원주가 가격
    fid_etc_cls_code: str,  # 기타 구분 코드
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 시세분석 
    종목별 투자자매매동향(일별)[종목별 투자자매매동향(일별)]
    종목별 투자자매매동향(일별) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): J:KRX, NX:NXT, UN:통합
        fid_input_iscd (str): 종목번호 (6자리)
        fid_input_date_1 (str): 입력 날짜(20250812)
        fid_org_adj_prc (str): 공란 입력
        fid_etc_cls_code (str): 공란 입력
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 종목별 투자자매매동향(일별) 데이터
        
    Example:
        >>> df1, df2 = investor_trade_by_stock_daily(
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_input_iscd="005930",
        ...     fid_input_date_1="20250812",
        ...     fid_org_adj_prc="",
        ...     fid_etc_cls_code=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '005930')")
        raise ValueError("fid_input_iscd is required. (e.g. '005930')")
    if not fid_input_date_1:
        logger.error("fid_input_date_1 is required. (e.g. '20250812')")
        raise ValueError("fid_input_date_1 is required. (e.g. '20250812')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    tr_id = "FHPTJ04160001"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_ORG_ADJ_PRC": fid_org_adj_prc,
        "FID_ETC_CLS_CODE": fid_etc_cls_code,
    }

    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                if isinstance(output_data, list):
                    current_data1 = pd.DataFrame(output_data)
                else:
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
                if isinstance(output_data, list):
                    current_data2 = pd.DataFrame(output_data)
                else:
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
            return investor_trade_by_stock_daily(
                fid_cond_mrkt_div_code,
                fid_input_iscd,
                fid_input_date_1,
                fid_org_adj_prc,
                fid_etc_cls_code,
                "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(API_URL)
        return pd.DataFrame(), pd.DataFrame()