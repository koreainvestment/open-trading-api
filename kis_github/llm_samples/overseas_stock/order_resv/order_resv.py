"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""


import sys
from typing import Optional
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 예약주문접수[v1_해외주식-002]
##############################################################################################

# 상수 정의
API_URL = "/uapi/overseas-stock/v1/trading/order-resv"

def order_resv(
    env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
    ord_dv: str,  # [필수] 매도매수구분 (ex. usBuy:미국매수, usSell:미국매도, asia:아시아)
    cano: str,  # [필수] 종합계좌번호 (ex. 12345678)
    acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 01)
    pdno: str,  # [필수] 상품번호
    ovrs_excg_cd: str,  # [필수] 해외거래소코드 (ex. NASD:나스닥, NYSE:뉴욕, AMEX:아멕스, SEHK:홍콩, SHAA:상해, SZAA:심천, TKSE:일본, HASE:하노이, VNSE:호치민)
    ft_ord_qty: str,  # [필수] FT주문수량
    ft_ord_unpr3: str,  # [필수] FT주문단가3
    sll_buy_dvsn_cd: Optional[str] = "",  # 매도매수구분코드 (ex. 아시아인경우만 사용, 01:매도,02:매수)
    rvse_cncl_dvsn_cd: Optional[str] = "",  # 정정취소구분코드 (ex. 아시아인경우만 사용, 00:매도/매수)
    prdt_type_cd: Optional[str] = "",  # 상품유형코드 (ex. 아시아인경우만 사용)
    ord_svr_dvsn_cd: Optional[str] = "",  # 주문서버구분코드 (ex. 0)
    rsvn_ord_rcit_dt: Optional[str] = "",  # 예약주문접수일자 (ex. 아시아인경우만 사용)
    ord_dvsn: Optional[str] = "",  # 주문구분 (ex. 미국 매수/매도인 경우만 사용)
    ovrs_rsvn_odno: Optional[str] = "",  # 해외예약주문번호 (ex. 아이사인 경우만 사용)
    algo_ord_tmd_dvsn_cd: Optional[str] = ""  # 알고리즘주문시간구분코드 (ex. TWAP, VWAP 주문에서만 사용, 02로 고정)
) -> pd.DataFrame:
    """
    미국거래소 운영시간 외 미국주식을 예약 매매하기 위한 API입니다.

    * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
    https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp

    ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)

    * 아래 각 국가의 시장별 예약주문 접수 가능 시간을 확인하시길 바랍니다.

    미국 예약주문 접수시간
    1) 10:00 ~ 23:20 / 10:00 ~ 22:20 (서머타임 시)
    2) 주문제한 : 16:30 ~ 16:45 경까지 (사유 : 시스템 정산작업시간)
    3) 23:30 정규장으로 주문 전송 (서머타임 시 22:30 정규장 주문 전송)
    4) 미국 거래소 운영시간(한국시간 기준) : 23:30 ~ 06:00 (썸머타임 적용 시 22:30 ~ 05:00)

    홍콩 예약주문 접수시간
    1) 09:00 ~ 10:20 접수, 10:30 주문전송
    2) 10:40 ~ 13:50 접수, 14:00 주문전송

    중국 예약주문 접수시간
    1) 09:00 ~ 10:20 접수, 10:30 주문전송
    2) 10:40 ~ 13:50 접수, 14:00 주문전송

    일본 예약주문 접수시간
    1) 09:10 ~ 12:20 까지 접수, 12:30 주문전송

    베트남 예약주문 접수시간
    1) 09:00 ~ 11:00 까지 접수, 11:15 주문전송
    2) 11:20 ~ 14:50 까지 접수, 15:00 주문전송

    * 예약주문 유의사항
    1) 예약주문 유효기간 : 당일
    - 미국장 마감 후, 미체결주문은 자동취소
    - 미국휴장 시, 익 영업일로 이전
    (미국예약주문화면에서 취소 가능)
    2) 증거금 및 잔고보유 : 체크 안함
    3) 주문전송 불가사유
    - 매수증거금 부족: 수수료 포함 매수금액부족, 환전, 시세이용료 출금, 인출에 의한 증거금 부족
    - 기타 매수증거금 부족, 매도가능수량 부족, 주권변경 등 권리발생으로 인한 주문불가사유 발생
    4) 지정가주문만 가능
    * 단 미국 예약매도주문(TTTT3016U)의 경우, MOO(장개시시장가)로 주문 접수 가능
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        ord_dv (str): [필수] 매도매수구분 (ex. usBuy:미국매수, usSell:미국매도, asia:아시아)
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 01)
        pdno (str): [필수] 상품번호
        ovrs_excg_cd (str): [필수] 해외거래소코드 (ex. NASD:나스닥, NYSE:뉴욕, AMEX:아멕스, SEHK:홍콩, SHAA:상해, SZAA:심천, TKSE:일본, HASE:하노이, VNSE:호치민)
        ft_ord_qty (str): [필수] FT주문수량
        ft_ord_unpr3 (str): [필수] FT주문단가3
        sll_buy_dvsn_cd (Optional[str]): 매도매수구분코드 (ex. 아시아인경우만 사용, 01:매도,02:매수)
        rvse_cncl_dvsn_cd (Optional[str]): 정정취소구분코드 (ex. 아시아인경우만 사용, 00:매도/매수)
        prdt_type_cd (Optional[str]): 상품유형코드 (ex. 아시아인경우만 사용)
        ord_svr_dvsn_cd (Optional[str]): 주문서버구분코드 (ex. 0)
        rsvn_ord_rcit_dt (Optional[str]): 예약주문접수일자 (ex. 아시아인경우만 사용)
        ord_dvsn (Optional[str]): 주문구분 (ex. 미국 매수/매도인 경우만 사용)
        ovrs_rsvn_odno (Optional[str]): 해외예약주문번호 (ex. 아이사인 경우만 사용)
        algo_ord_tmd_dvsn_cd (Optional[str]): 알고리즘주문시간구분코드 (ex. TWAP, VWAP 주문에서만 사용, 02로 고정)

    Returns:
        pd.DataFrame: 해외주식 예약주문접수 결과 데이터
        
    Example:
        >>> df = order_resv(env_dv="real", ord_dv="usBuy", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, pdno="TSLA", ovrs_excg_cd="NASD", ft_ord_qty="1", ft_ord_unpr3="900")
        >>> print(df)
    """

    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")
    
    if ord_dv == "":
        raise ValueError("ord_dv is required (e.g. 'usBuy', 'usSell', 'asia')")
    
    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '01')")
    
    if pdno == "":
        raise ValueError("pdno is required")
    
    if ovrs_excg_cd == "":
        raise ValueError("ovrs_excg_cd is required (e.g. 'NASD', 'NYSE', 'AMEX', 'SEHK', 'SHAA', 'SZAA', 'TKSE', 'HASE', 'VNSE')")
    
    if ft_ord_qty == "":
        raise ValueError("ft_ord_qty is required")
    
    if ft_ord_unpr3 == "":
        raise ValueError("ft_ord_unpr3 is required")

    # tr_id 설정
    if env_dv == "real":
        if ord_dv == "usBuy":
            tr_id = "TTTT3014U"
        elif ord_dv == "usSell":
            tr_id = "TTTT3016U"
        elif ord_dv == "asia":
            tr_id = "TTTS3013U"
        else:
            raise ValueError("ord_dv can only be 'usBuy', 'usSell' or 'asia'")
    elif env_dv == "demo":
        if ord_dv == "usBuy":
            tr_id = "VTTT3014U"
        elif ord_dv == "usSell":
            tr_id = "VTTT3016U"
        elif ord_dv == "asia":
            tr_id = "VTTS3013U"
        else:
            raise ValueError("ord_dv can only be 'usBuy', 'usSell' or 'asia'")
    else:
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "FT_ORD_QTY": ft_ord_qty,
        "FT_ORD_UNPR3": ft_ord_unpr3
    }
    
    # 옵션 파라미터 추가
    if sll_buy_dvsn_cd:
        params["SLL_BUY_DVSN_CD"] = sll_buy_dvsn_cd
    if rvse_cncl_dvsn_cd:
        params["RVSE_CNCL_DVSN_CD"] = rvse_cncl_dvsn_cd
    if prdt_type_cd:
        params["PRDT_TYPE_CD"] = prdt_type_cd
    if ord_svr_dvsn_cd:
        params["ORD_SVR_DVSN_CD"] = ord_svr_dvsn_cd
    if rsvn_ord_rcit_dt:
        params["RSVN_ORD_RCIT_DT"] = rsvn_ord_rcit_dt
    if ord_dvsn:
        params["ORD_DVSN"] = ord_dvsn
    if ovrs_rsvn_odno:
        params["OVRS_RSVN_ODNO"] = ovrs_rsvn_odno
    if algo_ord_tmd_dvsn_cd:
        params["ALGO_ORD_TMD_DVSN_CD"] = algo_ord_tmd_dvsn_cd
    
    res = ka._url_fetch(API_URL, tr_id, "", params, postFlag=True)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output, index=[0])
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 