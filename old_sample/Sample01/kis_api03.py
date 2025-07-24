# -*- coding: utf-8 -*-
"""
Created on Tue Feb 15 07:56:54 2022
"""
#kis_api module 을 찾을 수 없다는 에러가 나는 경우 sys.path에 kis_api.py 가 있는 폴더를 추가해준다.
import kis_auth as ka
import kis_ovrseastk as kb

import pandas as pd

import sys

# 토큰 발급
ka.auth()


#====|  [해외주식] 주문/계좌  |============================================================================================================================

# [해외주식] 주문/계좌 > 주문 (매수매도구분 buy,sell + 종목코드6자리 + 주문수량 + 주문단가)
# 지정가 기준이며 시장가 옵션(주문구분코드)을 사용하는 경우 kis_ovrseastk.py get_overseas_order 수정요망!
#rt_data = kb.get_overseas_order(ord_dv="buy", excg_cd="NASD", itm_no="TSLA", qty=1, unpr=170)
#rt_data = kb.get_overseas_order(ord_dv="buy", excg_cd="NASD", itm_no="AAPL", qty=1, unpr=216.75)
rt_data = kb.get_overseas_order(ord_dv="buy", excg_cd="NASD", itm_no="NVDA", qty=1, unpr=123.3)
print(rt_data.KRX_FWDG_ORD_ORGNO + "+" + rt_data.ODNO + "+" + rt_data.ORD_TMD) # 주문접수조직번호+주문접수번호+주문시각

# [해외주식] 주문/계좌 > 정정취소주문 (해외거래소코드excg_cd + 종목코드itm_no + 주문번호orgn_odno + 정정취소구분rvse_cncl_dvsn_cd + 수량qty + 주문단가unpr)
# 지정가 기준이며 시장가 옵션(주문구분코드)을 사용하는 경우 kis_ovrseastk.py get_overseas_order 수정요망!
rt_data = kb.get_overseas_order_rvsecncl(excg_cd="NASD", itm_no="TSLA", orgn_odno="0030089601", rvse_cncl_dvsn_cd="02", qty=1, unpr=0)
print(rt_data) # 주문접수조직번호+주문접수번호+주문시각

# [해외주식] 주문/계좌 > 해외주식 미체결내역 (해외거래소코드)
# 해외거래소코드 NASD:나스닥,NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
rt_data = kb.get_overseas_inquire_nccs(excg_cd="NASD")
print(rt_data)

# [해외주식] 주문/계좌 > 해외주식 미체결전량취소주문 (해외거래소코드excg_cd + 종목코드itm_no)
# 해외거래소코드 NASD:나스닥,NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
rt_data = kb.get_overseas_order_allcncl(excg_cd="NASD", itm_no="")
print(rt_data)

# [해외주식] 주문/계좌 > 해외주식 잔고 현황
# 해외거래소코드 NASD:나스닥,NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
# 거래통화코드 - USD : 미국달러,HKD : 홍콩달러,CNY : 중국위안화,JPY : 일본엔화,VND : 베트남동
rt_data = kb.get_overseas_inquire_balance(excg_cd="NASD", crcy_cd="")
print(rt_data)

# [해외주식] 주문/계좌 > 해외주식 잔고 내역
# 해외거래소코드 NASD:나스닥,NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
# 거래통화코드 - USD : 미국달러,HKD : 홍콩달러,CNY : 중국위안화,JPY : 일본엔화,VND : 베트남동
rt_data = kb.get_overseas_inquire_balance(excg_cd="NASD", crcy_cd="")
print(rt_data)

# [해외주식] 주문/계좌 > 해외주식 주문체결내역
# 해외거래소코드 NASD:미국시장 전체(나스닥,뉴욕,아멕스),NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
rt_data = kb.get_overseas_inquire_ccnl(st_dt="", ed_dt="")
print(rt_data)

