import sys
import logging

import pandas as pd

sys.path.extend(['..', '.'])
import kis_auth as ka
from domestic_bond_functions_ws import *

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
# [장내채권] 실시간시세 > 일반채권 실시간호가 [실시간-053]
##############################################################################################

kws.subscribe(request=bond_asking_price, data=["KR103502GA34", "KR6095572D81"])

##############################################################################################
# [장내채권] 실시간시세 > 일반채권 실시간체결가 [실시간-052]
##############################################################################################

kws.subscribe(request=bond_ccnl, data=["KR103502GA34", "KR6095572D81"])

##############################################################################################
# [장내채권] 실시간시세 > 채권지수 실시간체결가 [실시간-060]
##############################################################################################

kws.subscribe(request=bond_index_ccnl, data=[
    # 한경채권지수
    "KBPR01", "KBPR02", "KBPR03", "KBPR04",
    # KIS채권지수
    "KISR01", "MSBI07", "KTBL10", "MSBI09", "MSBI10", "CDIX01",
    # 매경채권지수
    "MKFR01", "MSBI01", "MSBI03", "MSBI10", "CORP01"
])


# 시작
def on_result(ws, tr_id, result, data_info):
    print(result)


kws.start(on_result=on_result)
