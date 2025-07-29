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
# [장내채권] 실시간시세 > 일반채권 실시간체결가 [실시간-052]
##############################################################################################


def bond_ccnl(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    일반채권 실시간체결가[H0BJCNT0] 구독 함수
    한국투자증권 웹소켓 API를 통해 일반채권의 실시간 체결가 데이터를 구독합니다.
    
    [참고자료]
    채권 종목코드 마스터파일은 "KIS포털 - API문서 - 종목정보파일 - 장내채권 - 채권코드" 참고 부탁드립니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)

    Returns:
        message (dict): 실시간 데이터 구독 결과 메시지
        columns (list[str]): 응답 데이터의 컬럼 정보

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = bond_ccnl("1", "005930")
        >>> print(msg, columns)


    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 빈 문자열일 수 없습니다.")

    tr_id = "H0BJCNT0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 구독 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
    columns = [
        "stnd_iscd",  # 표준종목코드
        "bond_isnm",  # 채권종목명
        "stck_cntg_hour",  # 주식체결시간
        "prdy_vrss_sign",  # 전일대비부호
        "prdy_vrss",  # 전일대비
        "prdy_ctrt",  # 전일대비율
        "stck_prpr",  # 현재가
        "cntg_vol",  # 체결거래량
        "stck_oprc",  # 시가
        "stck_hgpr",  # 고가
        "stck_lwpr",  # 저가
        "stck_prdy_clpr",  # 전일종가
        "bond_cntg_ert",  # 현재수익률
        "oprc_ert",  # 시가수익률
        "hgpr_ert",  # 고가수익률
        "lwpr_ert",  # 저가수익률
        "acml_vol",  # 누적거래량
        "prdy_vol",  # 전일거래량
        "cntg_type_cls_code",  # 체결유형코드
    ]

    return msg, columns
