"""
Created on 20250101 
@author: LaivData SJPark with cursor
"""


import sys
import time
from typing import Optional, Tuple
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 시세분석 > 당사 해외주식담보대출 가능 종목 [해외주식-051]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-price/v1/quotations/colable-by-company"

def colable_by_company(
    pdno: str,  # 상품번호
    natn_cd: str,  # 국가코드
    inqr_sqn_dvsn: str,  # 조회순서구분
    prdt_type_cd: str = "",  # 상품유형코드
    inqr_strt_dt: str = "",  # 조회시작일자
    inqr_end_dt: str = "",  # 조회종료일자
    inqr_dvsn: str = "",  # 조회구분
    rt_dvsn_cd: str = "",  # 비율구분코드
    rt: str = "",  # 비율
    loan_psbl_yn: str = "",  # 대출가능여부
    FK100: str = "",  # 연속조회검색조건100
    NK100: str = "",  # 연속조회키100
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    당사 해외주식담보대출 가능 종목 API입니다.
    한국투자 HTS(eFriend Plus) > [0497] 당사 해외주식담보대출 가능 종목 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

    한 번의 호출에 20건까지 조회가 가능하며 다음조회가 불가하기에, PDNO에 데이터 확인하고자 하는 종목코드를 입력하여 단건조회용으로 사용하시기 바랍니다.
    
    Args:
        pdno (str): [필수] 상품번호 (ex. AMD)
        natn_cd (str): [필수] 국가코드 (ex. 840:미국,344:홍콩,156:중국)
        inqr_sqn_dvsn (str): [필수] 조회순서구분 (ex. 01:이름순,02:코드순)
        prdt_type_cd (str): 상품유형코드
        inqr_strt_dt (str): 조회시작일자
        inqr_end_dt (str): 조회종료일자
        inqr_dvsn (str): 조회구분
        rt_dvsn_cd (str): 비율구분코드
        rt (str): 비율
        loan_psbl_yn (str): 대출가능여부
        FK100 (str): 연속조회검색조건100
        NK100 (str): 연속조회키100
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> df1, df2 = colable_by_company(pdno="AMD", natn_cd="840", inqr_sqn_dvsn="01")
        >>> print(df1)  # output1 데이터
        >>> print(df2)  # output2 데이터
    """

    # 필수 파라미터 검증
    if pdno == "":
        raise ValueError("pdno is required (e.g. 'AMD')")
    
    if natn_cd == "":
        raise ValueError("natn_cd is required (e.g. '840:미국,344:홍콩,156:중국')")
    
    if inqr_sqn_dvsn == "":
        raise ValueError("inqr_sqn_dvsn is required (e.g. '01:이름순,02:코드순')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "CTLN4050R"

    params = {
        "PDNO": pdno,
        "NATN_CD": natn_cd,
        "INQR_SQN_DVSN": inqr_sqn_dvsn,
        "PRDT_TYPE_CD": prdt_type_cd,
        "INQR_STRT_DT": inqr_strt_dt,
        "INQR_END_DT": inqr_end_dt,
        "INQR_DVSN": inqr_dvsn,
        "RT_DVSN_CD": rt_dvsn_cd,
        "RT": rt,
        "LOAN_PSBL_YN": loan_psbl_yn,
        "CTX_AREA_FK100": FK100,
        "CTX_AREA_NK100": NK100
    }
    
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 처리 (array)
        current_data1 = pd.DataFrame(res.getBody().output1)
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1
            
        # output2 처리 (object)
        current_data2 = pd.DataFrame([res.getBody().output2])
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2
            
        tr_cont = res.getHeader().tr_cont
        FK100 = res.getBody().ctx_area_fk100
        NK100 = res.getBody().ctx_area_nk100
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return colable_by_company(
                pdno, natn_cd, inqr_sqn_dvsn, prdt_type_cd, inqr_strt_dt, inqr_end_dt,
                inqr_dvsn, rt_dvsn_cd, rt, loan_psbl_yn, FK100, NK100, "N",
                dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=API_URL)
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2 