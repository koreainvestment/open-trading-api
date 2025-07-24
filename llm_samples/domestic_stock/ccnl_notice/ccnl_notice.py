"""
Created on 2025-07-08
@author: LaivData jjlee with cursor
"""

import logging
import sys

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 주식체결통보 [실시간-005]
##############################################################################################

def ccnl_notice(
        tr_type: str,
        tr_key: str,
        env_dv: str = "real",  # 실전모의구분
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간체결통보[H0STCNI0]
    국내주식 실시간 체결통보 수신 시에 (1) 주문·정정·취소·거부 접수 통보 와 (2) 체결 통보 가 모두 수신됩니다.
    (14번째 값(CNTG_YN;체결여부)가 2이면 체결통보, 1이면 주문·정정·취소·거부 접수 통보입니다.)

    ※ 모의투자는 H0STCNI9 로 변경하여 사용합니다.

    실시간 데이터 구독을 위한 웹소켓 함수입니다. 구독을 등록하거나 해제할 수 있습니다.

    Args:
        tr_type (str): [필수] 구독 등록("1")/해제("0") 여부
        tr_key (str): [필수] 종목코드 (예: "005930")
        env_dv (str): 실전모의구분 (real:실전, demo:모의)

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = ccnl_notice("1", "005930", env_dv="real")
        >>> print(msg, columns)

    웹소켓을 통해 실시간 데이터를 수신하며, 데이터는 암호화되어 제공됩니다. 
    AES256 KEY와 IV를 사용하여 복호화해야 합니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 필수 입력값입니다.")

    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real":
        tr_id = "H0STCNI0"  # 실전투자용 TR ID
    elif env_dv == "demo":
        tr_id = "H0STCNI9"  # 모의투자용 TR ID
    else:
        raise ValueError("env_dv는 'real' 또는 'demo'만 가능합니다.")

    params = {
        "tr_key": tr_key,
    }

    # 데이터 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
    columns = [
        "CUST_ID", "ACNT_NO", "ODER_NO", "ODER_QTY", "SELN_BYOV_CLS", "RCTF_CLS",
        "ODER_KIND", "ODER_COND", "STCK_SHRN_ISCD", "CNTG_QTY", "CNTG_UNPR",
        "STCK_CNTG_HOUR", "RFUS_YN", "CNTG_YN", "ACPT_YN", "BRNC_NO", "ACNT_NO2",
        "ACNT_NAME", "ORD_COND_PRC", "ORD_EXG_GB", "POPUP_YN", "FILLER", "CRDT_CLS",
        "CRDT_LOAN_DATE", "CNTG_ISNM40", "ODER_PRC"
    ]

    return msg, columns
