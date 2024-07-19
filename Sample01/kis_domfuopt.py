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

#====|  [국내선물옵션] 주문/계좌  |===========================================================================================================================

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 주문[v1_국내선물-001]
##############################################################################################
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_domfuopt_order(dv_cd="02", sll_buy_dvsn_cd="", dvsn_cd="01", itm_no="", qty=0, unpr=0, tr_cont="", FK100="", NK100="", dataframe=None):  # [국내선물옵션] 주문/계좌 > 선물옵션 주문
    url = '/uapi/domestic-futureoption/v1/trading/order'

    if dv_cd == "01":
        tr_id = "TTTO1101U" # 선물 옵션 매수 매도 주문 주간    [모의투자] VTTO1101U : 선물 옵션 매수 매도 주문 주간
    elif dv_cd == "02":
        tr_id = "JTCE1001U" # 선물 옵션 매수 매도 주문 야간    [모의투자] VTCE1001U : 선물 옵션 매수 매도 주문 야간
    else:
        print("선물옵션매수매도주문주간/선물옵션매수매도주문야간 구분 확인요망!!!")
        return None

    if sll_buy_dvsn_cd == "":
        print("매도매수구분코드 확인요망!!!")
        return None

    if itm_no == "":
        print("주문종목번호 확인요망!!!")
        return None

    if qty == 0:
        print("주문수량 확인요망!!!")
        return None

    #if unpr == 0:
    #    print("주문단가 확인요망!!!")
    #    return None

    params = {
        "ORD_PRCS_DVSN_CD": "02",               # 주문처리구분코드 02 : 주문전송
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,     # 매수매도구분코드
        "SHTN_PDNO": itm_no,                    # 종목코드(단축상품번호 6자리) 선물 6자리 (예: 101S03) 옵션 9자리 (예: 201S03370)
        "ORD_QTY": str(int(qty)),               # 주문수량
        "UNIT_PRICE": str(int(unpr)),           # 주문가격
        "NMPR_TYPE_CD": "",                     # 호가유형코드 ※ ORD_DVSN_CD(주문구분코드)를 입력한 경우 ""(공란)으로 입력해도 됨
        "KRX_NMPR_CNDT_CD": "",                 # 한국거래소호가조건코드 ※ ORD_DVSN_CD(주문구분코드)를 입력한 경우 ""(공란)으로 입력해도 됨
        "CTAC_TLNO": "",                        # 연락전화번호
        "FUOP_ITEM_DVSN_CD": "",                # 선물옵션종목구분코드
        "ORD_DVSN_CD": dvsn_cd                  # 주문구분코드 01 : 지정가 02 : 시장가 03 : 조건부 04 : 최유리  10 : 지정가(IOC) .....
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params, postFlag=True)
    if str(res.getBody().rt_cd) == "0":
        current_data = pd.DataFrame(res.getBody().output, index=[0])
        dataframe = current_data
    else:
        print(res.getBody().msg_cd + "," + res.getBody().msg1)
        dataframe = None

    return dataframe


