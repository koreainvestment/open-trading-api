import logging
import sys

sys.path.extend(['..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 - ELW 실시간호가[실시간-062]
##############################################################################################

def elw_asking_price(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    ELW 실시간호가[H0EWASP0]
    ELW 실시간 호가 정보를 실시간으로 구독하는 웹소켓 API입니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타냅니다.
        tr_key (str): [필수] 종목코드. 빈 문자열일 수 없습니다.

    Returns:
        message (dict): 실시간 데이터 구독에 대한 응답 메시지.
        columns (list[str]): 실시간 데이터의 컬럼 정보.

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생합니다.

    Example:
        >>> msg, columns = elw_asking_price("1", "005930")
        >>> print(msg, columns)

    [참고자료]
    종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key is required and cannot be an empty string")

    tr_id = "H0EWASP0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 구독 요청
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
        "askp10",
        "bidp1",
        "bidp2",
        "bidp3",
        "bidp4",
        "bidp5",
        "bidp6",
        "bidp7",
        "bidp8",
        "bidp9",
        "bidp10",
        "askp_rsqn1",
        "askp_rsqn2",
        "askp_rsqn3",
        "askp_rsqn4",
        "askp_rsqn5",
        "askp_rsqn6",
        "askp_rsqn7",
        "askp_rsqn8",
        "askp_rsqn9",
        "askp_rsqn10",
        "bidp_rsqn1",
        "bidp_rsqn2",
        "bidp_rsqn3",
        "bidp_rsqn4",
        "bidp_rsqn5",
        "bidp_rsqn6",
        "bidp_rsqn7",
        "bidp_rsqn8",
        "bidp_rsqn9",
        "bidp_rsqn10",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "antc_cnpr",
        "antc_cnqn",
        "antc_cntg_vrss_sign",
        "antc_cntg_vrss",
        "antc_cntg_prdy_ctrt",
        "lp_askp_rsqn1",
        "lp_askp_rsqn2",
        "lp_askp_rsqn3",
        "lp_bidp_rsqn4",
        "lp_askp_rsqn4",
        "lp_bidp_rsqn5",
        "lp_askp_rsqn5",
        "lp_bidp_rsqn6",
        "lp_askp_rsqn6",
        "lp_bidp_rsqn7",
        "lp_askp_rsqn7",
        "lp_askp_rsqn8",
        "lp_bidp_rsqn8",
        "lp_askp_rsqn9",
        "lp_bidp_rsqn9",
        "lp_askp_rsqn10",
        "lp_bidp_rsqn10",
        "lp_bidp_rsqn1",
        "lp_total_askp_rsqn",
        "lp_bidp_rsqn2",
        "lp_total_bidp_rsqn",
        "lp_bidp_rsqn3",
        "antc_vol",
    ]

    return msg, columns

##############################################################################################
# [국내주식] 실시간시세 - ELW 실시간체결가[실시간-061]
##############################################################################################

def elw_ccnl(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    ELW 실시간체결가[H0EWCNT0] 구독 함수
    ELW 실시간체결가 API를 통해 실시간 데이터를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타냅니다.
        tr_key (str): [필수] 종목코드를 입력합니다. 빈 문자열이 아니어야 합니다.

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 실시간 데이터의 컬럼 정보

    Example:
        >>> msg, columns = elw_ccnl("1", "005930")
        >>> print(msg, columns)

    [참고자료]
    종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 필수 입력값입니다.")

    tr_id = "H0EWCNT0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 구독 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
    columns = [
        "mksc_shrn_iscd", "stck_cntg_hour", "stck_prpr", "prdy_vrss_sign",
        "prdy_vrss", "prdy_ctrt", "wghn_avrg_stck_prc", "stck_oprc",
        "stck_hgpr", "stck_lwpr", "askp1", "bidp1", "cntg_vol", "acml_vol",
        "acml_tr_pbmn", "seln_cntg_csnu", "shnu_cntg_csnu", "ntby_cntg_csnu",
        "cttr", "seln_cntg_smtn", "shnu_cntg_smtn", "cntg_cls_code",
        "shnu_rate", "prdy_vol_vrss_acml_vol_rate", "oprc_hour",
        "oprc_vrss_prpr_sign", "oprc_vrss_prpr", "hgpr_hour",
        "hgpr_vrss_prpr_sign", "hgpr_vrss_prpr", "lwpr_hour",
        "lwpr_vrss_prpr_sign", "lwpr_vrss_prpr", "bsop_date",
        "new_mkop_cls_code", "trht_yn", "askp_rsqn1", "bidp_rsqn1",
        "total_askp_rsqn", "total_bidp_rsqn", "tmvl_val", "prit", "prmm_val",
        "gear", "prls_qryr_rate", "invl_val", "prmm_rate", "cfp", "lvrg_val",
        "delta", "gama", "vega", "theta", "rho", "hts_ints_vltl", "hts_thpr",
        "vol_tnrt", "prdy_smns_hour_acml_vol", "prdy_smns_hour_acml_vol_rate",
        "apprch_rate", "lp_hvol", "lp_hldn_rate", "lp_ntby_qty"
    ]

    return msg, columns

##############################################################################################
# [국내주식] 실시간시세 - ELW 실시간예상체결[실시간-063]
##############################################################################################

def elw_exp_ccnl(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    ELW 실시간예상체결[H0EWANC0]
    ELW 실시간예상체결 API입니다. 이 함수는 웹소켓을 통해 실시간 데이터를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타냅니다.
        tr_key (str): [필수] 종목코드. 빈 문자열일 수 없습니다.

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 응답 데이터의 컬럼 정보

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생합니다.

    Example:
        >>> msg, columns = elw_exp_ccnl("1", "005930")
        >>> print(msg, columns)

    [참고자료]
    종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key is required and cannot be an empty string")

    tr_id = "H0EWANC0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 구독 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터의 컬럼 정보
    columns = [
        "mksc_shrn_iscd",
        "stck_cntg_hour",
        "stck_prpr",
        "prdy_vrss_sign",
        "prdy_vrss",
        "prdy_ctrt",
        "wghn_avrg_stck_prc",
        "stck_oprc",
        "stck_hgpr",
        "stck_lwpr",
        "askp1",
        "bidp1",
        "cntg_vol",
        "acml_vol",
        "acml_tr_pbmn",
        "seln_cntg_csnu",
        "shnu_cntg_csnu",
        "ntby_cntg_csnu",
        "cttr",
        "seln_cntg_smtn",
        "shnu_cntg_smtn",
        "cntg_cls_code",
        "shnu_rate",
        "prdy_vol_vrss_acml_vol_rate",
        "oprc_hour",
        "oprc_vrss_prpr_sign",
        "oprc_vrss_prpr",
        "hgpr_hour",
        "hgpr_vrss_prpr_sign",
        "hgpr_vrss_prpr",
        "lwpr_hour",
        "lwpr_vrss_prpr_sign",
        "lwpr_vrss_prpr",
        "bsop_date",
        "new_mkop_cls_code",
        "trht_yn",
        "askp_rsqn1",
        "bidp_rsqn1",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "tmvl_val",
        "prit",
        "prmm_val",
        "gear",
        "prls_qryr_rate",
        "invl_val",
        "prmm_rate",
        "cfp",
        "lvrg_val",
        "delta",
        "gama",
        "vega",
        "theta",
        "rho",
        "hts_ints_vltl",
        "hts_thpr",
        "vol_tnrt",
        "lp_hvol",
        "lp_hldn_rate",
    ]

    return msg, columns