# [해외주식] 주문/계좌 > 해외주식 체결기준현재잔고
# dv : 01 보유종목, 02 외화잔고, 03 체결기준현재잔고
# dvsn : 01 원화, 02 외화
# natn 국가코드 : 000 전체,840 미국,344 홍콩,156 중국,392 일본,704 베트남
# mkt 거래시장코드 [Request body NATN_CD 000 설정]
# 00 : 전체 , (NATN_CD 840 인경우) 00:전체,01:나스닥(NASD),02:뉴욕거래소(NYSE),03:미국(PINK SHEETS),04:미국(OTCBB),05:아멕스(AMEX) (다른시장 API문서 참조)
rt_data = kb.get_overseas_inquire_present_balance(dv="02", dvsn="01", natn="000", mkt="00", inqr_dvsn="00")
print(rt_data)

# [해외주식] 주문/계좌 > 미국주간주문 (매수매도구분 buy,sell + 종목번호 + 주문수량 + 주문단가)
# 지정가 기준이며 시장가 옵션(주문구분코드)을 사용하는 경우 kis_ovrseastk.py get_overseas_order 수정요망!
#rt_data = kb.get_overseas_daytime_order(ord_dv="buy", excg_cd="NASD", itm_no="TSLA", qty=1, unpr=251)
#rt_data = kb.get_overseas_daytime_order(ord_dv="buy", excg_cd="NASD", itm_no="AAPL", qty=1, unpr=216.75)
rt_data = kb.get_overseas_daytime_order(ord_dv="buy", excg_cd="NASD", itm_no="NVDA", qty=1, unpr=123.3)
print(rt_data.KRX_FWDG_ORD_ORGNO + "+" + rt_data.ODNO + "+" + rt_data.ORD_TMD) # 주문접수조직번호+주문접수번호+주문시각

# [해외주식] 주문/계좌 > 미국주간정정취소 (해외거래소코드excg_cd + 종목코드itm_no + 주문번호orgn_odno + 정정취소구분rvse_cncl_dvsn_cd + 수량qty + 주문단가unpr)
# 지정가 기준이며 시장가 옵션(주문구분코드)을 사용하는 경우 kis_ovrseastk.py get_overseas_order 수정요망!
rt_data = kb.get_overseas_daytime_order_rvsecncl(excg_cd="NASD", itm_no="TSLA", orgn_odno="0030089601", rvse_cncl_dvsn_cd="02", qty=1, unpr=0)
print(rt_data) # 주문접수조직번호+주문접수번호+주문시각

# [해외주식] 주문/계좌 > 해외주식 기간손익[v1_해외주식-032] (해외거래소코드 + 통화코드 + 종목번호 6자리 + 조회시작일 + 조회종료일)
# 해외거래소코드 NASD:미국,SEHK:홍콩,SHAA:중국,TKSE:일본,HASE:베트남
rt_data = kb.get_overseas_inquire_period_profit(excg_cd="", crcy="", itm_no="", st_dt="20240601", ed_dt="20240709")
print(rt_data)
# [해외주식] 주문/계좌 > 해외주식 기간손익(매매일자종목별 기간손익) (해외거래소코드 + 통화코드 + 종목번호 6자리 + 조회시작일 + 조회종료일)
rt_data = kb.get_overseas_inquire_period_profit_output1(excg_cd="NASD", crcy="", itm_no="", st_dt="20240501", ed_dt="20240709")
print(rt_data)

# [해외주식] 주문/계좌 > 해외증거금 통화별조회
rt_data = kb.get_overseas_inquire_foreign_margin()
print(rt_data)

# [해외주식] 주문/계좌 > 해외증거금 일별거래내역 (해외거래소코드 + 매도매수구분코드 + 종목번호 6자리 + 조회시작일 + 조회종료일)
rt_data = kb.get_overseas_inquire_period_trans(excg_cd="", dvsn="", itm_no="", st_dt="20240601", ed_dt="20240709")
# [해외주식] 주문/계좌 > 해외증거금 일별거래내역[합계]
rt_data = kb.get_overseas_inquire_period_trans_output2(excg_cd="", dvsn="", itm_no="", st_dt="20240601", ed_dt="20240709")
print(rt_data)

# [해외주식] 주문/계좌 > 해외주식 결제기준현재잔고
# dv : 01 보유종목, 02 외화잔고, 03 결제기준현재잔고
# dt : 기준일자(YYYYMMDD)
# dvsn : 01 원화, 02 외화
# inqr_dvsn : 00(전체), 01(일반), 02(미니스탁)
rt_data = kb.get_overseas_inquire_paymt_stdr_balance(dv="03", dt="", dvsn="01", inqr_dvsn="00")
print(rt_data)

