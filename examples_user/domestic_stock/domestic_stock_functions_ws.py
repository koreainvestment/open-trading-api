import logging
import sys

sys.path.extend(['..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간호가 (KRX) [실시간-004]
##############################################################################################

def asking_price_krx(
        tr_type: str,
        tr_key: str,
        env_dv: str = "real",  # 실전모의구분
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간 호가 데이터 구독 (KRX)[H0STASP0]
    
    이 함수는 한국투자증권 웹소켓 API를 통해 실시간으로 국내주식의 호가 데이터를 구독합니다.
    웹소켓을 통해 실시간 데이터를 수신하며, 구독 등록 및 해제 기능을 제공합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)
        env_dv (str): 실전모의구분 (real: 실전, demo: 모의)

    Returns:
        message (dict): 실시간 데이터 구독에 대한 메시지 데이터
        columns (list[str]): 실시간 데이터의 컬럼 정보

    Raises:
        ValueError: 필수 파라미터가 누락되었거나 잘못된 경우 발생

    Example:
        >>> msg, columns = subscribe_krx_realtime_asking_price("1", "005930", env_dv="real")
        >>> print(msg, columns)

    실시간 데이터는 웹소켓을 통해 지속적으로 수신되며, 구독 해제 시까지 계속됩니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 필수 입력값입니다.")

    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real":
        tr_id = "H0STASP0"  # 실전투자용 TR ID
    elif env_dv == "demo":
        tr_id = "H0STASP0"  # 모의투자용 TR ID (웹소켓은 동일한 TR ID 사용)
    else:
        raise ValueError("env_dv는 'real' 또는 'demo'만 가능합니다.")

    params = {
        "tr_key": tr_key,
    }

    # 데이터 구독 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
    columns = [
        "MKSC_SHRN_ISCD", "BSOP_HOUR", "HOUR_CLS_CODE",
        "ASKP1", "ASKP2", "ASKP3", "ASKP4", "ASKP5",
        "ASKP6", "ASKP7", "ASKP8", "ASKP9", "ASKP10",
        "BIDP1", "BIDP2", "BIDP3", "BIDP4", "BIDP5",
        "BIDP6", "BIDP7", "BIDP8", "BIDP9", "BIDP10",
        "ASKP_RSQN1", "ASKP_RSQN2", "ASKP_RSQN3", "ASKP_RSQN4", "ASKP_RSQN5",
        "ASKP_RSQN6", "ASKP_RSQN7", "ASKP_RSQN8", "ASKP_RSQN9", "ASKP_RSQN10",
        "BIDP_RSQN1", "BIDP_RSQN2", "BIDP_RSQN3", "BIDP_RSQN4", "BIDP_RSQN5",
        "BIDP_RSQN6", "BIDP_RSQN7", "BIDP_RSQN8", "BIDP_RSQN9", "BIDP_RSQN10",
        "TOTAL_ASKP_RSQN", "TOTAL_BIDP_RSQN", "OVTM_TOTAL_ASKP_RSQN", "OVTM_TOTAL_BIDP_RSQN",
        "ANTC_CNPR", "ANTC_CNQN", "ANTC_VOL", "ANTC_CNTG_VRSS", "ANTC_CNTG_VRSS_SIGN",
        "ANTC_CNTG_PRDY_CTRT", "ACML_VOL", "TOTAL_ASKP_RSQN_ICDC", "TOTAL_BIDP_RSQN_ICDC",
        "OVTM_TOTAL_ASKP_ICDC", "OVTM_TOTAL_BIDP_ICDC", "STCK_DEAL_CLS_CODE"
    ]

    return msg, columns

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간호가 (NXT)
##############################################################################################

def asking_price_nxt(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간호가 (NXT)[H0NXASP0] 구독 함수
    국내주식 실시간호가 (NXT) API를 통해 실시간 데이터를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 값
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)

    Returns:
        message (dict): 실시간 데이터 메시지
        columns (list[str]): 데이터의 컬럼 정보

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = subscribe_asking_price("1", "005930")
        >>> print(msg, columns)

    Note:
        이 함수는 웹소켓을 통해 실시간 데이터를 구독합니다. 구독을 시작하면 실시간으로 데이터가 수신됩니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 빈 문자열일 수 없습니다.")

    tr_id = "H0NXASP0"

    params = {
        "tr_key": tr_key,
    }

    # 웹소켓을 통해 실시간 데이터 구독
    msg = ka.data_fetch(tr_id, tr_type, params)

    # API 메타데이터 기반 컬럼 정보
    columns = [
        "MKSC_SHRN_ISCD",
        "BSOP_HOUR",
        "HOUR_CLS_CODE",
        "ASKP1",
        "ASKP2",
        "ASKP3",
        "ASKP4",
        "ASKP5",
        "ASKP6",
        "ASKP7",
        "ASKP8",
        "ASKP9",
        "ASKP10",
        "BIDP1",
        "BIDP2",
        "BIDP3",
        "BIDP4",
        "BIDP5",
        "BIDP6",
        "BIDP7",
        "BIDP8",
        "BIDP9",
        "BIDP10",
        "ASKP_RSQN1",
        "ASKP_RSQN2",
        "ASKP_RSQN3",
        "ASKP_RSQN4",
        "ASKP_RSQN5",
        "ASKP_RSQN6",
        "ASKP_RSQN7",
        "ASKP_RSQN8",
        "ASKP_RSQN9",
        "ASKP_RSQN10",
        "BIDP_RSQN1",
        "BIDP_RSQN2",
        "BIDP_RSQN3",
        "BIDP_RSQN4",
        "BIDP_RSQN5",
        "BIDP_RSQN6",
        "BIDP_RSQN7",
        "BIDP_RSQN8",
        "BIDP_RSQN9",
        "BIDP_RSQN10",
        "TOTAL_ASKP_RSQN",
        "TOTAL_BIDP_RSQN",
        "OVTM_TOTAL_ASKP_RSQN",
        "OVTM_TOTAL_BIDP_RSQN",
        "ANTC_CNPR",
        "ANTC_CNQN",
        "ANTC_VOL",
        "ANTC_CNTG_VRSS",
        "ANTC_CNTG_VRSS_SIGN",
        "ANTC_CNTG_PRDY_CTRT",
        "ACML_VOL",
        "TOTAL_ASKP_RSQN_ICDC",
        "TOTAL_BIDP_RSQN_ICDC",
        "OVTM_TOTAL_ASKP_ICDC",
        "OVTM_TOTAL_BIDP_ICDC",
        "STCK_DEAL_CLS_CODE",
        "KMID_PRC",
        "KMID_TOTAL_RSQN",
        "KMID_CLS_CODE",
        "NMID_PRC",
        "NMID_TOTAL_RSQN",
        "NMID_CLS_CODE",
    ]

    return msg, columns

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간호가 (통합)
##############################################################################################

def asking_price_total(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간호가 (통합)[H0UNASP0]
    국내주식 실시간호가 (통합) API를 통해 실시간 데이터를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 값
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)

    Returns:
        message (dict): 실시간 데이터 메시지
        columns (list[str]): 응답 데이터의 컬럼 정보

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = subscribe_asking_price("1", "005930")
        >>> print(msg, columns)

    Note:
        이 함수는 웹소켓을 통해 실시간 데이터를 구독합니다. 구독을 시작하면 서버로부터 실시간 데이터가 지속적으로 전송됩니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 빈 문자열일 수 없습니다.")

    tr_id = "H0UNASP0"

    params = {
        "tr_key": tr_key,
    }

    # 웹소켓을 통해 실시간 데이터 구독
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터의 컬럼 정보
    columns = [
        "MKSC_SHRN_ISCD",
        "BSOP_HOUR",
        "HOUR_CLS_CODE",
        "ASKP1",
        "ASKP2",
        "ASKP3",
        "ASKP4",
        "ASKP5",
        "ASKP6",
        "ASKP7",
        "ASKP8",
        "ASKP9",
        "ASKP10",
        "BIDP1",
        "BIDP2",
        "BIDP3",
        "BIDP4",
        "BIDP5",
        "BIDP6",
        "BIDP7",
        "BIDP8",
        "BIDP9",
        "BIDP10",
        "ASKP_RSQN1",
        "ASKP_RSQN2",
        "ASKP_RSQN3",
        "ASKP_RSQN4",
        "ASKP_RSQN5",
        "ASKP_RSQN6",
        "ASKP_RSQN7",
        "ASKP_RSQN8",
        "ASKP_RSQN9",
        "ASKP_RSQN10",
        "BIDP_RSQN1",
        "BIDP_RSQN2",
        "BIDP_RSQN3",
        "BIDP_RSQN4",
        "BIDP_RSQN5",
        "BIDP_RSQN6",
        "BIDP_RSQN7",
        "BIDP_RSQN8",
        "BIDP_RSQN9",
        "BIDP_RSQN10",
        "TOTAL_ASKP_RSQN",
        "TOTAL_BIDP_RSQN",
        "OVTM_TOTAL_ASKP_RSQN",
        "OVTM_TOTAL_BIDP_RSQN",
        "ANTC_CNPR",
        "ANTC_CNQN",
        "ANTC_VOL",
        "ANTC_CNTG_VRSS",
        "ANTC_CNTG_VRSS_SIGN",
        "ANTC_CNTG_PRDY_CTRT",
        "ACML_VOL",
        "TOTAL_ASKP_RSQN_ICDC",
        "TOTAL_BIDP_RSQN_ICDC",
        "OVTM_TOTAL_ASKP_ICDC",
        "OVTM_TOTAL_BIDP_ICDC",
        "STCK_DEAL_CLS_CODE",
        "KMID_PRC",
        "KMID_TOTAL_RSQN",
        "KMID_CLS_CODE",
        "NMID_PRC",
        "NMID_TOTAL_RSQN",
        "NMID_CLS_CODE",
    ]

    return msg, columns

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간체결가(KRX) [실시간-003]
##############################################################################################

def ccnl_krx(
        tr_type: str,
        tr_key: str,
        env_dv: str = "real",  # 실전모의구분
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간체결가 (KRX)[H0STCNT0] 구독 함수

    이 함수는 한국투자증권 웹소켓 API를 통해 국내 주식의 실시간 체결가 데이터를 구독합니다.
    실시간 데이터를 구독하거나 구독 해제할 수 있습니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)
        env_dv (str): 실전모의구분 (real:실전, demo:모의)

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Raises:
        ValueError: tr_key가 빈 문자열인 경우
        ValueError: env_dv가 'real' 또는 'demo'가 아닌 경우

    Example:
        >>> msg, columns = ccnl_krx("1", "005930", env_dv="real")
        >>> print(msg, columns)

    실시간 데이터는 웹소켓을 통해 지속적으로 업데이트됩니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key is required and cannot be an empty string")

    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real":
        tr_id = "H0STCNT0"  # 실전투자용 TR ID
    elif env_dv == "demo":
        tr_id = "H0STCNT0"  # 모의투자용 TR ID (웹소켓은 동일한 TR ID 사용)
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "tr_key": tr_key,
    }

    # 데이터 구독 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
    columns = [
        "MKSC_SHRN_ISCD", "STCK_CNTG_HOUR", "STCK_PRPR", "PRDY_VRSS_SIGN",
        "PRDY_VRSS", "PRDY_CTRT", "WGHN_AVRG_STCK_PRC", "STCK_OPRC",
        "STCK_HGPR", "STCK_LWPR", "ASKP1", "BIDP1", "CNTG_VOL", "ACML_VOL",
        "ACML_TR_PBMN", "SELN_CNTG_CSNU", "SHNU_CNTG_CSNU", "NTBY_CNTG_CSNU",
        "CTTR", "SELN_CNTG_SMTN", "SHNU_CNTG_SMTN", "CCLD_DVSN", "SHNU_RATE",
        "PRDY_VOL_VRSS_ACML_VOL_RATE", "OPRC_HOUR", "OPRC_VRSS_PRPR_SIGN",
        "OPRC_VRSS_PRPR", "HGPR_HOUR", "HGPR_VRSS_PRPR_SIGN", "HGPR_VRSS_PRPR",
        "LWPR_HOUR", "LWPR_VRSS_PRPR_SIGN", "LWPR_VRSS_PRPR", "BSOP_DATE",
        "NEW_MKOP_CLS_CODE", "TRHT_YN", "ASKP_RSQN1", "BIDP_RSQN1",
        "TOTAL_ASKP_RSQN", "TOTAL_BIDP_RSQN", "VOL_TNRT",
        "PRDY_SMNS_HOUR_ACML_VOL", "PRDY_SMNS_HOUR_ACML_VOL_RATE",
        "HOUR_CLS_CODE", "MRKT_TRTM_CLS_CODE", "VI_STND_PRC"
    ]

    return msg, columns

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 주식체결통보 [실시간-005]
##############################################################################################

def ccnl_notice(
        tr_type: str,
        tr_key: str,
        env_dv: str = "real",  # 실전모의구분
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간체결통보[H0STCNI0]
    국내주식 실시간 체결통보 수신 시에 (1) 주문·정정·취소·거부 접수 통보 와 (2) 체결 통보 가 모두 수신됩니다.
    (14번째 값(CNTG_YN;체결여부)가 2이면 체결통보, 1이면 주문·정정·취소·거부 접수 통보입니다.)

    ※ 모의투자는 H0STCNI9 로 변경하여 사용합니다.

    실시간 데이터 구독을 위한 웹소켓 함수입니다. 구독을 등록하거나 해제할 수 있습니다.

    Args:
        tr_type (str): [필수] 구독 등록("1")/해제("0") 여부
        tr_key (str): [필수] 종목코드 (예: "005930")
        env_dv (str): 실전모의구분 (real:실전, demo:모의)

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = ccnl_notice("1", "005930", env_dv="real")
        >>> print(msg, columns)

    웹소켓을 통해 실시간 데이터를 수신하며, 데이터는 암호화되어 제공됩니다. 
    AES256 KEY와 IV를 사용하여 복호화해야 합니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 필수 입력값입니다.")

    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real":
        tr_id = "H0STCNI0"  # 실전투자용 TR ID
    elif env_dv == "demo":
        tr_id = "H0STCNI9"  # 모의투자용 TR ID
    else:
        raise ValueError("env_dv는 'real' 또는 'demo'만 가능합니다.")

    params = {
        "tr_key": tr_key,
    }

    # 데이터 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
    columns = [
        "CUST_ID", "ACNT_NO", "ODER_NO", "ODER_QTY", "SELN_BYOV_CLS", "RCTF_CLS",
        "ODER_KIND", "ODER_COND", "STCK_SHRN_ISCD", "CNTG_QTY", "CNTG_UNPR",
        "STCK_CNTG_HOUR", "RFUS_YN", "CNTG_YN", "ACPT_YN", "BRNC_NO", "ACNT_NO2",
        "ACNT_NAME", "ORD_COND_PRC", "ORD_EXG_GB", "POPUP_YN", "FILLER", "CRDT_CLS",
        "CRDT_LOAN_DATE", "CNTG_ISNM40", "ODER_PRC"
    ]

    return msg, columns

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간체결가 (NXT)
##############################################################################################

def ccnl_nxt(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간체결가 (NXT)[H0NXCNT0]
    국내주식 실시간체결가 (NXT) API를 통해 실시간 데이터를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 값
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)

    Returns:
        message (dict): 실시간 체결가 데이터 메시지
        columns (list[str]): 데이터의 컬럼 정보 리스트

    Example:
        >>> msg, columns = ccnl_nxt("1", "005930")
        >>> print(msg, columns)

    Note:
        이 함수는 웹소켓을 통해 실시간 데이터를 구독합니다. 구독을 시작하려면 tr_type을 "1"로 설정하고,
        구독을 해제하려면 "0"으로 설정하세요. tr_key는 유효한 종목코드를 입력해야 합니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 필수 입력값입니다. 유효한 종목코드를 입력하세요.")

    tr_id = "H0NXCNT0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 페치
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 컬럼 정보
    columns = [
        "MKSC_SHRN_ISCD", "STCK_CNTG_HOUR", "STCK_PRPR", "PRDY_VRSS_SIGN",
        "PRDY_VRSS", "PRDY_CTRT", "WGHN_AVRG_STCK_PRC", "STCK_OPRC",
        "STCK_HGPR", "STCK_LWPR", "ASKP1", "BIDP1", "CNTG_VOL", "ACML_VOL",
        "ACML_TR_PBMN", "SELN_CNTG_CSNU", "SHNU_CNTG_CSNU", "NTBY_CNTG_CSNU",
        "CTTR", "SELN_CNTG_SMTN", "SHNU_CNTG_SMTN", "CNTG_CLS_CODE",
        "SHNU_RATE", "PRDY_VOL_VRSS_ACML_VOL_RATE", "OPRC_HOUR",
        "OPRC_VRSS_PRPR_SIGN", "OPRC_VRSS_PRPR", "HGPR_HOUR",
        "HGPR_VRSS_PRPR_SIGN", "HGPR_VRSS_PRPR", "LWPR_HOUR",
        "LWPR_VRSS_PRPR_SIGN", "LWPR_VRSS_PRPR", "BSOP_DATE",
        "NEW_MKOP_CLS_CODE", "TRHT_YN", "ASKP_RSQN1", "BIDP_RSQN1",
        "TOTAL_ASKP_RSQN", "TOTAL_BIDP_RSQN", "VOL_TNRT",
        "PRDY_SMNS_HOUR_ACML_VOL", "PRDY_SMNS_HOUR_ACML_VOL_RATE",
        "HOUR_CLS_CODE", "MRKT_TRTM_CLS_CODE", "VI_STND_PRC"
    ]

    return msg, columns

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간체결가 (통합)
##############################################################################################

def ccnl_total(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간체결가 (통합)[H0UNCNT0]
    국내주식 실시간체결가 (통합) API를 통해 실시간 데이터를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 값
        tr_key (str): [필수] 종목코드, 실시간 데이터를 구독할 주식의 종목코드

    Returns:
        message (dict): 실시간 체결가 데이터 메시지
        columns (list[str]): 데이터의 컬럼 정보 리스트

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = ccnl_total("1", "005930")
        >>> print(msg, columns)

    Note:
        이 함수는 웹소켓을 통해 실시간 데이터를 구독합니다. 구독을 시작하려면 tr_type을 "1"로 설정하고,
        구독을 해제하려면 "0"으로 설정하십시오.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key is required and cannot be an empty string")

    tr_id = "H0UNCNT0"

    params = {
        "tr_key": tr_key,
    }

    # 웹소켓을 통해 실시간 데이터를 가져옵니다.
    msg = ka.data_fetch(tr_id, tr_type, params)

    # API 메타데이터에 기반한 정확한 컬럼 리스트
    columns = [
        "MKSC_SHRN_ISCD",
        "STCK_CNTG_HOUR",
        "STCK_PRPR",
        "PRDY_VRSS_SIGN",
        "PRDY_VRSS",
        "PRDY_CTRT",
        "WGHN_AVRG_STCK_PRC",
        "STCK_OPRC",
        "STCK_HGPR",
        "STCK_LWPR",
        "ASKP1",
        "BIDP1",
        "CNTG_VOL",
        "ACML_VOL",
        "ACML_TR_PBMN",
        "SELN_CNTG_CSNU",
        "SHNU_CNTG_CSNU",
        "NTBY_CNTG_CSNU",
        "CTTR",
        "SELN_CNTG_SMTN",
        "SHNU_CNTG_SMTN",
        "CNTG_CLS_CODE",
        "SHNU_RATE",
        "PRDY_VOL_VRSS_ACML_VOL_RATE",
        "OPRC_HOUR",
        "OPRC_VRSS_PRPR_SIGN",
        "OPRC_VRSS_PRPR",
        "HGPR_HOUR",
        "HGPR_VRSS_PRPR_SIGN",
        "HGPR_VRSS_PRPR",
        "LWPR_HOUR",
        "LWPR_VRSS_PRPR_SIGN",
        "LWPR_VRSS_PRPR",
        "BSOP_DATE",
        "NEW_MKOP_CLS_CODE",
        "TRHT_YN",
        "ASKP_RSQN1",
        "BIDP_RSQN1",
        "TOTAL_ASKP_RSQN",
        "TOTAL_BIDP_RSQN",
        "VOL_TNRT",
        "PRDY_SMNS_HOUR_ACML_VOL",
        "PRDY_SMNS_HOUR_ACML_VOL_RATE",
        "HOUR_CLS_CODE",
        "MRKT_TRTM_CLS_CODE",
        "VI_STND_PRC",
    ]

    return msg, columns

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간예상체결 (KRX) [실시간-041]
##############################################################################################

def exp_ccnl_krx(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간예상체결 (KRX)[H0STANC0]
    국내주식 실시간예상체결 API를 통해 실시간 데이터를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타냅니다.
        tr_key (str): [필수] 종목코드. 빈 문자열이 아니어야 하며, 유효한 종목코드 형식이어야 합니다.

    Returns:
        message (dict): 실시간 데이터 구독에 대한 메시지 데이터.
        columns (list[str]): 실시간 데이터의 컬럼 정보.

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생합니다.

    Example:
        >>> msg, columns = exp_ccnl_krx("1", "005930")
        >>> print(msg, columns)

    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key is required and cannot be an empty string")

    tr_id = "H0STANC0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 구독 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
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
        "vol_tnrt",
        "prdy_smns_hour_acml_vol",
        "prdy_smns_hour_acml_vol_rate",
        "hour_cls_code",
        "mrkt_trtm_cls_code",
    ]

    return msg, columns

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간예상체결 (NXT)
##############################################################################################

def exp_ccnl_nxt(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간예상체결 (NXT)[H0NXANC0]
    국내주식 실시간예상체결 (NXT) API를 통해 실시간 데이터를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 값
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)

    Returns:
        message (dict): 실시간 데이터 메시지
        columns (list[str]): 응답 데이터의 컬럼 정보

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = exp_ccnl_nxt("1", "005930")
        >>> print(msg, columns)

    Note:
        이 함수는 웹소켓을 통해 실시간 데이터를 구독합니다. 구독을 시작하면 실시간으로 데이터가 수신됩니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key is required and cannot be an empty string")

    tr_id = "H0NXANC0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 구독 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터의 컬럼 정보
    columns = [
        "MKSC_SHRN_ISCD",
        "STCK_CNTG_HOUR",
        "STCK_PRPR",
        "PRDY_VRSS_SIGN",
        "PRDY_VRSS",
        "PRDY_CTRT",
        "WGHN_AVRG_STCK_PRC",
        "STCK_OPRC",
        "STCK_HGPR",
        "STCK_LWPR",
        "ASKP1",
        "BIDP1",
        "CNTG_VOL",
        "ACML_VOL",
        "ACML_TR_PBMN",
        "SELN_CNTG_CSNU",
        "SHNU_CNTG_CSNU",
        "NTBY_CNTG_CSNU",
        "CTTR",
        "SELN_CNTG_SMTN",
        "SHNU_CNTG_SMTN",
        "CNTG_CLS_CODE",
        "SHNU_RATE",
        "PRDY_VOL_VRSS_ACML_VOL_RATE",
        "OPRC_HOUR",
        "OPRC_VRSS_PRPR_SIGN",
        "OPRC_VRSS_PRPR",
        "HGPR_HOUR",
        "HGPR_VRSS_PRPR_SIGN",
        "HGPR_VRSS_PRPR",
        "LWPR_HOUR",
        "LWPR_VRSS_PRPR_SIGN",
        "LWPR_VRSS_PRPR",
        "BSOP_DATE",
        "NEW_MKOP_CLS_CODE",
        "TRHT_YN",
        "ASKP_RSQN1",
        "BIDP_RSQN1",
        "TOTAL_ASKP_RSQN",
        "TOTAL_BIDP_RSQN",
        "VOL_TNRT",
        "PRDY_SMNS_HOUR_ACML_VOL",
        "PRDY_SMNS_HOUR_ACML_VOL_RATE",
        "HOUR_CLS_CODE",
        "MRKT_TRTM_CLS_CODE",
        "VI_STND_PRC",
    ]

    return msg, columns

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간예상체결(통합)
##############################################################################################

def exp_ccnl_total(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간예상체결 (통합)[H0UNANC0]
    국내주식 실시간예상체결 (통합) API입니다. 이 함수는 웹소켓을 통해 실시간 데이터를 구독하거나 구독 해제합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 값
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)

    Returns:
        message (dict): 실시간 데이터 메시지
        columns (list[str]): 데이터의 컬럼 정보

    Example:
        >>> msg, columns = exp_ccnl_total("1", "005930")
        >>> print(msg, columns)

    Note:
        웹소켓을 통해 실시간 데이터를 수신하며, 구독 등록 시 지속적으로 데이터가 업데이트됩니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 필수 입력값입니다. 빈 문자열을 사용할 수 없습니다.")

    tr_id = "H0UNANC0"

    params = {
        "tr_key": tr_key,
    }

    # 웹소켓을 통해 데이터를 가져옵니다.
    msg = ka.data_fetch(tr_id, tr_type, params)

    # API 메타데이터에 기반한 정확한 컬럼 리스트
    columns = [
        "MKSC_SHRN_ISCD",
        "STCK_CNTG_HOUR",
        "STCK_PRPR",
        "PRDY_VRSS_SIGN",
        "PRDY_VRSS",
        "PRDY_CTRT",
        "WGHN_AVRG_STCK_PRC",
        "STCK_OPRC",
        "STCK_HGPR",
        "STCK_LWPR",
        "ASKP1",
        "BIDP1",
        "CNTG_VOL",
        "ACML_VOL",
        "ACML_TR_PBMN",
        "SELN_CNTG_CSNU",
        "SHNU_CNTG_CSNU",
        "NTBY_CNTG_CSNU",
        "CTTR",
        "SELN_CNTG_SMTN",
        "SHNU_CNTG_SMTN",
        "CNTG_CLS_CODE",
        "SHNU_RATE",
        "PRDY_VOL_VRSS_ACML_VOL_RATE",
        "OPRC_HOUR",
        "OPRC_VRSS_PRPR_SIGN",
        "OPRC_VRSS_PRPR",
        "HGPR_HOUR",
        "HGPR_VRSS_PRPR_SIGN",
        "HGPR_VRSS_PRPR",
        "LWPR_HOUR",
        "LWPR_VRSS_PRPR_SIGN",
        "LWPR_VRSS_PRPR",
        "BSOP_DATE",
        "NEW_MKOP_CLS_CODE",
        "TRHT_YN",
        "ASKP_RSQN1",
        "BIDP_RSQN1",
        "TOTAL_ASKP_RSQN",
        "TOTAL_BIDP_RSQN",
        "VOL_TNRT",
        "PRDY_SMNS_HOUR_ACML_VOL",
        "PRDY_SMNS_HOUR_ACML_VOL_RATE",
        "HOUR_CLS_CODE",
        "MRKT_TRTM_CLS_CODE",
        "VI_STND_PRC",
    ]

    return msg, columns

##############################################################################################
# [국내주식] 실시간시세 > 국내지수 실시간체결 [실시간-026]
##############################################################################################

def index_ccnl(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내지수 실시간체결[H0UPCNT0] 구독 함수

    이 함수는 한국투자증권의 웹소켓 API를 통해 국내지수의 실시간 데이터를 구독합니다.
    실시간 데이터는 웹소켓을 통해 지속적으로 업데이트되며, 구독을 통해 실시간으로 데이터를 수신할 수 있습니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 값
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 응답 데이터의 컬럼 정보

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = subscribe_realtime_index("1", "005930")
        >>> print(msg, columns)

    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 필수 입력값입니다.")

    tr_id = "H0UPCNT0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 구독 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
    columns = [
        "bstp_cls_code", "bsop_hour", "prpr_nmix", "prdy_vrss_sign",
        "bstp_nmix_prdy_vrss", "acml_vol", "acml_tr_pbmn", "pcas_vol",
        "pcas_tr_pbmn", "prdy_ctrt", "oprc_nmix", "nmix_hgpr", "nmix_lwpr",
        "oprc_vrss_nmix_prpr", "oprc_vrss_nmix_sign", "hgpr_vrss_nmix_prpr",
        "hgpr_vrss_nmix_sign", "lwpr_vrss_nmix_prpr", "lwpr_vrss_nmix_sign",
        "prdy_clpr_vrss_oprc_rate", "prdy_clpr_vrss_hgpr_rate",
        "prdy_clpr_vrss_lwpr_rate", "uplm_issu_cnt", "ascn_issu_cnt",
        "stnr_issu_cnt", "down_issu_cnt", "lslm_issu_cnt", "qtqt_ascn_issu_cnt",
        "qtqt_down_issu_cnt", "tick_vrss"
    ]

    return msg, columns

##############################################################################################
# [국내주식] 실시간시세 > 국내지수 실시간예상체결 [실시간-027]
##############################################################################################

def index_exp_ccnl(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내지수 실시간예상체결[H0UPANC0] 구독 함수

    이 함수는 한국투자증권 웹소켓 API를 통해 국내지수의 실시간 데이터를 구독합니다.
    실시간 데이터는 웹소켓을 통해 지속적으로 업데이트되며, 구독 등록/해제 여부와 종목코드를 통해 데이터를 필터링합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 문자열
        tr_key (str): [필수] 종목코드를 나타내는 문자열. 빈 문자열일 수 없습니다.

    Returns:
        message (dict): 실시간 데이터 구독에 대한 응답 메시지
        columns (list[str]): 실시간 데이터의 컬럼 정보 리스트

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = index_exp_ccnl("1", "005930")
        >>> print(msg, columns)

    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key is required and cannot be an empty string")

    tr_id = "H0UPANC0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 구독 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
    columns = [
        "bstp_cls_code", "bsop_hour", "prpr_nmix", "prdy_vrss_sign",
        "bstp_nmix_prdy_vrss", "acml_vol", "acml_tr_pbmn", "pcas_vol",
        "pcas_tr_pbmn", "prdy_ctrt", "oprc_nmix", "nmix_hgpr", "nmix_lwpr",
        "oprc_vrss_nmix_prpr", "oprc_vrss_nmix_sign", "hgpr_vrss_nmix_prpr",
        "hgpr_vrss_nmix_sign", "lwpr_vrss_nmix_prpr", "lwpr_vrss_nmix_sign",
        "prdy_clpr_vrss_oprc_rate", "prdy_clpr_vrss_hgpr_rate",
        "prdy_clpr_vrss_lwpr_rate", "uplm_issu_cnt", "ascn_issu_cnt",
        "stnr_issu_cnt", "down_issu_cnt", "lslm_issu_cnt",
        "qtqt_ascn_issu_cnt", "qtqt_down_issu_cnt", "tick_vrss"
    ]

    return msg, columns

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

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 장운영정보 (KRX) [실시간-049]
##############################################################################################

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

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 장운영정보(NXT)
##############################################################################################

def market_status_nxt(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 장운영정보 (NXT)[H0NXMKO0]
    실시간으로 국내주식 장운영정보를 구독하거나 구독 해제하는 웹소켓 API입니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 값
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)

    Returns:
        message (dict): 실시간으로 수신된 메시지 데이터
        columns (list[str]): 응답 데이터의 컬럼 정보

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = market_status_nxt("1", "005930")
        >>> print(msg, columns)

    Note:
        이 함수는 웹소켓을 통해 실시간 데이터를 구독합니다. 구독을 시작하면 서버로부터 실시간 데이터가 지속적으로 전송됩니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 빈 문자열일 수 없습니다.")

    tr_id = "H0NXMKO0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 수신
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터의 컬럼 정보
    columns = [
        "MKSC_SHRN_ISCD",      # 종목코드
        "TRHT_YN",             # 거래정지 여부
        "TR_SUSP_REAS_CNTT",   # 거래 정지 사유 내용
        "MKOP_CLS_CODE",       # 장운영 구분 코드
        "ANTC_MKOP_CLS_CODE",  # 예상 장운영 구분 코드
        "MRKT_TRTM_CLS_CODE",  # 임의연장구분코드
        "DIVI_APP_CLS_CODE",   # 동시호가배분처리구분코드
        "ISCD_STAT_CLS_CODE",  # 종목상태구분코드
        "VI_CLS_CODE",         # VI적용구분코드
        "OVTM_VI_CLS_CODE",    # 시간외단일가VI적용구분코드
        "EXCH_CLS_CODE",       # 거래소 구분코드
    ]

    return msg, columns

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

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간회원사 (NXT)
##############################################################################################

def member_nxt(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간회원사 (NXT)[H0NXMBC0]
    국내주식 실시간회원사 (NXT) API를 통해 실시간 데이터를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 값
        tr_key (str): [필수] 종목코드, 빈 문자열이 아니어야 함

    Returns:
        message (dict): 실시간 데이터 메시지
        columns (list[str]): 응답 데이터의 컬럼 정보

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = member_nxt("1", "005930")
        >>> print(msg, columns)

    Note:
        이 함수는 웹소켓을 통해 실시간 데이터를 구독합니다. 구독을 시작하려면 tr_type을 "1"로 설정하고,
        구독을 해제하려면 "0"으로 설정하십시오.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 빈 문자열일 수 없습니다.")

    tr_id = "H0NXMBC0"

    params = {
        "tr_key": tr_key,
    }

    # 실시간 데이터 구독 요청
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

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 시간외 실시간체결가 (KRX) [실시간-042]
##############################################################################################

def overtime_ccnl_krx(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 시간외 실시간체결가 (KRX)[H0STOUP0]
    국내주식 시간외 실시간체결가 API입니다.
    국내주식 시간외 단일가(16:00~18:00) 시간대에 실시간체결가 데이터 확인 가능합니다.

    실시간 데이터 구독을 위한 웹소켓 함수입니다. 
    tr_type은 구독 등록("1") 또는 해제("0") 여부를 나타내며, 
    tr_key는 구독할 종목의 코드를 나타냅니다.

    [참고자료]
    종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부
        tr_key (str): [필수] 구독할 종목의 코드 (빈 문자열 불가)

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = overtime_ccnl_krx("1", "005930")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key is required and cannot be an empty string")

    tr_id = "H0STOUP0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
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
        "vol_tnrt",
        "prdy_smns_hour_acml_vol",
        "prdy_smns_hour_acml_vol_rate",
    ]

    return msg, columns

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 시간외 실시간예상체결 (KRX) [실시간-024]
##############################################################################################

def overtime_exp_ccnl_krx(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 시간외 실시간예상체결 (KRX)[H0STOAC0]
    국내주식 시간외 단일가(16:00~18:00) 시간대에 실시간예상체결 데이터를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타냅니다.
        tr_key (str): [필수] 종목코드. 빈 문자열이 아니어야 합니다.

    Returns:
        message (dict): 실시간 데이터 구독에 대한 메시지 데이터.
        columns (list[str]): 실시간 데이터의 컬럼 정보.

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생합니다.

    Example:
        >>> msg, columns = subscribe_overtime_exp_ccnl_krx("1", "005930")
        >>> print(msg, columns)

    실시간 데이터는 웹소켓을 통해 수신되며, 구독이 성공적으로 등록되면 실시간으로 데이터를 받을 수 있습니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 필수 입력값입니다.")

    tr_id = "H0STOAC0"

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
        "vol_tnrt",
        "prdy_smns_hour_acml_vol",
        "prdy_smns_hour_acml_vol_rate",
    ]

    return msg, columns

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간프로그램매매 (KRX)  [실시간-048]
##############################################################################################

def program_trade_krx(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간프로그램매매 (KRX)[H0STPGM0] 구독 함수

    이 함수는 한국투자증권 웹소켓 API를 통해 실시간으로 국내 주식의 프로그램 매매 데이터를 구독합니다.
    웹소켓을 통해 실시간 데이터를 수신하며, 구독 등록 및 해제를 지원합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 문자열
        tr_key (str): [필수] 종목코드. 빈 문자열이 아니어야 하며, 유효한 종목코드 형식이어야 합니다.

    Returns:
        message (dict): 웹소켓을 통해 수신된 메시지 데이터
        columns (list[str]): 응답 데이터의 컬럼 정보 리스트

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = program_trade_krx("1", "005930")
        >>> print(msg, columns)

    실시간 데이터는 웹소켓을 통해 지속적으로 수신되며, 구독 해제 요청을 보내기 전까지 계속됩니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 필수 입력값입니다.")

    # 거래 ID 설정
    tr_id = "H0STPGM0"

    # 요청 파라미터 설정
    params = {
        "tr_key": tr_key,
    }

    # 데이터 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터 컬럼 정보
    columns = [
        "mksc_shrn_iscd",  # 유가증권단축종목코드
        "stck_cntg_hour",  # 주식체결시간
        "seln_cnqn",       # 매도체결량
        "seln_tr_pbmn",    # 매도거래대금
        "shnu_cnqn",       # 매수2체결량
        "shnu_tr_pbmn",    # 매수2거래대금
        "ntby_cnqn",       # 순매수체결량
        "ntby_tr_pbmn",    # 순매수거래대금
        "seln_rsqn",       # 매도호가잔량
        "shnu_rsqn",       # 매수호가잔량
        "whol_ntby_qty",   # 전체순매수호가잔량
    ]

    return msg, columns

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간프로그램매매 (NXT)
##############################################################################################

def program_trade_nxt(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간프로그램매매 (NXT)[H0NXPGM0]
    국내주식 실시간프로그램매매 (NXT) API입니다. 이 함수는 웹소켓을 통해 실시간 데이터를 구독하거나 구독 해제합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 값
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)

    Returns:
        message (dict): 실시간 데이터 메시지
        columns (list[str]): 응답 데이터의 컬럼 정보

    Example:
        >>> msg, columns = program_trade_nxt("1", "005930")
        >>> print(msg, columns)

    Note:
        실시간 데이터는 웹소켓을 통해 지속적으로 업데이트됩니다. 구독을 해제하지 않으면 데이터 스트림이 계속 유지됩니다.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 필수 입력값입니다.")

    # 거래 ID 설정
    tr_id = "H0NXPGM0"

    # 요청 파라미터 설정
    params = {
        "tr_key": tr_key,
    }

    # 데이터 요청
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터의 컬럼 정보
    columns = [
        "MKSC_SHRN_ISCD",  # 유가증권 단축 종목코드
        "STCK_CNTG_HOUR",  # 주식 체결 시간
        "SELN_CNQN",       # 매도 체결량
        "SELN_TR_PBMN",    # 매도 거래 대금
        "SHNU_CNQN",       # 매수2 체결량
        "SHNU_TR_PBMN",    # 매수2 거래 대금
        "NTBY_CNQN",       # 순매수 체결량
        "NTBY_TR_PBMN",    # 순매수 거래 대금
        "SELN_RSQN",       # 매도호가잔량
        "SHNU_RSQN",       # 매수호가잔량
        "WHOL_NTBY_QTY",   # 전체순매수호가잔량
    ]

    return msg, columns

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간프로그램매매 (통합)
##############################################################################################

def program_trade_total(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내주식 실시간프로그램매매 (통합)[H0UNPGM0]
    국내주식 실시간프로그램매매 (통합) API를 통해 실시간 데이터를 구독합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 값
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)

    Returns:
        message (dict): 실시간 데이터 메시지
        columns (list[str]): 응답 데이터의 컬럼 정보

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = program_trade_total("1", "005930")
        >>> print(msg, columns)

    Note:
        이 함수는 웹소켓을 통해 실시간 데이터를 구독합니다. 
        구독을 시작하려면 tr_type을 "1"로 설정하고, 해제하려면 "0"으로 설정하세요.
    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key는 빈 문자열일 수 없습니다.")

    tr_id = "H0UNPGM0"

    params = {
        "tr_key": tr_key,
    }

    # 웹소켓을 통해 실시간 데이터 구독
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 데이터의 컬럼 정보
    columns = [
        "MKSC_SHRN_ISCD",  # 유가증권 단축 종목코드
        "STCK_CNTG_HOUR",  # 주식 체결 시간
        "SELN_CNQN",       # 매도 체결량
        "SELN_TR_PBMN",    # 매도 거래 대금
        "SHNU_CNQN",       # 매수2 체결량
        "SHNU_TR_PBMN",    # 매수2 거래 대금
        "NTBY_CNQN",       # 순매수 체결량
        "NTBY_TR_PBMN",    # 순매수 거래 대금
        "SELN_RSQN",       # 매도호가잔량
        "SHNU_RSQN",       # 매수호가잔량
        "WHOL_NTBY_QTY",   # 전체순매수호가잔량
    ]

    return msg, columns

