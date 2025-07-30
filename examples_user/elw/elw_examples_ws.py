import sys
import logging

import pandas as pd

sys.path.extend(['..', '.'])
import kis_auth as ka
from elw_functions_ws import *

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
# [국내주식] 실시간시세 - ELW 실시간호가[실시간-062]
##############################################################################################

kws.subscribe(request=elw_asking_price, data=["57LA24", "57L739", "57L650", "57L966", "52L181", "57LB38"])

##############################################################################################
# [국내주식] 실시간시세 - ELW 실시간체결가[실시간-061]
##############################################################################################

kws.subscribe(request=elw_ccnl, data=["57LA24", "57L739", "57L650", "57L966", "52L181", "57LB38"])

##############################################################################################
# [국내주식] 실시간시세 - ELW 실시간예상체결[실시간-063]
##############################################################################################

kws.subscribe(request=elw_exp_ccnl, data=["57LA24", "57L739", "57L650", "57L966", "52L181", "57LB38"])


# 시작
def on_result(ws, tr_id, result, data_info):
    print(result)


kws.start(on_result=on_result)
