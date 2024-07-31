# -*- coding: utf-8 -*-
"""
Created on Tue Feb 15 07:56:54 2022
"""
#kis_api module 을 찾을 수 없다는 에러가 나는 경우 sys.path에 kis_api.py 가 있는 폴더를 추가해준다.
import kis_auth as ka
import kis_ovrseafuopt as kb

import pandas as pd

import sys

# 토큰 발급
ka.auth()

#====|  [해외선물옵션] 주문/계좌  |============================================================================================================================

# [해외선물옵션] 주문/계좌 > 해외선물옵션주문 (종목번호<6자리 5자리> + 매수매도구분ord_dv + 가격구분dvsn + 주문수량qty + 주문가격limt_pric + 주문가격stop_pric)
# 매수매도구분ord_dv  01 : 매도, 02 : 매수   # 가격구분dvsn : 	1.지정, 2. 시장, 3. STOP, 4 S/L
# 주문가격limt_pric : 지정가인 경우 가격 입력 * 시장가, STOP주문인 경우, 빈칸("") 입력
# 주문가격stop_pric : STOP 주문 가격 입력   * 시장가, 지정가인 경우, 빈칸("") 입력
rt_data = kb.get_overseasfuopt_order(itm_no="OESU24 C6000", ord_dv="02", dvsn="1", qty=1, limt_pric=13.75, stop_pric=0)
print(rt_data.ORD_DT + "+" + rt_data.ODNO) # 주문일자+주문접수번호

# [해외선물옵션] 주문/계좌 > 해외선물옵션 정정취소주문 (정정취소구분dvsn + 원주문일자ord_dt + 원주문번호orgn_odno + 주문가격limt_pric + 주문가격stop_pric + 청산주문가격lqd_limt_pric + 청산주문가격lqd_stop_pric)
rt_data = kb.get_overseasfuopt_order_rvsecncl(dvsn="01", ord_dt="", orgn_odno="", limt_pric=0, stop_pric=0, lqd_limt_pric=0, lqd_stop_pric=0)
print(rt_data.ORD_DT + "+" + rt_data.ODNO) # 주문일자+주문접수번호

# [해외선물옵션] 주문/계좌 > 해외선물옵션 정정취소주문 (정정취소구분dvsn + 원주문일자ord_dt + 원주문번호orgn_odno + 주문가격limt_pric + 주문가격stop_pric + 청산주문가격lqd_limt_pric + 청산주문가격lqd_stop_pric)
rt_data = kb.get_overseasfuopt_order_rvsecncl(dvsn="01", ord_dt="", orgn_odno="", limt_pric=0, stop_pric=0, lqd_limt_pric=0, lqd_stop_pric=0)
print(rt_data.ORD_DT + "+" + rt_data.ODNO) # 주문일자+주문접수번호

# [해외선물옵션] 주문/계좌 > 해외선물옵션 정정취소주문 (체결미체결구분ccld_dv + 매도매수구분코드ord_dv + 선물옵션구분fuop_dvsn)
# 체결미체결구분 01:전체,02:체결,03:미체결    # 매도매수구분코드 %%:전체,01:매도,02:매수     # 선물옵션구분 00:전체 / 01:선물 / 02:옵션
rt_data = kb.get_overseasfuopt_inquire_ccld(ccld_dv="01", ord_dv="%%", fuop_dvsn="00")
print(rt_data)

# [해외선물옵션] 주문/계좌 > 해외선물옵션 미결제내역조회(잔고) (선물옵션구분fuop_dvsn)
# 선물옵션구분 00:전체 / 01:선물 / 02:옵션
rt_data = kb.get_overseasfuopt_inquire_unpd(fuop_dvsn="00")
print(rt_data)

