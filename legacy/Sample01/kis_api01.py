# -*- coding: utf-8 -*-
"""
Created on Tue Feb 15 07:56:54 2022
"""
#kis_api module 을 찾을 수 없다는 에러가 나는 경우 sys.path에 kis_api.py 가 있는 폴더를 추가해준다.
import kis_auth as ka
import kis_domstk as kb

import pandas as pd

import sys

# 토큰 발급
ka.auth()


#====|  국내주식(kis_domstk) import 파일을 하신후 프로그램에서 필요한 API 호출 샘플 아래 참고하시기 바랍니다.  |=====================
#====|  국내주식(kis_domstk) import 파일을 하신후 프로그램에서 필요한 API 호출 샘플 아래 참고하시기 바랍니다.  |=====================

#====|  국내선물옵션, 해외주식, 해외선물옵션, 채권 등 지속적으로 추가하도록 하겠습니다. 2024.05.16 KIS Developers Team  |======================

#====|  [국내주식] 주문/계좌  |============================================================================================================================

# [국내주식] 주문/계좌 > 주식현금주문 (매수매도구분 buy,sell + 종목번호 6자리 + 주문수량 + 주문단가)
# 지정가 기준이며 시장가 옵션(주문구분코드)을 사용하는 경우 kis_domstk.py get_order_cash 수정요망!
rt_data = kb.get_order_cash(ord_dv="buy",itm_no="071050", qty=10, unpr=65000)
print(rt_data.KRX_FWDG_ORD_ORGNO + "+" + rt_data.ODNO + "+" + rt_data.ORD_TMD) # 주문접수조직번호+주문접수번호+주문시각

# [국내주식] 주문/계좌 > 주식주문(정정취소) (한국거래소전송주문조직번호 5자리+원주문번호 10자리('0'을 채우지 않아도됨)+정정취소구분코드+정정및취소주문수량+잔량전부주문여부)
# 지정가 기준이며 시장가 옵션(주문구분코드)을 사용하는 경우 kis_domstk.py get_order_rvsecncl 수정요망!
rt_data = kb.get_order_rvsecncl(ord_orgno="06010", orgn_odno="0000224003", ord_dvsn="00", rvse_cncl_dvsn_cd="01", ord_qty=0, ord_unpr=64900, qty_all_ord_yn="Y")
print(rt_data.KRX_FWDG_ORD_ORGNO + "+" + rt_data.ODNO + "+" + rt_data.ORD_TMD) # 주문접수조직번호+주문접수번호+주문시각

# [국내주식] 주문/계좌 > 주식정정취소가능주문내역조회
rt_data = kb.get_inquire_psbl_rvsecncl_lst()
print(rt_data)

# [국내주식] 주문/계좌 > 주식일별주문체결(현황)조회
# dv="01"   01:3개월 이내 국내주식체결내역 (월단위 ex: 2024.04.25 이면 2024.01월~04월조회)
# dv="02"   02:3개월 이전 국내주식체결내역 (월단위 ex: 2024.04.25 이면 2024.01월이전)
rt_data = kb.get_inquire_daily_ccld_obj(dv="01")
print(rt_data)

# [국내주식] 주문/계좌 > 주식일별주문체결(내역)조회
# dv="01"   01:3개월 이내 국내주식체결내역 (월단위 ex: 2024.04.25 이면 2024.01월~04월조회)
# dv="02"   02:3개월 이전 국내주식체결내역 (월단위 ex: 2024.04.25 이면 2024.01월이전)
rt_data = kb.get_inquire_daily_ccld_lst(dv="01")
print(rt_data)

# [국내주식] 주문/계좌 > 주식잔고조회 (잔고현황)
rt_data = kb.get_inquire_balance_obj()
print(rt_data)

# [국내주식] 주문/계좌 > 주식잔고조회 (보유종목리스트)
rt_data = kb.get_inquire_balance_lst()
print(rt_data)


# [국내주식] 주문/계좌 > 매수가능조회 (종목번호 5자리 + 종목단가)
rt_data = kb.get_inquire_psbl_order(pdno="", ord_unpr=0)
ord_psbl_cash_value = rt_data.loc[0, 'ord_psbl_cash'] # ord_psbl_cash	주문가능현금
ord_psbl_cash_value = rt_data.loc[0, 'nrcvb_buy_amt'] # nrcvb_buy_amt	미수없는매수가능금액
print(rt_data)

# [국내주식] 주문/계좌 > 주식예약주문 (매수매도구분 buy,sell + 종목번호 6자리 + 주문수량 + 주문단가 + 주문구분코드 )
# 주문구분코드 : 00 : 지정가 01 : 시장가 02 : 조건부지정가 05 : 장전 시간외
rt_data = kb.get_order_resv(ord_dv="buy", itm_no="052400", qty=100, unpr=12650, ord_dvsn_cd="01")
print(rt_data.RSVN_ORD_SEQ) # 예약주문순번

# [국내주식] 주문/계좌 > 주식예약주문(취소) (예약주문순번)
rt_data = kb.get_order_resv_cncl(rsvn_ord_seq="93601")
print(rt_data)

# [국내주식] 주문/계좌 > 주식예약주문(정정)  (종목번호 6자리 + 주문수량 + 주문단가 + 매도매수구분코드 + 주문구분코드 + 주문대상잔고구분코드 + 예약주문순번)
# 매도매수구분코드 01 : 매도 02 : 매수
# 주문구분코드 00 : 지정가  01 : 시장가  02 : 조건부지정가  05 : 장전 시간외
# 주문대상잔고구분코드 10 : 현금  12 : 주식담보대출  14 : 대여상환   21 : 자기융자신규 .........
rt_data = kb.get_order_resv_rvse(pdno="052400", ord_qty=1, ord_unpr=12700, sll_buy_dvsn_cd="02", ord_dvsn="00", ord_objt_cblc_dvsn_cd="", rsvn_ord_seq=93605)
print(rt_data)

