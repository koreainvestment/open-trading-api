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
# [국내주식] 실시간시세 > 국내주식 장운영정보(통합)
##############################################################################################

def market_status_total(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 장운영정보 (통합)[H0UNMKO0] 실시간 데이터 구독 함수
    이 함수는 웹소켓을 통해 실시간으로 국내주식 장운영정보를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 값
        tr_key (str): [필수] 종목코드, 구독할 종목의 고유 코드

    Returns:
        message (dict): 실시간으로 수신된 메시지 데이터
        columns (list[str]): 수신된 데이터의 컬럼 정보

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = market_status_total("1", "005930")
        >>> print(msg, columns)

    Note:
        이 함수는 웹소켓을 통해 실시간 데이터를 구독하므로, 지속적인 데이터 수신이 가능합니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 필수 입력값입니다.")

    tr_id = "H0UNMKO0"

    params = {
        "tr_key": tr_key,
    }

    # kis 모듈을 사용하여 데이터 수신
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터의 컬럼 정보
    columns = [
        "TRHT_YN",               # 거래정지 여부
        "TR_SUSP_REAS_CNTT",     # 거래 정지 사유 내용
        "MKOP_CLS_CODE",         # 장운영 구분 코드
        "ANTC_MKOP_CLS_CODE",    # 예상 장운영 구분 코드
        "MRKT_TRTM_CLS_CODE",    # 임의연장구분코드
        "DIVI_APP_CLS_CODE",     # 동시호가배분처리구분코드
        "ISCD_STAT_CLS_CODE",    # 종목상태구분코드
        "VI_CLS_CODE",           # VI적용구분코드
        "OVTM_VI_CLS_CODE",      # 시간외단일가VI적용구분코드
        "EXCH_CLS_CODE",         # 거래소 구분코드
    ]

    return msg, columns