# [해외선물옵션] 주문/계좌 > 해외선물옵션 해외선물옵션 주문가능조회 (선물옵션구분fuop_dvsn)
# 선물옵션구분 00:전체 / 01:선물 / 02:옵션
rt_data = kb.get_overseasfuopt_inquire_psamount(itm_no="OESU24 C6000", dvsn="02", pric=0, ordyn="")
print(rt_data)

# [해외선물옵션] 주문/계좌 > 해외선물옵션 기간계좌손익 일별 (조회구분inqr_dvsn + 조회시작일자fr_dt + 조회종료일자to_dt + 통화코드crcy + 선물옵션구분fuop_dvsn")
# 조회구분코드 : 01 통화별, 02 종목별
rt_data = kb.get_overseasfuopt_inquire_period_ccld(inqr_dvsn="01", fr_dt="", to_dt="", crcy="%%%", fuop_dvsn="00")
print(rt_data)

# [해외선물옵션] 주문/계좌 > 해외선물옵션 일별 체결내역 (조회시작일자fr_dt + 조회종료일자to_dt + 선물옵션구분fuop_dvsn + 통화코드crcy + 매도매수구분코드dvsn)
rt_data = kb.get_overseasfuopt_inquire_daily_ccld(fr_dt="", to_dt="", fuop_dvsn="00", crcy="%%%", dvsn="%%")
print(rt_data)

# [해외선물옵션] 주문/계좌 > 해외선물옵션 예수금현황 (통화코드crcy + 조회일자inqr_dt)
rt_data = kb.get_overseasfuopt_inquire_deposit(crcy="%%%", inqr_dt="")
print(rt_data)

# [해외선물옵션] 주문/계좌 > 해외선물옵션 일별 주문내역 (조회시작일자fr_dt + 조회종료일자to_dt + 체결미체결구분ccld_dvsn + 매수매도구분dvsn + 선물옵션구분fuop_dvsn)
# ccld_dvsn  01:전체 / 02:체결 / 03:미체결         dvsn  %% : 전체 / 01 : 매도 / 02 : 매수       fuop_dvsn 	00:전체 / 01:선물 / 02:옵션
rt_data = kb.get_overseasfuopt_inquire_daily_order(fr_dt="20240401", to_dt="", ccld_dvsn="01", dvsn="%%", fuop_dvsn="00")
print(rt_data)

# [해외선물옵션] 주문/계좌 > 해외선물옵션 기간계좌거래내역 (조회시작일자fr_dt,  조회종료일자to_dt)
rt_data = kb.get_overseasfuopt_inquire_period_trans(fr_dt="20240101", to_dt="20240717")
print(rt_data)

# [해외선물옵션] 주문/계좌 > 해외선물옵션 증거금상세 (통화구분crcy + 조회일자inqr_dt)
rt_data = kb.get_overseasfuopt_inquire_margin_detail(crcy="TUS", inqr_dt="20240717")
print(rt_data)


#====|  [해외선물옵션] 기본시세  |============================================================================================================================

# [해외선물옵션] 기본시세 > 해외선물종목상세  (종목코드)
rt_data = kb.get_overseas_fuopt_stock_detail(itm_no="6EU24")
print(rt_data)    # 해외선물종목상세

# [해외선물옵션] 기본시세 > 해외선물종목현재가  (종목코드)
rt_data = kb.get_overseas_fuopt_inquire_price(itm_no="6EU24")
print(rt_data)    # 해외선물종목현재가

# [해외선물옵션] 기본시세 > 분봉조회  (종목코드 + 거래소시장코드 + 조회시작일 + 조회종료일 + 조회건수(120건) + 갭(5분))
# 조회일자 1주일 이내 (조회시작일~조회종료일)
rt_data = kb.get_overseas_fuopt_inquire_time_futurechartprice(itm_no="6EU24", exch="CME", st_dt="20240709", ed_dt="20240710", cnt="120", gap="5", idx="")
print(rt_data)    # 해외선물분봉조회

