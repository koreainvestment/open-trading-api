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
# [국내주식] 실시간시세 > 국내주식 실시간프로그램매매 (통합)
##############################################################################################

def program_trade_total(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간프로그램매매 (통합)[H0UNPGM0]
    국내주식 실시간프로그램매매 (통합) API를 통해 실시간 데이터를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 값
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)

    Returns:
        message (dict): 실시간 데이터 메시지
        columns (list[str]): 응답 데이터의 컬럼 정보

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = program_trade_total("1", "005930")
        >>> print(msg, columns)

    Note:
        이 함수는 웹소켓을 통해 실시간 데이터를 구독합니다. 
        구독을 시작하려면 tr_type을 "1"로 설정하고, 해제하려면 "0"으로 설정하세요.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 빈 문자열일 수 없습니다.")

    tr_id = "H0UNPGM0"

    params = {
        "tr_key": tr_key,
    }

    # 웹소켓을 통해 실시간 데이터 구독
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
