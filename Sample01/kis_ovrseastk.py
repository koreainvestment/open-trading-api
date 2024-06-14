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


#====|  [해외주식] 기본시세  |============================================================================================================================

##############################################################################################
# [해외주식] 기본시세 > 해외주식 현재체결가
##############################################################################################
def get_overseas_price_quot_search_info(excd="", itm_no="", tr_cont="", dataframe=None):
    url = '/uapi/overseas-price/v1/quotations/search-info'
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
# ※ 무료(매수/매도 각 10호가) : 나스닥 마켓센터에서 거래되는 호가 및 호가 잔량 정보
# ■ 무료 실시간 시세 서비스는 유료 실시간 시세 서비스 대비 평균 50% 수준에 해당하는 정보이므로
# 현재가/호가/순간체결량/차트 등에서 일시적·부분적 차이가 있을 수 있습니다.
# ■ 무료∙유료 모두 미국에 상장된 종목(뉴욕, 나스닥, 아멕스 등)의 시세를 제공하며, 동일한 시스템을 사용하여 주문∙체결됩니다.
# 단, 무료∙유료의 기반 데이터 차이로 호가 및 체결 데이터는 차이가 발생할 수 있고, 이로 인해 발생하는 손실에 대해서 당사가 책임지지 않습니다.
# ■ 무료 실시간 시세 서비스의 시가, 저가, 고가, 종가는 유료 실시간 시세 서비스와 다를 수 있으며,
# 종목별 과거 데이터(거래량, 시가, 종가, 고가, 차트 데이터 등)는 장 종료 후(오후 12시경) 유료 실시간 시세 서비스 데이터와 동일하게 업데이트됩니다.
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
        return get_overseas_price_quot_countries_holiday(dt, "N", FK100, NK100, dataframe)


##############################################################################################
# [해외주식] 기본시세 > 해외주식 현재가상세
# 개요
# 해외주식 현재가상세 API입니다.
# 해당 API를 활용하여 해외주식 종목의 매매단위(vnit), 호가단위(e_hogau), PER, PBR, EPS, BPS 등의 데이터를 확인하실 수 있습니다.
# 해외주식 시세는 무료시세(지연시세)만이 제공되며, API로는 유료시세(실시간시세)를 받아보실 수 없습니다.
# ※ 지연시세 지연시간 : 미국 - 실시간무료(0분지연) / 홍콩, 베트남, 중국 - 15분지연 / 일본 - 20분지연
#    미국의 경우 0분지연시세로 제공되나, 장중 당일 시가는 상이할 수 있으며, 익일 정정 표시됩니다.
# ※ 추후 HTS(efriend Plus) [7781] 시세신청(실시간) 화면에서 유료 서비스 신청 시 실시간 시세 수신할 수 있도록 변경 예정
# [미국주식시세 이용시 유의사항]
# ■ 무료 실시간 시세(0분 지연) 제공
# ※ 무료(매수/매도 각 10호가) : 나스닥 마켓센터에서 거래되는 호가 및 호가 잔량 정보
# ■ 무료 실시간 시세 서비스는 유료 실시간 시세 서비스 대비 평균 50% 수준에 해당하는 정보이므로
# 현재가/호가/순간체결량/차트 등에서 일시적·부분적 차이가 있을 수 있습니다.
# ■ 무료∙유료 모두 미국에 상장된 종목(뉴욕, 나스닥, 아멕스 등)의 시세를 제공하며, 동일한 시스템을 사용하여 주문∙체결됩니다.
# 단, 무료∙유료의 기반 데이터 차이로 호가 및 체결 데이터는 차이가 발생할 수 있고, 이로 인해 발생하는 손실에 대해서 당사가 책임지지 않습니다.
# ■ 무료 실시간 시세 서비스의 시가, 저가, 고가, 종가는 유료 실시간 시세 서비스와 다를 수 있으며,
# 종목별 과거 데이터(거래량, 시가, 종가, 고가, 차트 데이터 등)는 장 종료 후(오후 12시경) 유료 실시간 시세 서비스 데이터와 동일하게 업데이트됩니다.
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
# ※ 무료(매수/매도 각 10호가) : 나스닥 마켓센터에서 거래되는 호가 및 호가 잔량 정보
# ■ 무료 실시간 시세 서비스는 유료 실시간 시세 서비스 대비 평균 50% 수준에 해당하는 정보이므로
# 현재가/호가/순간체결량/차트 등에서 일시적·부분적 차이가 있을 수 있습니다.
# ■ 무료∙유료 모두 미국에 상장된 종목(뉴욕, 나스닥, 아멕스 등)의 시세를 제공하며, 동일한 시스템을 사용하여 주문∙체결됩니다.
# 단, 무료∙유료의 기반 데이터 차이로 호가 및 체결 데이터는 차이가 발생할 수 있고, 이로 인해 발생하는 손실에 대해서 당사가 책임지지 않습니다.
# ■ 무료 실시간 시세 서비스의 시가, 저가, 고가, 종가는 유료 실시간 시세 서비스와 다를 수 있으며,
# 종목별 과거 데이터(거래량, 시가, 종가, 고가, 차트 데이터 등)는 장 종료 후(오후 12시경) 유료 실시간 시세 서비스 데이터와 동일하게 업데이트됩니다.
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
        "PRDT_TYPE_CD": prdt_type_cd    # 종목유형
    }
    res = kis._url_fetch(url, tr_id, tr_cont, params)

    # Assuming 'output' is a dictionary that you want to convert to a DataFrame
    current_data = pd.DataFrame(res.getBody().output, index=[0])  # getBody() kis_auth.py 존재

    dataframe = current_data

    return dataframe




