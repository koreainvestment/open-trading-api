import sys
import logging
import pandas as pd
sys.path.extend(['..', '.'])

import kis_auth as ka
from domestic_stock_functions import *

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 인증
ka.auth()
trenv = ka.getTREnv()

# 삼성전자 현재가 시세 조회
result = inquire_price(env_dv="real", fid_cond_mrkt_div_code="J", fid_input_iscd="005930")
print(result)