# [해외선물옵션] 기본시세 > 해외선물 체결추이(주간)[해외선물-017]  (종목코드 + 거래소시장코드 + 조회시작일 + 조회종료일)
# 조회일자 1주일 이내 (조회시작일~조회종료일)
rt_data = kb.get_overseas_fuopt_weekly_ccnl(itm_no="6EU24", exch="CME", st_dt="20240709", ed_dt="20240710")
print(rt_data)    # 체결추이(주간)

# [해외선물옵션] 기본시세 > 해외선물 체결추이(일간)[해외선물-018]  (종목코드 + 거래소시장코드 + 조회시작일 + 조회종료일)
# 조회일자 1주일 이내 (조회시작일~조회종료일)
rt_data = kb.get_overseas_fuopt_daily_ccnl(itm_no="6EU24", exch="CME", st_dt="20240707", ed_dt="20240710")
print(rt_data)    # 체결추이(일간)

# [해외선물옵션] 기본시세 > 해외선물 체결추이(틱)[해외선물-019]  (종목코드 + 거래소시장코드)
# 조회일자는 당일만 조회하도록 샘플코드 구성
rt_data = kb.get_overseas_fuopt_tick_ccnl(itm_no="6EU24", exch="CME")
print(rt_data)    # 체결추이(틱)

# [해외선물옵션] 기본시세 > 해외선물 체결추이(월간)[해외선물-020]  (종목코드 + 거래소시장코드 + 조회시작일 + 조회종료일)
# 조회일자 1주일 이내 (조회시작일~조회종료일)
rt_data = kb.get_overseas_fuopt_monthly_ccnl(itm_no="6EU24", exch="CME", st_dt="20240707", ed_dt="20240710")
print(rt_data)    # 체결추이(일간)

# [해외선물옵션] 기본시세 > 해외선물 호가 [해외선물-031]  (종목코드)
rt_data = kb.get_overseas_fuopt_inquire_asking_price(itm_no="6EU24")
print(rt_data)    # 해외선물 호가

# [해외선물옵션] 기본시세 > 해외선물 상품기본정보 [해외선물-023]  (종목코드)
rt_data = kb.get_overseas_fuopt_search_contract_detail(itm_no01="6EU24")
print(rt_data)    # 해외선물 상품기본정보

# [해외선물옵션] 기본시세 > 해외선물 장운영시간 [해외선물-030]  (클래스코드 + 거래소코드 + 옵션여부)
rt_data = kb.get_overseas_fuopt_market_time(clas="", excg="CME", opt="%")
print(rt_data)    # 해외선물 장운영시간

# [해외선물옵션] 기본시세 > 해외선물 미결제추이 [해외선물-029]  (상품 + 거래소코드 + 옵션여부)
# 상품(PROD_ISCD) : 상품 (GE, ZB, ZF,ZN,ZT), 금속(GC, PA, PL,SI, HG),농산물(CC, CT,KC, OJ, SB, ZC,ZL, ZM, ZO, ZR, ZS, ZW),
#                  에너지(CL, HO, NG, WBS), 지수(ES, NQ, TF, YM, VX), 축산물(GF, HE, LE), 통화(6A, 6B, 6C, 6E, 6J, 6N, 6S, DX)
# 100건씩 조회되면 다음 페이지 조회는 응답메시지 (bsop_date 일자 순으로) 마지막 응답 데이터 일자 +1일 일자 값셋팅(bsop_date)하여 조회
rt_data = kb.get_overseas_fuopt_investor_unpd_trend(iscd="CL", dt="20240612", kbn="0", ctskey="1")
print(rt_data)    # 해외선물 장운영시간

# [해외선물옵션] 기본시세 > 해외옵션 호가 [해외선물-033]  (조회구분 + 옵션종목코드)
# dv(조회구분) : 01 현재가, 02 호가
rt_data = kb.get_overseas_fuopt_opt_asking_price(dv="02", itm_no="OESU24 C6000")
print(rt_data)    # 해외옵션 호가