##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 정정취소주문[v1_국내선물-002]
##############################################################################################
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_domfuopt_order_rvsecncl(dv_cd="01", rvse_cncl_dvsn_cd="", orgn_odno="", ord_dvsn="01", ord_qty=0,
                       ord_unpr=0, rmn_qty_yn="", tr_cont="", dataframe=None):  # [국내선물옵션] 선물옵션 정정취소주문[v1_국내선물-002]
    url = '/uapi/domestic-futureoption/v1/trading/order-rvsecncl'

    if dv_cd == "01":
        tr_id = "TTTO1103U" # 선물 옵션 정정 취소 주문 주간    [모의투자] VTTO1103U : 선물 옵션 정정 취소 주문 주간
    elif dv_cd == "02":
        tr_id = "JTCE1002U" # 선물 옵션 정정 취소 주문 야간    [모의투자] VTCE1002U : 선물 옵션 정정 취소 주문 야간
    else:
        print("선물옵션정정취소주문주간/선물옵션정정취소주문야간 구분 확인요망!!!")
        return None

    if not rvse_cncl_dvsn_cd in ["01","02"]:
        print("정정취소구분코드 확인요망!!!") # 정정:01. 취소:02
        return None

    if orgn_odno == "":
        print("원주문번호 확인요망!!!")
        return None

    if ord_dvsn == "":
        print("주문구분 확인요망!!!")
        return None

    if rmn_qty_yn == "Y" and ord_qty > 0:
        print("잔량전부 취소/정정주문인 경우 주문수량 0 처리!!!")
        ord_qty = 0

    if rmn_qty_yn == "N" and ord_qty == 0:
        print("취소/정정 수량 확인요망!!!")
        return None

    if rvse_cncl_dvsn_cd == "01" and ord_unpr == 0:
        print("주문단가 확인요망!!!")
        return None

    params = {
        "ORD_PRCS_DVSN_CD": "02",               # 주문처리구분코드 02 : 주문전송
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "RVSE_CNCL_DVSN_CD": rvse_cncl_dvsn_cd, # 정정취소구분코드 01 : 정정 02 : 취소
        "ORGN_ODNO": orgn_odno,                 # 원주문번호 정정 혹은 취소할 주문의 번호
        "ORD_QTY": str(int(ord_qty)),           # 주문수량  전량일 경우 0으로 입력, 일부수량 정정 및 취소 불가, 주문수량 반드시 입력 (공백 불가) 일부 미체결 시 잔량 전체에 대해서 취소 가능
        "UNIT_PRICE": str(int(ord_unpr)),       # 주문가격  시장가나 최유리의 경우 0으로 입력 (취소 시에도 0 입력)
        "NMPR_TYPE_CD": "",                     # 호가유형코드 ※ ORD_DVSN_CD(주문구분코드)를 입력한 경우 ""(공란)으로 입력해도 됨
        "KRX_NMPR_CNDT_CD": "",                 # 한국거래소호가조건코드 ※ ORD_DVSN_CD(주문구분코드)를 입력한 경우 ""(공란)으로 입력해도 됨
        "RMN_QTY_YN": rmn_qty_yn,               # 잔여수량여부 Y : 전량  N : 일부
        "FUOP_ITEM_DVSN_CD": "",                # 선물옵션종목구분코드 	(주간) 공란 (야간) 01:선물 02:콜옵션 03:풋옵션 04:스프레드
        "ORD_DVSN_CD": ord_dvsn                 # 주문구분코드 (취소) 01, (정정) 01 : 지정가 02 : 시장가 03 : 조건부 04 : 최유리  10 : 지정가(IOC) .....
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
# [국내선물옵션] 주문/계좌 > (야간)선물옵션 주문체결 내역조회 [국내선물-009]
##############################################################################################

# [국내선물옵션] 주문/계좌 > (야간)선물옵션 주문체결 내역조회 [국내선물-009] Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
#       (JTCE5005R)
# Output: DataFrame (Option) output2 API 문서 참조 등
def get_domfuopt_inquire_ngt_ccnl_obj(inqr_strt_dt=None, inqr_end_dt=None, sll_buy_dvsn_cd="00", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/domestic-futureoption/v1/trading/inquire-ngt-ccnl'
    tr_id = "JTCE5005R"

    if inqr_strt_dt is None:
        inqr_strt_dt = datetime.today().strftime("%Y%m%d")   # 시작일자 값이 없으면 현재일자
    if inqr_end_dt is None:
        inqr_end_dt  = datetime.today().strftime("%Y%m%d")   # 종료일자 값이 없으면 현재일자

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "STRT_ORD_DT": inqr_strt_dt,            # 시작주문일자
        "END_ORD_DT": inqr_end_dt,              # 종료주문일자
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,     # 매도매수구분코드 00:전체 01:매도, 02:매수
        "CCLD_NCCS_DVSN": "01",                 # 체결미체결구분
        "SORT_SQN": "",                         # 정렬순서 DS : 정순, 그외 : 역순
        "STRT_ODNO": "",                        # 시작주문번호 00:전체, 01:체결, 02:미체결
        "PDNO": "",                             # 상품번호 (종목번호)
        "MKET_ID_CD": "",                       # 시장ID코드
        "FUOP_DVSN_CD": "",                     # 선물옵션구분코드 	공란 : 전체, 01 : 선물, 02 : 옵션
        "SCRN_DVSN": "02",                      # 화면구분 02 default
        "CTX_AREA_FK200": FK100,                # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK200": NK100                 # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # print(res.getBody())
    if res.isOK():
        # API 응답의 output 속성이 스칼라 값인지 확인
        output_data = res.getBody().output2
        if not isinstance(output_data, list):
            # 스칼라 값이면 리스트로 감싸서 반환
            output_data = [output_data]

        # DataFrame 생성 시 index 매개변수를 추가하여 스칼라 값일 경우 처리
        current_data = pd.DataFrame(output_data, index=[0])

        return current_data

    else:
        res.printError()
        return pd.DataFrame()


# [국내선물옵션] 주문/계좌 > (야간)선물옵션 주문체결 내역조회 [국내선물-009] List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
#        (JTCE5005R)
# Output: DataFrame (Option) output1 API 문서 참조 등
def get_domfuopt_inquire_ngt_ccnl_lst(inqr_strt_dt=None, inqr_end_dt=None, sll_buy_dvsn_cd="00", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/domestic-futureoption/v1/trading/inquire-ngt-ccnl'
    tr_id = "JTCE5005R"

    if inqr_strt_dt == "":
        inqr_strt_dt = datetime.today().strftime("%Y%m%d")   # 시작일자 값이 없으면 현재일자
    if inqr_end_dt == "":
        inqr_end_dt  = datetime.today().strftime("%Y%m%d")   # 종료일자 값이 없으면 현재일자

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "STRT_ORD_DT": inqr_strt_dt,            # 시작주문일자
        "END_ORD_DT": inqr_end_dt,              # 종료주문일자
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,     # 매도매수구분코드 00:전체 01:매도, 02:매수
        "CCLD_NCCS_DVSN": "00",                 # 체결미체결구분
        "SORT_SQN": "DS",                       # 정렬순서 DS : 정순, 그외 : 역순
        "STRT_ODNO": "",                        # 시작주문번호 00:전체, 01:체결, 02:미체결
        "PDNO": "",                             # 상품번호 (종목번호)
        "MKET_ID_CD": "",                       # 시장ID코드
        "FUOP_DVSN_CD": "",                     # 선물옵션구분코드 	공란 : 전체, 01 : 선물, 02 : 옵션
        "SCRN_DVSN": "02",                      # 화면구분 02 default
        "CTX_AREA_FK200": FK100,                # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK200": NK100                 # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params) # API 호출, kis_auth.py에 존재

    # Assuming 'output1' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output1)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data

    tr_cont, FK100, NK100 = res.getHeader().tr_cont, res.getBody().ctx_area_fk200, res.getBody().ctx_area_nk200 # 페이징 처리 getHeader(), getBody() kis_auth.py 존재
    # print(dv, tr_cont, FK100, NK100)

    if tr_cont == "D" or tr_cont == "E": # 마지막 페이지
        print("The End")
        return dataframe
    elif tr_cont == "F" or tr_cont == "M": # 다음 페이지 존재하는 경우 자기 호출 처리
        print('Call Next')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        tr_cont = "N"  # 다음조회
        return get_domfuopt_inquire_ngt_ccnl_lst(inqr_strt_dt, inqr_end_dt, sll_buy_dvsn_cd, "N", FK100, NK100, dataframe)


##############################################################################################
# [국내선물옵션] 주문/계좌 > (야간)선물옵션 잔고현황 [국내선물-010]
##############################################################################################
# [국내선물옵션] 주문/계좌 > (야간)선물옵션 잔고현황 Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output2 -
def get_domfuopt_inquire_ngt_balance_obj(tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/domestic-futureoption/v1/trading/inquire-ngt-balance'
    tr_id = "JTCE6001R"

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "MGNA_DVSN": "01",                      # 증거금구분 01 : 개시, 02 : 유지
        "EXCC_STAT_CD": "1",                    # 정산상태코드 1 : 정산 (정산가격으로 잔고 조회) 2 : 본정산 (매입가격으로 잔고 조회)
        "CTX_AREA_FK200": FK100,                # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK200": NK100                 # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # print(res.getBody())
    if res.isOK():
        # API 응답의 output 속성이 스칼라 값인지 확인
        output_data = res.getBody().output2
        if not isinstance(output_data, list):
            # 스칼라 값이면 리스트로 감싸서 반환
            output_data = [output_data]

        # DataFrame 생성 시 index 매개변수를 추가하여 스칼라 값일 경우 처리
        current_data = pd.DataFrame(output_data, index=[0])

        return current_data

    else:
        res.printError()
        return pd.DataFrame()


# [국내선물옵션] 주문/계좌 > (야간)선물옵션 잔고현황 종목별 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output2 - 종목번호, 상품명(종목명), 매매구분명(매수매도구분), 전일매수수량 ... 등
def get_domfuopt_inquire_ngt_balance_lst(tr_cont="", FK100="", NK100="", dataframe=None):  # 국내주식주문 > 주식잔고조회(현재종목별 잔고)
    url = '/uapi/domestic-futureoption/v1/trading/inquire-ngt-balance'
    tr_id = "JTCE6001R"

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "MGNA_DVSN": "01",                      # 증거금구분 01 : 개시, 02 : 유지
        "EXCC_STAT_CD": "1",                    # 정산상태코드 1 : 정산 (정산가격으로 잔고 조회) 2 : 본정산 (매입가격으로 잔고 조회)
        "CTX_AREA_FK200": FK100,                # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK200": NK100                 # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params) # API 호출, kis_auth.py에 존재

    print(res.getBody())
    # Assuming 'output1' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output1)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data

    tr_cont, FK100, NK100 = res.getHeader().tr_cont, res.getBody().ctx_area_fk200, res.getBody().ctx_area_nk200 # 페이징 처리 getHeader(), getBody() kis_auth.py 존재

    if tr_cont == "D" or tr_cont == "E": # 마지막 페이지
        print("The End")
        return dataframe
    elif tr_cont == "F" or tr_cont == "M": # 다음 페이지 존재하는 경우 자기 호출 처리
        print('Call Next')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_domfuopt_inquire_ngt_balance_lst("N", FK100, NK100, dataframe)


##############################################################################################
# [국내선물옵션] 주문/계좌 > (야간)선물옵션 주문가능 조회 [국내선물-011]
##############################################################################################
# [국내선물옵션] 주문/계좌 > (야간)선물옵션 주문가능 조회 [국내선물-011] List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output2 -
def get_domfuopt_inquire_psbl_ngt_order(pdno="", sll_buy_dvsn_cd="", ord_unpr=0, ord_dvsn="01", tr_cont="", FK100="", NK100="", dataframe=None):  # 국내주식주문 > 매수가능조회
    url = '/uapi/domestic-futureoption/v1/trading/inquire-psbl-ngt-order'
    tr_id = "JTCE1004R"

    params = {
        "CANO": kis.getTREnv().my_acct,             # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod,     # 계좌상품코드 2자리
        "PDNO": pdno,                               # 상품번호
        "PRDT_TYPE_CD": "301",                      # 상품유형코드   	301 : 선물옵션
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,         # 매도매수구분코드	01 : 매도 , 02 : 매수
        "UNIT_PRICE": ord_unpr,                     # 주문가격
        "ORD_DVSN_CD": ord_dvsn                     # 주문구분코드 01 : 지정가 02 : 시장가 03 : 조건부 04 : 최유리 10 : 지정가(IOC) .....
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params) # API 호출, kis_auth.py에 존재

    print(res.getBody())
    if res.isOK():
        # API 응답의 output 속성이 스칼라 값인지 확인
        output_data = res.getBody().output
        if not isinstance(output_data, list):
            # 스칼라 값이면 리스트로 감싸서 반환
            output_data = [output_data]

        # DataFrame 생성 시 index 매개변수를 추가하여 스칼라 값일 경우 처리
        current_data = pd.DataFrame(output_data, index=[0])

        return current_data

    else:
        res.printError()
        return pd.DataFrame()
