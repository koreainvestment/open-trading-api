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
# [국내주식] 주문/계좌 > 주식일별주문체결조회[v1_국내주식-005]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/trading/inquire-daily-ccld"

def inquire_daily_ccld(
    env_dv: str,  # [필수] 실전모의구분 (real:실전, demo:모의)
    pd_dv: str,   # [필수] 3개월이전이내구분 (before:이전, inner:이내)
    cano: str,    # [필수] 종합계좌번호
    acnt_prdt_cd: str,  # [필수] 계좌상품코드
    inqr_strt_dt: str,  # [필수] 조회시작일자
    inqr_end_dt: str,   # [필수] 조회종료일자
    sll_buy_dvsn_cd: str,  # [필수] 매도매수구분코드 (00 : 전체 / 01 : 매도 / 02 : 매수)
    ccld_dvsn: str,  # [필수] 체결구분 (00 전체 / 01 체결 / 02 미체결)
    inqr_dvsn: str,  # [필수] 조회구분 (00 역순 / 01 정순)
    inqr_dvsn_3: str,  # [필수] 조회구분3 (00 전체 / 01 현금 / 02 신용 / 03 담보 / 04 대주 / 05 대여 / 06 자기융자신규/상환 / 07 유통융자신규/상환)
    pdno: str = "",  # 상품번호
    ord_gno_brno: str = "",  # 주문채번지점번호
    odno: str = "",  # 주문번호 (주문시 한국투자증권 시스템에서 채번된 주문번호)
    inqr_dvsn_1: str = "",  # 조회구분1 (없음: 전체 / 1: ELW / 2: 프리보드)
    FK100: str = "",  # 연속조회검색조건100 (공란: 최초 조회 / 이전 조회 Output 사용)
    NK100: str = "",  # 연속조회키100 (공란: 최초 조회 / 이전 조회 Output 사용)
    tr_cont: str = "",  # 연속거래여부
    excg_id_dvsn_cd: Optional[str] = "KRX",  # 거래소ID구분코드 (KRX / NXT / SOR / ALL)
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    주식일별주문체결조회 API입니다. 
    실전계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다. 
    모의계좌의 경우, 한 번의 호출에 최대 15건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다. 

    * 다만, 3개월 이전 체결내역 조회(CTSC9115R) 의 경우, 
    장중에는 많은 거래량으로 인해 순간적으로 DB가 밀렸거나 응답을 늦게 받거나 하는 등의 이슈가 있을 수 있어
    ① 가급적 장 종료 이후(15:30 이후) 조회하시고 
    ② 조회기간(INQR_STRT_DT와 INQR_END_DT 사이의 간격)을 보다 짧게 해서 조회하는 것을
    권유드립니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        pd_dv (str): [필수] 3개월이전이내구분 (ex. before:이전, inner:이내)
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드
        inqr_strt_dt (str): [필수] 조회시작일자
        inqr_end_dt (str): [필수] 조회종료일자
        sll_buy_dvsn_cd (str): [필수] 매도매수구분코드 (ex. 00 : 전체 / 01 : 매도 / 02 : 매수)
        pdno (str): 상품번호
        ccld_dvsn (str): [필수] 체결구분 (ex. 00 전체 / 01 체결 / 02 미체결)
        inqr_dvsn (str): [필수] 조회구분 (ex. 00 역순 / 01 정순)
        inqr_dvsn_3 (str): [필수] 조회구분3 (ex. 00 전체 / 01 현금 / 02 신용 / 03 담보 / 04 대주 / 05 대여 / 06 자기융자신규/상환 / 07 유통융자신규/상환)
        ord_gno_brno (str): 주문채번지점번호
        odno (str): 주문번호 (ex. 주문시 한국투자증권 시스템에서 채번된 주문번호)
        inqr_dvsn_1 (str): 조회구분1 (ex. 없음: 전체 / 1: ELW / 2: 프리보드)
        FK100 (str): 연속조회검색조건100 (ex. 공란: 최초 조회 / 이전 조회 Output 사용)
        NK100 (str): 연속조회키100 (ex. 공란: 최초 조회 / 이전 조회 Output 사용)
        tr_cont (str): 연속거래여부
        excg_id_dvsn_cd (Optional[str]): 거래소ID구분코드 (ex. KRX / NXT / SOR / ALL)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터프레임, output2 데이터프레임)
        
    Example:
        >>> df1, df2 = inquire_daily_ccld(
        ...     env_dv="real", pd_dv="inner", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod,
        ...     inqr_strt_dt="20220810", inqr_end_dt="20220810", 
        ...     sll_buy_dvsn_cd="00", pdno="005930", ccld_dvsn="00", 
        ...     inqr_dvsn="00", inqr_dvsn_3="00"
        ... )
        >>> print(df1)
        >>> print(df2)
    """

    # 필수 파라미터 검증
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real:실전', 'demo:모의')")
    
    if pd_dv == "":
        raise ValueError("pd_dv is required (e.g. 'before:이전', 'inner:이내')")
        
    if cano == "":
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required")
    
    if inqr_strt_dt == "":
        raise ValueError("inqr_strt_dt is required")
    
    if inqr_end_dt == "":
        raise ValueError("inqr_end_dt is required")
    
    if sll_buy_dvsn_cd == "":
        raise ValueError("sll_buy_dvsn_cd is required (e.g. '00 : 전체 / 01 : 매도 / 02 : 매수')")
    
    if ccld_dvsn == "":
        raise ValueError("ccld_dvsn is required (e.g. '00 전체 / 01 체결 / 02 미체결')")
    
    if inqr_dvsn == "":
        raise ValueError("inqr_dvsn is required (e.g. '00 역순 / 01 정순')")
    
    if inqr_dvsn_3 == "":
        raise ValueError("inqr_dvsn_3 is required (e.g. '00 전체 / 01 현금 / 02 신용 / 03 담보 / 04 대주 / 05 대여 / 06 자기융자신규/상환 / 07 유통융자신규/상환')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    # tr_id 설정
    if env_dv == "real":
        if pd_dv == "before":
            tr_id = "CTSC9215R"
        elif pd_dv == "inner":
            tr_id = "TTTC0081R"
        else:
            raise ValueError("pd_dv can only be 'before' or 'inner'")    
    elif env_dv == "demo":
        if pd_dv == "before":
            tr_id = "VTSC9215R"
        elif pd_dv == "inner":
            tr_id = "VTTC0081R"
        else:
            raise ValueError("pd_dv can only be 'before' or 'inner'")    
    else:
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "INQR_STRT_DT": inqr_strt_dt,
        "INQR_END_DT": inqr_end_dt,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "PDNO": pdno,
        "CCLD_DVSN": ccld_dvsn,
        "INQR_DVSN": inqr_dvsn,
        "INQR_DVSN_3": inqr_dvsn_3,
        "ORD_GNO_BRNO": ord_gno_brno,
        "ODNO": odno,
        "INQR_DVSN_1": inqr_dvsn_1,
        "CTX_AREA_FK100": FK100,
        "CTX_AREA_NK100": NK100
    }
    
    if excg_id_dvsn_cd is not None:
        params["EXCG_ID_DVSN_CD"] = excg_id_dvsn_cd
    
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 (array) 처리
        current_data1 = pd.DataFrame(res.getBody().output1)
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1
            
        # output2 (object) 처리
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
            return inquire_daily_ccld(
                env_dv, pd_dv, cano, acnt_prdt_cd, inqr_strt_dt, inqr_end_dt, 
                sll_buy_dvsn_cd, pdno, ccld_dvsn, inqr_dvsn, inqr_dvsn_3,
                ord_gno_brno, odno, inqr_dvsn_1, FK100, NK100, "N", 
                excg_id_dvsn_cd, dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame() 