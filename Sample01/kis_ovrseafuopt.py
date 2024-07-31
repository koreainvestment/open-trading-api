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


#====|  [해외선물옵션] 주문/계좌  |============================================================================================================================

##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 주문 [v1_해외선물-001]
# 해외선물옵션 주문 API 입니다.
#
# ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
#    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)
#
# ※ 종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
#    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
##############################################################################################
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseasfuopt_order(itm_no="", ord_dv="", dvsn="", qty=0, limt_pric=0, stop_pric=0, ccld_cd="6", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/trading/order'
    tr_id = "OTFM3001U"  # 선물옵션주문신규

    if itm_no == "":
        print("해외선물FX상품번호 확인요망!!!")
        return None

    if qty == 0:
        print("주문수량 확인요망!!!")
        return None

    if dvsn == "1" and limt_pric == 0:
        print("지정가주문인 경우 LIMIT주문가격 확인요망!!!")
        return None

    if dvsn == "3" and stop_pric == 0:
        print("STOP주문인 경우 STOP주문가격 확인요망!!!")
        return None

    if ord_dv not in ("01","02"):
        print("매수01/매도02 구분 확인요망!!!")
        return None

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "OVRS_FUTR_FX_PDNO": itm_no,            # 해외선물FX상품번호
        "SLL_BUY_DVSN_CD": ord_dv,              # 매도매수구분코드 01 : 매도, 02 : 매수
        "FM_LQD_USTL_CCLD_DT": "",              # FM청산미결제체결일자
        "FM_LQD_USTL_CCNO": "",                 # FM청산미결제체결번호
        "PRIC_DVSN_CD": dvsn,                   # 가격구분코드 1.지정, 2.시장, 3.STOP, 4.S/L
        "FM_LIMIT_ORD_PRIC": limt_pric,         # FMLIMIT주문가격 지정가인 경우 가격 입력 * 시장가, STOP주문인 경우, 빈칸("") 입력
        "FM_STOP_ORD_PRIC": stop_pric,          # FMSTOP주문가격 STOP 주문 가격 입력 * 시장가, 지정가인 경우, 빈칸("") 입력
        "FM_ORD_QTY": qty,                      # FM주문수량
        "FM_LQD_LMT_ORD_PRIC": "",              # FM청산LIMIT주문가격
        "FM_LQD_STOP_ORD_PRIC": "",             # FM청산STOP주문가격
        "CCLD_CNDT_CD": ccld_cd,                # 체결조건코드 일반적으로 6 (EOD, 지정가), GTD인 경우 5, 시장가인 경우만 2
        "CPLX_ORD_DVSN_CD": "0",                # 복합주문구분코드
        "ECIS_RSVN_ORD_YN": "N",                # 행사예약주문여부
        "FM_HDGE_ORD_SCRN_YN": "N"              # FM_HEDGE주문화면여부
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
# [해외선물옵션] 주문/계좌 > 해외선물옵션 정정취소주문 [v1_해외선물-002, 003]
##############################################################################################
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseasfuopt_order_rvsecncl(dvsn="", ord_dt="", orgn_odno="", limt_pric=0, stop_pric=0, lqd_limt_pric=0, lqd_stop_pric=0, tr_cont="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/trading/order-rvsecncl'

    if dvsn == "01": # 정정
        tr_id = "OTFM3002U"  # 해외선물옵션주문정정
    elif dvsn == "02": # 취소
        tr_id = "OTFM3003U"  # 해외선물옵션주문취소
    else:
        print("정정취소구분 dvsn 확인요망!!!")
        return None

    if ord_dt == "":
        print("원주문일자 확인요망!!!")
        return None

    if orgn_odno == "":
        print("원주문번호 확인요망!!!")
        return None


    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "ORGN_ORD_DT": ord_dt,                  # 원주문일자
        "ORGN_ODNO": orgn_odno,                 # 원주문번호 정정/취소시 주문번호(ODNO) 8자리를 문자열처럼 "0"을 포함해서 전송 (ex. ORGN_ODNO : 00360686)
        "FM_LIMIT_ORD_PRIC": limt_pric,         # LIMIT주문가격 (주문정정)시만 사용
        "FM_STOP_ORD_PRIC": stop_pric,          # STOP주문가격  (주문정정)시만 사용
        "FM_LQD_LMT_ORD_PRIC": lqd_limt_pric,   # 청산LIMIT주문가격 (주문정정)시만 사용
        "FM_LQD_STOP_ORD_PRIC": lqd_stop_pric,  # 청산STOP주문가격  (주문정정)시만 사용
        "FM_HDGE_ORD_SCRN_YN": "N",             # HEDGE주문화면여부 "N"
        "FM_MKPR_CVSN_YN": "N"                  # 시장가전환여부 (주문취소)시만 사용
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
# [해외선물옵션] 주문/계좌 > 해외선물옵션 당일주문내역조회 [v1_해외선물-004]
##############################################################################################
# 해외선물옵션 당일주문내역조회 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseasfuopt_inquire_ccld(ccld_dv="01", ord_dv="%%", fuop_dvsn="00", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/trading/inquire-ccld'
    tr_id = "OTFM3116R"

    t_cnt = 0

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "CCLD_NCCS_DVSN": ccld_dv,              # 체결미체결구분 01:전체,02:체결,03:미체결
        "SLL_BUY_DVSN_CD": ord_dv,              # 매도매수구분코드 %%:전체,01:매도,02:매수
        "FUOP_DVSN": fuop_dvsn,                 # 선물옵션구분 00:전체 / 01:선물 / 02:옵션
        "CTX_AREA_FK200": FK100,                # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK200": NK100                 # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    # current_data = res.getBody().output  # getBody() kis_auth.py 존재
    current_data = pd.DataFrame(res.getBody().output)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data

    tr_cont, FK100, NK100 = res.getHeader().tr_cont, res.getBody().ctx_area_fk200, res.getBody().ctx_area_nk200 # 페이징 처리 getHeader(), getBody() kis_auth.py 존재
    #print(tr_cont, FK100, NK100)

    if tr_cont == "D" or tr_cont == "E": # 마지막 페이지
        print("The End")
        current_data = pd.DataFrame(dataframe)
        cnt = current_data.count()

        # Initialize t_cnt if not already initialized
        try:
            t_cnt += cnt
        except NameError:
            t_cnt = cnt

        if t_cnt.empty:
            print("잔고내역 없음")
        else:
            print("잔고내역 있음")

        dataframe = current_data
        return dataframe
    elif tr_cont == "F" or tr_cont == "M": # 다음 페이지 존재하는 경우 자기 호출 처리
        print('Call Next')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_overseasfuopt_inquire_ccld(ccld_dv, ord_dv, fuop_dvsn, "N", FK100, NK100, dataframe)



##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 미결제내역조회(잔고) [v1_해외선물-005]
##############################################################################################
# 해외선물옵션 미결제내역조회(잔고) List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseasfuopt_inquire_unpd(fuop_dvsn="00", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/trading/inquire-unpd'
    tr_id = "OTFM1412R"

    t_cnt = 0

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "FUOP_DVSN": fuop_dvsn,                 # 선물옵션구분 00:전체 / 01:선물 / 02:옵션
        "CTX_AREA_FK100": FK100,                # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK100": NK100                 # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    # current_data = res.getBody().output  # getBody() kis_auth.py 존재
    current_data = pd.DataFrame(res.getBody().output)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data

    tr_cont, FK100, NK100 = res.getHeader().tr_cont, res.getBody().ctx_area_fk100, res.getBody().ctx_area_nk100 # 페이징 처리 getHeader(), getBody() kis_auth.py 존재
    #print(tr_cont, FK100, NK100)

    if tr_cont == "D" or tr_cont == "E": # 마지막 페이지
        print("The End")
        current_data = pd.DataFrame(dataframe)
        cnt = current_data.count()

        # Initialize t_cnt if not already initialized
        try:
            t_cnt += cnt
        except NameError:
            t_cnt = cnt

        if t_cnt.empty:
            print("잔고내역 없음")
        else:
            print("잔고내역 있음")

        dataframe = current_data
        return dataframe
    elif tr_cont == "F" or tr_cont == "M": # 다음 페이지 존재하는 경우 자기 호출 처리
        print('Call Next')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_overseasfuopt_inquire_unpd(fuop_dvsn, "N", FK100, NK100, dataframe)

##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 주문가능조회 [v1_해외선물-006]
##############################################################################################
# 해외선물옵션 주문가능조회 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseasfuopt_inquire_psamount(itm_no="", dvsn="", pric=0, ordyn="", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/trading/inquire-psamount'
    tr_id = "OTFM3304R"

    t_cnt = 0

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "OVRS_FUTR_FX_PDNO": itm_no,            # 해외선물FX상품번호
        "SLL_BUY_DVSN_CD": dvsn,                # 매도매수구분코드 01 : 매도 / 02 : 매수
        "FM_ORD_PRIC": pric,                    # 주문가격
        "ECIS_RSVN_ORD_YN": ordyn               # 행사예약주문여부
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params)

    if str(res.getBody().rt_cd) == "0":
        current_data = pd.DataFrame(res.getBody().output)
        dataframe = current_data
    else:
        print(res.getBody().msg_cd + "," + res.getBody().msg1)
        #print(res.getErrorCode() + "," + res.getErrorMessage())
        dataframe = None

    return dataframe


##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 기간계좌손익 일별[해외선물-010]
##############################################################################################
# 해외선물옵션 기간계좌손익 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseasfuopt_inquire_period_ccld(inqr_dvsn="", fr_dt="", to_dt="", crcy="%%%", fuop_dvsn="00", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/trading/inquire-period-ccld'
    tr_id = "OTFM3118R"

    t_cnt = 0

    if fr_dt =="":
        fr_dt = datetime.today().strftime("%Y%m%d")   # 기간손익 시작일자 값이 없으면 현재일자

    if to_dt =="":
        to_dt = datetime.today().strftime("%Y%m%d")   # 기간손익 종료일자 값이 없으면 현재일자

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "INQR_TERM_FROM_DT": fr_dt,             # 조회기간FROM일자
        "INQR_TERM_TO_DT": to_dt,               # 조회기간TO일자
        "CRCY_CD": crcy,                        # 통화코드 '%%% : 전체 TUS: TOT_USD / TKR: TOT_KRW KRW: 한국 / USD: 미국 EUR: EUR / HKD: 홍콩 CNY: 중국 / JPY: 일본'
        "WHOL_TRSL_YN": "N",                    # 전체환산여부
        "FUOP_DVSN": fuop_dvsn,                 # 선물옵션구분 00:전체 / 01:선물 / 02:옵션
        "CTX_AREA_FK200": FK100,                # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK200 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK200": NK100                 # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK200 값 : 다음페이지 조회시(2번째부터)
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    # current_data = res.getBody().output  # getBody() kis_auth.py 존재
    if inqr_dvsn == "01":
        current_data = pd.DataFrame(res.getBody().output1)
    else:
        current_data = pd.DataFrame(res.getBody().output2)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data

    tr_cont, FK100, NK100 = res.getHeader().tr_cont, res.getBody().ctx_area_fk200, res.getBody().ctx_area_nk200 # 페이징 처리 getHeader(), getBody() kis_auth.py 존재
    #print(tr_cont, FK100, NK100)

    if tr_cont == "D" or tr_cont == "E": # 마지막 페이지
        print("The End")
        current_data = pd.DataFrame(dataframe)
        cnt = current_data.count()

        # Initialize t_cnt if not already initialized
        try:
            t_cnt += cnt
        except NameError:
            t_cnt = cnt

        if t_cnt.empty:
            print("잔고내역 없음")
        else:
            print("잔고내역 있음")

        dataframe = current_data
        return dataframe
    elif tr_cont == "F" or tr_cont == "M": # 다음 페이지 존재하는 경우 자기 호출 처리
        print('Call Next')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_overseasfuopt_inquire_period_ccld(fr_dt, to_dt, crcy, fuop_dvsn, "N", FK100, NK100, dataframe)


##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 일별 체결내역[해외선물-011]
##############################################################################################
# 해외선물옵션 일별 체결내역 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseasfuopt_inquire_daily_ccld(fr_dt="", to_dt="", fuop_dvsn="00", crcy="%%%", dvsn="%%", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/trading/inquire-daily-ccld'
    tr_id = "OTFM3122R"

    t_cnt = 0

    if fr_dt =="":
        fr_dt = datetime.today().strftime("%Y%m%d")   # 기간손익 시작일자 값이 없으면 현재일자

    if to_dt =="":
        to_dt = datetime.today().strftime("%Y%m%d")   # 기간손익 종료일자 값이 없으면 현재일자

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "STRT_DT": fr_dt,                       # 시작일자
        "END_DT": to_dt,                        # 종료일자
        "FUOP_DVSN_CD": fuop_dvsn,              # 선물옵션구분코드 00:전체 / 01:선물 / 02:옵션
        "FM_PDGR_CD": "",                       # 상품군코드 	공란(Default)
        "CRCY_CD": crcy,                        # 통화코드 '%%% : 전체 TUS: TOT_USD / TKR: TOT_KRW KRW: 한국 / USD: 미국 EUR: EUR / HKD: 홍콩 CNY: 중국 / JPY: 일본 / VND: 베트남
        "FM_ITEM_FTNG_YN": "N",                 # 종목합산여부 "N"(Default)
        "SLL_BUY_DVSN_CD": dvsn,                # 매도매수구분코드 %%: 전체 / 01 : 매도 / 02 : 매수
        "CTX_AREA_FK200": FK100,                # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK200 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK200": NK100                 # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK200 값 : 다음페이지 조회시(2번째부터)
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    # current_data = res.getBody().output  # getBody() kis_auth.py 존재
    current_data = pd.DataFrame(res.getBody().output1)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data

    tr_cont, FK100, NK100 = res.getHeader().tr_cont, res.getBody().ctx_area_fk200, res.getBody().ctx_area_nk200 # 페이징 처리 getHeader(), getBody() kis_auth.py 존재
    #print(tr_cont, FK100, NK100)

    if tr_cont == "D" or tr_cont == "E": # 마지막 페이지
        print("The End")
        current_data = pd.DataFrame(dataframe)
        cnt = current_data.count()

        # Initialize t_cnt if not already initialized
        try:
            t_cnt += cnt
        except NameError:
            t_cnt = cnt

        if t_cnt.empty:
            print("잔고내역 없음")
        else:
            print("잔고내역 있음")

        dataframe = current_data
        return dataframe
    elif tr_cont == "F" or tr_cont == "M": # 다음 페이지 존재하는 경우 자기 호출 처리
        print('Call Next')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_overseasfuopt_inquire_daily_ccld(fr_dt, to_dt, fuop_dvsn, crcy, dvsn, "N", FK100, NK100, dataframe)


##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 예수금현황[해외선물-012]
##############################################################################################
# 해외선물옵션 예수금현황 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseasfuopt_inquire_deposit(crcy="TUS", inqr_dt="", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/trading/inquire-deposit'
    tr_id = "OTFM1411R"

    t_cnt = 0

    if inqr_dt =="":
        inqr_dt = datetime.today().strftime("%Y%m%d")   # 조회일자 값이 없으면 현재일자

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "CRCY_CD": crcy,                        # 통화코드 '%%% : 전체 TUS: TOT_USD / TKR: TOT_KRW KRW: 한국 / USD: 미국 EUR: EUR / HKD: 홍콩 CNY: 중국 / JPY: 일본 / VND: 베트남
        "INQR_DT": inqr_dt                      # 조회일자
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params)

    if str(res.getBody().rt_cd) == "0":
        current_data = pd.DataFrame(res.getBody().output)
        dataframe = current_data
    else:
        print(res.getBody().msg_cd + "," + res.getBody().msg1)
        #print(res.getErrorCode() + "," + res.getErrorMessage())
        dataframe = None

    return dataframe


