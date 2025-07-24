"""
Created on 20250129
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
# [국내주식] 시세분석 > 국내기관_외국인 매매종목가집계[국내주식-037]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/foreign-institution-total"

def foreign_institution_total(
    fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
    fid_cond_scr_div_code: str,   # 조건화면분류코드
    fid_input_iscd: str,          # 입력 종목코드
    fid_div_cls_code: str,        # 분류구분코드
    fid_rank_sort_cls_code: str,  # 순위정렬구분코드
    fid_etc_cls_code: str         # 기타구분정렬
) -> pd.DataFrame:
    """
    국내기관_외국인 매매종목가집계 API입니다.

    HTS(efriend Plus) [0440] 외국인/기관 매매종목 가집계 화면을 API로 구현한 사항으로 화면을 함께 보시면 기능 이해가 쉽습니다.

    증권사 직원이 장중에 집계/입력한 자료를 단순 누계한 수치로서, 
    입력시간은 외국인 09:30, 11:20, 13:20, 14:30 / 기관종합 10:00, 11:20, 13:20, 14:30 이며, 
    입력한 시간은 ±10분정도 차이가 발생할 수 있으며, 장운영 사정에 다라 변동될 수 있습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. V)
        fid_cond_scr_div_code (str): [필수] 조건화면분류코드 (ex. 16449)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 0000:전체,0001:코스피,1001:코스닥,...,FAQ 종목정보 다운로드(국내) - 업종코드 참조 )
        fid_div_cls_code (str): [필수] 분류구분코드 (ex. 0:수량정열, 1:금액정열)
        fid_rank_sort_cls_code (str): [필수] 순위정렬구분코드 (ex. 0:순매수상위,1:순매도상위)
        fid_etc_cls_code (str): [필수] 기타구분정렬 (ex. 0:전체,1:외국인,2:기관계,3:기타)

    Returns:
        pd.DataFrame: 국내기관_외국인 매매종목가집계 데이터
        
    Example:
        >>> df = foreign_institution_total("V", "16449", "0000", "0", "0", "0")
        >>> print(df)
    """

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'V')")
        
    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '16449')")
        
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '0000:전체,0001:코스피,1001:코스닥,...,FAQ 종목정보 다운로드(국내) - 업종코드 참조 ')")
        
    if fid_div_cls_code == "":
        raise ValueError("fid_div_cls_code is required (e.g. '0:수량정열, 1:금액정열')")
        
    if fid_rank_sort_cls_code == "":
        raise ValueError("fid_rank_sort_cls_code is required (e.g. '0:순매수상위,1:순매도상위')")
        
    if fid_etc_cls_code == "":
        raise ValueError("fid_etc_cls_code is required (e.g. '0:전체,1:외국인,2:기관계,3:기타')")

    tr_id = "FHPTJ04400000"  # 국내기관_외국인 매매종목가집계

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,    # 조건 시장 분류 코드
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,      # 조건화면분류코드
        "FID_INPUT_ISCD": fid_input_iscd,                    # 입력 종목코드
        "FID_DIV_CLS_CODE": fid_div_cls_code,                # 분류구분코드
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,    # 순위정렬구분코드
        "FID_ETC_CLS_CODE": fid_etc_cls_code                 # 기타구분정렬
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
            
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 