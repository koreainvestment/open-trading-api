"""
Created on 20250601 
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
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 주식잔고조회_실현손익[v1_국내주식-041]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/trading/inquire-balance-rlz-pl"

def inquire_balance_rlz_pl(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    afhr_flpr_yn: str,  # 시간외단일가여부
    inqr_dvsn: str,  # 조회구분
    unpr_dvsn: str,  # 단가구분
    fund_sttl_icld_yn: str,  # 펀드결제포함여부
    fncg_amt_auto_rdpt_yn: str,  # 융자금액자동상환여부
    prcs_dvsn: str,  # PRCS_DVSN
    ofl_yn: str = "",  # 오프라인여부
    cost_icld_yn: str = "",  # 비용포함여부
    FK100: str = "",  # 연속조회검색조건100
    NK100: str = "",  # 연속조회키100
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    주식잔고조회_실현손익 API입니다.
    한국투자 HTS(eFriend Plus) [0800] 국내 체결기준잔고 화면을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    (참고: 포럼 - 공지사항 - 신규 API 추가 안내(주식잔고조회_실현손익 외 1건))
    
    Args:
        cano (str): [필수] 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        afhr_flpr_yn (str): [필수] 시간외단일가여부 (N:기본값, Y:시간외단일가)
        inqr_dvsn (str): [필수] 조회구분 (00:전체)
        unpr_dvsn (str): [필수] 단가구분 (01:기본값)
        fund_sttl_icld_yn (str): [필수] 펀드결제포함여부 (N:포함하지 않음, Y:포함)
        fncg_amt_auto_rdpt_yn (str): [필수] 융자금액자동상환여부 (N:기본값)
        prcs_dvsn (str): [필수] PRCS_DVSN (00:전일매매포함, 01:전일매매미포함)
        ofl_yn (str): 오프라인여부
        cost_icld_yn (str): 비용포함여부
        FK100 (str): 연속조회검색조건100
        NK100 (str): 연속조회키100
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 주식잔고조회_실현손익 데이터 (output1, output2)
        
    Example:
        >>> df1, df2 = inquire_balance_rlz_pl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, afhr_flpr_yn="N", inqr_dvsn="02", unpr_dvsn="01", fund_sttl_icld_yn="N", fncg_amt_auto_rdpt_yn="N", prcs_dvsn="01")
        >>> print(df1)
        >>> print(df2)
    """

    # 필수 파라미터 검증
    if cano == "":
        raise ValueError("cano is required (e.g. '계좌번호 체계(8-2)의 앞 8자리')")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '계좌번호 체계(8-2)의 뒤 2자리')")
    
    if afhr_flpr_yn == "":
        raise ValueError("afhr_flpr_yn is required (e.g. 'N:기본값, Y:시간외단일가')")
    
    if inqr_dvsn == "":
        raise ValueError("inqr_dvsn is required (e.g. '00:전체')")
    
    if unpr_dvsn == "":
        raise ValueError("unpr_dvsn is required (e.g. '01:기본값')")
    
    if fund_sttl_icld_yn == "":
        raise ValueError("fund_sttl_icld_yn is required (e.g. 'N:포함하지 않음, Y:포함')")
    
    if fncg_amt_auto_rdpt_yn == "":
        raise ValueError("fncg_amt_auto_rdpt_yn is required (e.g. 'N:기본값')")
    
    if prcs_dvsn == "":
        raise ValueError("prcs_dvsn is required (e.g. '00:전일매매포함, 01:전일매매미포함')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "TTTC8494R"  # 주식잔고조회_실현손익

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "AFHR_FLPR_YN": afhr_flpr_yn,
        "OFL_YN": ofl_yn,
        "INQR_DVSN": inqr_dvsn,
        "UNPR_DVSN": unpr_dvsn,
        "FUND_STTL_ICLD_YN": fund_sttl_icld_yn,
        "FNCG_AMT_AUTO_RDPT_YN": fncg_amt_auto_rdpt_yn,
        "PRCS_DVSN": prcs_dvsn,
        "COST_ICLD_YN": cost_icld_yn,
        "CTX_AREA_FK100": FK100,
        "CTX_AREA_NK100": NK100
    }
    
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 처리
        current_data1 = pd.DataFrame(res.getBody().output1)
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1
            
        # output2 처리  
        current_data2 = pd.DataFrame(res.getBody().output2)
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
            return inquire_balance_rlz_pl(
                cano, acnt_prdt_cd, afhr_flpr_yn, inqr_dvsn, unpr_dvsn, 
                fund_sttl_icld_yn, fncg_amt_auto_rdpt_yn, prcs_dvsn, 
                ofl_yn, cost_icld_yn, FK100, NK100, "N", 
                dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 