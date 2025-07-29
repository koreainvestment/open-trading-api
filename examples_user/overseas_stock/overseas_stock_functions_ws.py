import logging
import sys

sys.path.extend(['..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 실시간시세 > 해외주식 실시간호가[실시간-021]
##############################################################################################

def asking_price(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    해외주식 실시간호가를 이용하여 미국시세 실시간 1호가(매수/매도) 시세가 무료로 제공됩니다. (미국은 유료시세 제공 X)

    아시아 국가의 경우, HTS(efriend Plus) [7781] 시세신청(실시간) 화면에서 유료 서비스 신청 시, 
    "해외주식 실시간호가 HDFSASP0" 을 이용하여 아시아국가 유료시세(실시간호가)를 받아보실 수 있습니다. (24.11.29 반영)
    (아시아 국가 무료시세는 "해외주식 지연호가(아시아) HDFSASP1" 를 이용하시기 바랍니다.)

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = asking_price("1", "DNASAAPL")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "HDFSASP0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "symb",
        "zdiv",
        "xymd",
        "xhms",
        "kymd",
        "khms",
        "bvol",
        "avol",
        "bdvl",
        "advl",
        "pbid1",
        "pask1",
        "vbid1",
        "vask1",
        "dbid1",
        "dask1"
    ]

    return msg, columns

##############################################################################################
# [해외주식] 실시간시세 > 해외주식 실시간체결통보[실시간-009]
##############################################################################################

def ccnl_notice(
        tr_type: str,
        tr_key: str,
        env_dv: str,
) -> tuple[dict, list[str]]:
    """
    해외주식 실시간체결통보 API입니다.

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 종목코드
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = ccnl_notice("1", trenv.my_htsid, "real")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real', 'demo')")

    # tr_id 구분
    if env_dv == "real":
        tr_id = "H0GSCNI0"
    elif env_dv == "demo":
        tr_id = "H0GSCNI9"
    else:
        raise ValueError("env_dv can only be real or demo")

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "CUST_ID",
        "ACNT_NO",
        "ODER_NO",
        "OODER_NO",
        "SELN_BYOV_CLS",
        "RCTF_CLS",
        "ODER_KIND2",
        "STCK_SHRN_ISCD",
        "CNTG_QTY",
        "CNTG_UNPR",
        "STCK_CNTG_HOUR",
        "RFUS_YN",
        "CNTG_YN",
        "ACPT_YN",
        "BRNC_NO",
        "ODER_QTY",
        "ACNT_NAME",
        "CNTG_ISNM",
        "ODER_COND",
        "DEBT_GB",
        "DEBT_DATE",
        "START_TM",
        "END_TM",
        "TM_DIV_TP"
    ]

    return msg, columns

##############################################################################################
# [해외주식] 실시간시세 > 해외주식 지연호가(아시아)[실시간-008]
##############################################################################################

def delayed_asking_price_asia(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    해외주식 지연호가(아시아)의 경우 아시아 무료시세(지연호가)가 제공됩니다.

    HTS(efriend Plus) [7781] 시세신청(실시간) 화면에서 유료 서비스 신청 시, 
    "해외주식 실시간호가 HDFSASP0" 을 이용하여 아시아국가 유료시세(실시간호가)를 받아보실 수 있습니다. (24.11.29 반영)

    ※ 지연시세 지연시간 : 홍콩, 베트남, 중국, 일본 - 15분지연

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = delayed_asking_price_asia("1", "DHKS00003")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "HDFSASP1"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "symb",
        "zdiv",
        "xymd",
        "xhms",
        "kymd",
        "khms",
        "bvol",
        "avol",
        "bdvl",
        "advl",
        "pbid1",
        "pask1",
        "vbid1",
        "vask1",
        "dbid1",
        "dask1"
    ]

    return msg, columns

##############################################################################################
# [해외주식] 실시간시세 > 해외주식 실시간지연체결가[실시간-007]
##############################################################################################

def delayed_ccnl(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    해외주식 실시간지연체결가의 경우 기본적으로 무료시세(지연체결가)가 제공되며, 
    아시아국가의 경우 HTS(efriend Plus) [7781] 시세신청(실시간) 화면에서 유료 서비스 신청 시 API로도 유료시세(실시간체결가)를 받아보실 수 있습니다. (24.11.29 반영)

    ※ 지연시세 지연시간 : 미국 - 실시간무료(0분지연) / 홍콩, 베트남, 중국, 일본 - 15분지연 (중국은 실시간시세 신청 시 무료실시간시세 제공)
    미국의 경우 0분지연시세로 제공되나, 장중 당일 시가는 상이할 수 있으며, 익일 정정 표시됩니다.

    해당 API로 미국주간거래(10:00~16:00) 시세 조회도 가능합니다. 
    ※ 미국주간거래 실시간 조회 시, 맨 앞자리(R), tr_key 중 시장구분 값을 다음과 같이 입력 → 나스닥: BAQ, 뉴욕: BAY, 아멕스: BAA

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = delayed_ccnl("1", "DNASAAPL")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "HDFSCNT0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "SYMB",
        "ZDIV",
        "TYMD",
        "XYMD",
        "XHMS",
        "KYMD",
        "KHMS",
        "OPEN",
        "HIGH",
        "LOW",
        "LAST",
        "SIGN",
        "DIFF",
        "RATE",
        "PBID",
        "PASK",
        "VBID",
        "VASK",
        "EVOL",
        "TVOL",
        "TAMT",
        "BIVL",
        "ASVL",
        "STRN",
        "MTYP"
    ]

    return msg, columns

