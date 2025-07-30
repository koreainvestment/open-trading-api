import sys
import logging

import pandas as pd

sys.path.extend(['..', '.'])
import kis_auth as ka
from etfetn_functions_ws import *

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
# [국내주식] 실시간시세 > 국내ETF NAV추이[실시간-051]
##############################################################################################

kws.subscribe(request=etf_nav_trend, data=["069500"])


# 시작
def on_result(ws, tr_id, result, data_info):
    print(result)


kws.start(on_result=on_result)
