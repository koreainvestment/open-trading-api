import sys
import logging

import pandas as pd

sys.path.extend(['..', '.'])
import kis_auth as ka
from overseas_futureoption_functions_ws import *

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 인증
ka.auth()
ka.auth_ws()
trenv = ka.getTREnv()

# 웹소켓 선언
kws = ka.KISWebSocket(api_url="/tryitout")

##############################################################################################
# [해외선물옵션]실시간시세 > 해외선물옵션 실시간호가[실시간-018]
##############################################################################################

kws.subscribe(request=asking_price, data=["SPIU25"])

##############################################################################################
# [해외선물옵션]실시간시세 > 해외선물옵션 실시간체결가[실시간-017]
##############################################################################################

kws.subscribe(request=ccnl, data=["1OZQ25"])

##############################################################################################
# [해외선물옵션]실시간시세 > 해외선물옵션 실시간체결내역통보[실시간-020]
##############################################################################################

kws.subscribe(request=ccnl_notice, data=[trenv.my_htsid])

##############################################################################################
# [해외선물옵션]실시간시세 > 해외선물옵션 실시간주문내역통보[실시간-019]
##############################################################################################

kws.subscribe(request=order_notice, data=[trenv.my_htsid])


# 시작
def on_result(ws, tr_id, result, data_info):
    print(result)


kws.start(on_result=on_result)
