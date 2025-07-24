"""
Created on 20250113 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 국내주식 상하한가 포착 [국내주식-190]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/capture-uplowprice"


def capture_uplowprice(
        fid_cond_mrkt_div_code: str,  # [필수] 조건시장분류코드 (ex. J:주식)
        fid_cond_scr_div_code: str,  # [필수] 조건화면분류코드 (ex. 11300)
        fid_prc_cls_code: str,  # [필수] 상하한가 구분코드 (ex. 0:상한가, 1:하한가)
        fid_div_cls_code: str,
        # [필수] 분류구분코드 (ex. 0:상하한가종목, 6:8%상하한가 근접, 5:10%상하한가 근접, 1:15%상하한가 근접, 2:20%상하한가 근접, 3:25%상하한가 근접)
        fid_input_iscd: str,  # [필수] 입력종목코드 (ex. 0000:전체, 0001:코스피, 1001:코스닥)
        fid_trgt_cls_code: str = "",  # 대상구분코드
        fid_trgt_exls_cls_code: str = "",  # 대상제외구분코드
        fid_input_price_1: str = "",  # 입력가격1
        fid_input_price_2: str = "",  # 입력가격2
        fid_vol_cnt: str = ""  # 거래량수
) -> pd.DataFrame:
    """
    국내주식 상하한가 포착 API입니다.
    한국투자 HTS(eFriend Plus) > [0917] 실시간 상하한가 포착 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건시장분류코드 (ex. J:주식)
        fid_cond_scr_div_code (str): [필수] 조건화면분류코드 (ex. 11300)
        fid_prc_cls_code (str): [필수] 상하한가 구분코드 (ex. 0:상한가, 1:하한가)
        fid_div_cls_code (str): [필수] 분류구분코드 (ex. 0:상하한가종목, 6:8%상하한가 근접, 5:10%상하한가 근접, 1:15%상하한가 근접, 2:20%상하한가 근접, 3:25%상하한가 근접)
        fid_input_iscd (str): [필수] 입력종목코드 (ex. 0000:전체, 0001:코스피, 1001:코스닥)
        fid_trgt_cls_code (str): 대상구분코드
        fid_trgt_exls_cls_code (str): 대상제외구분코드
        fid_input_price_1 (str): 입력가격1
        fid_input_price_2 (str): 입력가격2
        fid_vol_cnt (str): 거래량수

    Returns:
        pd.DataFrame: 상하한가 포착 데이터
        
    Example:
        >>> df = capture_uplowprice("J", "11300", "0", "0", "0000")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")

    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '11300')")

    if fid_prc_cls_code == "":
        raise ValueError("fid_prc_cls_code is required (e.g. '0', '1')")

    if fid_div_cls_code == "":
        raise ValueError("fid_div_cls_code is required (e.g. '0', '6', '5', '1', '2', '3')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '0000', '0001', '1001')")

    tr_id = "FHKST130000C0"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_PRC_CLS_CODE": fid_prc_cls_code,
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_TRGT_CLS_CODE": fid_trgt_cls_code,
        "FID_TRGT_EXLS_CLS_CODE": fid_trgt_exls_cls_code,
        "FID_INPUT_PRICE_1": fid_input_price_1,
        "FID_INPUT_PRICE_2": fid_input_price_2,
        "FID_VOL_CNT": fid_vol_cnt
    }

    res = ka._url_fetch(API_URL, tr_id, "", params)

    if res.isOK():
        return pd.DataFrame(res.getBody().output)
    else:
        res.printError(url=API_URL)
        return pd.DataFrame()
