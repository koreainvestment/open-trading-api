"""
Created on 20250101 
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 프로그램매매 종합현황(시간) [국내주식-114]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/comp-program-trade-today"

def comp_program_trade_today(
    fid_cond_mrkt_div_code: str,  # [필수] 시장 구분 코드 (J:KRX,NX:NXT,UN:통합)
    fid_mrkt_cls_code: str,       # [필수] 시장구분코드 (K:코스피, Q:코스닥)
    fid_sctn_cls_code: str = "",  # 구간 구분 코드
    fid_input_iscd: str = "",     # 입력종목코드
    fid_cond_mrkt_div_code1: str = "",  # 시장분류코드
    fid_input_hour_1: str = ""    # 입력시간
) -> pd.DataFrame:
    """
    프로그램매매 종합현황(시간) API입니다. 
    한국투자 HTS(eFriend Plus) > [0460] 프로그램매매 종합현황 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

    ※ 장시간(09:00~15:30) 동안의 최근 30분간의 데이터 확인이 가능하며, 다음조회가 불가합니다.
    ※ 장시간(09:00~15:30) 이후에는 bsop_hour 에 153000 ~ 170000 까지의 시간데이터가 출력되지만 데이터는 모두 동일한 장마감 데이터인 점 유의 부탁드립니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 시장 구분 코드 (ex. J:KRX,NX:NXT,UN:통합)
        fid_mrkt_cls_code (str): [필수] 시장구분코드 (ex. K:코스피, Q:코스닥)
        fid_sctn_cls_code (str): 구간 구분 코드
        fid_input_iscd (str): 입력종목코드
        fid_cond_mrkt_div_code1 (str): 시장분류코드
        fid_input_hour_1 (str): 입력시간
        
    Returns:
        pd.DataFrame: 프로그램매매 종합현황 데이터
        
    Example:
        >>> df = comp_program_trade_today("J", "K")
        >>> print(df)
    """
    
    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:KRX,NX:NXT,UN:통합')")
    
    if fid_mrkt_cls_code == "":
        raise ValueError("fid_mrkt_cls_code is required (e.g. 'K:코스피, Q:코스닥')")

    tr_id = "FHPPG04600101"  # 프로그램매매 종합현황(시간)

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,  # 시장 구분 코드
        "FID_MRKT_CLS_CODE": fid_mrkt_cls_code,            # 시장구분코드
        "FID_SCTN_CLS_CODE": fid_sctn_cls_code,            # 구간 구분 코드
        "FID_INPUT_ISCD": fid_input_iscd,                  # 입력종목코드
        "FID_COND_MRKT_DIV_CODE1": fid_cond_mrkt_div_code1,# 시장분류코드
        "FID_INPUT_HOUR_1": fid_input_hour_1               # 입력시간
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        # array 타입이므로 DataFrame으로 반환
        current_data = pd.DataFrame(res.getBody().output)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 