import sys
import logging

import pandas as pd

sys.path.extend(['..', '.'])
import kis_auth as ka
from etfetn_functions import *

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 인증
ka.auth()
trenv = ka.getTREnv()

##############################################################################################
# [국내주식] 기본시세 > ETF 구성종목시세[국내주식-073]
##############################################################################################

result1, result2 = inquire_component_stock_price(fid_cond_mrkt_div_code="J", fid_input_iscd="069500", fid_cond_scr_div_code="11216")
print(result1)
print(result2)

##############################################################################################
# [국내주식] 기본시세 > ETF/ETN 현재가[v1_국내주식-068]
##############################################################################################

result = inquire_price(fid_cond_mrkt_div_code="J", fid_input_iscd="005930")
print(result)

##############################################################################################
# [국내주식] 기본시세 > NAV 비교추이(일)[v1_국내주식-071]
##############################################################################################

result = nav_comparison_daily_trend(fid_cond_mrkt_div_code="J", fid_input_iscd="069500", fid_input_date_1="20240101", fid_input_date_2="20240220")
print(result)

##############################################################################################
# [국내주식] 기본시세 > NAV 비교추이(분)[v1_국내주식-070]
##############################################################################################

result = nav_comparison_time_trend(fid_cond_mrkt_div_code="E", fid_input_iscd="069500", fid_hour_cls_code="60")
print(result)

##############################################################################################
# [국내주식] 기본시세 > NAV 비교추이(종목)[v1_국내주식-069]
##############################################################################################

result1, result2 = nav_comparison_trend(fid_cond_mrkt_div_code="J", fid_input_iscd="069500")
print(result1)
print(result2)

