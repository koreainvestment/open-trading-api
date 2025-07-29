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
# [국내주식] 실시간시세 > 국내주식 시간외 실시간호가 (KRX) [실시간-025]
##############################################################################################


def overtime_asking_price_krx(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 시간외 실시간호가 (KRX)[H0STOAA0]
    국내주식 시간외 실시간호가 API입니다.
    국내주식 시간외 단일가(16:00~18:00) 시간대에 실시간호가 데이터 확인 가능합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = subscribe_overtime_asking_price_krx("1", "005930")
        >>> print(msg, columns)

    실시간 데이터는 웹소켓을 통해 지속적으로 수신됩니다. 구독을 해제하지 않으면 데이터가 계속 수신됩니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 필수 입력값입니다.")

    tr_id = "H0STOAA0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
    columns = [
        "mksc_shrn_iscd",
        "bsop_hour",
        "hour_cls_code",
        "askp1",
        "askp2",
        "askp3",
        "askp4",
        "askp5",
        "askp6",
        "askp7",
        "askp8",
        "askp9",
        "bidp1",
        "bidp2",
        "bidp3",
        "bidp4",
        "bidp5",
        "bidp6",
        "bidp7",
        "bidp8",
        "bidp9",
        "askp_rsqn1",
        "askp_rsqn2",
        "askp_rsqn3",
        "askp_rsqn4",
        "askp_rsqn5",
        "askp_rsqn6",
        "askp_rsqn7",
        "askp_rsqn8",
        "askp_rsqn9",
        "bidp_rsqn1",
        "bidp_rsqn2",
        "bidp_rsqn3",
        "bidp_rsqn4",
        "bidp_rsqn5",
        "bidp_rsqn6",
        "bidp_rsqn7",
        "bidp_rsqn8",
        "bidp_rsqn9",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "ovtm_total_askp_rsqn",
        "ovtm_total_bidp_rsqn",
        "antc_cnpr",
        "antc_cnqn",
        "antc_vol",
        "antc_cntg_vrss",
        "antc_cntg_vrss_sign",
        "antc_cntg_prdy_ctrt",
        "acml_vol",
        "total_askp_rsqn_icdc",
        "total_bidp_rsqn_icdc",
        "ovtm_total_askp_icdc",
        "ovtm_total_bidp_icdc",
    ]

    return msg, columns
