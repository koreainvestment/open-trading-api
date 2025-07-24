"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""


import sys
import time
from typing import Optional
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 시세분석 > 해외주식 기간별권리조회 [해외주식-052]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-price/v1/quotations/period-rights"

def period_rights(
    rght_type_cd: str,  # 권리유형코드
    inqr_dvsn_cd: str,  # 조회구분코드
    inqr_strt_dt: str,  # 조회시작일자
    inqr_end_dt: str,   # 조회종료일자
    pdno: str = "",     # 상품번호
    prdt_type_cd: str = "",  # 상품유형코드
    NK50: str = "",     # 연속조회키50
    FK50: str = "",     # 연속조회검색조건50
    tr_cont: str = "",  # 연속거래여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,     # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    해외주식 기간별권리조회 API입니다.
    한국투자 HTS(eFriend Plus) > [7520] 기간별해외증권권리조회 화면을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

    ※ 확정여부가 '예정'으로 표시되는 경우는 권리정보가 변경될 수 있으니 참고자료로만 활용하시기 바랍니다.
    
    Args:
        rght_type_cd (str): [필수] 권리유형코드 (%%:전체, 01:유상, 02:무상, 03:배당, 11:합병,14:액면분할, 15:액면병합, 17:감자, 54:WR청구,61:원리금상환, 71:WR소멸, 74:배당옵션, 75:특별배당, 76:ISINCODE변경, 77:실권주청약)
        inqr_dvsn_cd (str): [필수] 조회구분코드 (02:현지기준일, 03:청약시작일, 04:청약종료일)
        inqr_strt_dt (str): [필수] 조회시작일자 (20250101)
        inqr_end_dt (str): [필수] 조회종료일자 (20250131)
        pdno (str): 상품번호
        prdt_type_cd (str): 상품유형코드
        NK50 (str): 연속조회키50
        FK50 (str): 연속조회검색조건50
        tr_cont (str): 연속거래여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        pd.DataFrame: 해외주식 기간별권리조회 데이터
        
    Example:
        >>> df = period_rights("%%", "02", "20240417", "20240417")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if rght_type_cd == "":
        raise ValueError("rght_type_cd is required (e.g. '%%:전체, 01:유상, 02:무상, 03:배당, 11:합병,14:액면분할, 15:액면병합, 17:감자, 54:WR청구,61:원리금상환, 71:WR소멸, 74:배당옵션, 75:특별배당, 76:ISINCODE변경, 77:실권주청약')")
    
    if inqr_dvsn_cd == "":
        raise ValueError("inqr_dvsn_cd is required (e.g. '02:현지기준일, 03:청약시작일, 04:청약종료일')")
    
    if inqr_strt_dt == "":
        raise ValueError("inqr_strt_dt is required (e.g. '20250101')")
    
    if inqr_end_dt == "":
        raise ValueError("inqr_end_dt is required (e.g. '20250131')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    tr_id = "CTRGT011R"  # 해외주식 기간별권리조회

    params = {
        "RGHT_TYPE_CD": rght_type_cd,      # 권리유형코드
        "INQR_DVSN_CD": inqr_dvsn_cd,      # 조회구분코드
        "INQR_STRT_DT": inqr_strt_dt,      # 조회시작일자
        "INQR_END_DT": inqr_end_dt,        # 조회종료일자
        "PDNO": pdno,                      # 상품번호
        "PRDT_TYPE_CD": prdt_type_cd,      # 상품유형코드
        "CTX_AREA_NK50": NK50,             # 연속조회키50
        "CTX_AREA_FK50": FK50              # 연속조회검색조건50
    }
    
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
            
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data
            
        tr_cont = res.getHeader().tr_cont
        NK50 = res.getBody().ctx_area_nk50
        FK50 = res.getBody().ctx_area_fk50
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return period_rights(
                rght_type_cd, inqr_dvsn_cd, inqr_strt_dt, inqr_end_dt, 
                pdno, prdt_type_cd, NK50, FK50, "N", dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 