##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 일별 주문내역[해외선물-013]
##############################################################################################
# 해외선물옵션 일별 주문내역 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseasfuopt_inquire_daily_order(fr_dt="", to_dt="", ccld_dvsn="01", dvsn="%%", fuop_dvsn="00", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/trading/inquire-daily-order'
    tr_id = "OTFM3120R"

    t_cnt = 0

    if fr_dt =="":
        fr_dt = datetime.today().strftime("%Y%m%d")   # 기간손익 시작일자 값이 없으면 현재일자

    if to_dt =="":
        to_dt = datetime.today().strftime("%Y%m%d")   # 기간손익 종료일자 값이 없으면 현재일자

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "STRT_DT": fr_dt,                       # 시작일자
        "END_DT": to_dt,                        # 종료일자
        "FM_PDGR_CD": "",                       # 상품군코드
        "CCLD_NCCS_DVSN": ccld_dvsn,            # 체결미체결구분 01:전체 / 02:체결 / 03:미체결
        "SLL_BUY_DVSN_CD": dvsn,                # 매도매수구분코드 %%전체 / 01 : 매도 / 02 : 매수
        "FUOP_DVSN": fuop_dvsn,                 # 선물옵션구분 00:전체 / 01:선물 / 02:옵션
        "CTX_AREA_FK200": FK100,                # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK200 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK200": NK100                 # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK200 값 : 다음페이지 조회시(2번째부터)
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    # current_data = res.getBody().output  # getBody() kis_auth.py 존재
    current_data = pd.DataFrame(res.getBody().output)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data

    tr_cont, FK100, NK100 = res.getHeader().tr_cont, res.getBody().ctx_area_fk200, res.getBody().ctx_area_nk200 # 페이징 처리 getHeader(), getBody() kis_auth.py 존재
    #print(tr_cont, FK100, NK100)

    if tr_cont == "D" or tr_cont == "E": # 마지막 페이지
        print("The End")
        current_data = pd.DataFrame(dataframe)
        cnt = current_data.count()

        # Initialize t_cnt if not already initialized
        try:
            t_cnt += cnt
        except NameError:
            t_cnt = cnt

        if t_cnt.empty:
            print("잔고내역 없음")
        else:
            print("잔고내역 있음")

        dataframe = current_data
        return dataframe
    elif tr_cont == "F" or tr_cont == "M": # 다음 페이지 존재하는 경우 자기 호출 처리
        print('Call Next')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_overseasfuopt_inquire_daily_order(fr_dt, to_dt, ccld_dvsn, dvsn, fuop_dvsn, "N", FK100, NK100, dataframe)


