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
# [국내주식] 실시간시세 > 국내주식 실시간회원사 (KRX) [실시간-047]
##############################################################################################

def member_krx(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간 회원사 (KRX) 데이터 구독 함수 [H0STMBC0]

    이 함수는 한국투자증권 웹소켓 API를 통해 실시간으로 국내주식 회원사 데이터를 구독합니다.
    웹소켓을 통해 실시간 데이터를 수신하며, 구독 등록 및 해제를 지원합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 문자열
        tr_key (str): [필수] 종목코드를 나타내는 문자열. 빈 문자열일 수 없습니다.

    Returns:
        message (dict): 구독 요청에 대한 응답 메시지
        columns (list[str]): 응답 데이터의 컬럼 정보 리스트

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = member_krx("1", "005930")
        >>> print(msg, columns)

    Note:
        실시간 데이터는 웹소켓을 통해 지속적으로 수신됩니다. 구독 해제를 원할 경우, tr_type을 "0"으로 설정하여 호출하십시오.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key is required and cannot be an empty string")

    tr_id = "H0STMBC0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 구독 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터의 컬럼 정보
    columns = [
        "mksc_shrn_iscd",
        "seln2_mbcr_name1",
        "seln2_mbcr_name2",
        "seln2_mbcr_name3",
        "seln2_mbcr_name4",
        "seln2_mbcr_name5",
        "byov_mbcr_name1",
        "byov_mbcr_name2",
        "byov_mbcr_name3",
        "byov_mbcr_name4",
        "byov_mbcr_name5",
        "total_seln_qty1",
        "total_seln_qty2",
        "total_seln_qty3",
        "total_seln_qty4",
        "total_seln_qty5",
        "total_shnu_qty1",
        "total_shnu_qty2",
        "total_shnu_qty3",
        "total_shnu_qty4",
        "total_shnu_qty5",
        "seln_mbcr_glob_yn_1",
        "seln_mbcr_glob_yn_2",
        "seln_mbcr_glob_yn_3",
        "seln_mbcr_glob_yn_4",
        "seln_mbcr_glob_yn_5",
        "shnu_mbcr_glob_yn_1",
        "shnu_mbcr_glob_yn_2",
        "shnu_mbcr_glob_yn_3",
        "shnu_mbcr_glob_yn_4",
        "shnu_mbcr_glob_yn_5",
        "seln_mbcr_no1",
        "seln_mbcr_no2",
        "seln_mbcr_no3",
        "seln_mbcr_no4",
        "seln_mbcr_no5",
        "shnu_mbcr_no1",
        "shnu_mbcr_no2",
        "shnu_mbcr_no3",
        "shnu_mbcr_no4",
        "shnu_mbcr_no5",
        "seln_mbcr_rlim1",
        "seln_mbcr_rlim2",
        "seln_mbcr_rlim3",
        "seln_mbcr_rlim4",
        "seln_mbcr_rlim5",
        "shnu_mbcr_rlim1",
        "shnu_mbcr_rlim2",
        "shnu_mbcr_rlim3",
        "shnu_mbcr_rlim4",
        "shnu_mbcr_rlim5",
        "seln_qty_icdc1",
        "seln_qty_icdc2",
        "seln_qty_icdc3",
        "seln_qty_icdc4",
        "seln_qty_icdc5",
        "shnu_qty_icdc1",
        "shnu_qty_icdc2",
        "shnu_qty_icdc3",
        "shnu_qty_icdc4",
        "shnu_qty_icdc5",
        "glob_total_seln_qty",
        "glob_total_shnu_qty",
        "glob_total_seln_qty_icdc",
        "glob_total_shnu_qty_icdc",
        "glob_ntby_qty",
        "glob_seln_rlim",
        "glob_shnu_rlim",
        "seln2_mbcr_eng_name1",
        "seln2_mbcr_eng_name2",
        "seln2_mbcr_eng_name3",
        "seln2_mbcr_eng_name4",
        "seln2_mbcr_eng_name5",
        "byov_mbcr_eng_name1",
        "byov_mbcr_eng_name2",
        "byov_mbcr_eng_name3",
        "byov_mbcr_eng_name4",
        "byov_mbcr_eng_name5",
    ]

    return msg, columns
