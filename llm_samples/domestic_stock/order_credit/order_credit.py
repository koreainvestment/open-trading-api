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
# [국내주식] 주문/계좌 > 주식주문(신용)[v1_국내주식-002]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/trading/order-credit"

def order_credit(
    ord_dv: str,           # 매수매도구분 (buy:매수, sell:매도)
    cano: str,             # 종합계좌번호 (12345678)
    acnt_prdt_cd: str,     # 계좌상품코드 (01)
    pdno: str,             # 상품번호 (123456)
    crdt_type: str,        # 신용유형 
    loan_dt: str,          # 대출일자
    ord_dvsn: str,         # 주문구분
    ord_qty: str,          # 주문수량
    ord_unpr: str,         # 주문단가
    excg_id_dvsn_cd: str = "",      # 거래소ID구분코드 (KRX:한국거래소, NXT:넥스트레이드, SOR:SOR)
    sll_type: str = "",             # 매도유형
    rsvn_ord_yn: str = "",          # 예약주문여부 (Y: 예약주문, N: 신용주문)
    emgc_ord_yn: str = "",          # 비상주문여부
    pgtr_dvsn: str = "",            # 프로그램매매구분
    mgco_aptm_odno: str = "",       # 운용사지정주문번호
    lqty_tr_ngtn_dtl_no: str = "",  # 대량거래협상상세번호
    lqty_tr_agmt_no: str = "",      # 대량거래협정번호
    lqty_tr_ngtn_id: str = "",      # 대량거래협상자Id
    lp_ord_yn: str = "",            # LP주문여부
    mdia_odno: str = "",            # 매체주문번호
    ord_svr_dvsn_cd: str = "",      # 주문서버구분코드
    pgm_nmpr_stmt_dvsn_cd: str = "", # 프로그램호가신고구분코드
    cvrg_slct_rson_cd: str = "",    # 반대매매선정사유코드
    cvrg_seq: str = "",             # 반대매매순번
    cndt_pric: str = ""             # 조건가격
) -> pd.DataFrame:
    """
    국내주식주문(신용) API입니다. 
    ※ 모의투자는 사용 불가합니다.

    ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)
    
    Args:
        ord_dv (str): [필수] 매수매도구분 (ex. buy:매수, sell:매도)
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 01)
        pdno (str): [필수] 상품번호 (ex. 123456)
        crdt_type (str): [필수] 신용유형 (ex. [매도] 22:유통대주신규, 24:자기대주신규, 25:자기융자상환, 27:유통융자상환 / [매수] 21:자기융자신규, 23:유통융자신규 , 26:유통대주상환, 28:자기대주상환)
        loan_dt (str): [필수] 대출일자 (ex. [신용매수] 오늘날짜(yyyyMMdd), [신용매도] 매도할 종목의 대출일자(yyyyMMdd))
        ord_dvsn (str): [필수] 주문구분 
        ord_qty (str): [필수] 주문수량
        ord_unpr (str): [필수] 주문단가
        excg_id_dvsn_cd (str): 거래소ID구분코드 (ex. KRX:한국거래소, NXT:넥스트레이드, SOR:SOR)
        sll_type (str): 매도유형
        rsvn_ord_yn (str): 예약주문여부 (ex. Y: 예약주문, N: 신용주문)
        emgc_ord_yn (str): 비상주문여부
        pgtr_dvsn (str): 프로그램매매구분
        mgco_aptm_odno (str): 운용사지정주문번호
        lqty_tr_ngtn_dtl_no (str): 대량거래협상상세번호
        lqty_tr_agmt_no (str): 대량거래협정번호
        lqty_tr_ngtn_id (str): 대량거래협상자Id
        lp_ord_yn (str): LP주문여부
        mdia_odno (str): 매체주문번호
        ord_svr_dvsn_cd (str): 주문서버구분코드
        pgm_nmpr_stmt_dvsn_cd (str): 프로그램호가신고구분코드
        cvrg_slct_rson_cd (str): 반대매매선정사유코드
        cvrg_seq (str): 반대매매순번
        cndt_pric (str): 조건가격

    Returns:
        pd.DataFrame: 주식주문(신용) 결과 데이터
        
    Example:
        >>> df = order_credit(ord_dv="buy", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, pdno="005930", crdt_type="21", loan_dt="20220810", ord_dvsn="00", ord_qty="1", ord_unpr="55000")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if ord_dv == "" or ord_dv is None:
        raise ValueError("ord_dv is required (e.g. 'buy:매수, sell:매도')")
    
    if cano == "" or cano is None:
        raise ValueError("cano is required (e.g. '12345678')")
    
    if acnt_prdt_cd == "" or acnt_prdt_cd is None:
        raise ValueError("acnt_prdt_cd is required (e.g. '01')")
    
    if pdno == "" or pdno is None:
        raise ValueError("pdno is required (e.g. '123456')")
    
    if crdt_type == "" or crdt_type is None:
        raise ValueError("crdt_type is required (e.g. '[매도] 22:유통대주신규, 24:자기대주신규, 25:자기융자상환, 27:유통융자상환 / [매수] 21:자기융자신규, 23:유통융자신규 , 26:유통대주상환, 28:자기대주상환')")
    
    if loan_dt == "" or loan_dt is None:
        raise ValueError("loan_dt is required (e.g. '[신용매수] 오늘날짜(yyyyMMdd), [신용매도] 매도할 종목의 대출일자(yyyyMMdd)')")
    
    if ord_dvsn == "" or ord_dvsn is None:
        raise ValueError("ord_dvsn is required")
    
    if ord_qty == "" or ord_qty is None:
        raise ValueError("ord_qty is required")
    
    if ord_unpr == "" or ord_unpr is None:
        raise ValueError("ord_unpr is required")

    # tr_id 설정
    if ord_dv == "buy":
        tr_id = "TTTC0052U"
    elif ord_dv == "sell":
        tr_id = "TTTC0051U"
    else:
        raise ValueError("ord_dv can only be buy or sell")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "CRDT_TYPE": crdt_type,
        "LOAN_DT": loan_dt,
        "ORD_DVSN": ord_dvsn,
        "ORD_QTY": ord_qty,
        "ORD_UNPR": ord_unpr
    }
    
    # 옵션 파라미터 추가
    if excg_id_dvsn_cd:
        params["EXCG_ID_DVSN_CD"] = excg_id_dvsn_cd
    if sll_type:
        params["SLL_TYPE"] = sll_type
    if rsvn_ord_yn:
        params["RSVN_ORD_YN"] = rsvn_ord_yn
    if emgc_ord_yn:
        params["EMGC_ORD_YN"] = emgc_ord_yn
    if pgtr_dvsn:
        params["PGTR_DVSN"] = pgtr_dvsn
    if mgco_aptm_odno:
        params["MGCO_APTM_ODNO"] = mgco_aptm_odno
    if lqty_tr_ngtn_dtl_no:
        params["LQTY_TR_NGTN_DTL_NO"] = lqty_tr_ngtn_dtl_no
    if lqty_tr_agmt_no:
        params["LQTY_TR_AGMT_NO"] = lqty_tr_agmt_no
    if lqty_tr_ngtn_id:
        params["LQTY_TR_NGTN_ID"] = lqty_tr_ngtn_id
    if lp_ord_yn:
        params["LP_ORD_YN"] = lp_ord_yn
    if mdia_odno:
        params["MDIA_ODNO"] = mdia_odno
    if ord_svr_dvsn_cd:
        params["ORD_SVR_DVSN_CD"] = ord_svr_dvsn_cd
    if pgm_nmpr_stmt_dvsn_cd:
        params["PGM_NMPR_STMT_DVSN_CD"] = pgm_nmpr_stmt_dvsn_cd
    if cvrg_slct_rson_cd:
        params["CVRG_SLCT_RSON_CD"] = cvrg_slct_rson_cd
    if cvrg_seq:
        params["CVRG_SEQ"] = cvrg_seq
    if cndt_pric:
        params["CNDT_PRIC"] = cndt_pric
    
    res = ka._url_fetch(API_URL, tr_id, "", params, postFlag=True)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output, index=[0])
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 