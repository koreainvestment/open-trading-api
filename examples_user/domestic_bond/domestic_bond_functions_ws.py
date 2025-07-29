import logging
import sys

sys.path.extend(['..', '.'])
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
    일반채권 실시간호가[실시간-053]
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
    채권 종목코드 마스터파일은 "KIS포털 > API문서 > 종목정보파일 > 장내채권 - 채권코드" 참고 부탁드립니다.
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

    [참고자료]
    채권 종목코드 마스터파일은 "KIS포털 > API문서 > 종목정보파일 > 장내채권 - 채권코드" 참고 부탁드립니다.
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
    채권 종목코드 마스터파일은 "KIS포털 > API문서 > 종목정보파일 > 장내채권 - 채권코드" 참고 부탁드립니다.
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