# [국내주식] 주문/계좌 > 주식예약주문조회[v1_국내주식-020] (조회시작일자 + 조회종료일자)
rt_data = kb.get_order_resv_ccnl(inqr_strt_dt="20240429", inqr_end_dt="20240430")
print(rt_data)

# [국내주식] 주문/계좌 > 주식잔고조회_실현손익[v1_국내주식-041]
rt_data = kb.get_inquire_balance_rlz_pl_obj()
print(rt_data)
rt_data = kb.get_inquire_balance_rlz_pl_lst()
print(rt_data)

# [국내주식] 주문/계좌 > 신용매수가능조회
rt_data = kb.get_inquire_credit_psamount()
print(rt_data)

# [국내주식] 주문/계좌 > 기간별매매손익현황조회
rt_data = kb.get_inquire_period_trade_profit_obj()
print(rt_data)
rt_data = kb.get_inquire_period_trade_profit_lst()
print(rt_data)

# [국내주식] 주문/계좌 > 기간별손익일별합산조회
rt_data = kb.get_inquire_period_profit_obj()
print(rt_data)
rt_data = kb.get_inquire_period_profit_lst()
print(rt_data)




# [국내주식] 기본시세 > 주식현재가 시세 (종목번호 6자리)
rt_data = kb.get_inquire_price(itm_no="071050")
print(rt_data.stck_prpr+ " " + rt_data.prdy_vrss)    # 현재가, 전일대비

# [국내주식] 기본시세 > 주식현재가 체결 (종목번호 6자리)
rt_data = kb.get_inquire_ccnl(itm_no="071050")

# [국내주식] 기본시세 > 주식현재가 일자별 (종목번호 6자리 + 기간분류코드)
# 기간분류코드 	D : (일)최근 30거래일  W : (주)최근 30주   M : (월)최근 30개월
# 수정주가기준이며 수정주가미반영 기준을 원하시면 인자값 adj_prc_code="2" 추가
rt_data = kb.get_inquire_daily_price(itm_no="071050", period_code="M")

# [국내주식] 기본시세 > 주식현재가 호가 (종목번호 6자리)
rt_data = kb.get_inquire_asking_price_exp_ccn(itm_no="071050")

# [국내주식] 기본시세 > 주식현재가 예상체결 (출력구분="2" + 종목번호 6자리)
rt_data = kb.get_inquire_asking_price_exp_ccn(output_dv="2", itm_no="071050")

# [국내주식] 기본시세 > 주식현재가 투자자 (종목번호 6자리)
rt_data = kb.get_inquire_investor(itm_no="071050")

# [국내주식] 기본시세 > 주식현재가 회원사 (종목번호 6자리)
rt_data = kb.get_inquire_member(itm_no="071050")

# [국내주식] 기본시세 > 국내주식기간별시세(일/주/월/년) (현재)  (종목번호 6자리)
rt_data = kb.get_inquire_daily_itemchartprice(itm_no="071050")

# [국내주식] 기본시세 > 국내주식기간별시세(일/주/월/년) (기간별 데이터 Default는 일별이며 조회기간은 100일전(영업일수 아님)부터 금일까지)
rt_data = kb.get_inquire_daily_itemchartprice(output_dv="2", itm_no="071050")

# [국내주식] 기본시세 > 주식현재가 당일시간대별체결 (현재가 : 주식현재가, 전일대비, 전일대비율, 누적거래량,전일거래량, 대표시장한글명))
rt_data = kb.get_inquire_time_itemconclusion(itm_no="071050")

# [국내주식] 기본시세 > 주식현재가 당일시간대별체결 (시간대별체결내역)
rt_data = kb.get_inquire_time_itemconclusion(output_dv='2', itm_no="071050")  # 기준시각 미지정시 현재시각 이전 체결 내역이 30건 조회됨
rt_data = kb.get_inquire_time_itemconclusion(output_dv='2', itm_no="071050", inqr_hour='100000') # 지정 기준시각 이전 체결 내역이 30건 조회됨

# [국내주식] 기본시세 > 주식현재가 시간외현재주가 (시간외 현재가 : 주식현재가, 전일대비, 전일대비율, 누적거래량, 거래량, 거래대금, 단일가상한가 .... 등)
rt_data = kb.get_inquire_daily_overtimeprice(itm_no="071050")

# [국내주식] 기본시세 > 주식현재가 시간외일자별주가 (최근 30일)  (출력구분 + 종목번호 6자리)
rt_data = kb.get_inquire_daily_overtimeprice(output_dv='2', itm_no="071050")

# [국내주식] 기본시세 > 주식당일분봉조회  (종목번호 6자리)  (출력구분 + 종목번호 6자리)
rt_data = kb.get_inquire_time_itemchartprice(itm_no="071050")  #
rt_data = kb.get_inquire_time_itemchartprice(output_dv="2", itm_no="071050")

# [국내주식] 기본시세 > 주식현재가 시세2
rt_data = kb.get_inquire_daily_price_2(itm_no="071050")

# [국내주식] 기본시세 > ETF/ETN 현재가
rt_data = kb.get_quotations_inquire_price(itm_no="071050")

# [국내주식] 기본시세 > NAV 비교추이(종목)
rt_data = kb.get_quotations_nav_comparison_trend(itm_no="071050")   # ETF 종목 정보
rt_data = kb.get_quotations_nav_comparison_trend(output_dv="2", itm_no="071050") # ETF NAV 정보

# [국내주식] 업종/기타 > 국내휴장일조회
rt_data = kb.get_quotations_ch_holiday(dt="20240302")

print(rt_data)
