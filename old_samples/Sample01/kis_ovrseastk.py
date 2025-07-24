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


#====|  [해외주식] 주문/계좌  |============================================================================================================================

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 주문[v1_해외주식-001]
#
# * 모의투자의 경우, 모든 해외 종목 매매가 지원되지 않습니다. 일부 종목만 매매 가능한 점 유의 부탁드립니다.
#
# * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
# https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp
#
# * 해외 거래소 운영시간 외 API 호출 시 애러가 발생하오니 운영시간을 확인해주세요.
# * 해외 거래소 운영시간(한국시간 기준)
# 1) 미국 : 23:30 ~ 06:00 (썸머타임 적용 시 22:30 ~ 05:00)
# 2) 일본 : (오전) 09:00 ~ 11:30, (오후) 12:30 ~ 15:00
# 3) 상해 : 10:30 ~ 16:00
# 4) 홍콩 : (오전) 10:30 ~ 13:00, (오후) 14:00 ~ 17:00
#
# ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
#    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)
#
# ※ 종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
#    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
##############################################################################################
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseas_order(ord_dv="", excg_cd="", itm_no="", qty=0, unpr=0, tr_cont="", FK100="", NK100="", dataframe=None):  # 국내주식주문 > 주식주문(현금)
    url = '/uapi/overseas-stock/v1/trading/order'

    if ord_dv == "buy":
        if excg_cd in ("NASD","NYSE","AMEX"):
            tr_id = "TTTT1002U"  # 미국 매수 주문 [모의투자] VTTT1002U
        elif excg_cd == "SHEK":
            tr_id = "TTTS1002U"  # 홍콩 매수 주문 [모의투자] VTTS1002U
        elif excg_cd == "SHAA":
            tr_id = "TTTS0202U"  # 중국상해 매수 주문 [모의투자] VTTS0202U
        elif excg_cd == "SZAA":
            tr_id = "TTTS0305U"  # 중국심천 매수 주문 [모의투자] VTTS0305U
        elif excg_cd == "TKSE":
            tr_id = "TTTS0308U"  # 일본 매수 주문 [모의투자] VTTS0308U
        elif excg_cd in ("HASE", "VNSE"):
            tr_id = "TTTS0311U"  # 베트남(하노이,호치민) 매수 주문 [모의투자] VTTS0311U
        else:
            print("해외거래소코드 확인요망!!!")
            return None
    elif ord_dv == "sell":
        if excg_cd in ("NASD", "NYSE", "AMEX"):
            tr_id = "TTTT1006U"  # 미국 매도 주문 [모의투자] VTTT1006U
        elif excg_cd == "SHEK":
            tr_id = "TTTS1001U"  # 홍콩 매도 주문 [모의투자] VTTS1001U
        elif excg_cd == "SHAA":
            tr_id = "TTTS1005U"  # 중국상해 매도 주문 [모의투자] VTTS1005U
        elif excg_cd == "SZAA":
            tr_id = "TTTS0304U"  # 중국심천 매도 주문 [모의투자] VTTS0304U
        elif excg_cd == "TKSE":
            tr_id = "TTTS0307U"  # 일본 매도 주문 [모의투자] VTTS0307U
        elif excg_cd in ("HASE", "VNSE"):
            tr_id = "TTTS0310U"  # 베트남(하노이,호치민) 매도 주문 [모의투자] VTTS0311U
        else:
            print("해외거래소코드 확인요망!!!")
            return None
    else:
        print("매수/매도 구분 확인요망!")
        return None

    if itm_no == "":
        print("주문종목번호(상품번호) 확인요망!!!")
        return None

    if qty == 0:
        print("주문수량 확인요망!!!")
        return None

    if unpr == 0:
        print("해외주문단가 확인요망!!!")
        return None

    if ord_dv == "buy":
        sll_type = ""
    elif ord_dv == "sell":
        sll_type = "00"
    else:
        print("매수/매도 구분 확인요망!!!")
        return None

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "OVRS_EXCG_CD": excg_cd,                # 해외거래소코드
                                                # NASD:나스닥,NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
        "PDNO": itm_no,                         # 종목코드
        "ORD_DVSN": "00",                       # 주문구분 00:지정가, 01:시장가, 02:조건부지정가  나머지주문구분 API 문서 참조
        "ORD_QTY": str(int(qty)),               # 주문주식수
        "OVRS_ORD_UNPR": str(int(unpr)),        # 해외주문단가
        "SLL_TYPE": sll_type,                   # 판매유형
        "ORD_SVR_DVSN_CD": "0"                  # 주문서버구분코드l
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
# [해외주식] 주문/계좌 > 해외주식 정정취소주문[v1_해외주식-003]
##############################################################################################
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseas_order_rvsecncl(excg_cd="", itm_no="", orgn_odno="", rvse_cncl_dvsn_cd="", qty=0, unpr=0, tr_cont="", dataframe=None):
    url = '/uapi/overseas-stock/v1/trading/order-rvsecncl'

    if excg_cd in ("NASD", "NYSE", "AMEX"):
        tr_id = "TTTT1004U"  # 미국 매수 주문 [모의투자] VTTT1004U
    elif excg_cd == "SHEK":
        tr_id = "TTTS1003U"  # 홍콩 매수 주문 [모의투자] VTTS1003U
    elif excg_cd == "SHAA":
        tr_id = "TTTS0302U"  # 중국상해 매수 주문 [모의투자] VTTS0302U
    elif excg_cd == "SZAA":
        tr_id = "TTTS0306U"  # 중국심천 매수 주문 [모의투자] VTTS0306U
    elif excg_cd == "TKSE":
        tr_id = "TTTS0309U"  # 일본 매수 주문 [모의투자] VTTS0309U
    elif excg_cd in ("HASE", "VNSE"):
        tr_id = "TTTS0312U"  # 베트남(하노이,호치민) 매수 주문 [모의투자] VTTS0312U
    else:
        print("해외거래소코드 확인요망!!!")
        return None

    if orgn_odno == "":
        print("원주문번호 확인요망!!!")
        return None

    if not rvse_cncl_dvsn_cd in ["01","02"]:
        print("정정취소구분코드 확인요망!!!") # 정정:01. 취소:02
        return None

    if rvse_cncl_dvsn_cd == "01" and unpr == 0:
        print("주문단가 확인요망!!!")
        return None

    params = {
        "CANO": kis.getTREnv().my_acct,     # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "OVRS_EXCG_CD": excg_cd,            # 해외거래소코드 NASD:나스닥,NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
        "PDNO": itm_no,                     # 종목번호(상품번호)
        "ORGN_ODNO": orgn_odno,             # 원주문번호 정정 또는 취소할 원주문번호 (해외주식_주문 API ouput ODNO or 해외주식 미체결내역 API output ODNO 참고)
        "RVSE_CNCL_DVSN_CD": rvse_cncl_dvsn_cd, # 정정 : 01, 취소 : 02
        "ORD_QTY": str(int(qty)),           # 주문수량	[잔량전부 취소/정정주문] "0" 설정 ( QTY_ALL_ORD_YN=Y 설정 ) [잔량일부 취소/정정주문] 취소/정정 수량
        "OVRS_ORD_UNPR": str(int(unpr)),    # 주문단가 	[정정] 정정주문 1주당 가격 [취소] "0" 설정
        "MGCO_APTM_ODNO": "",               # 운용사지정주문번호
        "ORD_SVR_DVSN_CD": "0"              # 주문서버구분코드
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
# [해외주식] 주문/계좌 > 해외주식 전부취소주문[v1_해외주식-003]  (검증진행중)
##############################################################################################
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseas_order_allcncl(excg_cd="", itm_no="", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-stock/v1/trading/inquire-nccs'
    tr_id = "TTTS3018R"   # 모의투자 VTTS3018R

    t_cnt = 0

    if excg_cd == "": # 해외거래소코드 필수
        print("해외거래소코드 확인요망!!!")
        return None

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "OVRS_EXCG_CD": excg_cd,                # 해외거래소코드 NASD:나스닥,NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
        "SORT_SQN": "DS",                       # DS : 정순, 그외 : 역순
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
            print("미체결내역 없음")
        else:
            print("미체결내역 있음")

        for index, row in current_data.iterrows():
            print(row['odno'])
            r_odno = row['odno']
            res_cncl = get_overseas_order_rvsecncl(excg_cd="NASD", itm_no="", orgn_odno=r_odno, rvse_cncl_dvsn_cd="02")
            print(res_cncl)

        dataframe = current_data
        return dataframe
    elif tr_cont == "F" or tr_cont == "M": # 다음 페이지 존재하는 경우 자기 호출 처리
        print('Call Next')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_overseas_order_allcncl(excg_cd, itm_no, "N", FK100, NK100, dataframe)



##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 미체결내역[v1_해외주식-005]
# 접수된 해외주식 주문 중 체결되지 않은 미체결 내역을 조회하는 API입니다.
# 실전계좌의 경우, 한 번의 호출에 최대 40건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.
#
# * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
# https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp
#
# ※ 해외 거래소 운영시간(한국시간 기준)
# 1) 미국 : 23:30 ~ 06:00 (썸머타임 적용 시 22:30 ~ 05:00)
# 2) 일본 : (오전) 09:00 ~ 11:30, (오후) 12:30 ~ 15:00
# 3) 상해 : 10:30 ~ 16:00
# 4) 홍콩 : (오전) 10:30 ~ 13:00, (오후) 14:00 ~ 17:00
##############################################################################################
# 해외주식 미체결내역 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseas_inquire_nccs(excg_cd="", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-stock/v1/trading/inquire-nccs'
    tr_id = "TTTS3018R"   # 모의투자 VTTS3018R

    t_cnt = 0

    if excg_cd == "": # 해외거래소코드 필수
        print("해외거래소코드 확인요망!!!")
        return None

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "OVRS_EXCG_CD": excg_cd,                # 해외거래소코드 NASD:나스닥,NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
        "SORT_SQN": "DS",                       # DS : 정순, 그외 : 역순
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
    print(tr_cont, FK100, NK100)

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
            print("미체결내역 없음")
        else:
            print("미체결내역 있음")

        dataframe = current_data
        return dataframe
    elif tr_cont == "F" or tr_cont == "M": # 다음 페이지 존재하는 경우 자기 호출 처리
        print('Call Next')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_overseas_inquire_nccs(excg_cd, "N", FK100, NK100, dataframe)


##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 잔고_현황 [v1_해외주식-006]
# 해외주식 잔고를 조회하는 API 입니다.
# 한국투자 HTS(eFriend Plus) > [7600] 해외주식 종합주문 화면의 좌측 하단 '실시간잔고' 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
# 다만 미국주간거래 가능종목에 대해서는 frcr_evlu_pfls_amt(외화평가손익금액), evlu_pfls_rt(평가손익율), ovrs_stck_evlu_amt(해외주식평가금액), now_pric2(현재가격2) 값이 HTS와는 상이하게 표출될 수 있습니다.
# (주간시간 시간대에 HTS는 주간시세로 노출, API로는 야간시세로 노출)
#
# 실전계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.
#
# * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
# https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp
#
# * 미니스탁 잔고는 해당 API로 확인이 불가합니다.
##############################################################################################
# 해외주식 잔고 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseas_inquire_balance(excg_cd="", crcy_cd="", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-stock/v1/trading/inquire-balance'
    tr_id = "TTTS3012R"   # 모의투자 VTTS3012R

    t_cnt = 0

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "OVRS_EXCG_CD": excg_cd,                # 해외거래소코드 NASD:나스닥,NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
        "TR_CRCY_CD": crcy_cd,                  # 거래통화코드 USD : 미국달러,HKD : 홍콩달러,CNY : 중국위안화,JPY : 일본엔화,VND : 베트남동
        "CTX_AREA_FK200": FK100,                # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK200": NK100                 # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params)

    if str(res.getBody().rt_cd) == "0":
        current_data = pd.DataFrame(res.getBody().output2, index=[0])
        dataframe = current_data
    else:
        print(res.getBody().msg_cd + "," + res.getBody().msg1)
        #print(res.getErrorCode() + "," + res.getErrorMessage())
        dataframe = None

    return dataframe


##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 잔고 내역[v1_해외주식-006]
# 해외주식 잔고를 조회하는 API 입니다.
# 한국투자 HTS(eFriend Plus) > [7600] 해외주식 종합주문 화면의 좌측 하단 '실시간잔고' 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
# 다만 미국주간거래 가능종목에 대해서는 frcr_evlu_pfls_amt(외화평가손익금액), evlu_pfls_rt(평가손익율), ovrs_stck_evlu_amt(해외주식평가금액), now_pric2(현재가격2) 값이 HTS와는 상이하게 표출될 수 있습니다.
# (주간시간 시간대에 HTS는 주간시세로 노출, API로는 야간시세로 노출)
#
# 실전계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.
#
# * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
# https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp
#
# * 미니스탁 잔고는 해당 API로 확인이 불가합니다.
##############################################################################################
# 해외주식 잔고 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseas_inquire_balance_lst(excg_cd="", crcy_cd="", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-stock/v1/trading/inquire-balance'
    tr_id = "TTTS3012R"   # 모의투자 VTTS3012R

    t_cnt = 0

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "OVRS_EXCG_CD": excg_cd,                # 해외거래소코드 NASD:나스닥,NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
        "TR_CRCY_CD": crcy_cd,                  # 거래통화코드 USD : 미국달러,HKD : 홍콩달러,CNY : 중국위안화,JPY : 일본엔화,VND : 베트남동
        "CTX_AREA_FK200": FK100,                # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK200": NK100                 # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
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
    print(tr_cont, FK100, NK100)

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
        return get_overseas_inquire_balance_lst(excg_cd, crcy_cd, "N", FK100, NK100, dataframe)


##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 주문체결내역[v1_해외주식-007]
# 일정 기간의 해외주식 주문 체결 내역을 확인하는 API입니다.
# 실전계좌의 경우, 한 번의 호출에 최대 20건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.
# 모의계좌의 경우, 한 번의 호출에 최대 15건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.
#
# * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
# https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp
#
# ※ 해외 거래소 운영시간(한국시간 기준)
# 1) 미국 : 23:30 ~ 06:00 (썸머타임 적용 시 22:30 ~ 05:00)
# 2) 일본 : (오전) 09:00 ~ 11:30, (오후) 12:30 ~ 15:00
# 3) 상해 : 10:30 ~ 16:00
# 4) 홍콩 : (오전) 10:30 ~ 13:00, (오후) 14:00 ~ 17:00
##############################################################################################
# 해외주식 주문체결내역 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseas_inquire_ccnl(st_dt="", ed_dt="", ord_dv="00", ccld_dv="00", excg_cd="%", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-stock/v1/trading/inquire-ccnl'
    tr_id = "TTTS3035R"   # 모의투자 VTTS3035R

    t_cnt = 0

    if st_dt =="":
        st_dt = datetime.today().strftime("%Y%m%d")   # 주문내역조회 시작일자 값이 없으면 현재일자

    if ed_dt =="":
        ed_dt = datetime.today().strftime("%Y%m%d")   # 주문내역조회 종료일자 값이 없으면 현재일자

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "PDNO": "%",                            # 전종목일 경우 "%" 입력  ※ 모의투자계좌의 경우 ""(전체 조회)만 가능
        "ORD_STRT_DT": st_dt,                   # YYYYMMDD 형식 (현지시각 기준)
        "ORD_END_DT": ed_dt,                    # YYYYMMDD 형식 (현지시각 기준)
        "SLL_BUY_DVSN": ord_dv,                 # 매도매수구분 00:전체,01:매도,02:매수   ※ 모의투자계좌의 경우 "00"(전체 조회)만 가능
        "CCLD_NCCS_DVSN": ccld_dv,              # 체결미체결구분 00:전체,01:체결,02:미체결 ※ 모의투자계좌의 경우 "00"(전체 조회)만 가능
        "OVRS_EXCG_CD": excg_cd,                # 해외거래소코드, 전종목일 경우 "%" 입력, NASD:미국시장 전체(나스닥,뉴욕,아멕스),NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
        "SORT_SQN": "DS",                       # DS:정순,AS:역순, ※ 모의투자계좌의 경우 정렬순서 사용불가(Default : DS(정순))
        "ORD_DT": "",                           # "" (Null 값 설정)
        "ORD_GNO_BRNO": "",                     # "" (Null 값 설정)
        "ODNO": "",                             # "" (Null 값 설정)
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
        return get_overseas_inquire_ccnl(st_dt, ed_dt, ord_dv, ccld_dv, excg_cd, "N", FK100, NK100, dataframe)



##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 체결기준현재잔고[v1_해외주식-008]
# 해외주식 잔고를 체결 기준으로 확인하는 API 입니다.
#
# HTS(eFriend Plus) [0839] 해외 체결기준잔고 화면을 API로 구현한 사항으로 화면을 함께 보시면 기능 이해가 쉽습니다.
#
# (※모의계좌의 경우 output3(외화평가총액 등 확인 가능)만 정상 출력됩니다.
# 잔고 확인을 원하실 경우에는 해외주식 잔고[v1_해외주식-006] API 사용을 부탁드립니다.)
#
# * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
# https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp
#
# 해외주식 체결기준현재잔고 유의사항
# 1. 해외증권 체결기준 잔고현황을 조회하는 화면입니다.
# 2. 온라인국가는 수수료(국내/해외)가 반영된 최종 정산금액으로 잔고가 변동되며, 결제작업 지연등으로 인해 조회시간은 차이가 발생할 수 있습니다.
#    - 아시아 온라인국가 : 매매일 익일    08:40 ~ 08:45분 경
#    - 미국 온라인국가   : 당일 장 종료후 08:40 ~ 08:45분 경
#   ※ 단, 애프터연장 참여 신청계좌는 10:30 ~ 10:35분 경(Summer Time : 09:30 ~ 09:35분 경)에 최종 정산금액으로 변동됩니다.
# 3. 미국 현재가 항목은 주간시세 및 애프터시세는 반영하지 않으며, 정규장 마감 후에는 종가로 조회됩니다.
# 4. 온라인국가를 제외한 국가의 현재가는 실시간 시세가 아니므로 주문화면의 잔고 평가금액 등과 차이가 발생할 수 있습니다.
# 5. 해외주식 담보대출 매도상환 체결내역은 해당 잔고화면에 반영되지 않습니다.
#    결제가 완료된 이후 외화잔고에 포함되어 반영되오니 참고하여 주시기 바랍니다.
# 6. 외화평가금액은 당일 최초고시환율이 적용된 금액으로 실제 환전금액과는 차이가 있습니다.
# 7. 미국은 메인 시스템이 아닌 별도 시스템을 통해 거래되므로, 18시 10~15분 이후 발생하는 미국 매매내역은 해당 화면에 실시간으로 반영되지 않으니 하단 내용을 참고하여 안내하여 주시기 바랍니다.
#    [외화잔고 및 해외 유가증권 현황 조회]
#    - 일반/통합증거금 계좌 : 미국장 종료 + 30분 후 부터 조회 가능
#                             단, 통합증거금 계좌에 한해 주문금액은 외화잔고 항목에 실시간 반영되며, 해외 유가증권 현황은 반영되지
#                             않아 해외 유가증권 평가금액이 과다 또는 과소 평가될 수 있습니다.
#    - 애프터연장 신청계좌  : 실시간 반영
#                             단, 시스템정산작업시간(23:40~00:10) 및 거래량이 많은 경우 메인시스템에 반영되는 시간으로 인해 차이가
#                             발생할 수 있습니다.
#    ※ 배치작업시간에 따라 시간은 변동될 수 있습니다.
##############################################################################################
# 해외주식 체결기준현재잔고 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseas_inquire_present_balance(dv="03", dvsn="01", natn="000", mkt="00", inqr_dvsn="00", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-stock/v1/trading/inquire-present-balance'
    tr_id = "CTRP6504R"   # 모의투자 VTRP6504R

    t_cnt = 0

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "WCRC_FRCR_DVSN_CD": dvsn,              # 원화외화구분코드 01 : 원화, 02 : 외화
        "NATN_CD": natn,                        # 국가코드 000 전체, 840 미국, 344 홍콩, 156 중국, 392 일본, 704 베트남
        "TR_MKET_CD": mkt,                      # 거래시장코드 00:전체 (API문서 참조)
        "INQR_DVSN_CD": inqr_dvsn               # 00 : 전체,01 : 일반해외주식,02 : 미니스탁
    }


    res = kis._url_fetch(url, tr_id, tr_cont, params)

    if str(res.getBody().rt_cd) == "0":
        if dv == "01":
            current_data = pd.DataFrame(res.getBody().output1)
        elif dv == "02":
            current_data = pd.DataFrame(res.getBody().output2)
        else:
            current_data = pd.DataFrame(res.getBody().output3, index=[0])
        dataframe = current_data
    else:
        print(res.getBody().msg_cd + "," + res.getBody().msg1)
        #print(res.getErrorCode() + "," + res.getErrorMessage())
        dataframe = None

    return dataframe

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 매수가능금액조회[v1_해외주식-014]
# 해외주식 매수가능금액조회 API입니다.
#
# * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
# https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp
##############################################################################################
# 해외주식 매수가능금액조회 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseas_inquire_psamount(dv="03", dvsn="01", natn="000", mkt="00", inqr_dvsn="00", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-stock/v1/trading/inquire-psamount'
    tr_id = "TTTS3007R"   # 모의투자 VTTS3007R

    t_cnt = 0

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "OVRS_EXCG_CD": dvsn,              # 원화외화구분코드 01 : 원화, 02 : 외화
        "OVRS_ORD_UNPR": natn,                        # 국가코드 000 전체, 840 미국, 344 홍콩, 156 중국, 392 일본, 704 베트남
        "ITEM_CD": inqr_dvsn               # 00 : 전체,01 : 일반해외주식,02 : 미니스탁
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

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 미국주간주문[v1_해외주식-026]
# 해외주식 미국주간주문 API입니다.
#
# * 미국주식 주간거래 시 아래 참고 부탁드립니다.
# . 포럼 > FAQ > 미국주식 주간거래 시 어떤 API를 사용해야 하나요?
#
# * 미국주간거래의 경우, 모든 미국 종목 매매가 지원되지 않습니다. 일부 종목만 매매 가능한 점 유의 부탁드립니다.
#
# * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
# https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp
#
# * 미국주간거래시간 외 API 호출 시 에러가 발생하오니 운영시간을 확인해주세요.
# . 주간거래(장전거래)(한국시간 기준) : 10:00 ~ 18:00 (Summer Time 동일)
#
# * 한국투자증권 해외주식 시장별 매매안내(매매수수료, 거래시간 안내, 결제일 정보, 환전안내)
#    https://securities.koreainvestment.com/main/bond/research/_static/TF03ca050000.jsp
#
# ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
#    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)
#
# ※ 종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
#    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
##############################################################################################
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseas_daytime_order(ord_dv="", excg_cd="", itm_no="", qty=0, unpr=0, tr_cont="", FK100="", NK100="", dataframe=None):  # 국내주식주문 > 주식주문(현금)
    url = '/uapi/overseas-stock/v1/trading/daytime-order'

    if ord_dv == "buy":
        tr_id = "TTTS6036U"  # 미국주간매수
    elif ord_dv == "sell":
        tr_id = "TTTS6037U"  # 미국주간매도
    else:
        print("매수매도구분(ord_dv) 확인요망!!!")
        return None

    if excg_cd == "":
        print("해외거래소코드(excg_cd) 확인요망!!!")
        return None

    if itm_no == "":
        print("주문종목번호(itm_no 상품번호) 확인요망!!!")
        return None

    if qty == 0:
        print("주문수량(qty) 확인요망!!!")
        return None

    if unpr == 0:
        print("해외주문단가(unpr) 확인요망!!!")
        return None

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "OVRS_EXCG_CD": excg_cd,                # 해외거래소코드 NASD:나스닥,NYSE:뉴욕,AMEX:아멕스
        "PDNO": itm_no,                         # 종목코드
        "ORD_DVSN": "00",                       # 주문구분 00:지정가 * 주간거래는 지정가만 가능
        "ORD_QTY": str(int(qty)),               # 주문주식수
        "OVRS_ORD_UNPR": str(int(unpr)),        # 해외주문단가
        "CTAC_TLNO": "",                        # 연락전화번호
        "MGCO_APTM_ODNO": "",                   # 운용사지정주문번호
        "ORD_SVR_DVSN_CD": "0"                  # 주문서버구분코드
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
# [해외주식] 주문/계좌 > 해외주식 미국주간정정취소[v1_해외주식-027]
##############################################################################################
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseas_daytime_order_rvsecncl(excg_cd="", itm_no="", orgn_odno="", rvse_cncl_dvsn_cd="", qty=0, unpr=0, tr_cont="", dataframe=None):
    url = '/uapi/overseas-stock/v1/trading/daytime-order-rvsecncl'

    tr_id = "TTTS6038U"  # 미국주간정정취소

    if excg_cd == "":
        print("해외거래소코드(excg_cd) 확인요망!!!")
        return None

    if itm_no == "":
        print("주문종목번호(itm_no 상품번호) 확인요망!!!")
        return None

    if orgn_odno == "":
        print("원주문번호(orgn_odno) 확인요망!!!")
        return None

    if not rvse_cncl_dvsn_cd in ["01","02"]:
        print("정정취소구분코드(rvse_cncl_dvsn_cd) 확인요망!!!") # 정정:01. 취소:02
        return None

    if rvse_cncl_dvsn_cd == "01" and unpr == 0:
        print("주문단가(unpr) 확인요망!!!")
        return None

    params = {
        "CANO": kis.getTREnv().my_acct,     # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "OVRS_EXCG_CD": excg_cd,            # 해외거래소코드 NASD:나스닥,NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
        "PDNO": itm_no,                     # 종목번호(상품번호)
        "ORGN_ODNO": orgn_odno,             # 원주문번호 정정 또는 취소할 원주문번호 (해외주식_주문 API ouput ODNO or 해외주식 미체결내역 API output ODNO 참고)
        "RVSE_CNCL_DVSN_CD": rvse_cncl_dvsn_cd, # 정정 : 01, 취소 : 02
        "ORD_QTY": str(int(qty)),           # 주문수량	[잔량전부 취소/정정주문] "0" 설정 ( QTY_ALL_ORD_YN=Y 설정 ) [잔량일부 취소/정정주문] 취소/정정 수량
        "OVRS_ORD_UNPR": str(int(unpr)),    # 해외주문단가 	[정정] 소수점 포함, 1주당 가격 [취소] "0" 설정
        "CTAC_TLNO": "",                    # 연락전화번호
        "MGCO_APTM_ODNO": "",               # 운용사지정주문번호
        "ORD_SVR_DVSN_CD": "0"              # 주문서버구분코드
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
# [해외주식] 주문/계좌 > 해외주식 기간손익[v1_해외주식-032]
# 해외주식 기간손익 API입니다.
# 한국투자 HTS(eFriend Plus) > [7717] 해외 기간손익 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
#
# * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
# https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp
#
# [해외 기간손익 유의 사항]
# ■ 단순 매체결내역을 기초로 만든 화면으로 매도체결시점의 체결기준 매입단가와 비교하여 손익이 계산됩니다.
#   결제일의 환율과 금액을 기준으로 산출하는 해외주식 양도소득세 계산방식과는 상이하오니, 참고용으로만 활용하여 주시기 바랍니다.
# ■ 기간손익은 매매일 익일부터 조회가능합니다.
# ■ 매입금액/매도금액 원화 환산 시 매도일의 환율이 적용되어있습니다.
# ■ 손익금액의 비용은 "매도비용" 만 포함되어있습니다. 단, 동일 종목의 매수/매도가 동시에 있는 경우에는 해당일 발생한 매수비용도 함께 계산됩니다.
# ■ 담보상환내역은 기간손익화면에 표시되지 많으니 참고하여 주시기 바랍니다.
##############################################################################################
# 해외주식 기간손익 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseas_inquire_period_profit(excg_cd="", crcy="", itm_no="", st_dt="", ed_dt="", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-stock/v1/trading/inquire-period-profit'
    tr_id = "TTTS3039R"

    t_cnt = 0

    if st_dt =="":
        st_dt = datetime.today().strftime("%Y%m%d")   # 기간손익 시작일자 값이 없으면 현재일자

    if ed_dt =="":
        ed_dt = datetime.today().strftime("%Y%m%d")   # 기간손익 종료일자 값이 없으면 현재일자

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "OVRS_EXCG_CD": excg_cd,                # 해외거래소코드, 공란:전체,NASD:미국,SEHK:홍콩,SHAA:중국,TKSE:일본,HASE:베트남
        "NATN_CD": "",                          # 국가코드 공란(Default)
        "CRCY_CD": crcy,                        # 통화코드 공란:전체,USD:미국달러,HKD:홍콩달러,CNY:중국위안화,JPY:일본엔화,VND:베트남동
        "PDNO": itm_no,                         # 상품번호 공란:전체
        "INQR_STRT_DT": st_dt,                  # 조회시작일자 YYYYMMDD
        "INQR_END_DT": ed_dt,                   # 조회종료일자 YYYYMMDD
        "WCRC_FRCR_DVSN_CD": "02",              # 원화외화구분코드 	01 : 외화, 02 : 원화
        "CTX_AREA_FK200": FK100,                # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK200": NK100                 # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params)

    if str(res.getBody().rt_cd) == "0":
        current_data = pd.DataFrame(res.getBody().output2, index=[0])
        dataframe = current_data
    else:
        print(res.getBody().msg_cd + "," + res.getBody().msg1)
        #print(res.getErrorCode() + "," + res.getErrorMessage())
        dataframe = None

    return dataframe

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 기간손익[v1_해외주식-032]
##############################################################################################
# 해외주식 기간손익 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseas_inquire_period_profit_output1(excg_cd="", crcy="", itm_no="", st_dt="", ed_dt="", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-stock/v1/trading/inquire-period-profit'
    tr_id = "TTTS3039R"

    t_cnt = 0

    if st_dt =="":
        st_dt = datetime.today().strftime("%Y%m%d")   # 기간손익 시작일자 값이 없으면 현재일자

    if ed_dt =="":
        ed_dt = datetime.today().strftime("%Y%m%d")   # 기간손익 종료일자 값이 없으면 현재일자

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "OVRS_EXCG_CD": excg_cd,                # 해외거래소코드, 공란:전체,NASD:미국,SEHK:홍콩,SHAA:중국,TKSE:일본,HASE:베트남
        "NATN_CD": "",                          # 국가코드 공란(Default)
        "CRCY_CD": crcy,                        # 통화코드 공란:전체,USD:미국달러,HKD:홍콩달러,CNY:중국위안화,JPY:일본엔화,VND:베트남동
        "PDNO": itm_no,                         # 상품번호 공란:전체
        "INQR_STRT_DT": st_dt,                  # 조회시작일자 YYYYMMDD
        "INQR_END_DT": ed_dt,                   # 조회종료일자 YYYYMMDD
        "WCRC_FRCR_DVSN_CD": "02",              # 원화외화구분코드 	01 : 외화, 02 : 원화
        "CTX_AREA_FK200": FK100,                # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK200": NK100                 # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
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
        return get_overseas_inquire_period_profit_output1(excg_cd, crcy, itm_no, st_dt, ed_dt, "N", FK100, NK100, dataframe)


##############################################################################################
# [해외주식] 주문/계좌 > 해외증거금 통화별조회 [해외주식-035]
# 해외증거금 통화별조회 API입니다.
# 한국투자 HTS(eFriend Plus) > [7718] 해외주식 증거금상세 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
##############################################################################################
# 해외주식 기간손익 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseas_inquire_foreign_margin(tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-stock/v1/trading/foreign-margin'
    tr_id = "TTTC2101R"

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod # 계좌상품코드 2자리
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params)

    if str(res.getBody().rt_cd) == "0":
        current_data = pd.DataFrame(res.getBody().output)
        dataframe = current_data.loc[current_data.crcy_cd != ""]  # 통화코드(crcy_cd) 값이 없는 경우 제외
    else:
        print(res.getBody().msg_cd + "," + res.getBody().msg1)
        #print(res.getErrorCode() + "," + res.getErrorMessage())
        dataframe = None

    return dataframe


##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 일별거래내역 [해외주식-063]
# 해외주식 일별거래내역 API입니다.
# 한국투자 HTS(eFriend Plus) > [0828] 해외증권 일별거래내역 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
#
# ※ 체결가격, 매매금액, 정산금액, 수수료 원화금액은 국내 결제일까지는 예상환율로 적용되고, 국내 결제일 익일부터 확정환율로 적용됨으로 금액이 변경될 수 있습니다.
# ※ 해외증권 투자 및 업무문의 안내: 한국투자증권 해외투자지원부 02)3276-5300
##############################################################################################
# 해외주식 일별거래내역 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseas_inquire_period_trans(excg_cd="", dvsn="", itm_no="", st_dt="", ed_dt="", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-stock/v1/trading/inquire-period-trans'
    tr_id = "CTOS4001R"

    t_cnt = 0

    if st_dt =="":
        st_dt = datetime.today().strftime("%Y%m%d")   # 기간손익 시작일자 값이 없으면 현재일자

    if ed_dt =="":
        ed_dt = datetime.today().strftime("%Y%m%d")   # 기간손익 종료일자 값이 없으면 현재일자

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "ERLM_STRT_DT": st_dt,                  # 조회시작일자 YYYYMMDD
        "ERLM_END_DT": ed_dt,                   # 조회종료일자 YYYYMMDD
        "OVRS_EXCG_CD": excg_cd,                # 해외거래소코드, 공란:전체,NASD:미국,SEHK:홍콩,SHAA:중국,TKSE:일본,HASE:베트남
        "PDNO": itm_no,                         # 상품번호 공란:전체
        "SLL_BUY_DVSN_CD": dvsn,                # 매도매수구분코드 00(전체), 01(매도), 02(매수)
        "LOAN_DVSN_CD": "",                     # 대출구분코드 	01 : 외화, 02 : 원화
        "CTX_AREA_FK100": FK100,                # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK100": NK100                 # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
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

    tr_cont, FK100, NK100 = res.getHeader().tr_cont, res.getBody().ctx_area_fk100, res.getBody().ctx_area_nk100  # 페이징 처리 getHeader(), getBody() kis_auth.py 존재
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
        return get_overseas_inquire_period_trans(excg_cd, dvsn, itm_no, st_dt, ed_dt, "N", FK100, NK100, dataframe)


##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 일별거래내역합계 [해외주식-063]
##############################################################################################
# 해외주식 일별거래내역합계 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseas_inquire_period_trans_output2(excg_cd="", dvsn="", itm_no="", st_dt="", ed_dt="", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-stock/v1/trading/inquire-period-trans'
    tr_id = "CTOS4001R"

    t_cnt = 0

    params = {
        "CANO": kis.getTREnv().my_acct,  # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod,  # 계좌상품코드 2자리
        "ERLM_STRT_DT": st_dt,  # 조회시작일자 YYYYMMDD
        "ERLM_END_DT": ed_dt,  # 조회종료일자 YYYYMMDD
        "OVRS_EXCG_CD": excg_cd,  # 해외거래소코드, 공란:전체,NASD:미국,SEHK:홍콩,SHAA:중국,TKSE:일본,HASE:베트남
        "PDNO": itm_no,  # 상품번호 공란:전체
        "SLL_BUY_DVSN_CD": dvsn,  # 매도매수구분코드 00(전체), 01(매도), 02(매수)
        "LOAN_DVSN_CD": "",  # 대출구분코드 	01 : 외화, 02 : 원화
        "CTX_AREA_FK100": FK100,  # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK100": NK100  # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
    }

    res = kis._url_fetch(url, tr_id, tr_cont, params)

    if str(res.getBody().rt_cd) == "0":
        current_data = pd.DataFrame(res.getBody().output2, index=[0])
        dataframe = current_data
    else:
        print(res.getBody().msg_cd + "," + res.getBody().msg1)
        #print(res.getErrorCode() + "," + res.getErrorMessage())
        dataframe = None

    return dataframe


##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 결제기준잔고 [해외주식-064]
# 해외주식 결제기준잔고 API입니다.
# 한국투자 HTS(eFriend Plus) > [0829] 해외 결제기준잔고 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
#
# ※ 적용환율은 당일 매매기준이며, 현재가의 경우 지연된 시세로 평가되므로 실제매도금액과 상이할 수 있습니다.
# ※ 주문가능수량 : 보유수량 - 미결제 매도수량
# ※ 매입금액 계산 시 결제일의 최초고시환율을 적용하므로, 금일 최초고시환율을 적용하는 체결기준 잔고와는 상이합니다.
# ※ 해외증권 투자 및 업무문의 안내: 한국투자증권 해외투자지원부 02)3276-5300
##############################################################################################
# 해외주식 결제기준잔고 List를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output API 문서 참조 등
def get_overseas_inquire_paymt_stdr_balance(dv="03", dt="", dvsn="01", inqr_dvsn="00", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-stock/v1/trading/inquire-paymt-stdr-balance'
    tr_id = "CTRP6010R"

    t_cnt = 0

    if dt =="":
        dt = datetime.today().strftime("%Y%m%d")   # 기간손익 시작일자 값이 없으면 현재일자

    params = {
        "CANO": kis.getTREnv().my_acct,         # 종합계좌번호 8자리
        "ACNT_PRDT_CD": kis.getTREnv().my_prod, # 계좌상품코드 2자리
        "BASS_DT": dt,                          # 기준일자(YYYYMMDD)
        "WCRC_FRCR_DVSN_CD": dvsn,              # 원화외화구분코드 01 : 원화, 02 : 외화
        "INQR_DVSN_CD": inqr_dvsn               # 00 : 전체,01 : 일반해외주식,02 : 미니스탁
    }


    res = kis._url_fetch(url, tr_id, tr_cont, params)

    if str(res.getBody().rt_cd) == "0":
        if dv == "01":
            current_data = pd.DataFrame(res.getBody().output1)
        elif dv == "02":
            current_data = pd.DataFrame(res.getBody().output2)
        else:
            current_data = pd.DataFrame(res.getBody().output3, index=[0])
        dataframe = current_data
    else:
        print(res.getBody().msg_cd + "," + res.getBody().msg1)
        #print(res.getErrorCode() + "," + res.getErrorMessage())
        dataframe = None

    return dataframe






























#====|  [해외주식] 기본시세  |============================================================================================================================

##############################################################################################
# [해외주식] 기본시세 > 해외주식 현재체결가
##############################################################################################
def get_overseas_price_quot_price(excd="", itm_no="", tr_cont="", dataframe=None):
    url = '/uapi/overseas-price/v1/quotations/price'
    tr_id = "HHDFS00000300" # 해외주식 현재체결가

    params = {
        "AUTH": "",             # 사용자권한정보 : 사용안함
        "EXCD": excd,           # 거래소코드 	HKS : 홍콩,NYS : 뉴욕,NAS : 나스닥,AMS : 아멕스,TSE : 도쿄,SHS : 상해,SZS : 심천,SHI : 상해지수
                                #           SZI : 심천지수,HSX : 호치민,HNX : 하노이,BAY : 뉴욕(주간),BAQ : 나스닥(주간),BAA : 아멕스(주간)
        "SYMB": itm_no          # 종목번호
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output, index=[0])

    dataframe = current_data

    return dataframe

##############################################################################################
# [해외주식] 기본시세 > 해외주식 기간별시세
##############################################################################################
def get_overseas_price_quot_dailyprice(excd="", itm_no="", gubn="", bymd="", modp="0", tr_cont="", dataframe=None):
    url = '/uapi/overseas-price/v1/quotations/dailyprice'
    tr_id = "HHDFS76240000" # 해외주식 기간별시세

    if bymd is None:
        bymd = datetime.today().strftime("%Y%m%d")   # 종료일자 값이 없으면 현재일자

    params = {
        "AUTH": "",             # (사용안함) 사용자권한정보
        "EXCD": excd,           # 거래소코드 	HKS : 홍콩,NYS : 뉴욕,NAS : 나스닥,AMS : 아멕스,TSE : 도쿄,SHS : 상해,SZS : 심천,SHI : 상해지수
                                #           SZI : 심천지수,HSX : 호치민,HNX : 하노이,BAY : 뉴욕(주간),BAQ : 나스닥(주간),BAA : 아멕스(주간)
        "SYMB": itm_no,         # 종목번호
        "GUBN": gubn,           # 일/주/월구분 0:일. 1:주, 2:월
        "BYMD": bymd,           # 조회기준일자(YYYYMMDD) ※ 공란 설정 시, 기준일 오늘 날짜로 설정
        "MODP": modp,           # 수정주가반영여부 0 : 미반영, 1 : 반영
        "KEYB": ""              # (사용안함) NEXT KEY BUFF  응답시 다음값이 있으면 값이 셋팅되어 있으므로 다음 조회시 응답값 그대로 셋팅
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output2)

    dataframe = current_data

    return dataframe

###########################################################################
# [해외주식] 기본시세 > 해외주식 종목/지수/환율기간별시세(일/주/월/년) → 기본정보
###########################################################################
# 해외주식 종목/지수/환율기간별시세(일/주/월/년) API입니다.
# 해외지수 당일 시세의 경우 지연시세 or 종가시세가 제공됩니다.
# ※ 해당 API로 미국주식 조회 시, 다우30, 나스닥100, S&P500 종목만 조회 가능합니다.
#   더 많은 미국주식 종목 시세를 이용할 시에는, 해외주식기간별시세 API 사용 부탁드립니다.
###########################################################################
def get_overseas_price_quot_inquire_daily_price(div="N", itm_no="", inqr_strt_dt="", inqr_end_dt="", period="D", tr_cont="", dataframe=None):
    url = '/uapi/overseas-price/v1/quotations/inquire-daily-chartprice'
    tr_id = "FHKST03030100" # 해외주식 종목/지수/환율기간별시세(일/주/월/년)

    if inqr_strt_dt is None:
        inqr_strt_dt = datetime.today().strftime("%Y%m%d")   # 시작일자 값이 없으면 현재일자
    if inqr_end_dt is None:
        inqr_end_dt = datetime.today().strftime("%Y%m%d")    # 종료일자 값이 없으면 현재일자

    params = {
        "FID_COND_MRKT_DIV_CODE": div,             # 시장 분류 코드 N: 해외지수, X 환율, I: 국채, S:금선물
        "FID_INPUT_ISCD": itm_no,                  # 종목번호 ※ 해외주식 마스터 코드 참조 (포럼 > FAQ > 종목정보 다운로드 > 해외주식)
                                                   # ※ 해당 API로 미국주식 조회 시, 다우30, 나스닥100, S&P500 종목만 조회 가능합니다. 더 많은 미국주식 종목 시세를 이용할 시에는, 해외주식기간별시세 API 사용 부탁드립니다.
        "FID_INPUT_DATE_1": inqr_strt_dt,          # 시작일자(YYYYMMDD)
        "FID_INPUT_DATE_2": inqr_end_dt,           # 종료일자(YYYYMMDD)
        "FID_PERIOD_DIV_CODE": period              # 기간분류코드 D:일, W:주, M:월, Y:년
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output1, index=[0])

    dataframe = current_data

    return dataframe

##############################################################################################
# [해외주식] 기본시세 > 해외주식 종목/지수/환율기간별시세(일/주/월/년) → 일자별정보 (최대 30일까지 조회)
##############################################################################################
def get_overseas_price_quot_inquire_daily_chartprice(div="N", itm_no="", inqr_strt_dt="", inqr_end_dt="", period="D", tr_cont="", dataframe=None):
    url = '/uapi/overseas-price/v1/quotations/inquire-daily-chartprice'
    tr_id = "FHKST03030100" # 해외주식 종목/지수/환율기간별시세(일/주/월/년)

    if inqr_strt_dt is None:
        inqr_strt_dt = datetime.today().strftime("%Y%m%d")   # 시작일자 값이 없으면 현재일자
    if inqr_end_dt is None:
        inqr_end_dt = datetime.today().strftime("%Y%m%d")    # 종료일자 값이 없으면 현재일자

    params = {
        "FID_COND_MRKT_DIV_CODE": div,             # 시장 분류 코드 N: 해외지수, X 환율, I: 국채, S:금선물
        "FID_INPUT_ISCD": itm_no,                  # 종목번호 ※ 해외주식 마스터 코드 참조 (포럼 > FAQ > 종목정보 다운로드 > 해외주식)
                                                   # ※ 해당 API로 미국주식 조회 시, 다우30, 나스닥100, S&P500 종목만 조회 가능합니다. 더 많은 미국주식 종목 시세를 이용할 시에는, 해외주식기간별시세 API 사용 부탁드립니다.
        "FID_INPUT_DATE_1": inqr_strt_dt,          # 시작일자(YYYYMMDD)
        "FID_INPUT_DATE_2": inqr_end_dt,           # 종료일자(YYYYMMDD)
        "FID_PERIOD_DIV_CODE": period              # 기간분류코드 D:일, W:주, M:월, Y:년
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output2)

    dataframe = current_data

    return dataframe

###########################################################################
# [해외주식] 기본시세 > 해외주식조건검색 → 기본정보
###########################################################################
# 해외주식 조건검색 API입니다.
# # 현재 조건검색 결과값은 최대 100개까지 조회 가능합니다. 다음 조회(100개 이후의 값) 기능에 대해서는 개선검토 중에 있습니다.
# # ※ 그날 거래량이나 시세 형성이 안된 종목은 해외주식 기간별시세(HHDFS76240000)에서는 조회되지만
#    해외주식 조건검색(HHDFS76410000)에서 조회되지 않습니다. (EX. NAS AATC)
#
# [미국주식시세 이용시 유의사항]
# ■ 무료 실시간 시세(0분 지연) 제공
# ※ 무료(매수/매도 각 1호가) : 나스닥 마켓센터에서 거래되는 호가 및 호가 잔량 정보
# ※ 유료(매수/매도 각 1호가) : 미국 전체 거래소들의 통합 주문체결 및 최우선 호가
# ■ 무료 실시간 시세 서비스는 유료 실시간 시세 서비스 대비 평균 50% 수준에 해당하는 정보이므로
# 현재가/호가/순간체결량/차트 등에서 일시적·부분적 차이가 있을 수 있습니다.
# ■ 무료∙유료 모두 미국에 상장된 종목(뉴욕, 나스닥, 아멕스 등)의 시세를 제공하며, 동일한 시스템을 사용하여 주문∙체결됩니다.
# 단, 무료∙유료의 기반 데이터 차이로 호가 및 체결 데이터는 차이가 발생할 수 있고, 이로 인해 발생하는 손실에 대해서 당사가 책임지지 않습니다.
# ■ 무료 실시간 시세 서비스의 시가, 저가, 고가, 종가는 유료 실시간 시세 서비스와 다를 수 있으며,
# 종목별 과거 데이터(거래량, 시가, 종가, 고가, 차트 데이터 등)는 장 종료 후(오후 12시경) 유료 실시간 시세 서비스 데이터와 동일하게 업데이트됩니다.
# ■ 유료 실시간 시세 서비스는 신청 시 1~12개월까지 기간 선택 후 해당 요금을 일괄 납부하며,
# 해지 시 해지한 달의 말일까지 시세 제공 후 남은 기간 해당 금액이 환급되니 유의하시기 바랍니다.
# (출처: 한국투자증권 외화증권 거래설명서 - https://www.truefriend.com/main/customer/guide/Guide.jsp?&cmd=TF04ag010002¤tPage=1&num=64)
###########################################################################
def get_overseas_price_quot_inquire_search(div="02", excd="", pr_st="", pr_en="", rate_st="", rate_en="", vol_st="", vol_en="",
                                           per_st="", per_en="", eps_st="", eps_en="", amt_st="", amt_en="", shar_st="",
                                           shar_en="", valx_st="", valx_en="", tr_cont="", dataframe=None):
    url = '/uapi/overseas-price/v1/quotations/inquire-search'
    tr_id = "HHDFS76410000" # [해외주식] 기본시세 > 해외주식조건검색

    pr_yn = ""
    rate_yn = ""
    vol_yn = ""
    per_yn = ""
    eps_yn = ""
    amt_yn = ""
    shar_yn = ""
    valx_yn = ""
    if pr_st != "" and pr_en != "":
        pr_yn = "1"
    if rate_st != "" and rate_en != "":
        rate_yn = "1"
    if vol_st != "" and vol_en != "":
        vol_yn = "1"
    if per_st != "" and per_en != "":
        per_yn = "1"
    if eps_st != "" and eps_en != "":
        eps_yn = "1"
    if amt_st != "" and amt_en != "":
        amt_yn = "1"
    if shar_st != "" and shar_en != "":
        shar_yn = "1"
    if valx_st != "" and valx_en != "":
        valx_yn = "1"

    params = {
        "AUTH": "",	             # (사용안함)사용자권한정보(Null 값 설정)
        "EXCD": excd,	         # 거래소코드	NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄
        "CO_YN_PRICECUR": pr_yn, # 현재가선택조건	해당조건 사용시(1), 미사용시 필수항목아님
        "CO_ST_PRICECUR": pr_st, # 현재가시작범위가
        "CO_EN_PRICECUR": pr_en, # 현재가끝범위가
        "CO_YN_RATE": rate_yn,	 # 등락율선택조건	해당조건 사용시(1), 미사용시 필수항목아님
        "CO_ST_RATE": rate_st,	 # 등락율시작율
        "CO_EN_RATE": rate_en,	 # 등락율끝율
        "CO_YN_VOLUME": vol_yn,	 # 거래량선택조건	해당조건 사용시(1), 미사용시 필수항목아님
        "CO_ST_VOLUME": vol_st,  # 거래량시작량
        "CO_EN_VOLUME": vol_en,	 # 거래량끝량
        "CO_YN_PER": per_yn,	 # PER선택조건 해당조건 사용시(1), 미사용시 필수항목아님
        "CO_ST_PER": per_st,	 # PER시작
        "CO_EN_PER": per_en,	 # PER끝
        "CO_YN_EPS": eps_yn,	 # EPS선택조건 해당조건 사용시(1), 미사용시 필수항목아님
        "CO_ST_EPS": eps_st,	 # EPS시작
        "CO_EN_EPS": eps_en,	 # EPS끝
        "CO_YN_AMT": amt_yn,	 # 거래대금선택조건 해당조건 사용시(1), 미사용시 필수항목아님
        "CO_ST_AMT": amt_st,	 # 거래대금시작금
        "CO_EN_AMT": amt_en,	 # 거래대금끝금
        "CO_YN_SHAR": shar_yn,	 # 발행주식수선택조건 해당조건 사용시(1), 미사용시 필수항목아님
        "CO_ST_SHAR": shar_st,	 # 발행주식시작수
        "CO_EN_SHAR": shar_en,	 # 발행주식끝수
        "CO_YN_VALX": valx_yn,	 # 시가총액선택조건
        "CO_ST_VALX": valx_st,	 # 시가총액시작액
        "CO_EN_VALX": valx_en,	 # 시가총액끝액
        "KEYB": ""  # (사용안함)NEXT KEY BUFF
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    if div == "01":
        current_data = pd.DataFrame(res.getBody().output2)
    else:
        current_data = pd.DataFrame(res.getBody().output1, index=[0])
    dataframe = current_data

    return dataframe


###########################################################################
# [해외주식] 기본시세 > 해외결제일자조회[해외주식]
###########################################################################
# 해외결제일자조회 API입니다.
###########################################################################
def get_overseas_price_quot_countries_holiday(dt="", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-stock/v1/quotations/countries-holiday'
    tr_id = "CTOS5011R"    # [해외주식] 기본시세 > 해외결제일자조회

    if dt == "":
        dt = datetime.today().strftime("%Y%m%d")   # 시작일자 값이 없으면 현재일자

    params = {
        "TRAD_DT": dt,	       # 기준일자(YYYYMMDD)
        "CTX_AREA_FK": FK100,  # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK 값 : 다음페이지 조회시(2번째부터)
        "CTX_AREA_NK": NK100   # 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK 값 : 다음페이지 조회시(2번째부터)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)  # API 호출

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output)

    # Append to the existing DataFrame if it exists
    if dataframe is not None:
        dataframe = pd.concat([dataframe, current_data], ignore_index=True)  #
    else:
        dataframe = current_data

    tr_cont, FK100, NK100 = res.getHeader().tr_cont, res.getBody().ctx_area_fk, res.getBody().ctx_area_nk  # 페이징 처리 getHeader(), getBody() kis_auth.py 존재
    # print(tr_cont, FK100, NK100)

    if tr_cont == "D" or tr_cont == "E":  # 마지막 페이지
        print("The End")
        return dataframe
    elif tr_cont == "F" or tr_cont == "M":  # 다음 페이지 존재하는 경우 자기 호출 처리
        print('Call Next')
        time.sleep(0.1)  # 시스템 안정적 운영을 위하여 반드시 지연 time 필요
        return get_overseas_price_quot_countries_holiday(dt, "N", FK100, NK100, dataframe)


##############################################################################################
# [해외주식] 기본시세 > 해외주식 현재가상세
# 개요
# 해외주식 현재가상세 API입니다.
# 해당 API를 활용하여 해외주식 종목의 매매단위(vnit), 호가단위(e_hogau), PER, PBR, EPS, BPS 등의 데이터를 확인하실 수 있습니다.
# 해외주식 시세는 무료시세(지연시세)만이 제공되며, API로는 유료시세(실시간시세)를 받아보실 수 없습니다.
# ※ 지연시세 지연시간 : 미국 - 실시간무료(0분지연) / 홍콩, 베트남, 중국 - 15분지연 / 일본 - 15분지연
#    미국의 경우 0분지연시세로 제공되나, 장중 당일 시가는 상이할 수 있으며, 익일 정정 표시됩니다.
# ※ 추후 HTS(efriend Plus) [7781] 시세신청(실시간) 화면에서 유료 서비스 신청 시 실시간 시세 수신할 수 있도록 변경 예정
# [미국주식시세 이용시 유의사항]
# ■ 무료 실시간 시세(0분 지연) 제공
# ※ 무료(매수/매도 각 1호가) : 나스닥 마켓센터에서 거래되는 호가 및 호가 잔량 정보
# ※ 유료(매수/매도 각 1호가) : 미국 전체 거래소들의 통합 주문체결 및 최우선 호가
# ■ 무료 실시간 시세 서비스는 유료 실시간 시세 서비스 대비 평균 50% 수준에 해당하는 정보이므로
# 현재가/호가/순간체결량/차트 등에서 일시적·부분적 차이가 있을 수 있습니다.
# ■ 무료∙유료 모두 미국에 상장된 종목(뉴욕, 나스닥, 아멕스 등)의 시세를 제공하며, 동일한 시스템을 사용하여 주문∙체결됩니다.
# 단, 무료∙유료의 기반 데이터 차이로 호가 및 체결 데이터는 차이가 발생할 수 있고, 이로 인해 발생하는 손실에 대해서 당사가 책임지지 않습니다.
# ■ 무료 실시간 시세 서비스의 시가, 저가, 고가, 종가는 유료 실시간 시세 서비스와 다를 수 있으며,
# 종목별 과거 데이터(거래량, 시가, 종가, 고가, 차트 데이터 등)는 장 종료 후(오후 12시경) 유료 실시간 시세 서비스 데이터와 동일하게 업데이트됩니다.
# ■ 유료 실시간 시세 서비스는 신청 시 1~12개월까지 기간 선택 후 해당 요금을 일괄 납부하며,
# 해지 시 해지한 달의 말일까지 시세 제공 후 남은 기간 해당 금액이 환급되니 유의하시기 바랍니다.
# (출처: 한국투자증권 외화증권 거래설명서 - https://www.truefriend.com/main/customer/guide/Guide.jsp?&cmd=TF04ag010002¤tPage=1&num=64)
##############################################################################################
# 해외주식 현재가상세 시세 Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output
def get_overseas_price_quot_price_detail(excd="", itm_no="", tr_cont="", dataframe=None):
    url = '/uapi/overseas-price/v1/quotations/price-detail'
    tr_id = "HHDFS76200200" # 해외주식 현재가상세

    params = {
        "AUTH": "",         # 시장 분류 코드 	J : 주식/ETF/ETN, W: ELW
        "EXCD": excd,       # 	종목번호 (6자리) ETN의 경우, Q로 시작 (EX. Q500001)
        "SYMB": itm_no      # 종목번호 (6자리) ETN의 경우, Q로 시작 (EX. Q500001)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output, index=[0])  # getBody() kis_auth.py 존재

    dataframe = current_data

    return dataframe

##############################################################################################
# [해외주식] 기본시세 > 해외주식분봉조회
# 해외주식분봉조회 API입니다.
# 실전계좌의 경우, 최근 120건까지 확인 가능합니다.
#
# ※ 해외주식 분봉은 정규장만 제공됩니다.
#
# [미국주식시세 이용시 유의사항]
# ■ 무료 실시간 시세(0분 지연) 제공
# ※ 무료(매수/매도 각 1호가) : 나스닥 마켓센터에서 거래되는 호가 및 호가 잔량 정보
# ※ 유료(매수/매도 각 1호가) : 미국 전체 거래소들의 통합 주문체결 및 최우선 호가
# ■ 무료 실시간 시세 서비스는 유료 실시간 시세 서비스 대비 평균 50% 수준에 해당하는 정보이므로
# 현재가/호가/순간체결량/차트 등에서 일시적·부분적 차이가 있을 수 있습니다.
# ■ 무료∙유료 모두 미국에 상장된 종목(뉴욕, 나스닥, 아멕스 등)의 시세를 제공하며, 동일한 시스템을 사용하여 주문∙체결됩니다.
# 단, 무료∙유료의 기반 데이터 차이로 호가 및 체결 데이터는 차이가 발생할 수 있고, 이로 인해 발생하는 손실에 대해서 당사가 책임지지 않습니다.
# ■ 무료 실시간 시세 서비스의 시가, 저가, 고가, 종가는 유료 실시간 시세 서비스와 다를 수 있으며,
# 종목별 과거 데이터(거래량, 시가, 종가, 고가, 차트 데이터 등)는 장 종료 후(오후 12시경) 유료 실시간 시세 서비스 데이터와 동일하게 업데이트됩니다.
# ■ 유료 실시간 시세 서비스는 신청 시 1~12개월까지 기간 선택 후 해당 요금을 일괄 납부하며,
# 해지 시 해지한 달의 말일까지 시세 제공 후 남은 기간 해당 금액이 환급되니 유의하시기 바랍니다.
# (출처: 한국투자증권 외화증권 거래설명서 - https://www.truefriend.com/main/customer/guide/Guide.jsp?&cmd=TF04ag010002¤tPage=1&num=64)
##############################################################################################
# 해외주식 해외주식분봉조회 시세 Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output
def get_overseas_price_quot_inquire_time_itemchartprice(div="02", excd="", itm_no="", nmin="", pinc="0", tr_cont="", dataframe=None):
    url = '/uapi/overseas-price/v1/quotations/inquire-time-itemchartprice'
    tr_id = "HHDFS76950200" # 해외주식 해외주식분봉조회

    params = {
        "AUTH": "",         # 시장 분류 코드 	J : 주식/ETF/ETN, W: ELW
        "EXCD": excd,       # 거래소코드 	HKS : 홍콩,NYS : 뉴욕,NAS : 나스닥,AMS : 아멕스,TSE : 도쿄,SHS : 상해,SZS : 심천,SHI : 상해지수
                            #           SZI : 심천지수,HSX : 호치민,HNX : 하노이,BAY : 뉴욕(주간),BAQ : 나스닥(주간),BAA : 아멕스(주간)
        "SYMB": itm_no,     # 종목코드(ex. TSLA)
        "NMIN": nmin,       # 분갭 분단위(1: 1분봉, 2: 2분봉, ...)
        "PINC": pinc,       # 전일포함여부(0:당일 1:전일포함)
        "NEXT": "",         # (사용안함)다음여부
        "NREC": "120",      # 요청갯수 레코드요청갯수 (최대 120)
        "FILL": "",         # (사용안함)미체결채움구분
        "KEYB": ""          # (사용안함)NEXT KEY BUFF
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    if div == "02":
        current_data = pd.DataFrame(res.getBody().output2)
    else:
        current_data = pd.DataFrame(res.getBody().output1, index=[0])

    dataframe = current_data

    return dataframe


##############################################################################################
# [해외주식] 기본시세 > 해외지수분봉조회
# 해외지수분봉조회 API입니다.
# 실전계좌의 경우, 최근 102건까지 확인 가능합니다.
##############################################################################################
# 해외주식 해외지수분봉조회 시세 Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output
def get_overseas_price_quot_inquire_time_indexchartprice(div="01", code="N", iscd="", tm_dv="0", inc="N", tr_cont="", dataframe=None):
    url = '/uapi/overseas-price/v1/quotations/inquire-time-indexchartprice'
    tr_id = "FHKST03030200" # 해외주식 해외지수분봉조회

    params = {
        "FID_COND_MRKT_DIV_CODE": code,           # 시장 분류 코드	 N 해외지수, X 환율, KX 원화환율
        "FID_INPUT_ISCD": iscd,                   # 종목코드
        "FID_HOUR_CLS_CODE": tm_dv,               # 시간 구분 코드 0: 정규장, 1: 시간외
        "FID_PW_DATA_INCU_YN": inc                # 과거 데이터 포함 여부 (Y/N)
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    if div == "02":
        current_data = pd.DataFrame(res.getBody().output2)
    else:
        current_data = pd.DataFrame(res.getBody().output1, index=[0])

    dataframe = current_data

    return dataframe


##############################################################################################
# [해외주식] 기본시세 > 해외주식 상품기본정보
##############################################################################################
# 해외주식 상품기본정보 시세 Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output
def get_overseas_price_search_info(itm_no="", prdt_type_cd="", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-price/v1/quotations/search-info'
    tr_id = "CTPF1702R" # 해외주식 상품기본정보

    params = {
        "PDNO": itm_no,                 # 종목번호 (6자리) ETN의 경우, Q로 시작 (EX. Q500001)
        "PRDT_TYPE_CD": prdt_type_cd    # 종목유형 	512 미국 나스닥 / 513 미국 뉴욕 / 529 미국 아멕스 / 515 일본 / 501 홍콩 / 543 홍콩CNY / 558 홍콩USD
                                        #           507 베트남 하노이 / 508 베트남 호치민 / 551 중국 상해A / 552 중국 심천A
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output, index=[0])  # getBody() kis_auth.py 존재

    dataframe = current_data

    return dataframe


##############################################################################################
# [해외주식] 기본시세 > 해외주식 현재가 1호가
# 해외주식 현재가 호가 API입니다.
# 한국투자 HTS(eFriend Plus) > [7620] 해외주식 현재가 화면에서 "왼쪽 호가 창" 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
#
# ※ 지연시세 지연시간 : 미국 - 실시간무료(0분지연, 나스닥 마켓센터에서 거래되는 호가 및 호가 잔량 정보)
#                                 홍콩, 베트남, 중국 - 15분지연 / 일본 - 15분지연
#    미국의 경우 0분지연시세로 제공되나, 장중 당일 시가는 상이할 수 있으며, 익일 정정 표시됩니다.
# ※ 추후 HTS(efriend Plus) [7781] 시세신청(실시간) 화면에서 유료 서비스 신청 시 유료시세 수신할 수 있도록 변경 예정
#
# [미국주식시세 이용시 유의사항]
# ■ 무료 실시간 시세(0분 지연) 제공
# ※ 무료(매수/매도 각 1호가) : 나스닥 마켓센터에서 거래되는 호가 및 호가 잔량 정보
# ※ 유료(매수/매도 각 1호가) : 미국 전체 거래소들의 통합 주문체결 및 최우선 호가
# ■ 무료 실시간 시세 서비스는 유료 실시간 시세 서비스 대비 평균 50% 수준에 해당하는 정보이므로
# 현재가/호가/순간체결량/차트 등에서 일시적·부분적 차이가 있을 수 있습니다.
# ■ 무료∙유료 모두 미국에 상장된 종목(뉴욕, 나스닥, 아멕스 등)의 시세를 제공하며, 동일한 시스템을 사용하여 주문∙체결됩니다.
# 단, 무료∙유료의 기반 데이터 차이로 호가 및 체결 데이터는 차이가 발생할 수 있고, 이로 인해 발생하는 손실에 대해서 당사가 책임지지 않습니다.
# ■ 무료 실시간 시세 서비스의 시가, 저가, 고가, 종가는 유료 실시간 시세 서비스와 다를 수 있으며,
# 종목별 과거 데이터(거래량, 시가, 종가, 고가, 차트 데이터 등)는 장 종료 후(오후 12시경) 유료 실시간 시세 서비스 데이터와 동일하게 업데이트됩니다.
# ■ 유료 실시간 시세 서비스는 신청 시 1~12개월까지 기간 선택 후 해당 요금을 일괄 납부하며,
# 해지 시 해지한 달의 말일까지 시세 제공 후 남은 기간 해당 금액이 환급되니 유의하시기 바랍니다.
# (출처: 한국투자증권 외화증권 거래설명서 - https://www.truefriend.com/main/customer/guide/Guide.jsp?&cmd=TF04ag010002¤tPage=1&num=64)
##############################################################################################
# 해외주식 해외주식 현재가 1호가 Object를 DataFrame 으로 반환
# Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
# Output: DataFrame (Option) output
def get_overseas_price_inquire_asking_price(div="", excd="", itm_no="", tr_cont="", FK100="", NK100="", dataframe=None):
    url = '/uapi/overseas-price/v1/quotations/inquire-asking-price'
    tr_id = "HHDFS76200100" # 해외주식 현재가 1호가

    params = {
        "AUTH": "",             # (사용안함) 공백
        "EXCD": excd,           # 거래소코드
        "SYMB": itm_no          # 종목코드
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    if div == "01":
        current_data = pd.DataFrame(res.getBody().output1, index=[0])  # 01:기본시세
    elif div == "02":
        current_data = pd.DataFrame(res.getBody().output2, index=[0])  # 02:1호가
    else:
        current_data = pd.DataFrame(res.getBody().output3, index=[0])  # getBody() kis_auth.py 존재


    dataframe = current_data

    return dataframe



