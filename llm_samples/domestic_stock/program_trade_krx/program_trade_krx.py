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
# [국내주식] 실시간시세 > 국내주식 실시간프로그램매매 (KRX)  [실시간-048]
##############################################################################################

def program_trade_krx(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간프로그램매매 (KRX)[H0STPGM0] 구독 함수

    이 함수는 한국투자증권 웹소켓 API를 통해 실시간으로 국내 주식의 프로그램 매매 데이터를 구독합니다.
    웹소켓을 통해 실시간 데이터를 수신하며, 구독 등록 및 해제를 지원합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 문자열
        tr_key (str): [필수] 종목코드. 빈 문자열이 아니어야 하며, 유효한 종목코드 형식이어야 합니다.

    Returns:
        message (dict): 웹소켓을 통해 수신된 메시지 데이터
        columns (list[str]): 응답 데이터의 컬럼 정보 리스트

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = program_trade_krx("1", "005930")
        >>> print(msg, columns)

    실시간 데이터는 웹소켓을 통해 지속적으로 수신되며, 구독 해제 요청을 보내기 전까지 계속됩니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 필수 입력값입니다.")

    # 거래 ID 설정
    tr_id = "H0STPGM0"

    # 요청 파라미터 설정
    params = {
        "tr_key": tr_key,
    }

    # 데이터 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
    columns = [
        "mksc_shrn_iscd",  # 유가증권단축종목코드
        "stck_cntg_hour",  # 주식체결시간
        "seln_cnqn",       # 매도체결량
        "seln_tr_pbmn",    # 매도거래대금
        "shnu_cnqn",       # 매수2체결량
        "shnu_tr_pbmn",    # 매수2거래대금
        "ntby_cnqn",       # 순매수체결량
        "ntby_tr_pbmn",    # 순매수거래대금
        "seln_rsqn",       # 매도호가잔량
        "shnu_rsqn",       # 매수호가잔량
        "whol_ntby_qty",   # 전체순매수호가잔량
    ]

    return msg, columns