##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 기간계좌거래내역[해외선물-014]
##############################################################################################
# 해외선물옵션 기간계좌거래내역 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseasfuopt_inquire_period_trans(fr_dt="", to_dt="", trtype="1", crcy="%%%", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/trading/inquire-period-trans'
    tr_id = "OTFM3114R"

    t_cnt = 0

    if fr_dt =="":
        fr_dt = datetime.today().strftime("%Y%m%d")   # 기간손익 시작일자 값이 없으면 현재일자

    if to_dt =="":
        to_dt = datetime.today().strftime("%Y%m%d")   # 기간손익 종료일자 값이 없으면 현재일자

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "INQR_TERM_FROM_DT": fr_dt,             # 시작일자
        "INQR_TERM_TO_DT": to_dt,               # 종료일자
        "ACNT_TR_TYPE_CD": trtype,              # 계좌거래유형코드 1: 전체, 2:입출금 , 3: 결제
        "CRCY_CD": crcy,                        # 통화코드  %%% : 전체  TUS: TOT_USD / TKR: TOT_KRW / KRW: 한국 / USD: 미국 / EUR: EUR / HKD: 홍콩 / CNY: 중국 / JPY: 일본 / VND: 베트남
        "PWD_CHK_YN": "N",                      # 사용안함
        "CTX_AREA_FK100": FK100,                # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK200 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK100": NK100                 # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK200 값 : 다음페이지 조회시(2번째부터)
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    # current_data = res.getBody().output  # getBody() kis_auth.py 존재
    current_data = pd.DataFrame(res.getBody().output)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data

    tr_cont, FK100, NK100 = res.getHeader().tr_cont, res.getBody().ctx_area_fk100, res.getBody().ctx_area_nk100 # 페이징 처리 getHeader(), getBody() kis_auth.py 존재
    #print(tr_cont, FK100, NK100)

    if tr_cont == "D" or tr_cont == "E": # 마지막 페이지
        print("The End")
        current_data = pd.DataFrame(dataframe)
        cnt = current_data.count()

        # Initialize t_cnt if not already initialized
        try:
            t_cnt += cnt
        except NameError:
            t_cnt = cnt

        if t_cnt.empty:
            print("잔고내역 없음")
        else:
            print("잔고내역 있음")

        dataframe = current_data
        return dataframe
    elif tr_cont == "F" or tr_cont == "M": # 다음 페이지 존재하는 경우 자기 호출 처리
        print('Call Next')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_overseasfuopt_inquire_period_trans(fr_dt, to_dt, trtype, crcy, "N", FK100, NK100, dataframe)

