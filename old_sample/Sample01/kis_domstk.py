
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 16:57:19 2023

@author: Administrator
"""
import kis_auth as kis

import time, copy
import requests
import json

import pandas as pd

from collections import namedtuple
from datetime import datetime
from pandas import DataFrame

#====|  [국내주식] 주문/계좌  |===========================================================================================================================

##############################################################################################
# [국내주식] 주문/계좌 > 주식주문(현금)[v1_국내주식-001]
##############################################################################################
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_order_cash(ord_dv="", itm_no="", qty=0, unpr=0, tr_cont="", FK100="", NK100="", dataframe=None):  # 국내주식주문 > 주식주문(현금)
    url = '/uapi/domestic-stock/v1/trading/order-cash'

    if ord_dv == "buy":
        tr_id = "TTTC0802U" # 주식 현금 매수 주문    [모의투자] VTTC0802U : 주식 현금 매수 주문
    elif ord_dv == "sell":
        tr_id = "TTTC0801U" # 주식 현금 매도 주문    [모의투자] VTTC0801U : 주식 현금 매도 주문
    else:
        print("매수현금/매도현금 구분 확인요망!!!")
        return None

    if itm_no == "":
        print("주문종목번호 확인요망!!!")
        return None

    if qty == 0:
        print("주문수량 확인요망!!!")
        return None

    if unpr == 0:
        print("주문단가 확인요망!!!")
        return None

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "PDNO": itm_no,                         # 종목코드(6자리) ETN의 경우, Q로 시작 (EX. Q500001)
        "ORD_DVSN": "00",                       # 주문구분 00:지정가, 01:시장가, 02:조건부지정가  나머지주문구분 API 문서 참조
        "ORD_QTY": str(int(qty)),               # 주문주식수
        "ORD_UNPR": str(int(unpr))              # 주문단가
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params, postFlag=True)
    if str(res.getBody().rt_cd) == "0":
        current_data = pd.DataFrame(res.getBody().output, index=[0])
        dataframe = current_data
    else:
        print(res.getBody().msg_cd + "," + res.getBody().msg1)
        #print(res.getErrorCode() + "," + res.getErrorMessage())
        dataframe = None

    return dataframe


##############################################################################################
# [국내주식] 주문/계좌 > 주식주문(정정취소)[v1_국내주식-003]
##############################################################################################
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_order_rvsecncl(ord_orgno="", orgn_odno="", ord_dvsn="", rvse_cncl_dvsn_cd="", ord_qty=0, ord_unpr=0, qty_all_ord_yn="", tr_cont="", dataframe=None):  # 국내주식주문 > 주식주문(정정취소)
    url = '/uapi/domestic-stock/v1/trading/order-rvsecncl'
    tr_id = "TTTC0803U"  # 주식 정정 취소 주문    [모의투자] VTTC0803U : 주식 정정 취소 주문

    if ord_orgno == "":
        print("주문조직번호 확인요망!!!")
        return None

    if orgn_odno == "":
        print("원주문번호 확인요망!!!")
        return None

    if ord_dvsn == "":
        print("주문구분 확인요망!!!")
        return None

    if not rvse_cncl_dvsn_cd in ["01","02"]:
        print("정정취소구분코드 확인요망!!!") # 정정:01. 취소:02
        return None

    if qty_all_ord_yn == "Y" and ord_qty > 0:
        print("잔량전부 취소/정정주문인 경우 주문수량 0 처리!!!")
        ord_qty = 0

    if qty_all_ord_yn == "N" and ord_qty == 0:
        print("취소/정정 수량 확인요망!!!")
        return None

    if rvse_cncl_dvsn_cd == "01" and ord_unpr == 0:
        print("주문단가 확인요망!!!")
        return None

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "KRX_FWDG_ORD_ORGNO": ord_orgno,        # 주문조직번호 API output의 odno(주문번호) 값 입력주문시 한국투자증권 시스템에서 채번된 주문조직번호
        "ORGN_ODNO": orgn_odno,                 # 주식일별주문체결조회 API output의 odno(주문번호) 값 입력주문시 한국투자증권 시스템에서 채번된 주문번호
        "ORD_DVSN": ord_dvsn,                   # 주문구분 00:지정가, 01:시장가, 02:조건부지정가  나머지주문구분 API 문서 참조
        "RVSE_CNCL_DVSN_CD": rvse_cncl_dvsn_cd, # 정정 : 01, 취소 : 02
        "ORD_QTY": str(int(ord_qty)),           # 주문주식수 	[잔량전부 취소/정정주문] "0" 설정 ( QTY_ALL_ORD_YN=Y 설정 ) [잔량일부 취소/정정주문] 취소/정정 수량
        "ORD_UNPR": str(int(ord_unpr)),         # 주문단가 	[정정] 정정주문 1주당 가격 [취소] "0" 설정
        "QTY_ALL_ORD_YN": qty_all_ord_yn        # 잔량전부주문여부 [정정/취소] Y : 잔량전부, N : 잔량일부
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params, postFlag=True)

    if str(res.getBody().rt_cd) == "0":
        current_data = pd.DataFrame(res.getBody().output, index=[0])
        dataframe = current_data
    else:
        print(res.getBody().msg_cd + "," + res.getBody().msg1)
        #print(res.getErrorCode() + "," + res.getErrorMessage())
        dataframe = None

    return dataframe


##############################################################################################
# [국내주식] 주문/계좌 > 주식정정취소가능주문조회[v1_국내주식-004]
##############################################################################################

# 국내주식주문 > 주식정정취소가능주문조회 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_inquire_psbl_rvsecncl_lst(tr_cont="", FK100="", NK100="", dataframe=None):  # 국내주식주문 > 주식정정취소가능주문조회
    url = '/uapi/domestic-stock/v1/trading/inquire-psbl-rvsecncl'
    tr_id = "TTTC8036R"

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "INQR_DVSN_1": "1",                     # 조회구분1(정렬순서)  0:조회순서, 1:주문순, 2:종목순
        "INQR_DVSN_2": "0",                     # 조회구분2 0:전체, 1:매도, 2:매수
        "CTX_AREA_FK100": FK100,                # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK100": NK100                 # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output2' is a dictionary that you want to convert to a DataFrame
    # current_data = res.getBody().output  # getBody() kis_auth.py 존재
    current_data = pd.DataFrame(res.getBody().output)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data

    tr_cont, FK100, NK100 = res.getHeader().tr_cont, res.getBody().ctx_area_fk100, res.getBody().ctx_area_nk100 # 페이징 처리 getHeader(), getBody() kis_auth.py 존재
    # print(tr_cont, FK100, NK100)

    if tr_cont == "D" or tr_cont == "E": # 마지막 페이지
        print("The End")
        current_data = pd.DataFrame(dataframe)
        dataframe = current_data
        return dataframe
    elif tr_cont == "F" or tr_cont == "M": # 다음 페이지 존재하는 경우 자기 호출 처리
        print('Call Next')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_inquire_psbl_rvsecncl_lst("N", FK100, NK100, dataframe)



##############################################################################################
# [국내주식] 주문/계좌 > 주식일별주문체결조회
##############################################################################################

# 국내주식주문 > 주식일별주문체결조회 Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
#        dv 기간구분 - 01:3개월 이내(TTTC8001R),  02:3개월 이전(CTSC9115R)
# Output: DataFrame (Option) output2 API 문서 참조 등
def get_inquire_daily_ccld_obj(dv="01", inqr_strt_dt=None, inqr_end_dt=None, tr_cont="", FK100="", NK100="", dataframe=None):  # 국내주식주문 > 주식일별주문체결조회
    url = '/uapi/domestic-stock/v1/trading/inquire-daily-ccld'

    if dv == "01":
        tr_id = "TTTC8001R"  # 01:3개월 이내 국내주식체결내역 (월단위 ex: 2024.04.25 이면 2024.01월~04월조회)
    else:
        tr_id = "CTSC9115R"  # 02:3개월 이전 국내주식체결내역 (월단위 ex: 2024.04.25 이면 2024.01월이전)

    if inqr_strt_dt is None:
        inqr_strt_dt = datetime.today().strftime("%Y%m%d")   # 시작일자 값이 없으면 현재일자
    if inqr_end_dt is None:
        inqr_end_dt  = datetime.today().strftime("%Y%m%d")   # 종료일자 값이 없으면 현재일자

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "INQR_STRT_DT": inqr_strt_dt,           # 조회시작일자
        "INQR_END_DT": inqr_end_dt,             # 조회종료일자
        "SLL_BUY_DVSN_CD": "00",                # 매도매수구분코드 00:전체 01:매도, 02:매수
        "INQR_DVSN": "01",                      # 조회구분(정렬순서)  00:역순, 01:정순
        "PDNO": "",                             # 종목번호(6자리)
        "CCLD_DVSN": "00",                      # 체결구분 00:전체, 01:체결, 02:미체결
        "ORD_GNO_BRNO": "",                     # 사용안함
        "ODNO": "",                             # 주문번호
        "INQR_DVSN_3": "00",                    # 조회구분3 00:전체, 01:현금, 02:융자, 03:대출, 04:대주
        "INQR_DVSN_1": "0",                     # 조회구분1 공란 : 전체, 1 : ELW, 2 : 프리보드
        "CTX_AREA_FK100": FK100,                # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK100": NK100                 # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output2' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output2, index=[0])

    dataframe = current_data

    return dataframe


# 주식일별주문체결조회 종목별 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
#        dv 기간구분 - 01:3개월 이내(TTTC8001R),  02:3개월 이전(CTSC9115R)
# Output: DataFrame (Option) output1 API 문서 참조 등
def get_inquire_daily_ccld_lst(dv="01", inqr_strt_dt="", inqr_end_dt="", tr_cont="", FK100="", NK100="", dataframe=None):  # 국내주식주문 > 주식일별주문체결조회
    url = '/uapi/domestic-stock/v1/trading/inquire-daily-ccld'

    if dv == "01":
        tr_id = "TTTC8001R"  # 01:3개월 이내 국내주식체결내역 (월단위 ex: 2024.04.25 이면 2024.01월~04월조회)
    else:
        tr_id = "CTSC9115R"  # 02:3개월 이전 국내주식체결내역 (월단위 ex: 2024.04.25 이면 2024.01월이전)

    if inqr_strt_dt == "":
        inqr_strt_dt = datetime.today().strftime("%Y%m%d")   # 시작일자 값이 없으면 현재일자
    if inqr_end_dt == "":
        inqr_end_dt  = datetime.today().strftime("%Y%m%d")   # 종료일자 값이 없으면 현재일자

    params = {
        "CANO": kis.getTREnv().my_acct, # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "INQR_STRT_DT": inqr_strt_dt, # 조회시작일자
        "INQR_END_DT": inqr_end_dt,   # 조회종료일자
        "SLL_BUY_DVSN_CD": "00", # 매도매수구분코드 00:전체 01:매도, 02:매수
        "INQR_DVSN": "01", # 조회구분(정렬순서)  00:역순, 01:정순
        "PDNO": "", # 종목번호(6자리)
        "CCLD_DVSN": "00",  #체결구분 00:전체, 01:체결, 02:미체결
        "ORD_GNO_BRNO": "", # 사용안함
        "ODNO": "", #주문번호
        "INQR_DVSN_3": "00", # 조회구분3 00:전체, 01:현금, 02:융자, 03:대출, 04:대주
        "INQR_DVSN_1": "", # 조회구분1 공란 : 전체, 1 : ELW, 2 : 프리보드
        "CTX_AREA_FK100": FK100, # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK100": NK100  # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params) # API 호출, kis_auth.py에 존재

    # Assuming 'output1' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output1)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data

    tr_cont, FK100, NK100 = res.getHeader().tr_cont, res.getBody().ctx_area_fk100, res.getBody().ctx_area_nk100 # 페이징 처리 getHeader(), getBody() kis_auth.py 존재
    # print(dv, tr_cont, FK100, NK100)

    if tr_cont == "D" or tr_cont == "E": # 마지막 페이지
        print("The End")
        return dataframe
    elif tr_cont == "F" or tr_cont == "M": # 다음 페이지 존재하는 경우 자기 호출 처리
        print('Call Next')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_inquire_daily_ccld_lst(dv, inqr_strt_dt, inqr_end_dt, "N", FK100, NK100, dataframe)


##############################################################################################
# [국내주식] 주문/계좌 > 주식잔고조회(현재잔고)
##############################################################################################


# 주식계좌잔고 Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output2 - 예수금총금액, 익일정산금액, 가수도정산금액, 전일매수금액, 금일매수금액, 총평가금액... 등
def get_inquire_balance_obj(tr_cont="", FK100="", NK100="", dataframe=None):  # 국내주식주문 > 주식잔고조회(현재잔고)
    url = '/uapi/domestic-stock/v1/trading/inquire-balance'
    tr_id = "TTTC8434R"

    params = {
        "CANO": kis.getTREnv().my_acct, # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "AFHR_FLPR_YN": "N", # 시간외단일가여부 Y:시간외단일가
        "OFL_YN": "", #오프라인여부 사용안함
        "INQR_DVSN": "00", # 00 : 전체
        "UNPR_DVSN": "01", # 단가구분 01:기본값
        "FUND_STTL_ICLD_YN": "N", # 펀드결제분포함여부 N:포함하지않음
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "00", # 00 : 전일매매포함, 01 : 전일매매미포함
        #"COST_ICLD_YN": "N",
        "CTX_AREA_FK100": FK100, # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK100": NK100  # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output2' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output2)  # getBody() kis_auth.py 존재

    dataframe = current_data

    return dataframe


# 주식계좌잔고 종목별 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output2 - 종목번호, 상품명(종목명), 매매구분명(매수매도구분), 전일매수수량 ... 등
def get_inquire_balance_lst(tr_cont="", FK100="", NK100="", dataframe=None):  # 국내주식주문 > 주식잔고조회(현재종목별 잔고)
    url = '/uapi/domestic-stock/v1/trading/inquire-balance'
    tr_id = "TTTC8434R"
    params = {
        "CANO": kis.getTREnv().my_acct, # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "AFHR_FLPR_YN": "N", # 시간외단일가여부 Y:시간외단일가
        "OFL_YN": "", #오프라인여부 사용안함
        "INQR_DVSN": "00", # 00 : 전체
        "UNPR_DVSN": "01", # 단가구분 01:기본값
        "FUND_STTL_ICLD_YN": "N", # 펀드결제분포함여부 N:포함하지않음
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "00", # 00 : 전일매매포함, 01 : 전일매매미포함
        #"COST_ICLD_YN": "N",
        "CTX_AREA_FK100": FK100, # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK100": NK100  # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params) # API 호출, kis_auth.py에 존재

    # Assuming 'output1' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output1)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data

    tr_cont, FK100, NK100 = res.getHeader().tr_cont, res.getBody().ctx_area_fk100, res.getBody().ctx_area_nk100 # 페이징 처리 getHeader(), getBody() kis_auth.py 존재
    print(tr_cont, FK100, NK100)

    if tr_cont == "D" or tr_cont == "E": # 마지막 페이지
        print("The End")
        return dataframe
    elif tr_cont == "F" or tr_cont == "M": # 다음 페이지 존재하는 경우 자기 호출 처리
        print('Call Next')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_inquire_balance_lst("N", FK100, NK100, dataframe)

##############################################################################################
# [국내주식] 주문/계좌 > 매수가능조회
##############################################################################################
# 국내주식주문 > 매수가능조회[v1_국내주식-007] List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output2 -
def get_inquire_psbl_order(pdno="", ord_unpr=0, tr_cont="", FK100="", NK100="", dataframe=None):  # 국내주식주문 > 매수가능조회
    url = '/uapi/domestic-stock/v1/trading/inquire-psbl-order'
    tr_id = "TTTC8908R"
    params = {
        "CANO": kis.getTREnv().my_acct,             # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod,     # 계좌상품코드 2자리
        "PDNO": pdno,                               # 상품번호
        "ORD_UNPR": ord_unpr,                       # 주문단가   1주당 가격 ※ 시장가(ORD_DVSN:01)로 조회 시, 공란으로 입력
        "ORD_DVSN": "00",                           # 주문구분 공란 시, 매수수량 없이 매수금액만 조회됨 00 : 지정가,01 : 시장가,02 : 조건부지정가,03 : 최유리지정가
        "CMA_EVLU_AMT_ICLD_YN": "N",                # CMA평가금액포함여부 Y : 포함, N : 포함하지 않음
        "OVRS_ICLD_YN": "Y"                         # 해외포함여부 Y : 포함, N : 포함하지 않음
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params) # API 호출, kis_auth.py에 존재

    # print(res.getBody())
    if res.isOK():
        # API 응답의 output 속성이 스칼라 값인지 확인
        output_data = res.getBody().output
        if not isinstance(output_data, list):
            # 스칼라 값이면 리스트로 감싸서 반환
            output_data = [output_data]

        # DataFrame 생성 시 index 매개변수를 추가하여 스칼라 값일 경우 처리
        # tdf = pd.DataFrame(output_data, index=[0])
        #cf1 = ['ord_psbl_cash', 'ruse_psbl_amt', 'fund_rpch_chgs', 'psbl_qty_calc_unpr', 'nrcvb_buy_amt', 'nrcvb_buy_qty', 'max_buy_amt', 'max_buy_qty', 'cma_evlu_amt', 'ovrs_re_use_amt_wcrc', 'ord_psbl_frcr_amt_wcrc']
        #cf2 = ['주문가능현금', '주문가능대용', '재사용가능금액', '펀드환매대금', '가능수량계산단가', '미수없는매수금액', '미수없는매수수량', '최대매수금액', '최대매수수량', 'CMA평가금액', '해외재사용금액원화', '주문가능외화금액원화']
        #tdf = tdf[cf1]
        #ren_dict = dict(zip(cf1, cf2))
        # return tdf.rename(columns=ren_dict)

        # DataFrame 생성 시 index 매개변수를 추가하여 스칼라 값일 경우 처리
        current_data = pd.DataFrame(output_data, index=[0])

        return current_data

    else:
        res.printError()
        return pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 주식예약주문[v1_국내주식-017]
##############################################################################################
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_order_resv(ord_dv="", itm_no="", qty=0, unpr=0, ord_dvsn_cd="", tr_cont="", FK100="", NK100="", dataframe=None):  # 국내주식주문 > 주식주문(현금)
    url = '/uapi/domestic-stock/v1/trading/order-resv'
    tr_id = "CTSC0008U"     # 국내예약매수입력, 주문예약매도입력

    if ord_dv == "buy":
        sll_buy_dvsn_cd = "02"      # 주식 예약 매수 주문
    elif ord_dv == "sell":
        sll_buy_dvsn_cd = "01"      # 주식 예약 매도 주문
    else:
        print("매도매수구분코드 확인요망!!!")
        return None

    if itm_no == "":
        print("주문종목번호 확인요망!!!")
        return None

    if qty == 0:
        print("주문수량 확인요망!!!")
        return None

    if unpr == 0:
        print("주문단가 확인요망!!!")
        return None

    if ord_dvsn_cd == "":
        print("주문구분코드 확인요망!!!")
        return None

    if unpr == 0:
        print("주문단가 확인요망!!!")
        return None

    ord_objt_cbcl_dvsn_cd = "10"  # [매도매수구분코드 01:매도/02:매수시 사용] 10 : 현금 이 아닌경우는 API문서 참조

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "PDNO": itm_no,                         # 종목코드(6자리) ETN의 경우, Q로 시작 (EX. Q500001)
        "ORD_QTY": str(int(qty)),               # 주문주식수
        "ORD_UNPR": str(int(unpr)),             # 주문단가
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,     # 매도매수구분코드 01 : 매도, 02 : 매수
        "ORD_DVSN_CD": "00",                    # 주문구분 00:지정가, 01:시장가, 02:조건부지정가, 05 : 장전 시간외
        "ORD_OBJT_CBLC_DVSN_CD": ord_objt_cbcl_dvsn_cd,  # [매도매수구분코드 01:매도/02:매수시 사용] 10 : 현금
        # [매도매수구분코드 01:매도시 사용] 12:주식담보대출, 14:대여상환, 21:자기융자신규, 22:유통대주신규, 23:유통융자신규,
        #                24:자기대주신규, 25:자기융자상환, 26:유통대주상환, 27:유통융자상환, 28:자기대주상환
        "RSVN_ORD_END_DT": ""	                # 예약주문종료일자 * (YYYYMMDD) 현재 일자보다 이후로 설정해야 함
                                                # * RSVN_ORD_END_DT(예약주문종료일자)를 안 넣으면 다음날 주문처리되고 예약주문은 종료됨
                                                # * RSVN_ORD_END_DT(예약주문종료일자)는 익영업일부터 달력일 기준으로 공휴일 포함하여 최대 30일이 되는 일자까지 입력 가능
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params, postFlag=True)
    if str(res.getBody().rt_cd) == "0":
        current_data = res.getBody().output  # getBody() kis_auth.py 존재
        dataframe = current_data
    else:
        print(res.getBody().msg_cd + "," + res.getBody().msg1)
        #print(res.getErrorCode() + "," + res.getErrorMessage())
        dataframe = None

    return dataframe



##############################################################################################
# [국내주식] 주문/계좌 > 주식예약주문취소[v1_국내주식-018,019]
##############################################################################################
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_order_resv_cncl(rsvn_ord_seq="", tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 주문/계좌 > 주식예약주문취소
    url = '/uapi/domestic-stock/v1/trading/order-resv-rvsecncl'
    tr_id = "CTSC0009U"  # 국내주식예약 취소주문

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "RSVN_ORD_SEQ": str(int(rsvn_ord_seq))  # 예약주문순번    [정정/취소]
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params, postFlag=True)

    if str(res.getBody().rt_cd) == "0":
        current_data = res.getBody().output  # getBody() kis_auth.py 존재
        dataframe = current_data
    else:
        print(res.getBody().msg_cd + "," + res.getBody().msg1)
        #print(res.getErrorCode() + "," + res.getErrorMessage())
        dataframe = None

    return dataframe



##############################################################################################
# [국내주식] 주문/계좌 > 주식예약주문정정[v1_국내주식-018,019]
# get_order_resv_rvse(rsvn_ord_seq="", pdno="", ord_qty=0, ord_unpr=0, ord_dvsn="", sll_buy_dvsn_cd=""):  # 국내주식주문 > 주식예약주문정정취소
##############################################################################################
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_order_resv_rvse(pdno="", ord_qty=0, ord_unpr=0, sll_buy_dvsn_cd="", ord_dvsn="", ord_objt_cblc_dvsn_cd="",
                        rsvn_ord_seq="", rsvn_ord_orgno="", rsvn_ord_ord_dt="", tr_cont="", FK100="", NK100="", dataframe=None ): # 국내주식주문 > 주식예약주문정정취소
    url = '/uapi/domestic-stock/v1/trading/order-resv-rvsecncl'
    tr_id = "CTSC0013U"  # 국내주식예약정정주문  * 모의투자 사용 불가

    if ord_qty == 0:
        print("주문주식수 확인요망!!!") #
        return None

    if ord_unpr == 0:
        print("주문단가 확인요망!!!") # 정정] 1주당 가격 * 장전 시간외, 시장가의 경우 1주당 가격을 공란으로 비우지 않음 "0"으로 입력 권고
        return None

    if sll_buy_dvsn_cd == "":
        print("매수매도구분코드 확인요망!!!") # [정정]  01 : 매도 02 : 매수
        return None

    if ord_dvsn == "":
        print("주문구분코드 확인요망!!!") # [정정] 00 : 지정가, 01 : 시장가, 02 : 조건부지정가, 05 : 장전 시간외
        return None

    ord_objt_cblc_dvsn_cd = "10"  # 주문대상잔고구분코드 기본값 10 : 현금으로 셋팅
    #if ord_objt_cblc_dvsn_cd == "":
    #    print("주문대상잔고구분코드!!!") # 10 : 현금, 12 : 주식담보대출, 14 : 대여상환, 21 : 자기융자신규
    #    return None

    if rsvn_ord_seq == "":
        print("예약주문번호 확인요망(rsvn_ord_seq)!!!")
        return None

    print(rsvn_ord_seq)
    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "PDNO": pdno,                           # 종목코드(6자리)
        "ORD_QTY": str(int(ord_qty)),           # 주문주식수 	[잔량전부 취소/정정주문] "0" 설정 ( QTY_ALL_ORD_YN=Y 설정 ) [잔량일부 취소/정정주문] 취소/정정 수량
        "ORD_UNPR": str(int(ord_unpr)),         # 주문단가 	[정정] 1주당 가격 * 장전 시간외, 시장가의 경우 1주당 가격을 공란으로 비우지 않음 "0"으로 입력 권고
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,     # 매도매수구분코드 [정정] 01 : 매도, 02 : 매수
        "ORD_DVSN_CD": ord_dvsn,                # 주문구분 	[정정]00 : 지정가, 01 : 시장가, 02 : 조건부지정가, 05 : 장전 시간외
        "ORD_OBJT_CBLC_DVSN_CD": ord_objt_cblc_dvsn_cd, # 주문대상잔고구분코드 	[정정]10 : 현금, 12 : 주식담보대출, 14 : 대여상환, 21 : 자기융자신규 나머지는 API문서 참조
        "LOAN_DT": "",                          # 대출일자       [정정] 입력필수아님
        "RSVN_ORD_END_DT": "",                  # 예약주문종료일자 [정정] 입력필수아님
        "CTAL_TLNO": "",                        # 연락전화번호    [정정] 입력필수아님
        "RSVN_ORD_SEQ": str(int(rsvn_ord_seq)), # 예약주문순번    [정정/취소] 입력필수
        "RSVN_ORD_ORGNO": "",                   # 예약주문조직번호 [정정/취소] 입력불필요
        "RSVN_ORD_ORD_DT": ""                   # 예약주문주문일자 [정정/취소] 입력불필요
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params, postFlag=True)

    if str(res.getBody().rt_cd) == "0":
        current_data = res.getBody().output  # getBody() kis_auth.py 존재
        print(res.getBody().msg_cd + "," + res.getBody().msg1)
        dataframe = current_data
    else:
        print(res.getBody().msg_cd + "," + res.getBody().msg1)
        #print(res.getErrorCode() + "," + res.getErrorMessage())
        dataframe = None

    return dataframe

##############################################################################################
# [국내주식] 주문/계좌 > 주식예약주문조회[v1_국내주식-020]
##############################################################################################
# [국내주식] 주문/계좌 > 주식예약주문조회[v1_국내주식-020] List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output2 -
def get_order_resv_ccnl(inqr_strt_dt=None, inqr_end_dt=None, ord_seq=0, tr_cont="", FK100="", NK100="", dataframe=None):  # 국내주식주문 > 매수가능조회
    url = '/uapi/domestic-stock/v1/trading/order-resv-ccnl'
    tr_id = "CTSC0004R"

    if inqr_strt_dt is None:
        inqr_strt_dt = datetime.today().strftime("%Y%m%d")   # 시작일자 값이 없으면 현재일자
    if inqr_end_dt is None:
        inqr_end_dt  = datetime.today().strftime("%Y%m%d")   # 종료일자 값이 없으면 현재일자

    params = {
        "RSVN_ORD_ORD_DT": inqr_strt_dt, # 예약주문시작일자
        "RSVN_ORD_END_DT": inqr_end_dt,  # 예약주문종료일자
        "RSVN_ORD_SEQ": ord_seq,         # 예약주문순번
        "TMNL_MDIA_KIND_CD": "00",       # 단말매체종류코드
        "CANO": kis.getTREnv().my_acct,  # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "PRCS_DVSN_CD": "0",             # 처리구분코드
        "CNCL_YN": "",                   # 오프라인여부 사용안함
        "PDNO": "",                      # 종목코드(6자리) (공백 입력 시 전체 조회)
        "SLL_BUY_DVSN_CD": "",           # 매도매수구분코드
        "CTX_AREA_FK200": FK100,         # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK200 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK200": NK100          # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK200 값 : 다음페이지 조회시(2번째부터)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params) # API 호출, kis_auth.py에 존재

    # Assuming 'output1' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data

    tr_cont, FK100, NK100 = res.getHeader().tr_cont, res.getBody().ctx_area_fk200, res.getBody().ctx_area_nk200 # 페이징 처리 getHeader(), getBody() kis_auth.py 존재
    print(tr_cont, FK100, NK100)

    if tr_cont == "D" or tr_cont == "E": # 마지막 페이지
        print("The End")
        return dataframe
    elif tr_cont == "F" or tr_cont == "M": # 다음 페이지 존재하는 경우 자기 호출 처리
        print('Call Next')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_order_resv_ccnl(inqr_strt_dt, inqr_end_dt, ord_seq, "N", FK100, NK100, dataframe)

##############################################################################################
# [국내주식] 주문/계좌 > 주식잔고조회_실현손익
##############################################################################################
# 주식잔고조회_실현손익 object DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output2 - 종목번호(상품번호), 종목명(상품명), 매매구분명, 전일매수수량, 전일매도수량, 금일매수수량... 등
def get_inquire_balance_rlz_pl_obj(tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 주문/계좌 > 주식잔고조회_실현손익 (잔고조회 Output2)
    url = '/uapi/domestic-stock/v1/trading/inquire-balance-rlz-pl'
    tr_id = "TTTC8494R"

    params = {
        "CANO": kis.getTREnv().my_acct,          # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod,  # 계좌상품코드 2자리
        "AFHR_FLPR_YN": "N",                     # 시간외단일가여부 Y:시간외단일가
        "OFL_YN": "",                            # 오프라인여부 사용안함
        "INQR_DVSN": "00",                       # 00 : 전체
        "UNPR_DVSN": "01",                       # 단가구분 01:기본값
        "FUND_STTL_ICLD_YN": "N",                # 펀드결제분포함여부 N:포함하지않음
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "00",                       # 00 : 전일매매포함, 01 : 전일매매미포함
        "COST_ICLD_YN": "N",
        "CTX_AREA_FK100": FK100, # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK100": NK100  # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    print(res.getBody())  # 오류 원인 확인 필요시 사용
    # Assuming 'Output2' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output2)  # getBody() kis_auth.py 존재

    dataframe = current_data

    return dataframe

# 주식잔고조회_실현손익 list DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output2 - 예수금총금액, 익일정산금액, 가수도정산금액, CMA평가금액, 전일매수금액, 금일매수금액 ... 등
def get_inquire_balance_rlz_pl_lst(tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 주문/계좌 > 주식잔고조회_실현손익 (보유주식내역 Output2)
    url = '/uapi/domestic-stock/v1/trading/inquire-balance-rlz-pl'
    tr_id = "TTTC8494R"

    params = {
        "CANO": kis.getTREnv().my_acct,          # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod,  # 계좌상품코드 2자리
        "AFHR_FLPR_YN": "N",                     # 시간외단일가여부 Y:시간외단일가
        "OFL_YN": "",                            # 오프라인여부 사용안함
        "INQR_DVSN": "00",                       # 00 : 전체
        "UNPR_DVSN": "01",                       # 단가구분 01:기본값
        "FUND_STTL_ICLD_YN": "N",                # 펀드결제분포함여부 N:포함하지않음
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "00",                       # 00 : 전일매매포함, 01 : 전일매매미포함
        "COST_ICLD_YN": "N",
        "CTX_AREA_FK100": FK100, # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK100": NK100  # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)  # API 호출, kis_auth.py에 존재

    # print(res.getBody())  # 오류 원인 확인 필요시 사용
    # Assuming 'output1' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output1)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data

    tr_cont, FK100, NK100 = res.getHeader().tr_cont, res.getBody().ctx_area_fk100, res.getBody().ctx_area_nk100  # 페이징 처리 getHeader(), getBody() kis_auth.py 존재
    print(tr_cont, FK100, NK100)

    if tr_cont == "D" or tr_cont == "E":  # 마지막 페이지
        print("The End")
        return dataframe
    elif tr_cont == "F" or tr_cont == "M":  # 다음 페이지 존재하는 경우 자기 호출 처리
        print('Call Next')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_inquire_balance_rlz_pl_lst("N", FK100, NK100, dataframe)


##############################################################################################
# [국내주식] 주문/계좌 > 신용매수가능조회
##############################################################################################
# 신용매수가능조회 object DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output1 - 주문가능현금, 주문가능대용, 재사용가능금액, 펀드환매대금, 가능수량계산단가, 미수없는매수금액... 등
def get_inquire_credit_psamount(pdno="", ord_unpr ="", tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 주문/계좌 > 신용매수가능조회
    url = '/uapi/domestic-stock/v1/trading/inquire-credit-psamount'
    tr_id = "TTTC8909R"

    params = {
        "CANO": kis.getTREnv().my_acct,          # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod,  # 계좌상품코드 2자리
        "PDNO": pdno,                            # 종목번호(상품번호)
        "ORD_UNPR": "",                          # 주문단가 1주당 가격 * 장전 시간외, 장후 시간외, 시장가의 경우 1주당 가격을 공란으로 비우지 않음 "0"으로 입력 권고
        "ORD_DVSN": "00",                        # 주문구분 00: 지정가
        "CRDT_TYPE": "21",                       # 신용유형 "":기본값
        "CMA_EVLU_AMT_ICLD_YN": "N",             # CMA평가금액포함여부
        "OVRS_ICLD_YN": "N"                      # 펀드결제분포함여부 N:포함하지않음
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    print(res.getBody())  # 오류 원인 확인 필요시 사용
    # Assuming 'Output2' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output1)  # getBody() kis_auth.py 존재

    dataframe = current_data

    return dataframe


##############################################################################################
# [국내주식] 주문/계좌 > 기간별매매손익현황조회
##############################################################################################
# 기간별매매손익현황조회 object DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output2 - 매도수량합계, 매도거래금액합계, 매도수수료합계, 매도제세금합계, 매도정산금액합계, 매수수량합계... 등
def get_inquire_period_trade_profit_obj(inqr_strt_dt=None, inqr_end_dt=None, tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 주문/계좌 > 기간별매매손익현황내역 (output2)
    url = '/uapi/domestic-stock/v1/trading/inquire-period-trade-profit'
    tr_id = "TTTC8715R"

    if inqr_strt_dt is None:
        inqr_strt_dt = datetime.today().strftime("%Y%m%d")   # 시작일자 값이 없으면 현재일자
    if inqr_end_dt is None:
        inqr_end_dt  = datetime.today().strftime("%Y%m%d")   # 종료일자 값이 없으면 현재일자

    params = {
        "CANO": kis.getTREnv().my_acct,          # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod,  # 계좌상품코드 2자리
        "SORT_DVSN": "00",                       # 정렬구분
        "PDNO": "",                              # 상품번호
        "INQR_STRT_DT": inqr_strt_dt,            # 조회시작일자
        "INQR_END_DT": inqr_end_dt,              # 조회종료일자
        "CBLC_DVSN": "00",                       # 잔고구분
        "CTX_AREA_FK100": FK100, # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK100": NK100  # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # print(res.getBody().output2)  # 오류 원인 확인 필요시 사용
    # Assuming 'Output2' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output2, index=[0])  # getBody() kis_auth.py 존재
    dataframe = current_data
    return dataframe

# 기간별매매손익현황조회 object DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output1 - 매매일자, 상품번호, 상품명, 매매구분명, 대출일자, 보유수량... 등
def get_inquire_period_trade_profit_lst(inqr_strt_dt=None, inqr_end_dt=None, tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 주문/계좌 > 기간별매매손익현황조회 (output1)
    url = '/uapi/domestic-stock/v1/trading/inquire-period-trade-profit'
    tr_id = "TTTC8715R"

    if inqr_strt_dt is None:
        inqr_strt_dt = datetime.today().strftime("%Y%m%d")   # 시작일자 값이 없으면 현재일자
    if inqr_end_dt is None:
        inqr_end_dt  = datetime.today().strftime("%Y%m%d")   # 종료일자 값이 없으면 현재일자

    params = {
        "CANO": kis.getTREnv().my_acct,          # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod,  # 계좌상품코드 2자리
        "SORT_DVSN": "00",                       # 정렬구분
        "PDNO": "",                              # 상품번호
        "INQR_STRT_DT": inqr_strt_dt,            # 조회시작일자
        "INQR_END_DT": inqr_end_dt,              # 조회종료일자
        "CBLC_DVSN": "00",                       # 잔고구분
        "CTX_AREA_FK100": FK100, # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK100": NK100  # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params) # API 호출, kis_auth.py에 존재

    # Assuming 'output1' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output1)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data

    tr_cont, FK100, NK100 = res.getHeader().tr_cont, res.getBody().ctx_area_fk100, res.getBody().ctx_area_nk100 # 페이징 처리 getHeader(), getBody() kis_auth.py 존재
    print(tr_cont, FK100, NK100)

    if tr_cont == "D" or tr_cont == "E": # 마지막 페이지
        print("The End")
        return dataframe
    elif tr_cont == "F" or tr_cont == "M": # 다음 페이지 존재하는 경우 자기 호출 처리
        print('Call Next')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_inquire_period_trade_profit_lst(inqr_strt_dt, inqr_end_dt, "N", FK100, NK100, dataframe)


##############################################################################################
# [국내주식] 주문/계좌 > 기간별손익일별합산조회
##############################################################################################
# 기간별매매손익현황조회 object DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output2 - 매도수량합계, 매도거래금액합계, 매도수수료합계, 매도제세금합계, 매도정산금액합계, 매수수량합계... 등
def get_inquire_period_profit_obj(inqr_strt_dt=None, inqr_end_dt=None, tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 주문/계좌 > 기간별손익일별합산조회 (output2)
    url = '/uapi/domestic-stock/v1/trading/inquire-period-profit'
    tr_id = "TTTC8708R"

    if inqr_strt_dt is None:
        inqr_strt_dt = datetime.today().strftime("%Y%m%d")   # 시작일자 값이 없으면 현재일자
    if inqr_end_dt is None:
        inqr_end_dt  = datetime.today().strftime("%Y%m%d")   # 종료일자 값이 없으면 현재일자

    params = {
        "CANO": kis.getTREnv().my_acct,          # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod,  # 계좌상품코드 2자리
        "INQR_DVSN": "00",                       # 조회구분
        "SORT_DVSN": "00",                       # 정렬구분
        "PDNO": "",                              # 상품번호
        "INQR_STRT_DT": inqr_strt_dt,            # 조회시작일자
        "INQR_END_DT": inqr_end_dt,              # 조회종료일자
        "CBLC_DVSN": "00",                       # 잔고구분
        "CTX_AREA_FK100": FK100, # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK100": NK100  # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # print(res.getBody().output2)  # 오류 원인 확인 필요시 사용
    # Assuming 'Output2' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output2, index=[0])  # getBody() kis_auth.py 존재
    dataframe = current_data
    return dataframe

# 기간별손익일별합산조회 object DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output1 - 매매일자, 상품번호, 상품명, 매매구분명, 대출일자, 보유수량... 등
def get_inquire_period_profit_lst(inqr_strt_dt=None, inqr_end_dt=None, tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 주문/계좌 > 기간별손익일별합산조회 (output1)
    url = '/uapi/domestic-stock/v1/trading/inquire-period-profit'
    tr_id = "TTTC8708R"

    if inqr_strt_dt is None:
        inqr_strt_dt = datetime.today().strftime("%Y%m%d")   # 시작일자 값이 없으면 현재일자
    if inqr_end_dt is None:
        inqr_end_dt  = datetime.today().strftime("%Y%m%d")   # 종료일자 값이 없으면 현재일자

    params = {
        "CANO": kis.getTREnv().my_acct,          # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod,  # 계좌상품코드 2자리
        "INQR_DVSN": "00",                       # 조회구분
        "SORT_DVSN": "00",                       # 정렬구분
        "PDNO": "",                              # 상품번호
        "INQR_STRT_DT": inqr_strt_dt,            # 조회시작일자
        "INQR_END_DT": inqr_end_dt,              # 조회종료일자
        "CBLC_DVSN": "00",                       # 잔고구분
        "CTX_AREA_FK100": FK100, # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK100": NK100  # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params) # API 호출, kis_auth.py에 존재

    # Assuming 'output1' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output1)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data

    tr_cont, FK100, NK100 = res.getHeader().tr_cont, res.getBody().ctx_area_fk100, res.getBody().ctx_area_nk100 # 페이징 처리 getHeader(), getBody() kis_auth.py 존재
    print(tr_cont, FK100, NK100)

    if tr_cont == "D" or tr_cont == "E": # 마지막 페이지
        print("The End")
        return dataframe
    elif tr_cont == "F" or tr_cont == "M": # 다음 페이지 존재하는 경우 자기 호출 처리
        print('Call Next')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_inquire_period_profit_lst(inqr_strt_dt, inqr_end_dt, "N", FK100, NK100, dataframe)

#====|  [국내주식] 기본시세  |============================================================================================================================

##############################################################################################
# [국내주식] 기본시세 > 주식현재가 시세
##############################################################################################
# 주식현재가 시세 Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output
def get_inquire_price(div_code="J", itm_no="", tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 기본시세 > 주식현재가 시세
    url = '/uapi/domestic-stock/v1/quotations/inquire-price'
    tr_id = "FHKST01010100" # 주식현재가 시세

    params = {
        "FID_COND_MRKT_DIV_CODE": div_code, # 시장 분류 코드 	J : 주식/ETF/ETN, W: ELW
        "FID_INPUT_ISCD": itm_no            # 	종목번호 (6자리) ETN의 경우, Q로 시작 (EX. Q500001)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output, index=[0])  # getBody() kis_auth.py 존재

    dataframe = current_data

    return dataframe

##############################################################################################
# [국내주식] 기본시세 > 주식현재가 체결  (최근체결 건 30건만 조회)
##############################################################################################
# 주식현재가 체결 Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output
def get_inquire_ccnl(div_code="J", itm_no="", tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 기본시세 > 주식현재가 체결
    url = '/uapi/domestic-stock/v1/quotations/inquire-ccnl'
    tr_id = "FHKST01010300"  # 주식현재가 체결

    params = {
        "FID_COND_MRKT_DIV_CODE": div_code, # 시장 분류 코드 	J : 주식/ETF/ETN, W: ELW
        "FID_INPUT_ISCD": itm_no            # 	종목번호 (6자리) ETN의 경우, Q로 시작 (EX. Q500001)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # print(res.getBody())  # 오류 원인 확인 필요시 사용
    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output)  # getBody() kis_auth.py 존재

    dataframe = current_data

    return dataframe


##############################################################################################
# [국내주식] 기본시세 > 주식현재가 일자별  (최근 30일만 조회)
# 주식현재가 일자별 API입니다. 일/주/월별 주가를 확인할 수 있으며 최근 30일(주,별)로 제한되어 있습니다.
##############################################################################################
# 주식현재가 일자별 Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output
def get_inquire_daily_price(div_code="J", itm_no="", period_code="D", adj_prc_code="1", tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 기본시세 > 주식현재가 일자별
    url = '/uapi/domestic-stock/v1/quotations/inquire-daily-price'
    tr_id = "FHKST01010400"  # 주식현재가 일자별

    params = {
        "FID_COND_MRKT_DIV_CODE": div_code, # 시장 분류 코드 	J : 주식/ETF/ETN, W: ELW
        "FID_INPUT_ISCD": itm_no,           # 종목번호 (6자리) ETN의 경우, Q로 시작 (EX. Q500001)
        "FID_PERIOD_DIV_CODE": period_code, # 기간분류코드 D : (일)최근 30거래일, W : (주)최근 30주, M : (월)최근 30개월
        "FID_ORG_ADJ_PRC": adj_prc_code     # 0 : 수정주가반영, 1 : 수정주가미반영 * 수정주가는 액면분할/액면병합 등 권리 발생 시 과거 시세를 현재 주가에 맞게 보정한 가격
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # print(res.getBody())  # 오류 원인 확인 필요시 사용
    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output)  # getBody() kis_auth.py 존재

    dataframe = current_data

    return dataframe


##############################################################################################
# [국내주식] 기본시세 > 주식현재가 호가/예상체결
# 주식현재가 호가 예상체결 API입니다. 매수 매도 호가를 확인하실 수 있습니다. 실시간 데이터를 원하신다면 웹소켓 API를 활용하세요.
##############################################################################################
# 주식현재가 일자별 Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output
def get_inquire_asking_price_exp_ccn(output_dv='1', div_code="J", itm_no="", tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 기본시세 > 주식현재가 호가/예상체결
    url = '/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn'
    tr_id = "FHKST01010200"  # 주식현재가 호가 예상체결

    params = {
        "FID_COND_MRKT_DIV_CODE": div_code, # 시장 분류 코드 	J : 주식/ETF/ETN, W: ELW
        "FID_INPUT_ISCD": itm_no           # 종목번호 (6자리) ETN의 경우, Q로 시작 (EX. Q500001)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # print(res.getBody())  # 오류 원인 확인 필요시 사용
    # Assuming 'output1' is a dictionary that you want to convert to a DataFrame
    if output_dv == "1":
        current_data = pd.DataFrame(res.getBody().output1, index=[0])  # 호가조회  * getBody() kis_auth.py 존재
    else:
        current_data = pd.DataFrame(res.getBody().output2, index=[0])  # 예상체결가조회

    dataframe = current_data

    return dataframe


##############################################################################################
# [국내주식] 기본시세 > 주식현재가 투자자 (최근 30일 조회)
# 주식현재가 투자자 API입니다. 개인, 외국인, 기관 등 투자 정보를 확인할 수 있습니다.
#
# [유의사항]
# - 외국인은 외국인(외국인투자등록 고유번호가 있는 경우)+기타 외국인을 지칭합니다.
# - 당일 데이터는 장 종료 후 제공됩니다.
##############################################################################################
# 주식현재가 투자자 Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output
def get_inquire_investor(div_code="J", itm_no="", tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 기본시세 > 주식현재가 투자자
    url = '/uapi/domestic-stock/v1/quotations/inquire-investor'
    tr_id = "FHKST01010900"  # 주식현재가 투자자

    params = {
        "FID_COND_MRKT_DIV_CODE": div_code, # 시장 분류 코드 	J : 주식/ETF/ETN, W: ELW
        "FID_INPUT_ISCD": itm_no           # 종목번호 (6자리) ETN의 경우, Q로 시작 (EX. Q500001)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # print(res.getBody())  # 오류 원인 확인 필요시 사용
    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output)  # 호가조회  * getBody() kis_auth.py 존재

    # @참고 전일대비 부호(prdy_vrss_sign) 1 : 상한, 2 : 상승, 3 : 보합, 4 : 하한, 5 : 하락
    dataframe = current_data

    return dataframe


##############################################################################################
# [국내주식] 기본시세 > 주식현재가 회원사
# 주식 현재가 회원사 API입니다. 회원사의 투자 정보를 확인할 수 있습니다..
##############################################################################################
# 주식현재가 회원사 Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output
def get_inquire_member(div_code="J", itm_no="", tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 기본시세 > 주식현재가 회원사
    url = '/uapi/domestic-stock/v1/quotations/inquire-member'
    tr_id = "FHKST01010600"  # 주식현재가 회원사

    params = {
        "FID_COND_MRKT_DIV_CODE": div_code, # 시장 분류 코드 	J : 주식/ETF/ETN, W: ELW
        "FID_INPUT_ISCD": itm_no           # 종목번호 (6자리) ETN의 경우, Q로 시작 (EX. Q500001)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # print(res.getBody())  # 오류 원인 확인 필요시 사용
    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output, index=[0])  # 호가조회  * getBody() kis_auth.py 존재

    dataframe = current_data

    return dataframe


##############################################################################################
# [국내주식] 기본시세 > 국내주식기간별시세(일/주/월/년)
# 국내주식기간별시세(일/주/월/년) API입니다.
# 실전계좌/모의계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능합니다.
##############################################################################################
# 국내주식기간별시세(일/주/월/년) Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output
def get_inquire_daily_itemchartprice(div_code="J", itm_no="", tr_cont="", inqr_strt_dt=None, inqr_end_dt=None, period_code="D", adj_prc="1", FK100="", NK100="", dataframe=None):  # [국내주식] 기본시세 > 국내주식기간별시세(일/주/월/년)
    url = '/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice'
    tr_id = "FHKST03010100"  # 주식현재가 회원사

    if inqr_strt_dt is None:
        inqr_strt_dt = (datetime.now()-timedelta(days=14)).strftime("%Y%m%d")   # 시작일자 값이 없으면 현재일자
    if inqr_end_dt is None:
        inqr_end_dt  = datetime.today().strftime("%Y%m%d")   # 종료일자 값이 없으면 현재일자

    print(inqr_strt_dt)
    print(inqr_end_dt)
    params = {
        "FID_COND_MRKT_DIV_CODE": div_code, # 시장 분류 코드 	J : 주식/ETF/ETN, W: ELW
        "FID_INPUT_ISCD": itm_no,           # 종목번호 (6자리) ETN의 경우, Q로 시작 (EX. Q500001)
        "FID_INPUT_DATE_1": inqr_strt_dt,   # 입력 날짜 (시작) 조회 시작일자 (ex. 20220501)
        "FID_INPUT_DATE_2": inqr_end_dt,    # 입력 날짜 (종료) 조회 종료일자 (ex. 20220530)
        "FID_PERIOD_DIV_CODE": period_code, # 기간분류코드 D:일봉, W:주봉, M:월봉, Y:년봉
        "FID_ORG_ADJ_PRC": adj_prc          # 수정주가 0:수정주가 1:원주가
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # print(res.getBody())  # 오류 원인 확인 필요시 사용
    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output1, index=[0])  # 호가조회  * getBody() kis_auth.py 존재

    dataframe = current_data

    return dataframe


##############################################################################################
# [국내주식] 기본시세 > 국내주식기간별시세(일/주/월/년)
# 국내주식기간별시세(일/주/월/년) API입니다.
# 실전계좌/모의계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능합니다.
##############################################################################################
# 국내주식기간별시세(일/주/월/년) Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output
def get_inquire_daily_itemchartprice(output_dv="1", div_code="J", itm_no="", inqr_strt_dt=None, inqr_end_dt=None, period_code="D", adj_prc="1", tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 기본시세 > 국내주식기간별시세(일/주/월/년)
    url = '/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice'
    tr_id = "FHKST03010100"  # 국내주식기간별시세

    if inqr_strt_dt is None:
        inqr_strt_dt = (datetime.now()-timedelta(days=100)).strftime("%Y%m%d")   # 시작일자 값이 없으면 현재일자
    if inqr_end_dt is None:
        inqr_end_dt  = datetime.today().strftime("%Y%m%d")   # 종료일자 값이 없으면 현재일자

    params = {
        "FID_COND_MRKT_DIV_CODE": div_code, # 시장 분류 코드 	J : 주식/ETF/ETN, W: ELW
        "FID_INPUT_ISCD": itm_no,           # 종목번호 (6자리) ETN의 경우, Q로 시작 (EX. Q500001)
        "FID_INPUT_DATE_1": inqr_strt_dt,   # 입력 날짜 (시작) 조회 시작일자 (ex. 20220501)
        "FID_INPUT_DATE_2": inqr_end_dt,    # 입력 날짜 (종료) 조회 종료일자 (ex. 20220530)
        "FID_PERIOD_DIV_CODE": period_code, # 기간분류코드 D:일봉, W:주봉, M:월봉, Y:년봉
        "FID_ORG_ADJ_PRC": adj_prc          # 수정주가 0:수정주가 1:원주가
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # print(res.getBody())  # 오류 원인 확인 필요시 사용
    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    if output_dv == "1":
        current_data = pd.DataFrame(res.getBody().output1, index=[0])  # 호가조회  * getBody() kis_auth.py 존재
    else:
        current_data = pd.DataFrame(res.getBody().output2)  # 호가조회  * getBody() kis_auth.py 존재

    dataframe = current_data

    return dataframe


##############################################################################################
# [국내주식] 기본시세 > 주식현재가 당일시간대별체결
# 기준시각(HHMMSS) 이전 체결 내역 30건 조회됨 (시간 미지정시 현재시각 기준)
##############################################################################################
# 주식현재가 당일시간대별체결 Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output
def get_inquire_time_itemconclusion(output_dv="1", div_code="J", itm_no="", inqr_hour=None, tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 기본시세 > 주식현재가 당일시간대별체결
    url = '/uapi/domestic-stock/v1/quotations/inquire-time-itemconclusion'
    tr_id = "FHPST01060000"  # 주식현재가 당일시간대별체결

    if inqr_hour is None:
        now = datetime.now()

        # 시, 분, 초 추출
        hour = now.hour
        minute = now.minute
        second = now.second

        # HHMMSS 형식으로 조합
        inqr_hour  = f"{hour:02d}{minute:02d}{second:02d}" # 현재 시간 가져오기

    params = {
        "FID_COND_MRKT_DIV_CODE": div_code, # 시장 분류 코드 	J : 주식/ETF/ETN, W: ELW
        "FID_INPUT_ISCD": itm_no,           # 종목번호 (6자리) ETN의 경우, Q로 시작 (EX. Q500001)
        "FID_INPUT_HOUR_1": inqr_hour       # 기준시간 (6자리; HH:MM:SS) ex) 155000 입력시 15시 50분 00초 기준 이전 체결 내역이 조회됨
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # print(res.getBody())  # 오류 원인 확인 필요시 사용
    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    if output_dv == "1":
        current_data = pd.DataFrame(res.getBody().output1, index=[0])  # 호가조회  * getBody() kis_auth.py 존재
    else:
        current_data = pd.DataFrame(res.getBody().output2)  # 호가조회  * getBody() kis_auth.py 존재

    dataframe = current_data

    return dataframe

##############################################################################################
# [국내주식] 기본시세 > 주식현재가 시간외일자별주가
# 기준시각(HHMMSS) 이전 체결 내역 30건 조회됨 (시간 미지정시 현재시각 기준)
##############################################################################################
# 주식현재가 시간외일자별주가 Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output
def get_inquire_daily_overtimeprice(output_dv="1", div_code="J", itm_no="", tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 기본시세 > 주식현재가 시간외일자별주가
    url = '/uapi/domestic-stock/v1/quotations/inquire-daily-overtimeprice'
    tr_id = "FHPST02320000"  # 주식현재가 시간외일자별주가

    params = {
        "FID_COND_MRKT_DIV_CODE": div_code, # 시장 분류 코드 	J : 주식/ETF/ETN, W: ELW
        "FID_INPUT_ISCD": itm_no           # 종목번호 (6자리) ETN의 경우, Q로 시작 (EX. Q500001)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # print(res.getBody())  # 오류 원인 확인 필요시 사용
    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    if output_dv == "1":
        current_data = pd.DataFrame(res.getBody().output1, index=[0])  # 시간외 현재가  * getBody() kis_auth.py 존재
    else:
        current_data = pd.DataFrame(res.getBody().output2)  # 일자별 시간외주가 최근 30일

    dataframe = current_data

    return dataframe

##############################################################################################
# [국내주식] 기본시세 > 주식당일분봉조회
# 실전계좌/모의계좌의 경우, 한 번의 호출에 최대 30건까지 확인 가능합니다.
##############################################################################################
# 주식당일분봉조회 Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output
def get_inquire_time_itemchartprice(output_dv="1", div_code="J", itm_no="", inqr_hour=None, incu_yn="N", tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 기본시세 > 주식당일분봉조회
    url = '/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice'
    tr_id = "FHKST03010200"  # 주식당일분봉조회

    if inqr_hour is None:
        now = datetime.now()

        # 시, 분, 초 추출
        hour = now.hour
        minute = now.minute
        second = now.second

        # HHMMSS 형식으로 조합
        inqr_hour  = f"{hour:02d}{minute:02d}{second:02d}" # 현재 시간 가져오기

    params = {
        "FID_ETC_CLS_CODE": "",              # 시장 분류 코드 	J : 주식/ETF/ETN, W: ELW
        "FID_COND_MRKT_DIV_CODE": div_code,  # 시장 분류 코드 	J : 주식/ETF/ETN, W: ELW
        "FID_INPUT_ISCD": itm_no,            # 종목번호 (6자리) ETN의 경우, Q로 시작 (EX. Q500001)
        "FID_INPUT_HOUR_1": inqr_hour,       # 조회대상(FID_COND_MRKT_DIV_CODE)에 따라 입력하는 값 상이
                                             # 종목(J)일 경우, 조회 시작일자(HHMMSS)
                                             #    ex) "123000" 입력 시 12시 30분 이전부터 1분 간격으로 조회
                                             # 업종(U)일 경우, 조회간격(초) (60 or 120 만 입력 가능)
                                             #    ex) "60" 입력 시 현재시간부터 1분간격으로 조회
                                             #        "120" 입력 시 현재시간부터 2분간격으로 조회
                                             # ※ FID_INPUT_HOUR_1 에 미래일시 입력 시에 현재가로 조회됩니다.
                                             #    ex) 오전 10시에 113000 입력 시에 오전 10시~11시30분 사이의 데이터가 오전 10시 값으로 조회됨
        "FID_PW_DATA_INCU_YN": incu_yn       # 과거 데이터 포함 여부(Y/N) * 업종(U) 조회시에만 동작하는 구분값 N : 당일데이터만 조회, Y : 이후데이터도 조회
                                             # (조회시점이 083000(오전8:30)일 경우 전일자 업종 시세 데이터도 같이 조회됨)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # print(res.getBody())  # 오류 원인 확인 필요시 사용
    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    if output_dv == "1":
        current_data = pd.DataFrame(res.getBody().output1, index=[0])  # 현재가  * getBody() kis_auth.py 존재
    else:
        current_data = pd.DataFrame(res.getBody().output2)  # 시간별 분봉

    dataframe = current_data

    return dataframe

##############################################################################################
# [국내주식] 기본시세 > 주식현재가 시세2
##############################################################################################
# 주식현재가 시세2 Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output
def get_inquire_daily_price_2(div_code="J", itm_no="", tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 기본시세 > 주식현재가 시세2
    url = '/uapi/domestic-stock/v1/quotations/inquire-price-2'
    tr_id = "FHPST01010000"  # 주식현재가 시세2

    params = {
        "FID_COND_MRKT_DIV_CODE": div_code, # 시장 분류 코드 	J : 주식/ETF/ETN, W: ELW
        "FID_INPUT_ISCD": itm_no           # 종목번호 (6자리) ETN의 경우, Q로 시작 (EX. Q500001)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # print(res.getBody())  # 오류 원인 확인 필요시 사용
    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output, index=[0])  # 시세2  * getBody() kis_auth.py 존재

    dataframe = current_data

    return dataframe

##############################################################################################
# [국내주식] 기본시세 > ETF/ETN 현재가
# 한국투자 HTS(eFriend Plus) > [0240] ETF/ETN 현재가 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다
##############################################################################################
# ETF/ETN 현재가 Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output
def get_quotations_inquire_price(div_code="J", itm_no="", tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 기본시세 > ETF/ETN 현재가
    url = '/uapi/etfetn/v1/quotations/inquire-price'
    tr_id = "FHPST02400000"  # ETF/ETN 현재가

    params = {
        "FID_COND_MRKT_DIV_CODE": div_code, # 시장 분류 코드 	J : 주식/ETF/ETN, W: ELW
        "FID_INPUT_ISCD": itm_no           # 종목번호 (6자리) ETN의 경우, Q로 시작 (EX. Q500001)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # print(res.getBody())  # 오류 원인 확인 필요시 사용
    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output, index=[0])  # 시세2  * getBody() kis_auth.py 존재

    dataframe = current_data

    return dataframe

##############################################################################################
# [국내주식] 기본시세 > NAV 비교추이(종목)
# 한국투자 HTS(eFriend Plus) > [0244] ETF/ETN 비교추이(NAV/IIV) 좌측 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
##############################################################################################
# NAV 비교추이(종목) Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output
def get_quotations_nav_comparison_trend(output_dv="1", div_code="J", itm_no="", tr_cont="", FK100="", NK100="", dataframe=None):  # [국내주식] 기본시세 > NAV 비교추이(종목)
    url = '/uapi/etfetn/v1/quotations/nav-comparison-trend'
    tr_id = "FHPST02440000"  # NAV 비교추이(종목)

    params = {
        "FID_COND_MRKT_DIV_CODE": div_code, # 시장 분류 코드 	J : 주식/ETF/ETN, W: ELW
        "FID_INPUT_ISCD": itm_no           # 종목번호 (6자리) ETN의 경우, Q로 시작 (EX. Q500001)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # print(res.getBody())  # 오류 원인 확인 필요시 사용
    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    if output_dv == "1":
        current_data = pd.DataFrame(res.getBody().output1, index=[0])  # 현재가  * getBody() kis_auth.py 존재
    else:
        current_data = pd.DataFrame(res.getBody().output2, index=[0])  # 시간별 분봉

    dataframe = current_data

    return dataframe



##############################################################################################
# [국내주식] 업종/기타 > 국내휴장일조회
# 국내휴장일조회 API입니다.
# 영업일, 거래일, 개장일, 결제일 여부를 조회할 수 있습니다.
# 주문을 넣을 수 있는지 확인하고자 하실 경우 개장일여부(opnd_yn)을 사용하시면 됩니다.
##############################################################################################
def get_quotations_ch_holiday(dt="", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/domestic-stock/v1/quotations/chk-holiday'
    tr_id = "CTCA0903R"  # 국내휴장일조회

    params = {
        "BASS_DT": dt, # 시장 분류 코드 	J : 주식/ETF/ETN, W: ELW
        "CTX_AREA_FK": FK100,  # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK": NK100  # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # print(res.getBody())  # 오류 원인 확인 필요시 사용
    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output)

    dataframe = current_data

    # 첫 번째 값만 선택하여 반환
    first_value = current_data.iloc[0] if not current_data.empty else None

    return first_value
