import sys
import logging

import pandas as pd

sys.path.extend(['..', '.'])
import kis_auth as ka
from domestic_futureoption_functions import *

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 인증
ka.auth()
trenv = ka.getTREnv()

##############################################################################################
# [국내선물옵션] 기본시세 > 국내옵션전광판_콜풋[국내선물-022]
##############################################################################################

result1, result2 = display_board_callput(
            fid_cond_mrkt_div_code="O",
            fid_cond_scr_div_code="20503",
            fid_mrkt_cls_code="CO",
            fid_mtrt_cnt="202508",
            fid_mrkt_cls_code1="PO"
        )
print(result1)
print(result2)

##############################################################################################
# [국내선물옵션] 기본시세 > 국내옵션전광판_선물[국내선물-023]
##############################################################################################

result = display_board_futures(
            fid_cond_mrkt_div_code="F",
            fid_cond_scr_div_code="20503",
            fid_cond_mrkt_cls_code="MKI"
        )
print(result)

##############################################################################################
# [국내선물옵션] 기본시세 > 국내옵션전광판_옵션월물리스트[국내선물-020]
##############################################################################################

result = display_board_option_list(fid_cond_scr_div_code="509")
print(result)

##############################################################################################
# [국내선물옵션] 기본시세 > 국내선물 기초자산 시세[국내선물-021]
##############################################################################################

output1, output2 = display_board_top(fid_cond_mrkt_div_code="F", fid_input_iscd="101W09")
print(output1)
print(output2)

##############################################################################################
# [국내선물옵션] 기본시세 > 선물옵션 일중예상체결추이[국내선물-018]
##############################################################################################

result1, result2 = exp_price_trend(fid_input_iscd="101W09", fid_cond_mrkt_div_code="F")
print(result1)
print(result2)

##############################################################################################
# [국내선물옵션] 기본시세 > 선물옵션 시세호가[v1_국내선물-007]
##############################################################################################

result1, result2 = inquire_asking_price(fid_cond_mrkt_div_code="F", fid_input_iscd="101W09", env_dv="real")
print(result1)
print(result2)

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 잔고현황[v1_국내선물-004]
##############################################################################################

result1, result2 = inquire_balance(env_dv="real", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, mgna_dvsn="01",
                                           excc_stat_cd="1")
print(result1)
print(result2)

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 잔고정산손익내역[v1_국내선물-013]
##############################################################################################

result1, result2 = inquire_balance_settlement_pl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, inqr_dt="20230906")
print(result1)
print(result2)

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 잔고평가손익내역[v1_국내선물-015]
##############################################################################################

result1, result2 = inquire_balance_valuation_pl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, mgna_dvsn="01",
                                                        excc_stat_cd="1")
print(result1)
print(result2)

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 주문체결내역조회[v1_국내선물-003]
##############################################################################################

result1, result2 = inquire_ccnl(
            env_dv="real",
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            strt_ord_dt="20220730",
            end_ord_dt="20220830",
            sll_buy_dvsn_cd="00",
            ccld_nccs_dvsn="00",
            sort_sqn="DS"
        )
print(result1)
print(result2)

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 기준일체결내역[v1_국내선물-016]
##############################################################################################

result1, result2 = inquire_ccnl_bstime(
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            ord_dt="20230920",
            fuop_tr_strt_tmd="000000",
            fuop_tr_end_tmd="240000"
        )
print(result1)
print(result2)

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션기간약정수수료일별[v1_국내선물-017]
##############################################################################################

result1, result2 = inquire_daily_amount_fee(
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            inqr_strt_day="20240401",
            inqr_end_day="20240625"
        )
print(result1)
print(result2)

##############################################################################################
# [국내선물옵션] 기본시세 > 선물옵션기간별시세(일/주/월/년)[v1_국내선물-008]
##############################################################################################

output1, output2 = inquire_daily_fuopchartprice(
            fid_cond_mrkt_div_code="F",
            fid_input_iscd="101W09",
            fid_input_date_1="20250301",
            fid_input_date_2="20250810",
            fid_period_div_code="D",
            env_dv="real"
        )
print(output1)
print(output2)

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 총자산현황[v1_국내선물-014]
##############################################################################################

result = inquire_deposit(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod)
print(result)

##############################################################################################
# [국내선물옵션] 주문/계좌 > (야간)선물옵션 잔고현황 [국내선물-010]
##############################################################################################

result1, result2 = inquire_ngt_balance(
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            mgna_dvsn="01",
            excc_stat_cd="1"
        )
print(result1)
print(result2)

##############################################################################################
# [국내선물옵션] 주문/계좌 > (야간)선물옵션 주문체결 내역조회 [국내선물-009]
##############################################################################################

result1, result2 = inquire_ngt_ccnl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, strt_ord_dt="20250610",
                                            end_ord_dt="20250613", sll_buy_dvsn_cd="00", ccld_nccs_dvsn="00")
print(result1)
print(result2)

##############################################################################################
# [국내선물옵션] 기본시세 > 선물옵션 시세[v1_국내선물-006]
##############################################################################################

result1, result2, result3 = inquire_price(
            fid_cond_mrkt_div_code="F",
            fid_input_iscd="101W09",
            env_dv="real"
        )
print(result1)
print(result2)
print(result3)

##############################################################################################
# [국내선물옵션] 주문/계좌 > (야간)선물옵션 주문가능 조회 [국내선물-011]
##############################################################################################

result = inquire_psbl_ngt_order(
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            pdno="101W09",
            prdt_type_cd="301",
            sll_buy_dvsn_cd="02",
            unit_price="322",
            ord_dvsn_cd="01"
        )
print(result)

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 주문가능[v1_국내선물-005]
##############################################################################################

result = inquire_psbl_order(
            env_dv="real",
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            pdno="101W09",
            sll_buy_dvsn_cd="02",
            unit_price="1",
            ord_dvsn_cd="01"
        )
print(result)

##############################################################################################
# [국내선물옵션] 기본시세 > 선물옵션 분봉조회[v1_국내선물-012]
##############################################################################################

result1, result2 = inquire_time_fuopchartprice(
            fid_cond_mrkt_div_code="F",
            fid_input_iscd="101T12",
            fid_hour_cls_code="60",
            fid_pw_data_incu_yn="Y",
            fid_fake_tick_incu_yn="N",
            fid_input_date_1="20230901",
            fid_input_hour_1="100000"
        )
print(result1)
print(result2)

##############################################################################################
# [국내선물옵션] 주문/계좌 > (야간)선물옵션 증거금 상세 [국내선물-024]
##############################################################################################

result1, result2, result3 = ngt_margin_detail(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, mgna_dvsn_cd="01")
print(result1)
print(result2)
print(result3)

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 주문[v1_국내선물-001]
##############################################################################################

result = order(
            env_dv="real",
            ord_dv="day",
            ord_prcs_dvsn_cd="02",
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            sll_buy_dvsn_cd="02",
            shtn_pdno="101W09",
            ord_qty="1",
            unit_price="0",
            nmpr_type_cd="02",
            krx_nmpr_cndt_cd="0",
            ord_dvsn_cd="02"
        )
print(result)

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 정정취소주문[v1_국내선물-002]
##############################################################################################

result = order_rvsecncl(
            env_dv="real",
            day_dv="day",
            ord_prcs_dvsn_cd="02",
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            rvse_cncl_dvsn_cd="02",
            orgn_odno="0000004018",
            ord_qty="0",
            unit_price="0",
            nmpr_type_cd="02",
            krx_nmpr_cndt_cd="0",
            rmn_qty_yn="Y",
            ord_dvsn_cd="01"
        )
print(result)

