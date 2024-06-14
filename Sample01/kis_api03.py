# -*- coding: utf-8 -*-
"""
Created on Tue Feb 15 07:56:54 2022
"""
#kis_api module 을 찾을 수 없다는 에러가 나는 경우 sys.path에 kis_auth.py, kis_ovrseastk.py 가 있는 폴더를 추가해준다.
import kis_auth as ka
import kis_ovrseastk as kb

import pandas as pd

import sys

# 토큰 발급
ka.auth()

#====|  [해외주식] 기본시세  |============================================================================================================================

# [해외주식] 기본시세 > 해외주식 현재체결가
rt_data = kb.get_overseas_price_quot_search_info(excd="NAS", itm_no="AAPL")
print(rt_data)    # 해외주식 현재체결가

# [해외주식] 기본시세 > 해외주식 기간별시세  ※ 기준일(bymd) 지정일자 이후 100일치 조회, 미입력시 당일자 기본 셋팅
rt_data = kb.get_overseas_price_quot_dailyprice(excd="NAS", itm_no="AAPL", gubn="0", bymd="")
print(rt_data)    # 해외주식 기간별시세

# [해외주식] 기본시세 > 해외주식 종목/지수/환율기간별시세(일/주/월/년)  ※ 기준일(bymd) 지정일자 이후 100일치 조회, 미입력시 당일자 기본 셋팅
rt_data = kb.get_overseas_price_quot_inquire_daily_price(div="N", itm_no="AAPL", inqr_strt_dt="", inqr_end_dt="", period="D")
rt_data = kb.get_overseas_price_quot_inquire_daily_chartprice(div="N", itm_no="AAPL", inqr_strt_dt="20240605", inqr_end_dt="20240610", period="D")
print(rt_data)    # 해외주식 종목/지수/환율기간별시세(일/주/월/년)

# [해외주식] 기본시세 > 해외주식조건검색  div 01 : 검색결과종목수, 02:검색결과종목리스트
rt_data = kb.get_overseas_price_quot_inquire_search(div="02", excd="NAS", pr_st="160", pr_en="170")
print(rt_data)    # 해외주식조건검색

# [해외주식] 기본시세 > 해외결재일자조회
rt_data = kb.get_overseas_price_quot_countries_holiday(dt="")
print(rt_data)    # 해외결재일자조회

# [해외주식] 기본시세 > 해외주식 현재가상세
rt_data = kb.get_overseas_price_quot_price_detail(excd="NAS", itm_no="AAPL")
print(rt_data)    # 해외주식 현재가상세

# [해외주식] 기본시세 > 해외주식 해외주식분봉조회 div- 02 : 분봉데이터, 01:시장별장운영시간
rt_data = kb.get_overseas_price_quot_inquire_time_itemchartprice(div="02", excd="NAS", itm_no="AAPL", nmin="", pinc="0")
print(rt_data)    # 해외주식 해외주식분봉조회

# [해외주식] 기본시세 > 해외주식 해외지수분봉조회 div- 02 : 분봉데이터, 01:지수정보
rt_data = kb.get_overseas_price_quot_inquire_time_indexchartprice(div="02", code="N", iscd="SPX", tm_dv="0", inc="Y")
print(rt_data)    # 해외주식 해외지수분봉조회