#====|  [해외주식] 기본시세  |============================================================================================================================

# [해외주식] 기본시세 > 해외주식 현재체결가 (해외거래소코드, 종목번호)
rt_data = kb.get_overseas_price_quot_search_info(excd="NAS", itm_no="AAPL")
print(rt_data)    # 해외주식 현재체결가

# [해외주식] 기본시세 > 해외주식 기간별시세
# ※ 기준일(bymd) 지정일자 이후 100일치 조회, 미입력시 당일자 기본 셋팅
rt_data = kb.get_overseas_price_quot_dailyprice(excd="NAS", itm_no="AAPL", gubn="0", bymd="")
print(rt_data)    # 해외주식 기간별시세

# [해외주식] 기본시세 > 해외주식 종목/지수/환율기간별시세(일/주/월/년)
# ※ 기준일(bymd) 지정일자 이후 100일치 조회, 미입력시 당일자 기본 셋팅
rt_data = kb.get_overseas_price_quot_inquire_daily_price(div="N", itm_no="AAPL", inqr_strt_dt="", inqr_end_dt="", period="D")
rt_data = kb.get_overseas_price_quot_inquire_daily_chartprice(div="N", itm_no="AAPL", inqr_strt_dt="20240605", inqr_end_dt="20240610", period="D")
print(rt_data)    # 해외주식 종목/지수/환율기간별시세(일/주/월/년)

# [해외주식] 기본시세 > 해외주식조건검색  div 01 : 검색결과종목수, 02:검색결과종목리스트
rt_data = kb.get_overseas_price_quot_inquire_search(div="02", excd="NAS", pr_st="160", pr_en="170")
print(rt_data)    # 해외주식조건검색

# [해외주식] 기본시세 > 해외결재일자조회 (기준일자)
rt_data = kb.get_overseas_price_quot_countries_holiday(dt="")
print(rt_data)    # 해외결재일자조회

# [해외주식] 기본시세 > 해외주식 현재가상세 (해외거래소시장코드, 종목코드)
rt_data = kb.get_overseas_price_quot_price_detail(excd="NAS", itm_no="AAPL")
print(rt_data)    # 해외주식 현재가상세

# [해외주식] 기본시세 > 해외주식 해외주식분봉조회 (조회구분 div-02:분봉데이터,01:시장별장운영시간, 해외거래소시장코드, 종목코드, 분갭, 전일포함여부)
rt_data = kb.get_overseas_price_quot_inquire_time_itemchartprice(div="02", excd="NAS", itm_no="AAPL", nmin="", pinc="0")
print(rt_data)    # 해외주식 해외주식분봉조회

# [해외주식] 기본시세 > 해외주식 해외지수분봉조회 (조회구분 div-02:분봉데이터,01:지수정보, 조건시장분류코드, 입력종목코드, 시간구분코드, 과거데이터포함여부)
rt_data = kb.get_overseas_price_quot_inquire_time_indexchartprice(div="02", code="N", iscd="SPX", tm_dv="0", inc="Y")
print(rt_data)    # 해외주식 해외지수분봉조회

# [해외주식] 기본시세 > 해외주식 상품기본정보 (종목번호, 종목유형)
# 종목유형 : 512 미국 나스닥/513 미국 뉴욕/529 미국 아멕스/515 일본/501 홍콩/543 홍콩CNY/558 홍콩USD/507 베트남 하노이/508 베트남 호치민/551 중국 상해A/552 중국 심천A
rt_data = kb.get_overseas_price_search_info(itm_no="AAPL", prdt_type_cd="512")
print("종목코드("+rt_data.std_pdno+") 종목명(" +rt_data.prdt_eng_name+") 거래시장(" +rt_data.ovrs_excg_cd+":" +rt_data.tr_mket_name+")")    # 해외주식 상품기본정보
print(rt_data)   # 해외주식 상품기본정보

# [해외주식] 기본시세 > 해외주식 현재가 10호가 (조회구분 01:기본시세 02:10호가 , 해외거래소코드, 종목번호)
rt_data = kb.get_overseas_price_inquire_asking_price(div="02", excd="NAS", itm_no="AAPL")
print(rt_data)   # 해외주식 상품기본정보

