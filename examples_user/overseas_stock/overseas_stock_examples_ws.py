import sys
import logging

import pandas as pd

sys.path.extend(['..', '.'])
import kis_auth as ka
from overseas_stock_functions_ws import *

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
# [해외주식] 실시간시세 > 해외주식 실시간호가[실시간-021]
##############################################################################################

kws.subscribe(request=asking_price, data=["RBAQAAPL"])

##############################################################################################
# [해외주식] 실시간시세 > 해외주식 실시간체결통보[실시간-009]
##############################################################################################

kws.subscribe(request=ccnl_notice, data=[trenv.my_htsid], kwargs={"env_dv": "real"})

##############################################################################################
# [해외주식] 실시간시세 > 해외주식 지연호가(아시아)[실시간-008]
##############################################################################################

kws.subscribe(request=delayed_asking_price_asia, data=["DHKS00003"])

##############################################################################################
# [해외주식] 실시간시세 > 해외주식 실시간지연체결가[실시간-007]
##############################################################################################

kws.subscribe(request=delayed_ccnl, data=["DHKS00003"])


# 시작
def on_result(ws, tr_id, result, data_info):
    print(result)


kws.start(on_result=on_result)