##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 예수금현황[해외선물-012]
##############################################################################################
# 해외선물옵션 예수금현황 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseasfuopt_inquire_margin_detail(crcy="TUS", inqr_dt="", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/trading/margin-detail'
    tr_id = "OTFM3115R"

    t_cnt = 0

    if inqr_dt =="":
        inqr_dt = datetime.today().strftime("%Y%m%d")   # 조회일자 값이 없으면 현재일자

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "CRCY_CD": crcy,                        # 통화코드 '%%% : 전체 TUS: TOT_USD / TKR: TOT_KRW KRW: 한국 / USD: 미국 EUR: EUR / HKD: 홍콩 CNY: 중국 / JPY: 일본 / VND: 베트남
        "INQR_DT": inqr_dt                      # 조회일자
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params)

    if str(res.getBody().rt_cd) == "0":
        current_data = pd.DataFrame(res.getBody().output, index=[0])
        dataframe = current_data
    else:
        print(res.getBody().msg_cd + "," + res.getBody().msg1)
        #print(res.getErrorCode() + "," + res.getErrorMessage())
        dataframe = None

    return dataframe


#====|  [해외선물옵션] 기본시세  |============================================================================================================================

##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물종목상세 [v1_해외선물-008]
# (중요) 해외선물옵션시세 출력값을 해석하실 때 ffcode.mst(해외선물종목마스터 파일)에 있는 sCalcDesz(계산 소수점) 값을 활용하셔야 정확한 값을 받아오실 수 있습니다.
#
# - ffcode.mst(해외선물종목마스터 파일) 다운로드 방법 2가지
#   1) 한국투자증권 Github의 파이썬 샘플코드를 사용하여 mst 파일 다운로드 및 excel 파일로 정제
#      https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/overseas_future_code.py
#
#   2) 혹은 포럼 - FAQ - 종목정보 다운로드 - 해외선물옵션 클릭하셔서 ffcode.mst(해외선물종목마스터 파일)을 다운로드 후
#      Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외선물옵션정보.h)를 참고하여 해석
#
# - 소수점 계산 시, ffcode.mst(해외선물종목마스터 파일)의 sCalcDesz(계산 소수점) 값 참고
#   EX) ffcode.mst 파일의 sCalcDesz(계산 소수점) 값
#        품목코드 6A 계산소수점 -4 → 시세 6882.5 수신 시 0.68825 로 해석
#        품목코드 GC 계산소수점 -1 → 시세 19225 수신 시 1922.5 로 해석
#
# [참고자료]
# ※ 종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
#    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
##############################################################################################
def get_overseas_fuopt_stock_detail(itm_no="", tr_cont="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/quotations/stock-detail'
    tr_id = "HHDFC55010100" # 해외선물종목상세

    params = {
        "SRS_CD": itm_no          # 종목코드
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output1, index=[0])

    dataframe = current_data

    return dataframe

##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물종목현재가 [v1_해외선물-009]
# (중요) 해외선물옵션시세 출력값을 해석하실 때 ffcode.mst(해외선물종목마스터 파일)에 있는 sCalcDesz(계산 소수점) 값을 활용하셔야 정확한 값을 받아오실 수 있습니다.
#
# - ffcode.mst(해외선물종목마스터 파일) 다운로드 방법 2가지
#   1) 한국투자증권 Github의 파이썬 샘플코드를 사용하여 mst 파일 다운로드 및 excel 파일로 정제
#      https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/overseas_future_code.py
#
#   2) 혹은 포럼 - FAQ - 종목정보 다운로드 - 해외선물옵션 클릭하셔서 ffcode.mst(해외선물종목마스터 파일)을 다운로드 후
#      Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외선물옵션정보.h)를 참고하여 해석
#
# - 소수점 계산 시, ffcode.mst(해외선물종목마스터 파일)의 sCalcDesz(계산 소수점) 값 참고
#   EX) ffcode.mst 파일의 sCalcDesz(계산 소수점) 값
#        품목코드 6A 계산소수점 -4 → 시세 6882.5 수신 시 0.68825 로 해석
#        품목코드 GC 계산소수점 -1 → 시세 19225 수신 시 1922.5 로 해석
#
# [참고자료]
# ※ 종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
#    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
##############################################################################################
def get_overseas_fuopt_inquire_price(itm_no="", tr_cont="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/quotations/inquire-price'
    tr_id = "HHDFC55010000" # 해외선물종목현재가

    params = {
        "SRS_CD": itm_no          # 종목코드
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output1, index=[0])

    dataframe = current_data

    return dataframe


##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물 분봉조회[해외선물-016]
# 해외선물분봉조회 API입니다. 반드시 아래 호출방법을 확인하시고 호출 사용하시기 바랍니다.
#
# ※ 해외선물분봉조회 조회 방법
# params
# . START_DATE_TIME: 공란 입력 ("")
# . CLOSE_DATE_TIME: 조회일자 입력 ("20231214")
# . QRY_CNT: 120 입력 시, 가장 최근 분봉 120건 조회,
#                 240 입력 시, 240 이전 분봉 ~ 120 이전 분봉 조회
#                 360 입력 시, 360 이전 분봉 ~ 240 이전 분봉 조회
# . QRY_TP: 처음조회시, 공백 입력
#               다음조회시, P 입력
# . INDEX_KEY: 처음조회시, 공백 입력
#                   다음조회시, 이전 조회 응답의 output2 > index_key 값 입력
#
# * 따라서 분봉데이터를 기간별로 수집하고자 하실 경우 QRY_TP, INDEX_KEY 값을 이용하시면서 다음조회하시면 됩니다.
##############################################################################################
def get_overseas_fuopt_inquire_time_futurechartprice(itm_no="", exch="", st_dt="", ed_dt="", dvsn="", cnt="", gap="", idx="", tr_cont="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/quotations/inquire-time-futurechartprice'
    tr_id = "HHDFC55020400" # 해외선물 분봉조회

    params = {
        "SRS_CD": itm_no,           # 종목코드
        "EXCH_CD": exch,            # 거래소코드
        "START_DATE_TIME": st_dt,   # 조회시작일시
        "CLOSE_DATE_TIME": ed_dt,   # 조회종료일시
        "QRY_TP": dvsn,             # 조회구분
        "QRY_CNT": cnt,             # 요청개수
        "QRY_GAP": gap,             # 묶음개수
        "INDEX_KEY": idx            # 이전조회KEY
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)  # API 호출

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output1)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data

    tr_cont, idx = res.getHeader().tr_cont, res.getBody().output2['index_key']  # 페이징 처리 getHeader(), getBody() kis_auth.py 존재

    if idx == "":
        idx = "99991231" # 다음페이지 값이 없으면 종료 처리를 위해 임의 날자 값 셋팅

    date1 = datetime.strptime(idx[:8], '%Y%m%d') # 응답 index_key 다음날자 값 날자형 변환
    date2 = datetime.strptime(st_dt,   '%Y%m%d') # 조회시작일자 날자형 변환
    date3 = datetime.strptime(ed_dt,   '%Y%m%d') # 조회종료일자 날자형 변환
    #print(date1, date2, date3)

    if date1 >= date2 and date1 <= date3:  # 조회시작일자 ~ 조회종료일자 까지 다음페이지 조회
        print('Call Next ( ' + idx[:8] + ' )')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_overseas_fuopt_inquire_time_futurechartprice(itm_no, exch, st_dt, ed_dt, "P", cnt, gap, idx, tr_cont, dataframe)
    else:  # 조회시작일자 ~ 조회종료일자 이외 날자인경우 종료 처리
        #print("The End")
        print('The End ( ' + idx[:8] + ' )')
        return dataframe


##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물 체결추이(주간)[해외선물-017]
# 해외선물옵션 체결추이(주간) API입니다.
# 한국투자 HTS(eFriend Force) > [5502] 해외선물옵션 체결추이 화면에서 "주간" 선택 시 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
##############################################################################################
def get_overseas_fuopt_weekly_ccnl(itm_no="", exch="", st_dt="", ed_dt="", dvsn="Q", cnt="40", gap="", idx="", tr_cont="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/quotations/weekly-ccnl'
    tr_id = "HHDFC55020000" # 체결추이(주간)

    params = {
        "SRS_CD": itm_no,           # 종목코드
        "EXCH_CD": exch,            # 거래소코드
        "START_DATE_TIME": st_dt,   # 조회시작일시
        "CLOSE_DATE_TIME": ed_dt,   # 조회종료일시
        "QRY_TP": dvsn,             # 조회구분
        "QRY_CNT": cnt,             # 요청개수
        "QRY_GAP": gap,             # 묶음개수
        "INDEX_KEY": idx            # 이전조회KEY
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)  # API 호출

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output2)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data

    tr_cont, idx = res.getHeader().tr_cont, res.getBody().output1['index_key']  # 페이징 처리 getHeader(), getBody() kis_auth.py 존재

    if idx == "":
        idx = "99991231"  # 다음페이지 값이 없으면 종료 처리를 위해 임의 날자 값 셋팅

    date1 = datetime.strptime(str(idx),  '%Y%m%d') # 응답 index_key 다음날자 값 날자형 변환
    date2 = datetime.strptime(str(st_dt),'%Y%m%d') # 조회시작일자 날자형 변환
    date3 = datetime.strptime(str(ed_dt),'%Y%m%d') # 조회종료일자 날자형 변환
    #print(date1, date2, date3)

    if date1 >= date2 and date1 <= date3:  # 조회시작일자 ~ 조회종료일자 까지 다음페이지 조회
        print('Call Next ( ' + idx[:8] + ' )')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_overseas_fuopt_weekly_ccnl(itm_no, exch, st_dt, ed_dt, "P", cnt, gap, idx, tr_cont, dataframe)
    else:  # 조회시작일자 ~ 조회종료일자 이외 날자인경우 종료 처리
        #print("The End")
        print('The End ( ' + idx[:8] + ' )')
        return dataframe


##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물 체결추이(일간)[해외선물-018]
# 해외선물옵션 체결추이(일간) API입니다.
# 한국투자 HTS(eFriend Force) > [5502] 해외선물옵션 체결추이 화면에서 "일간" 선택 시 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
##############################################################################################
def get_overseas_fuopt_daily_ccnl(itm_no="", exch="", st_dt="", ed_dt="", dvsn="Q", cnt="40", gap="", idx="", tr_cont="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/quotations/daily-ccnl'
    tr_id = "HHDFC55020100" # 체결추이(일간)

    params = {
        "SRS_CD": itm_no,           # 종목코드
        "EXCH_CD": exch,            # 거래소코드
        "START_DATE_TIME": st_dt,   # 조회시작일시
        "CLOSE_DATE_TIME": ed_dt,   # 조회종료일시
        "QRY_TP": dvsn,             # 조회구분
        "QRY_CNT": cnt,             # 요청개수
        "QRY_GAP": gap,             # 묶음개수
        "INDEX_KEY": idx            # 이전조회KEY
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)  # API 호출

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output2)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data.loc[current_data.data_date.between(st_dt, ed_dt)] # 조회일자 범위만큼 추출하여 dataframe에 셋팅

    tr_cont, idx = res.getHeader().tr_cont, res.getBody().output1['index_key']  # 페이징 처리 getHeader(), getBody() kis_auth.py 존재

    if idx == "":
        idx = "99991231"  # 다음페이지 값이 없으면 종료 처리를 위해 임의 날자 값 셋팅

    date1 = datetime.strptime(str(idx),  '%Y%m%d') # 응답 index_key 다음날자 값 날자형 변환
    date2 = datetime.strptime(str(st_dt),'%Y%m%d') # 조회시작일자 날자형 변환
    date3 = datetime.strptime(str(ed_dt),'%Y%m%d') # 조회종료일자 날자형 변환
    #print(date1, date2, date3)

    if date1 >= date2 and date1 <= date3:  # 조회시작일자 ~ 조회종료일자 까지 다음페이지 조회
        print('Call Next ( ' + idx[:8] + ' )')
        time.sleep(0.05)
        return get_overseas_fuopt_daily_ccnl(itm_no, exch, st_dt, ed_dt, "P", cnt, gap, idx, tr_cont, dataframe)
    else:  # 조회시작일자 ~ 조회종료일자 이외 날자인경우 종료 처리
        #print("The End")
        print('The End ( ' + idx[:8] + ' )')
        return dataframe


##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물 체결추이(틱)[해외선물-019]
# 해외선물옵션 체결추이(틱) API입니다.
# 한국투자 HTS(eFriend Force) > [5502] 해외선물옵션 체결추이 화면에서 "Tick" 선택 시 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
##############################################################################################
def get_overseas_fuopt_tick_ccnl(itm_no="", exch="", st_dt="", ed_dt="", dvsn="Q", cnt="40", gap="", idx="", tr_cont="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/quotations/tick-ccnl'
    tr_id = "HHDFC55020200" # 체결추이(틱)

    if st_dt =="":
        st_dt = datetime.today().strftime("%Y%m%d")   # 주문내역조회 시작일자 값이 없으면 현재일자

    if ed_dt =="":
        ed_dt = datetime.today().strftime("%Y%m%d")   # 주문내역조회 종료일자 값이 없으면 현재일자

    params = {
        "SRS_CD": itm_no,           # 종목코드
        "EXCH_CD": exch,            # 거래소코드
        "START_DATE_TIME": st_dt,   # 조회시작일시
        "CLOSE_DATE_TIME": ed_dt,   # 조회종료일시
        "QRY_TP": dvsn,             # 조회구분
        "QRY_CNT": cnt,             # 요청개수
        "QRY_GAP": gap,             # 묶음개수
        "INDEX_KEY": idx            # 이전조회KEY
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)  # API 호출

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output2)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data.loc[current_data.data_date.between(ed_dt, ed_dt)] # 조회일자 범위만큼 추출하여 dataframe에 셋팅
        #dataframe = current_data  # 조회일자 범위만큼 추출하여 dataframe에 셋팅

    tr_cont, idx = res.getHeader().tr_cont, res.getBody().output1['index_key']  # 페이징 처리 getHeader(), getBody() kis_auth.py 존재

    if idx == "":
        idx = "99991231"  # 다음페이지 값이 없으면 종료 처리를 위해 임의 날자 값 셋팅

    date1 = datetime.strptime(str(idx[:8]),  '%Y%m%d') # 응답 index_key 다음날자 값 날자형 변환
    date2 = datetime.strptime(str(st_dt),'%Y%m%d') # 조회시작일자 날자형 변환
    date3 = datetime.strptime(str(ed_dt),'%Y%m%d') # 조회종료일자 날자형 변환
    #print(date1, date2, date3)

    if date1 == date3:  # 조회시작일자 ~ 조회종료일자 까지 다음페이지 조회
        print('Call Next ( ' + idx + ' )')
        time.sleep(0.05)
        return get_overseas_fuopt_tick_ccnl(itm_no, exch, st_dt, ed_dt, "P", cnt, gap, idx, tr_cont, dataframe)
    else:  # 조회시작일자 ~ 조회종료일자 이외 날자인경우 종료 처리
        #print("The End")
        print('The End ( ' + idx + ' )')
        return dataframe

##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물 체결추이(월간)[해외선물-020]
# 해외선물옵션 체결추이(월간) API입니다.
# 한국투자 HTS(eFriend Force) > [5502] 해외선물옵션 체결추이 화면에서 "월간" 선택 시 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
##############################################################################################
def get_overseas_fuopt_monthly_ccnl(itm_no="", exch="", st_dt="", ed_dt="", dvsn="Q", cnt="40", gap="", idx="", tr_cont="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/quotations/monthly-ccnl'
    tr_id = "HHDFC55020300" # 체결추이(월간)

    params = {
        "SRS_CD": itm_no,           # 종목코드
        "EXCH_CD": exch,            # 거래소코드
        "START_DATE_TIME": st_dt,   # 조회시작일시
        "CLOSE_DATE_TIME": ed_dt,   # 조회종료일시
        "QRY_TP": dvsn,             # 조회구분
        "QRY_CNT": cnt,             # 요청개수
        "QRY_GAP": gap,             # 묶음개수
        "INDEX_KEY": idx            # 이전조회KEY
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)  # API 호출

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output2)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data  #.loc[current_data.data_date.between(st_dt, ed_dt)] # 조회일자 범위만큼 추출하여 dataframe에 셋팅

    tr_cont, idx = res.getHeader().tr_cont, res.getBody().output1['index_key']  # 페이징 처리 getHeader(), getBody() kis_auth.py 존재

    if idx == "":
        idx = "99991231"  # 다음페이지 값이 없으면 종료 처리를 위해 임의 날자 값 셋팅

    date1 = datetime.strptime(str(idx),  '%Y%m%d') # 응답 index_key 다음날자 값 날자형 변환
    date2 = datetime.strptime(str(st_dt),'%Y%m%d') # 조회시작일자 날자형 변환
    date3 = datetime.strptime(str(ed_dt),'%Y%m%d') # 조회종료일자 날자형 변환
    #print(date1, date2, date3)

    if date1 >= date2 and date1 <= date3:  # 조회시작일자 ~ 조회종료일자 까지 다음페이지 조회
        print('Call Next ( ' + idx[:8] + ' )')
        time.sleep(0.05)
        return get_overseas_fuopt_monthly_ccnl(itm_no, exch, st_dt, ed_dt, "P", cnt, gap, idx, tr_cont, dataframe)
    else:  # 조회시작일자 ~ 조회종료일자 이외 날자인경우 종료 처리
        #print("The End")
        print('The End ( ' + idx[:8] + ' )')
        return dataframe


##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물 호가 [해외선물-031]
# (중요) 해외선물옵션시세 출력값을 해석하실 때 ffcode.mst(해외선물종목마스터 파일)에 있는 sCalcDesz(계산 소수점) 값을 활용하셔야 정확한 값을 받아오실 수 있습니다.
#
# - ffcode.mst(해외선물종목마스터 파일) 다운로드 방법 2가지
#   1) 한국투자증권 Github의 파이썬 샘플코드를 사용하여 mst 파일 다운로드 및 excel 파일로 정제
#      https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/overseas_future_code.py
#
#   2) 혹은 포럼 - FAQ - 종목정보 다운로드 - 해외선물옵션 클릭하셔서 ffcode.mst(해외선물종목마스터 파일)을 다운로드 후
#      Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외선물옵션정보.h)를 참고하여 해석
#
# - 소수점 계산 시, ffcode.mst(해외선물종목마스터 파일)의 sCalcDesz(계산 소수점) 값 참고
#   EX) ffcode.mst 파일의 sCalcDesz(계산 소수점) 값
#        품목코드 6A 계산소수점 -4 → 시세 6882.5 수신 시 0.68825 로 해석
#        품목코드 GC 계산소수점 -1 → 시세 19225 수신 시 1922.5 로 해석
#
# [참고자료]
# ※ 종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
#    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
##############################################################################################
def get_overseas_fuopt_inquire_asking_price(itm_no="", tr_cont="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/quotations/inquire-asking-price'
    tr_id = "HHDFC86000000" # 해외선물호가

    params = {
        "SRS_CD": itm_no          # 종목코드
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output1, index=[0])

    dataframe = current_data

    return dataframe


##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물 상품기본정보 [해외선물-023]
# 해외선물옵션 상품기본정보 API입니다.
# QRY_CNT에 SRS_CD 요청 개수 입력, SRS_CD_01 ~SRS_CD_32 까지 최대 32건의 상품코드 추가 입력하여 해외선물옵션 상품기본정보 확인이 가능합니다. (아래 Example 참고)
##############################################################################################
def get_overseas_fuopt_search_contract_detail(cnt="1", itm_no01="", tr_cont="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/quotations/search-contract-detail'
    tr_id = "HHDFC55200000" # 해외선물 상품기본정보

    params = {
        "QRY_CNT": cnt,         # 요청개수
        "SRS_CD_01": itm_no01   # 종목코드
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output2)

    dataframe = current_data

    return dataframe


##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물 장운영시간 [해외선물-030]
# 해외선물 장운영시간 API입니다.
# 한국투자 HTS(eFriend Force) > [6773] 해외선물 장운영시간 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
##############################################################################################
def get_overseas_fuopt_market_time(clas="", excg="CME", opt="%", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/quotations/market-time'
    tr_id = "OTFM2229R" # 해외선물 장운영시간

    t_cnt = 0

    params = {
        "FM_PDGR_CD": "",           # 상품군코드 ""
        "FM_CLAS_CD": clas,         # 클래스코드 공백(전체), 001(통화), 002(금리), 003(지수), 004(농산물),005(축산물),006(금속),007(에너지)
        "FM_EXCG_CD": excg,         # 거래소코드 CME(CME), EUREX(EUREX), HKEx(HKEx), ICE(ICE), SGX(SGX), OSE(OSE), ASX(ASX),
                                    #          CBOE(CBOE), MDEX(MDEX), NYSE(NYSE),BMF(BMF),FTX(FTX), HNX(HNX), ETC(기타)'
        "OPT_YN": opt,              # 옵션여부 %(전체), N(선물), Y(옵션)
        "CTX_AREA_FK200": FK100,    # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK200": NK100     # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    # current_data = res.getBody().output  # getBody() kis_auth.py 존재
    current_data = pd.DataFrame(res.getBody().output)

    print(current_data)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data.loc[current_data.fm_pdgr_cd != ""]  # 상품군코드(fm_pdgr_cd) 값이 없는 경우 제외

    tr_cont, FK100, NK100 = res.getHeader().tr_cont, res.getBody().ctx_area_fk200, res.getBody().ctx_area_nk200  # 페이징 처리 getHeader(), getBody() kis_auth.py 존재
    # print(tr_cont, FK100, NK100)

    if tr_cont == "D" or tr_cont == "E":  # 마지막 페이지
        print("The End")
        current_data = pd.DataFrame(dataframe)
        cnt = current_data.count()

        # Initialize t_cnt if not already initialized
        try:
            t_cnt += cnt
        except NameError:
            t_cnt = cnt

        if t_cnt.empty:
            print("잔고내역 없음")
        else:
            print("잔고내역 있음")

        dataframe = current_data
        return dataframe
    elif tr_cont == "F" or tr_cont == "M":  # 다음 페이지 존재하는 경우 자기 호출 처리
        print('Call Next')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_overseas_fuopt_market_time(clas, excg, opt, "N", FK100, NK100, dataframe)



##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물 미결제추이 [해외선물-029]
# 해외선물 미결제추이 API입니다.
# 한국투자 HTS(eFriend Force) > [5503] 해외선물 미결제약정추이 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
#
# ※ 해외선물 투자자별 미결제약정 추이 자료설명
# 1. 해외선물 투자자별 미결제약정 자료는 미국상품선물위원회(CFTC)에서 매주 1회 발표하고 있습니다.
# 2. 기준일은 매주 화요일이며, 발표는 매주 금요일 15:30 (미국동부표준시)에 하며, 당사는 매주 토요일 아침에 자료를 업데이트하고 있습니다.
# 3. 활용방법 : CFTC에서 발표하는 미결제약점 동향자료는 각 선물시장의 투기자금 동향을 파약하는데 용이하며, 특히, 상품시장에서 유용하게 활용할 수 있습니다.
# 4. 주요항목 설명
# . 투기거래자 : 실물보유 또는 보유중인 실물에 대한 헤지목적이 아닌 가격변동에 따른 이익을 목적으로 거래하는 고객으로 주로 투자은행, 자산운용사, 헤지펀드, 개인투자자등임
# ﻿﻿. 헤지거래자 : 실물보유 또는 보유중인 실물에 대한 헤지목적으로 거래하는 고객으로 주로 일반기업, 생산업체, 원자재공급업체등임.
# ﻿﻿. 보고누락분 : 시장전체 미결제약정과 투기거래자와 헤지거래자 보고분 합계와의 차이로 투자주제가 확인안된 거래임.
# . 투자자 : 최종거래고객 기준이 아닌 거래소 회원 단위 기준임.
# 5. CFTC 홈페이지: http://www.cftc.gov/index.htm
##############################################################################################
def get_overseas_fuopt_investor_unpd_trend(iscd="CL", dt="", kbn="", ctskey="", tr_cont="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/quotations/investor-unpd-trend'
    tr_id = "HHDDB95030000" # 해외선물 상품기본정보

    params = {
        "PROD_ISCD": iscd,  # 상품 (GE, ZB, ZF,ZN,ZT), 금속(GC, PA, PL,SI, HG),
                            # 농산물(CC, CT,KC, OJ, SB, ZC,ZL, ZM, ZO, ZR, ZS, ZW),
                            # 에너지(CL, HO, NG, WBS), 지수(ES, NQ, TF, YM, VX),
                            # 축산물(GF, HE, LE), 통화(6A, 6B, 6C, 6E, 6J, 6N, 6S, DX)
        "BSOP_DATE": dt,    # 일자 기준일(ex)20240513)
        "UPMU_GUBUN": kbn,  # 구분 	0(수량), 1(증감)
        "CTS_KEY": ctskey   # "" 사용안함
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output2)

    dataframe = current_data

    return dataframe



##############################################################################################
# [해외선물옵션] 기본시세 > 해외옵션 호가 [해외선물-033]
# 해외옵션 호가 API입니다.
# 한국투자 HTS(eFriend Force) > [5501] 해외선물옵션 현재가 화면 의 "왼쪽 상단 현재가" 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
##############################################################################################
def get_overseas_fuopt_opt_asking_price(dv="01", itm_no="", tr_cont="", dataframe=None):
    url = '/uapi/overseas-futureoption/v1/quotations/opt-asking-price'
    tr_id = "HHDFO86000000" # 해외옵션 호가

    params = {
        "SRS_CD": itm_no   # 종목코드 예)OESM24 C5340
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    if dv == "01":
        current_data = pd.DataFrame(res.getBody().output1, index=[0])
    else :
        current_data = pd.DataFrame(res.getBody().output2)

    dataframe = current_data

    return dataframe
