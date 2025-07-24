"""
Created on 20250112
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
# [국내주식] 주문/계좌 > 주식주문(현금)[v1_국내주식-001]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/trading/order-cash"

def order_cash(
    env_dv: str,  # 실전모의구분 (real:실전, demo:모의)
    ord_dv: str,  # 매도매수구분 (buy:매수, sell:매도)
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    pdno: str,  # 상품번호 (종목코드)
    ord_dvsn: str,  # 주문구분
    ord_qty: str,  # 주문수량
    ord_unpr: str,  # 주문단가
    excg_id_dvsn_cd: str,  # 거래소ID구분코드
    sll_type: str = "",  # 매도유형 (매도주문 시)
    cndt_pric: str = ""  # 조건가격
) -> pd.DataFrame:
    """
    국내주식주문(현금) API 입니다.

    ※ TTC0802U(현금매수) 사용하셔서 미수매수 가능합니다. 단, 거래하시는 계좌가 증거금40%계좌로 신청이 되어있어야 가능합니다. 
    ※ 신용매수는 별도의 API가 준비되어 있습니다.

    ※ ORD_QTY(주문수량), ORD_UNPR(주문단가) 등을 String으로 전달해야 함에 유의 부탁드립니다.

    ※ ORD_UNPR(주문단가)가 없는 주문은 상한가로 주문금액을 선정하고 이후 체결이되면 체결금액로 정산됩니다.

    ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)

    ※ 종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
    
    Args:
        env_dv (str): [필수] 실전모의구분 (real:실전, demo:모의)
        ord_dv (str): [필수] 매도매수구분 (buy:매수, sell:매도)
        cano (str): [필수] 종합계좌번호 (종합계좌번호)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (상품유형코드)
        pdno (str): [필수] 상품번호 (종목코드(6자리) , ETN의 경우 7자리 입력)
        ord_dvsn (str): [필수] 주문구분
        ord_qty (str): [필수] 주문수량
        ord_unpr (str): [필수] 주문단가
        excg_id_dvsn_cd (str): [필수] 거래소ID구분코드 (KRX)
        sll_type (str): 매도유형 (매도주문 시) (01:일반매도,02:임의매매,05:대차매도)
        cndt_pric (str): 조건가격 (스탑지정가호가 주문 시 사용)

    Returns:
        pd.DataFrame: 주식주문 결과 데이터
        
    Example:
        >>> df = order_cash(env_dv="demo", ord_dv="buy", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, pdno="005930", ord_dvsn="00", ord_qty="1", ord_unpr="70000", excg_id_dvsn_cd="KRX")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if env_dv == "" or env_dv is None:
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")
        
    if ord_dv == "" or ord_dv is None:
        raise ValueError("ord_dv is required (e.g. 'buy:매수, sell:매도')")
        
    if cano == "" or cano is None:
        raise ValueError("cano is required (e.g. '종합계좌번호')")
        
    if acnt_prdt_cd == "" or acnt_prdt_cd is None:
        raise ValueError("acnt_prdt_cd is required (e.g. '상품유형코드')")
        
    if pdno == "" or pdno is None:
        raise ValueError("pdno is required (e.g. '종목코드(6자리) , ETN의 경우 7자리 입력')")
        
    if ord_dvsn == "" or ord_dvsn is None:
        raise ValueError("ord_dvsn is required (e.g. '')")
        
    if ord_qty == "" or ord_qty is None:
        raise ValueError("ord_qty is required (e.g. '')")
        
    if ord_unpr == "" or ord_unpr is None:
        raise ValueError("ord_unpr is required (e.g. '')")
        
    if excg_id_dvsn_cd == "" or excg_id_dvsn_cd is None:
        raise ValueError("excg_id_dvsn_cd is required (e.g. 'KRX')")

    # tr_id 설정
    if env_dv == "real":
        if ord_dv == "sell":
            tr_id = "TTTC0011U"
        elif ord_dv == "buy":
            tr_id = "TTTC0012U"
        else:
            raise ValueError("ord_dv can only be sell or buy")
    elif env_dv == "demo":
        if ord_dv == "sell":
            tr_id = "VTTC0011U"
        elif ord_dv == "buy":
            tr_id = "VTTC0012U"
        else:
            raise ValueError("ord_dv can only be sell or buy")
    else:
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")

    params = {
        "CANO": cano,  # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "PDNO": pdno,  # 상품번호
        "ORD_DVSN": ord_dvsn,  # 주문구분
        "ORD_QTY": ord_qty,  # 주문수량
        "ORD_UNPR": ord_unpr,  # 주문단가
        "EXCG_ID_DVSN_CD": excg_id_dvsn_cd,  # 거래소ID구분코드
        "SLL_TYPE": sll_type,  # 매도유형
        "CNDT_PRIC": cndt_pric  # 조건가격
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params, postFlag=True)
    
    if res.isOK():
        current_data = pd.DataFrame([res.getBody().output])
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 