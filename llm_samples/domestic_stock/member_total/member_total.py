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
# [국내주식] 실시간시세 > 국내주식 실시간회원사 (통합)
##############################################################################################

def member_total(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간회원사 (통합)[H0UNMBC0]
    국내주식 실시간회원사 (통합) API입니다. 이 함수는 웹소켓을 통해 실시간 데이터를 구독하거나 구독 해제합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 값
        tr_key (str): [필수] 종목코드, 빈 문자열이 아니어야 함

    Returns:
        message (dict): 실시간으로 수신된 메시지 데이터
        columns (list[str]): 응답 데이터의 컬럼 정보

    Example:
        >>> msg, columns = member_total("1", "005930")
        >>> print(msg, columns)

    Note:
        이 함수는 실시간 데이터를 처리하기 위해 웹소켓을 사용합니다. 구독을 등록하면 실시간으로 데이터가 수신됩니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 필수 입력값입니다.")

    tr_id = "H0UNMBC0"

    params = {
        "tr_key": tr_key,
    }

    # 웹소켓을 통해 데이터 수신
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터의 컬럼 정보
    columns = [
        "MKSC_SHRN_ISCD",
        "SELN2_MBCR_NAME1",
        "SELN2_MBCR_NAME2",
        "SELN2_MBCR_NAME3",
        "SELN2_MBCR_NAME4",
        "SELN2_MBCR_NAME5",
        "BYOV_MBCR_NAME1",
        "BYOV_MBCR_NAME2",
        "BYOV_MBCR_NAME3",
        "BYOV_MBCR_NAME4",
        "BYOV_MBCR_NAME5",
        "TOTAL_SELN_QTY1",
        "TOTAL_SELN_QTY2",
        "TOTAL_SELN_QTY3",
        "TOTAL_SELN_QTY4",
        "TOTAL_SELN_QTY5",
        "TOTAL_SHNU_QTY1",
        "TOTAL_SHNU_QTY2",
        "TOTAL_SHNU_QTY3",
        "TOTAL_SHNU_QTY4",
        "TOTAL_SHNU_QTY5",
        "SELN_MBCR_GLOB_YN_1",
        "SELN_MBCR_GLOB_YN_2",
        "SELN_MBCR_GLOB_YN_3",
        "SELN_MBCR_GLOB_YN_4",
        "SELN_MBCR_GLOB_YN_5",
        "SHNU_MBCR_GLOB_YN_1",
        "SHNU_MBCR_GLOB_YN_2",
        "SHNU_MBCR_GLOB_YN_3",
        "SHNU_MBCR_GLOB_YN_4",
        "SHNU_MBCR_GLOB_YN_5",
        "SELN_MBCR_NO1",
        "SELN_MBCR_NO2",
        "SELN_MBCR_NO3",
        "SELN_MBCR_NO4",
        "SELN_MBCR_NO5",
        "SHNU_MBCR_NO1",
        "SHNU_MBCR_NO2",
        "SHNU_MBCR_NO3",
        "SHNU_MBCR_NO4",
        "SHNU_MBCR_NO5",
        "SELN_MBCR_RLIM1",
        "SELN_MBCR_RLIM2",
        "SELN_MBCR_RLIM3",
        "SELN_MBCR_RLIM4",
        "SELN_MBCR_RLIM5",
        "SHNU_MBCR_RLIM1",
        "SHNU_MBCR_RLIM2",
        "SHNU_MBCR_RLIM3",
        "SHNU_MBCR_RLIM4",
        "SHNU_MBCR_RLIM5",
        "SELN_QTY_ICDC1",
        "SELN_QTY_ICDC2",
        "SELN_QTY_ICDC3",
        "SELN_QTY_ICDC4",
        "SELN_QTY_ICDC5",
        "SHNU_QTY_ICDC1",
        "SHNU_QTY_ICDC2",
        "SHNU_QTY_ICDC3",
        "SHNU_QTY_ICDC4",
        "SHNU_QTY_ICDC5",
        "GLOB_TOTAL_SELN_QTY",
        "GLOB_TOTAL_SHNU_QTY",
        "GLOB_TOTAL_SELN_QTY_ICDC",
        "GLOB_TOTAL_SHNU_QTY_ICDC",
        "GLOB_NTBY_QTY",
        "GLOB_SELN_RLIM",
        "GLOB_SHNU_RLIM",
        "SELN2_MBCR_ENG_NAME1",
        "SELN2_MBCR_ENG_NAME2",
        "SELN2_MBCR_ENG_NAME3",
        "SELN2_MBCR_ENG_NAME4",
        "SELN2_MBCR_ENG_NAME5",
        "BYOV_MBCR_ENG_NAME1",
        "BYOV_MBCR_ENG_NAME2",
        "BYOV_MBCR_ENG_NAME3",
        "BYOV_MBCR_ENG_NAME4",
        "BYOV_MBCR_ENG_NAME5",
    ]

    return msg, columns
