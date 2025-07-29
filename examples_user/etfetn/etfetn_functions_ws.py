import logging
import sys

sys.path.extend(['..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 > 국내ETF NAV추이[실시간-051]
##############################################################################################

def etf_nav_trend(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    국내ETF NAV추이[H0STNAV0] 실시간 데이터 구독 함수

    이 함수는 한국투자증권의 웹소켓 API를 통해 실시간으로 국내 ETF의 NAV 추이를 구독합니다.
    구독을 시작하거나 해제할 수 있으며, 실시간 데이터를 수신합니다.

    Args:
        tr_type (str): [필수] 구독 등록("1") 또는 해제("0") 여부를 나타내는 문자열
        tr_key (str): [필수] 종목코드 (빈 문자열 불가)

    Returns:
        message (dict): 수신된 메시지 데이터
        columns (list[str]): 수신된 데이터의 컬럼 정보

    Raises:
        ValueError: tr_key가 빈 문자열인 경우 발생

    Example:
        >>> msg, columns = etf_nav_trend("1", "005930")
        >>> print(msg, columns)

    """

    # 필수 파라미터 검증
    if not tr_key:
        raise ValueError("tr_key is required and cannot be an empty string")

    tr_id = "H0STNAV0"

    params = {
        "tr_key": tr_key,
    }

    # 데이터 수신
    msg = ka.data_fetch(tr_id, tr_type, params)

    # 응답 컬럼 정보
    columns = [
        "rt_cd",               # 성공 실패 여부
        "msg_cd",              # 응답코드
        "output1",             # 응답상세
        "msg1",                # 응답메세지
        "mksc_shrn_iscd",      # 유가증권단축종목코드
        "nav",                 # NAV
        "nav_prdy_vrss_sign",  # NAV전일대비부호
        "nav_prdy_vrss",       # NAV전일대비
        "nav_prdy_ctrt",       # NAV전일대비율
        "oprc_nav",            # NAV시가
        "hprc_nav",            # NAV고가
        "lprc_nav",            # NAV저가
    ]

    return msg, columns

