"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""


import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 종목조건검색조회 [국내주식-039]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/psearch-result"

def psearch_result(
    user_id: str,  # 사용자 HTS ID
    seq: str       # 사용자조건 키값
) -> pd.DataFrame:
    """
    HTS(efriend Plus) [0110] 조건검색에서 등록 및 서버저장한 나의 조건 목록을 확인할 수 있는 API입니다.
    종목조건검색 목록조회 API(/uapi/domestic-stock/v1/quotations/psearch-title)의 output인 'seq'을 종목조건검색조회 API(/uapi/domestic-stock/v1/quotations/psearch-result)의 input으로 사용하시면 됩니다.

    ※ 시스템 안정성을 위해 API로 제공되는 조건검색 결과의 경우 조건당 100건으로 제한을 둔 점 양해 부탁드립니다.

    ※ [0110] 화면의 '대상변경' 설정사항은 HTS [0110] 사용자 조건검색 화면에만 적용됨에 유의 부탁드립니다.

    ※ '조회가 계속 됩니다. (다음을 누르십시오.)' 오류 발생 시 해결방법
    → HTS(efriend Plus) [0110] 조건검색 화면에서 조건을 등록하신 후, 왼쪽 하단의 "사용자조건 서버저장" 클릭하셔서 등록한 조건들을 서버로 보낸 후 다시 API 호출 시도 부탁드립니다.

    ※ {"rt_cd":"1","msg_cd":"MCA05918","msg1":"종목코드 오류입니다."} 메시지 발생 이유
    → 조건검색 결과 검색된 종목이 0개인 경우 위 응답값을 수신하게 됩니다.
    
    Args:
        user_id (str): [필수] 사용자 HTS ID
        seq (str): [필수] 사용자조건 키값 (종목조건검색 목록조회 API의 output인 'seq'을 이용)

    Returns:
        pd.DataFrame: 종목조건검색조회 데이터
        
    Example:
        >>> df = psearch_result(user_id=trenv.my_htsid, seq="0")
        >>> print(df)
    """

    if user_id == "":
        raise ValueError("user_id is required")
    
    if seq == "":
        raise ValueError("seq is required (e.g. '종목조건검색 목록조회 API의 output인 'seq'을 이용')")

    tr_id = "HHKST03900400"  # 종목조건검색조회

    params = {
        "user_id": user_id,  # 사용자 HTS ID
        "seq": seq           # 사용자조건 키값
    }
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output2)
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 