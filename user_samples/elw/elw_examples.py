import sys
import logging

import pandas as pd

sys.path.extend(['..', '.'])
import kis_auth as ka
from elw_functions import *

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 인증
ka.auth()
trenv = ka.getTREnv()

##############################################################################################
# [국내주식] ELW시세 - ELW 비교대상종목조회[국내주식-183]
##############################################################################################

df = compare_stocks(fid_cond_scr_div_code="11517", fid_input_iscd="005930")
print(df)

##############################################################################################
# [국내주식] ELW시세 - ELW 종목검색[국내주식-166]
##############################################################################################

df = cond_search(fid_cond_mrkt_div_code="W", fid_cond_scr_div_code="11510", fid_rank_sort_cls_code="0", fid_input_cnt_1="100")
print(df)

##############################################################################################
# [국내주식] ELW시세 - ELW 만기예정/만기종목[국내주식-184]
##############################################################################################

df = expiration_stocks(fid_cond_mrkt_div_code="W", fid_cond_scr_div_code="11547", fid_input_date_1="20240402", fid_input_date_2="20240408", fid_div_cls_code="2", fid_etc_cls_code="", fid_unas_input_iscd="000000", fid_input_iscd_2="00000", fid_blng_cls_code="0", fid_input_option_1="")
print(df)

##############################################################################################
# [국내주식] ELW시세 - ELW 지표순위[국내주식-169]
##############################################################################################

df = indicator(fid_cond_mrkt_div_code="W", fid_cond_scr_div_code="20279", fid_unas_input_iscd="000000", fid_input_iscd="00000", fid_div_cls_code="0", fid_input_price_1="", fid_input_price_2="", fid_input_vol_1="", fid_input_vol_2="", fid_rank_sort_cls_code="0", fid_blng_cls_code="0")
print(df)

##############################################################################################
# [국내주식] ELW시세 - ELW 투자지표추이(체결)[국내주식-172]
##############################################################################################

df = indicator_trend_ccnl(fid_cond_mrkt_div_code="W", fid_input_iscd="58J297")
print(df)

##############################################################################################
# [국내주식] ELW시세 - ELW 투자지표추이(일별)[국내주식-173]
##############################################################################################

df = indicator_trend_daily(fid_cond_mrkt_div_code="W", fid_input_iscd="57K281")
print(df)

##############################################################################################
# [국내주식] ELW시세 - ELW 투자지표추이(분별)[국내주식-174]
##############################################################################################

df = indicator_trend_minute(fid_cond_mrkt_div_code="W", fid_input_iscd="58J297", fid_hour_cls_code="60", fid_pw_data_incu_yn="N")
print(df)

##############################################################################################
# [국내주식] ELW시세 - ELW LP매매추이 [국내주식-182]
##############################################################################################

df1, df2 = lp_trade_trend(fid_cond_mrkt_div_code="W", fid_input_iscd="52K577")
print(df1)
print(df2)

##############################################################################################
# [국내주식] ELW시세 - ELW 신규상장종목[국내주식-181]
##############################################################################################

df = newly_listed(fid_cond_mrkt_div_code="W", fid_cond_scr_div_code="11548", fid_div_cls_code="02", fid_unas_input_iscd="000000", fid_input_iscd_2="00003", fid_input_date_1="20240402", fid_blng_cls_code="0")
print(df)

##############################################################################################
# [국내주식] ELW시세 - ELW 당일급변종목[국내주식-171]
##############################################################################################

df = quick_change(fid_cond_mrkt_div_code="W", fid_cond_scr_div_code="20287", fid_unas_input_iscd="000000", fid_input_iscd="00000", fid_mrkt_cls_code="A", fid_input_price_1="", fid_input_price_2="", fid_input_vol_1="", fid_input_vol_2="", fid_hour_cls_code="1", fid_input_hour_1="", fid_input_hour_2="", fid_rank_sort_cls_code="1", fid_blng_cls_code="0")
print(df)

##############################################################################################
# [국내주식] ELW시세 - ELW 민감도 순위[국내주식-170]
##############################################################################################

