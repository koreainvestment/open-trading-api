# -*- coding: utf-8 -*-
"""
Created on Tue Feb 15 07:56:54 2022
"""
#kis_api module 을 찾을 수 없다는 에러가 나는 경우 sys.path에 kis_api.py 가 있는 폴더를 추가해준다.
import kis_auth as ka
import kis_domfuopt as kb

import pandas as pd

import sys

# 토큰 발급
ka.auth()

#====|  국내선물옵션(야간포함)(kis_domfuopt) import 파일을 하신후 프로그램에서 필요한 API 호출 샘플 아래 참고하시기 바랍니다.  |=======================
#====|  국내선물옵션(야간포함)(kis_domfuopt) import 파일을 하신후 프로그램에서 필요한 API 호출 샘플 아래 참고하시기 바랍니다.  |=======================
#====|  국내선물옵션(야간포함)(kis_domfuopt) import 파일을 하신후 프로그램에서 필요한 API 호출 샘플 아래 참고하시기 바랍니다.  |=======================

#====|  국내선물옵션, 해외주식, 해외선물옵션, 채권 등 지속적으로 추가하도록 하겠습니다. 2024.05.16 KIS Developers Team  |======================


#====|  [국내선물옵션] 주문/계좌  |============================================================================================================================

# [국내선물옵션] 주문/계좌 > 선물옵션 주문[v1_국내선물-001] (주간:01/야간(Eurex):02구분 + 매수매도구분 buy,sell + 종목번호 + 주문수량 + 주문단가)
# 지정가 기준이며 시장가 옵션(주문구분코드)을 사용하는 경우 kis_domstk.py get_order_cash 수정요망!
rt_data = kb.get_domfuopt_order(dv_cd="01", sll_buy_dvsn_cd="02", dvsn_cd="02", itm_no="101V06", qty=100, unpr=0)
print(rt_data)

# [국내선물옵션] 주문/계좌 > 선물옵션 정정취소주문[v1_국내선물-002] (주간:01/야간(Eurex):02구분 + 정정취소구분코드(정정:01. 취소:02) + 원주문번호 + 주문구분 + 주문수량 + 주문단가 + 잔량전부여부)
# 지정가 기준이며 시장가 옵션(주문구분코드)을 사용하는 경우 kis_domfuopt.py get_domfuopt_order_rvsecncl 수정요망!
rt_data = kb.get_domfuopt_order_rvsecncl(orgn_odno="0000362027", ord_dvsn="01", rvse_cncl_dvsn_cd="01", ord_qty=1, ord_unpr=366.45, rmn_qty_yn="")
print(rt_data) 

# [[국내선물옵션] 주문/계좌 > (야간)선물옵션 주문체결 현황조회 [국내선물-009] (조회시작일 + 조회종료일)
rt_data = kb.get_domfuopt_inquire_ngt_ccnl_obj(inqr_strt_dt="20230701", inqr_end_dt="20230731")
print(rt_data)

# [국내선물옵션] 주문/계좌 > (야간)선물옵션 주문체결 내역조회 [국내선물-009] (조회시작일 + 조회종료일)
rt_data = kb.get_domfuopt_inquire_ngt_ccnl_lst(inqr_strt_dt="20230701", inqr_end_dt="20230731")
print(rt_data)

# [국내선물옵션] 주문/계좌 > (야간)선물옵션 잔고현황 [국내선물-010]
rt_data = kb.get_domfuopt_inquire_ngt_balance_obj()
print(rt_data)

# [국내선물옵션] 주문/계좌 > (야간)선물옵션 잔고현황
rt_data = kb.get_domfuopt_inquire_ngt_balance_lst()
print(rt_data)

# [국내선물옵션] 주문/계좌 > (야간)선물옵션 주문가능 조회 [국내선물-011]
rt_data = kb.get_domfuopt_inquire_psbl_ngt_order(pdno="101V06", sll_buy_dvsn_cd="02", ord_unpr=0)
print(rt_data)
