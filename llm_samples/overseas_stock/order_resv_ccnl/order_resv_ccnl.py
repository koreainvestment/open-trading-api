"""
Created on 20250601 
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
# [해외주식] 주문/계좌 > 해외주식 예약주문접수취소[v1_해외주식-004]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-stock/v1/trading/order-resv-ccnl"

def order_resv_ccnl(
    env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
    nat_dv: str,  # [필수] 국가구분 (ex. us:미국)
    cano: str,    # [필수] 종합계좌번호 (ex. 12345678)
    acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 01)
    rsvn_ord_rcit_dt: str,  # [필수] 해외주문접수일자
    ovrs_rsvn_odno: str     # [필수] 해외예약주문번호 (ex. 해외주식_예약주문접수 API Output ODNO(주문번호) 참고)
) -> pd.DataFrame:
    """
    접수된 미국주식 예약주문을 취소하기 위한 API입니다.
    (해외주식 예약주문접수 시 Return 받은 ODNO를 참고하여 API를 호출하세요.)

    * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
    https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp

    ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        nat_dv (str): [필수] 국가구분 (ex. us:미국)
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 01)
        rsvn_ord_rcit_dt (str): [필수] 해외주문접수일자
        ovrs_rsvn_odno (str): [필수] 해외예약주문번호 (ex. 해외주식_예약주문접수 API Output ODNO(주문번호) 참고)

    Returns:
        pd.DataFrame: 해외주식 예약주문접수취소 결과 데이터
        
    Example:
        >>> df = order_resv_ccnl(env_dv="real", nat_dv="us", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, rsvn_ord_rcit_dt="20220810", ovrs_rsvn_odno="0030008244")
        >>> print(df)
    """

    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")
    
    if nat_dv == "":
        raise ValueError("nat_dv is required (e.g. 'us')")
    
    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '01')")
    
    if rsvn_ord_rcit_dt == "":
        raise ValueError("rsvn_ord_rcit_dt is required")
    
    if ovrs_rsvn_odno == "":
        raise ValueError("ovrs_rsvn_odno is required")

    # tr_id 설정
    if env_dv == "real":
        if nat_dv == "us":
            tr_id = "TTTT3017U"
        else:
            raise ValueError("nat_dv can only be 'us'")
    elif env_dv == "demo":
        if nat_dv == "us":
            tr_id = "VTTT3017U"
        else:
            raise ValueError("nat_dv can only be 'us'")
    else:
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "RSVN_ORD_RCIT_DT": rsvn_ord_rcit_dt,
        "OVRS_RSVN_ODNO": ovrs_rsvn_odno
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params, postFlag=True)
    
    if res.isOK():
        # output은 object 자료형이므로 DataFrame으로 변환
        current_data = pd.DataFrame([res.getBody().output])
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 