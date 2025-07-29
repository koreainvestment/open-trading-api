"""
Created on 2025-07-09
@author: LaivData jjlee with cursor
"""

import logging
import sys

sys.path.extend(['../..', '.'])
import kis_auth as ka

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 장운영정보 (KRX) [실시간-049]
##############################################################################################

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def market_status_krx(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 장운영정보 (KRX)[H0STMKO0] 실시간 데이터 구독 함수
    이 함수는 국내주식 장운영정보를 실시간으로 구독하거나 구독 해제합니다.
    연결된 종목의 VI 발동 시와 VI 해제 시에 데이터가 수신됩니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 문자열
        tr_key (str): [필수] 종목코드. 빈 문자열이 아니어야 하며, 유효한 종목코드 형식이어야 합니다.

    Returns:
        message (dict): 서버로부터 수신된 메시지 데이터
        columns (list[str]): 응답 데이터의 컬럼 정보

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = market_status_krx("1", "005930")
        >>> print(msg, columns)

    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 필수 입력값입니다.")

    tr_id = "H0STMKO0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
    columns = [
        "mksc_shrn_iscd",      # 유가증권단축종목코드
        "trht_yn",             # 거래정지여부
        "tr_susp_reas_cntt",   # 거래정지사유내용
        "mkop_cls_code",       # 장운영구분코드
        "antc_mkop_cls_code",  # 예상장운영구분코드
        "mrkt_trtm_cls_code",  # 임의연장구분코드
        "divi_app_cls_code",   # 동시호가배분처리구분코드
        "iscd_stat_cls_code",  # 종목상태구분코드
        "vi_cls_code",         # VI적용구분코드
        "ovtm_vi_cls_code",    # 시간외단일가VI적용구분코드
        "EXCH_CLS_CODE",       # 거래소구분코드
    ]

    return msg, columns
