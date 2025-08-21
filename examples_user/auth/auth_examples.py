import sys
import logging

import pandas as pd

sys.path.extend(['..', '.'])
import kis_auth as ka
from auth_functions import *

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 인증
ka.auth()
trenv = ka.getTREnv()

##############################################################################################
# [인증] OAuth 접근토큰 발급
##############################################################################################

df = auth_token(grant_type="client_credentials", appkey=trenv.my_app, appsecret=trenv.my_sec, env_dv="real")
print(df)

##############################################################################################
# [인증] WebSocket 웹소켓 접속키 발급
##############################################################################################

df = auth_ws_token(grant_type="client_credentials",  appkey=trenv.my_app, appsecret=trenv.my_sec, env_dv="real")
print(df)

