"""
Created on 2025-07-09
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
# [국내주식] 실시간시세 > 국내주식 실시간프로그램매매 (NXT)
##############################################################################################

def program_trade_nxt(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간프로그램매매 (NXT)[H0NXPGM0]
    국내주식 실시간프로그램매매 (NXT) API입니다. 이 함수는 웹소켓을 통해 실시간 데이터를 구독하거나 구독 해제합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 값
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)

    Returns:
        message (dict): 실시간 데이터 메시지
        columns (list[str]): 응답 데이터의 컬럼 정보

    Example:
        >>> msg, columns = program_trade_nxt("1", "005930")
        >>> print(msg, columns)

    Note:
        실시간 데이터는 웹소켓을 통해 지속적으로 업데이트됩니다. 구독을 해제하지 않으면 데이터 스트림이 계속 유지됩니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 필수 입력값입니다.")

    # 거래 ID 설정
    tr_id = "H0NXPGM0"

    # 요청 파라미터 설정
    params = {
        "tr_key": tr_key,
    }

    # 데이터 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터의 컬럼 정보
    columns = [
        "MKSC_SHRN_ISCD",  # 유가증권 단축 종목코드
        "STCK_CNTG_HOUR",  # 주식 체결 시간
        "SELN_CNQN",       # 매도 체결량
        "SELN_TR_PBMN",    # 매도 거래 대금
        "SHNU_CNQN",       # 매수2 체결량
        "SHNU_TR_PBMN",    # 매수2 거래 대금
        "NTBY_CNQN",       # 순매수 체결량
        "NTBY_TR_PBMN",    # 순매수 거래 대금
        "SELN_RSQN",       # 매도호가잔량
        "SHNU_RSQN",       # 매수호가잔량
        "WHOL_NTBY_QTY",   # 전체순매수호가잔량
    ]

    return msg, columns