df = sensitivity(fid_cond_mrkt_div_code="W", fid_cond_scr_div_code="20285", fid_unas_input_iscd="000000", fid_input_iscd="00000", fid_div_cls_code="0", fid_input_price_1="", fid_input_price_2="", fid_input_vol_1="", fid_input_vol_2="", fid_rank_sort_cls_code="0", fid_input_rmnn_dynu_1="", fid_input_date_1="", fid_blng_cls_code="0")
print(df)

##############################################################################################
# [국내주식] ELW시세 - ELW 민감도 추이(체결)[국내주식-175]
##############################################################################################

df = sensitivity_trend_ccnl(fid_cond_mrkt_div_code="W", fid_input_iscd="58J297")
print(df)

##############################################################################################
# [국내주식] ELW시세 - ELW 민감도 추이(일별)[국내주식-176]
##############################################################################################

df = sensitivity_trend_daily(fid_cond_mrkt_div_code="W", fid_input_iscd="58J438")
print(df)

##############################################################################################
# [국내주식] ELW시세 - ELW 기초자산 목록조회[국내주식-185]
##############################################################################################

df = udrl_asset_list(fid_cond_scr_div_code="11541", fid_rank_sort_cls_code="0", fid_input_iscd="00000")
print(df)

##############################################################################################
# [국내주식] ELW시세 - ELW 기초자산별 종목시세[국내주식-186]
##############################################################################################

df = udrl_asset_price(fid_cond_mrkt_div_code="W", fid_cond_scr_div_code="11541", fid_mrkt_cls_code="A", fid_input_iscd="00000", fid_unas_input_iscd="005930", fid_vol_cnt="1000", fid_trgt_exls_cls_code="0", fid_input_price_1="1000", fid_input_price_2="5000", fid_input_vol_1="100", fid_input_vol_2="1000", fid_input_rmnn_dynu_1="30", fid_input_rmnn_dynu_2="90", fid_option="0", fid_input_option_1="", fid_input_option_2="")
print(df)

##############################################################################################
# [국내주식] ELW시세 - ELW 상승률순위[국내주식-167]
##############################################################################################

df = updown_rate(fid_cond_mrkt_div_code="W", fid_cond_scr_div_code="20277", fid_unas_input_iscd="000000", fid_input_iscd="00000", fid_input_rmnn_dynu_1="0", fid_div_cls_code="0", fid_input_price_1="", fid_input_price_2="", fid_input_vol_1="", fid_input_vol_2="", fid_input_date_1="", fid_rank_sort_cls_code="0", fid_blng_cls_code="0", fid_input_date_2="")
print(df)

##############################################################################################
# [국내주식] ELW시세 - ELW 변동성추이(체결)[국내주식-177]
##############################################################################################

df = volatility_trend_ccnl(fid_cond_mrkt_div_code="W", fid_input_iscd="58J297")
print(df)

##############################################################################################
# [국내주식] ELW시세 - ELW 변동성추이(일별)[국내주식-178]
##############################################################################################

df = volatility_trend_daily(fid_cond_mrkt_div_code="W", fid_input_iscd="58J297")
print(df)

##############################################################################################
# [국내주식] ELW시세 - ELW 변동성추이(분별)[국내주식-179]
##############################################################################################

df = volatility_trend_minute(fid_cond_mrkt_div_code="W", fid_input_iscd="58J297", fid_hour_cls_code="60", fid_pw_data_incu_yn="N")
print(df)

##############################################################################################
# [국내주식] ELW시세 - ELW 변동성추이(틱)[국내주식-180]
##############################################################################################

df = volatility_trend_tick(fid_cond_mrkt_div_code="W", fid_input_iscd="58J297")
print(df)

##############################################################################################
# [국내주식] ELW시세 - ELW 거래량순위[국내주식-168]
##############################################################################################

df = volume_rank(fid_cond_mrkt_div_code="W", fid_cond_scr_div_code="20278", fid_unas_input_iscd="000000", fid_input_iscd="00000", fid_input_rmnn_dynu_1="", fid_div_cls_code="0", fid_input_price_1="0", fid_input_price_2="100000", fid_input_vol_1="0", fid_input_vol_2="1000000", fid_input_date_1="20250101", fid_rank_sort_cls_code="0", fid_blng_cls_code="0", fid_input_iscd_2="0000", fid_input_date_2="")
print(df)

