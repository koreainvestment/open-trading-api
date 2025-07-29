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
# [국내주식] 실시간시세 > 국내지수 실시간프로그램매매 [실시간-028]
##############################################################################################

def index_program_trade(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내지수 실시간프로그램매매[H0UPPGM0] 구독 함수

    이 함수는 한국투자증권의 웹소켓 API를 통해 국내지수의 실시간 프로그램 매매 데이터를 구독합니다.
    실시간 데이터를 구독하거나 구독 해제할 수 있습니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 문자열
        tr_key (str): [필수] 종목코드를 나타내는 문자열. 빈 문자열일 수 없습니다.

    Returns:
        message (dict): 웹소켓으로부터 수신된 메시지 데이터
        columns (list[str]): 응답 데이터의 컬럼 정보 리스트

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = index_program_trade("1", "005930")
        >>> print(msg, columns)

    참고자료:
    종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key is required and cannot be an empty string")

    tr_id = "H0UPPGM0"

    params = {
        "tr_key": tr_key,
    }

    # 웹소켓을 통해 데이터 구독 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터의 컬럼 정보
    columns = [
        "bstp_cls_code", "bsop_hour", "arbt_seln_entm_cnqn", "arbt_seln_onsl_cnqn",
        "arbt_shnu_entm_cnqn", "arbt_shnu_onsl_cnqn", "nabt_seln_entm_cnqn",
        "nabt_seln_onsl_cnqn", "nabt_shnu_entm_cnqn", "nabt_shnu_onsl_cnqn",
        "arbt_seln_entm_cntg_amt", "arbt_seln_onsl_cntg_amt", "arbt_shnu_entm_cntg_amt",
        "arbt_shnu_onsl_cntg_amt", "nabt_seln_entm_cntg_amt", "nabt_seln_onsl_cntg_amt",
        "nabt_shnu_entm_cntg_amt", "nabt_shnu_onsl_cntg_amt", "arbt_smtn_seln_vol",
        "arbt_smtm_seln_vol_rate", "arbt_smtn_seln_tr_pbmn", "arbt_smtm_seln_tr_pbmn_rate",
        "arbt_smtn_shnu_vol", "arbt_smtm_shnu_vol_rate", "arbt_smtn_shnu_tr_pbmn",
        "arbt_smtm_shnu_tr_pbmn_rate", "arbt_smtn_ntby_qty", "arbt_smtm_ntby_qty_rate",
        "arbt_smtn_ntby_tr_pbmn", "arbt_smtm_ntby_tr_pbmn_rate", "nabt_smtn_seln_vol",
        "nabt_smtm_seln_vol_rate", "nabt_smtn_seln_tr_pbmn", "nabt_smtm_seln_tr_pbmn_rate",
        "nabt_smtn_shnu_vol", "nabt_smtm_shnu_vol_rate", "nabt_smtn_shnu_tr_pbmn",
        "nabt_smtm_shnu_tr_pbmn_rate", "nabt_smtn_ntby_qty", "nabt_smtm_ntby_qty_rate",
        "nabt_smtn_ntby_tr_pbmn", "nabt_smtm_ntby_tr_pbmn_rate", "whol_entm_seln_vol",
        "entm_seln_vol_rate", "whol_entm_seln_tr_pbmn", "entm_seln_tr_pbmn_rate",
        "whol_entm_shnu_vol", "entm_shnu_vol_rate", "whol_entm_shnu_tr_pbmn",
        "entm_shnu_tr_pbmn_rate", "whol_entm_ntby_qt", "entm_ntby_qty_rat",
        "whol_entm_ntby_tr_pbmn", "entm_ntby_tr_pbmn_rate", "whol_onsl_seln_vol",
        "onsl_seln_vol_rate", "whol_onsl_seln_tr_pbmn", "onsl_seln_tr_pbmn_rate",
        "whol_onsl_shnu_vol", "onsl_shnu_vol_rate", "whol_onsl_shnu_tr_pbmn",
        "onsl_shnu_tr_pbmn_rate", "whol_onsl_ntby_qty", "onsl_ntby_qty_rate",
        "whol_onsl_ntby_tr_pbmn", "onsl_ntby_tr_pbmn_rate", "total_seln_qty",
        "whol_seln_vol_rate", "total_seln_tr_pbmn", "whol_seln_tr_pbmn_rate",
        "shnu_cntg_smtn", "whol_shun_vol_rate", "total_shnu_tr_pbmn",
        "whol_shun_tr_pbmn_rate", "whol_ntby_qty", "whol_smtm_ntby_qty_rate",
        "whol_ntby_tr_pbmn", "whol_ntby_tr_pbmn_rate", "arbt_entm_ntby_qty",
        "arbt_entm_ntby_tr_pbmn", "arbt_onsl_ntby_qty", "arbt_onsl_ntby_tr_pbmn",
        "nabt_entm_ntby_qty", "nabt_entm_ntby_tr_pbmn", "nabt_onsl_ntby_qty",
        "nabt_onsl_ntby_tr_pbmn", "acml_vol", "acml_tr_pbmn",
    ]

    return msg, columns
