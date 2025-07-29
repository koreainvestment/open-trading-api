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
# [장내채권] 실시간시세 > 일반채권 실시간호가 [실시간-053]
##############################################################################################

def bond_asking_price(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    일반채권 실시간호가[H0BJASP0]
    일반채권 실시간호가 API를 통해 실시간 데이터를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타냅니다.
        tr_key (str): [필수] 종목코드. 빈 문자열일 수 없습니다.

    Returns:
        message (dict): 실시간 데이터 메시지.
        columns (list[str]): 응답 데이터의 컬럼 정보.

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생합니다.

    Example:
        >>> msg, columns = bond_asking_price("1", "005930")
        >>> print(msg, columns)
        
    [참고자료]
    채권 종목코드 마스터파일은 "KIS포털 - API문서 - 종목정보파일 - 장내채권 - 채권코드" 참고 부탁드립니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key is required and cannot be an empty string")

    tr_id = "H0BJASP0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
    columns = [
        "stnd_iscd",
        "stck_cntg_hour",
        "askp_ert1",
        "bidp_ert1",
        "askp1",
        "bidp1",
        "askp_rsqn1",
        "bidp_rsqn1",
        "askp_ert2",
        "bidp_ert2",
        "askp2",
        "bidp2",
        "askp_rsqn2",
        "bidp_rsqn2",
        "askp_ert3",
        "bidp_ert3",
        "askp3",
        "bidp3",
        "askp_rsqn3",
        "bidp_rsqn3",
        "askp_ert4",
        "bidp_ert4",
        "askp4",
        "bidp4",
        "askp_rsqn4",
        "bidp_rsqn4",
        "askp_ert5",
        "bidp_ert5",
        "askp5",
        "bidp5",
        "askp_rsqn52",
        "bidp_rsqn53",
        "total_askp_rsqn",
        "total_bidp_rsqn",
    ]

    return msg, columns
