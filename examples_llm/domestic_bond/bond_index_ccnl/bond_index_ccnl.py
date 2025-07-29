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
# [장내채권] 실시간시세 > 채권지수 실시간체결가 [실시간-060]
##############################################################################################


def bond_index_ccnl(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    채권지수 실시간체결가[H0BICNT0]
    채권지수 실시간체결가 API를 통해 실시간 데이터를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타냅니다.
        tr_key (str): [필수] 구독할 종목코드. 빈 문자열이 아니어야 합니다.

    Returns:
        message (dict): 구독 요청에 대한 응답 메시지.
        columns (list[str]): 실시간 데이터의 컬럼 정보.

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생합니다.

    Example:
        >>> msg, columns = bond_index_ccnl("1", "005930")
        >>> print(msg, columns)

    [참고자료]
    채권 종목코드 마스터파일은 "KIS포털 - API문서 - 종목정보파일 - 장내채권 - 채권코드" 참고 부탁드립니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key is required and cannot be an empty string")

    tr_id = "H0BICNT0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 구독 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
    columns = [
        "nmix_id",  # 지수ID
        "stnd_date1",  # 기준일자1
        "trnm_hour",  # 전송시간
        "totl_ernn_nmix_oprc",  # 총수익지수시가지수
        "totl_ernn_nmix_hgpr",  # 총수익지수최고가
        "totl_ernn_nmix_lwpr",  # 총수익지수최저가
        "totl_ernn_nmix",  # 총수익지수
        "prdy_totl_ernn_nmix",  # 전일총수익지수
        "totl_ernn_nmix_prdy_vrss",  # 총수익지수전일대비
        "totl_ernn_nmix_prdy_vrss_sign",  # 총수익지수전일대비부호
        "totl_ernn_nmix_prdy_ctrt",  # 총수익지수전일대비율
        "clen_prc_nmix",  # 순가격지수
        "mrkt_prc_nmix",  # 시장가격지수
        "bond_call_rnvs_nmix",  # Call재투자지수
        "bond_zero_rnvs_nmix",  # Zero재투자지수
        "bond_futs_thpr",  # 선물이론가격
        "bond_avrg_drtn_val",  # 평균듀레이션
        "bond_avrg_cnvx_val",  # 평균컨벡서티
        "bond_avrg_ytm_val",  # 평균YTM
        "bond_avrg_frdl_ytm_val",  # 평균선도YTM
    ]

    return msg, columns
