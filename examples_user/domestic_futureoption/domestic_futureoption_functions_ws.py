import logging
import sys

sys.path.extend(['..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내선물옵션] 실시간시세 > 상품선물 실시간체결가[실시간-022]
##############################################################################################

def commodity_futures_realtime_conclusion(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    상품선물 실시간체결가 API입니다.
    실시간 웹소켓 연결을 통해 상품선물의 실시간 체결가 정보를 수신할 수 있습니다.
    현재가, 시고저가, 체결량, 누적거래량, 이론가, 베이시스, 괴리율 등의 상세 정보를 제공합니다.
    매도/매수 호가, 체결 건수, 미결제 약정 수량 등의 선물거래 필수 정보를 포함합니다.

    Args:
        tr_type (str): [필수] 구독 등록/해제 여부 (ex. "1": 구독, "2": 해제)
        tr_key (str): [필수] 종목코드 (ex. 101S12)

    Returns:
        message (str): 메시지 데이터

    Example:
        >>> msg, columns = commodity_futures_realtime_conclusion("1", "101S12")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is empty")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0CFCNT0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "futs_shrn_iscd",
        "bsop_hour",
        "futs_prdy_vrss",
        "prdy_vrss_sign",
        "futs_prdy_ctrt",
        "futs_prpr",
        "futs_oprc",
        "futs_hgpr",
        "futs_lwpr",
        "last_cnqn",
        "acml_vol",
        "acml_tr_pbmn",
        "hts_thpr",
        "mrkt_basis",
        "dprt",
        "nmsc_fctn_stpl_prc",
        "fmsc_fctn_stpl_prc",
        "spead_prc",
        "hts_otst_stpl_qty",
        "otst_stpl_qty_icdc",
        "oprc_hour",
        "oprc_vrss_prpr_sign",
        "oprc_vrss_nmix_prpr",
        "hgpr_hour",
        "hgpr_vrss_prpr_sign",
        "hgpr_vrss_nmix_prpr",
        "lwpr_hour",
        "lwpr_vrss_prpr_sign",
        "lwpr_vrss_nmix_prpr",
        "shnu_rate",
        "cttr",
        "esdg",
        "otst_stpl_rgbf_qty_icdc",
        "thpr_basis",
        "futs_askp1",
        "futs_bidp1",
        "askp_rsqn1",
        "bidp_rsqn1",
        "seln_cntg_csnu",
        "shnu_cntg_csnu",
        "ntby_cntg_csnu",
        "seln_cntg_smtn",
        "shnu_cntg_smtn",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "prdy_vol_vrss_acml_vol_rate",
        "dscs_bltr_acml_qty",
        "dynm_mxpr",
        "dynm_llam",
        "dynm_prc_limt_yn"
    ]

    return msg, columns

##############################################################################################
# [국내선물옵션] 실시간시세 > 상품선물 실시간호가[실시간-023]
##############################################################################################

def commodity_futures_realtime_quote(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    상품선물 실시간호가 API입니다.
    실시간 웹소켓 연결을 통해 상품선물 매도/매수 호가 정보를 실시간으로 수신할 수 있습니다.
    실전계좌만 지원되며, 모의투자는 지원하지 않습니다.
    선물옵션 호가 데이터는 0.2초 필터링 옵션이 적용됩니다.

    Args:
        tr_type (str): [필수] 구독 등록/해제 여부 (ex. "1": 구독, "2": 해제)
        tr_key (str): [필수] 종목코드 (ex. 101S12)

    Returns:
        message (str): 메시지 데이터

    Example:
        >>> msg, columns = commodity_futures_realtime_quote("1", "101S12")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0CFASP0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "futs_shrn_iscd",
        "bsop_hour",
        "futs_askp1",
        "futs_askp2",
        "futs_askp3",
        "futs_askp4",
        "futs_askp5",
        "futs_bidp1",
        "futs_bidp2",
        "futs_bidp3",
        "futs_bidp4",
        "futs_bidp5",
        "askp_csnu1",
        "askp_csnu2",
        "askp_csnu3",
        "askp_csnu4",
        "askp_csnu5",
        "bidp_csnu1",
        "bidp_csnu2",
        "bidp_csnu3",
        "bidp_csnu4",
        "bidp_csnu5",
        "askp_rsqn1",
        "askp_rsqn2",
        "askp_rsqn3",
        "askp_rsqn4",
        "askp_rsqn5",
        "bidp_rsqn1",
        "bidp_rsqn2",
        "bidp_rsqn3",
        "bidp_rsqn4",
        "bidp_rsqn5",
        "total_askp_csnu",
        "total_bidp_csnu",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "total_askp_rsqn_icdc",
        "total_bidp_rsqn_icdc"
    ]

    return msg, columns

##############################################################################################
# [국내선물옵션] 실시간시세 > 선물옵션 실시간체결통보[실시간-012]
##############################################################################################

def fuopt_ccnl_notice(
        tr_type: str,
        tr_key: str,
):
    """
    선물옵션 실시간체결통보 API입니다.
    실시간 웹소켓 연결을 통해 선물옵션 거래의 실시간 체결 통보를 수신할 수 있습니다.
    주문접수, 체결, 정정, 취소 등의 거래 상태 변화를 실시간으로 통보받을 수 있습니다.
    고객ID, 계좌번호, 주문번호, 체결수량, 체결단가 등의 상세 거래 정보를 포함합니다.
    실전계좌와 모의투자 모두 지원됩니다.

    Args:
        tr_type (str): [필수] 구독 등록/해제 여부 (ex. "1": 구독, "2": 해제)
        tr_key (str): [필수] 코드 (ex. dttest11)

    Returns:
        message (str): 메시지 데이터

    Example:
        >>> msg, columns = fuopt_ccnl_notice("1", trenv.my_htsid)
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0IFCNI0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "cust_id",
        "acnt_no", 
        "oder_no",
        "ooder_no",
        "seln_byov_cls",
        "rctf_cls",
        "oder_kind2",
        "stck_shrn_iscd",
        "cntg_qty",
        "cntg_unpr",
        "stck_cntg_hour",
        "rfus_yn",
        "cntg_yn",
        "acpt_yn",
        "brnc_no",
        "oder_qty",
        "acnt_name",
        "cntg_isnm",
        "oder_cond",
        "ord_grp",
        "ord_grpseq",
        "order_prc"
    ]

    return msg, columns

##############################################################################################
# [국내선물옵션] 실시간시세 > 주식선물 실시간예상체결 [실시간-031]
##############################################################################################

def futures_exp_ccnl(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    [국내선물옵션] 실시간시세 > 주식선물 실시간예상체결 [실시간-031]

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = futures_exp_ccnl("1", "111W07")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0ZFANC0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "futs_shrn_iscd",
        "bsop_hour",
        "antc_cnpr",
        "antc_cntg_vrss",
        "antc_cntg_vrss_sign",
        "antc_cntg_prdy_ctrt",
        "antc_mkop_cls_code",
        "antc_cnqn"
    ]

    return msg, columns

##############################################################################################
# [국내선물옵션] 실시간시세 > 지수선물 실시간체결가[실시간-010]
##############################################################################################

def index_futures_realtime_conclusion(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    지수선물 실시간체결가 API입니다.
    실시간 웹소켓 연결을 통해 지수선물의 실시간 체결가 정보를 수신할 수 있습니다.
    현재가, 시고저가, 체결량, 누적거래량, 이론가, 베이시스, 괴리율 등의 상세 정보를 제공합니다.
    매도/매수 호가, 체결 건수, 미결제 약정 수량 등의 선물거래 필수 정보를 포함합니다.
    실전계좌만 지원되며 모의투자는 미지원됩니다.

    Args:
        tr_type (str): [필수] 구독 등록/해제 여부 (ex. "1": 구독, "2": 해제)
        tr_key (str): [필수] 코드 (ex. 101S12)

    Returns:
        message (str): 메시지 데이터

    Example:
        >>> msg, columns = index_futures_realtime_conclusion("1", "101S12")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0IFCNT0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "futs_shrn_iscd",
        "bsop_hour",
        "futs_prdy_vrss",
        "prdy_vrss_sign",
        "futs_prdy_ctrt",
        "futs_prpr",
        "futs_oprc",
        "futs_hgpr",
        "futs_lwpr",
        "last_cnqn",
        "acml_vol",
        "acml_tr_pbmn",
        "hts_thpr",
        "mrkt_basis",
        "dprt",
        "nmsc_fctn_stpl_prc",
        "fmsc_fctn_stpl_prc",
        "spead_prc",
        "hts_otst_stpl_qty",
        "otst_stpl_qty_icdc",
        "oprc_hour",
        "oprc_vrss_prpr_sign",
        "oprc_vrss_nmix_prpr",
        "hgpr_hour",
        "hgpr_vrss_prpr_sign",
        "hgpr_vrss_nmix_prpr",
        "lwpr_hour",
        "lwpr_vrss_prpr_sign",
        "lwpr_vrss_nmix_prpr",
        "shnu_rate",
        "cttr",
        "esdg",
        "otst_stpl_rgbf_qty_icdc",
        "thpr_basis",
        "futs_askp1",
        "futs_bidp1",
        "askp_rsqn1",
        "bidp_rsqn1",
        "seln_cntg_csnu",
        "shnu_cntg_csnu",
        "ntby_cntg_csnu",
        "seln_cntg_smtn",
        "shnu_cntg_smtn",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "prdy_vol_vrss_acml_vol_rate",
        "dscs_bltr_acml_qty",
        "dynm_mxpr",
        "dynm_llam",
        "dynm_prc_limt_yn"
    ]

    return msg, columns

##############################################################################################
# [국내선물옵션] 실시간시세 > 지수선물 실시간호가[실시간-011]
##############################################################################################

def index_futures_realtime_quote(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    지수선물 실시간호가 API입니다.
    실시간 웹소켓 연결을 통해 지수선물의 실시간 호가 정보를 수신할 수 있습니다.
    매도/매수 호가 1~5단계, 호가 건수, 호가 잔량 등의 상세 정보를 제공합니다.
    선물옵션 호가 데이터는 0.2초 필터링 옵션이 적용됩니다.
    실전계좌만 지원되며 모의투자는 미지원됩니다.

    Args:
        tr_type (str): [필수] 구독 등록/해제 여부 (ex. "1": 구독, "2": 해제)
        tr_key (str): [필수] 코드 (ex. 101S12)

    Returns:
        message (str): 메시지 데이터

    Example:
        >>> msg, columns = index_futures_realtime_quote("1", "101S12")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0IFASP0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "futs_shrn_iscd",
        "bsop_hour",
        "futs_askp1",
        "futs_askp2",
        "futs_askp3",
        "futs_askp4",
        "futs_askp5",
        "futs_bidp1",
        "futs_bidp2",
        "futs_bidp3",
        "futs_bidp4",
        "futs_bidp5",
        "askp_csnu1",
        "askp_csnu2",
        "askp_csnu3",
        "askp_csnu4",
        "askp_csnu5",
        "bidp_csnu1",
        "bidp_csnu2",
        "bidp_csnu3",
        "bidp_csnu4",
        "bidp_csnu5",
        "askp_rsqn1",
        "askp_rsqn2",
        "askp_rsqn3",
        "askp_rsqn4",
        "askp_rsqn5",
        "bidp_rsqn1",
        "bidp_rsqn2",
        "bidp_rsqn3",
        "bidp_rsqn4",
        "bidp_rsqn5",
        "total_askp_csnu",
        "total_bidp_csnu",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "total_askp_rsqn_icdc",
        "total_bidp_rsqn_icdc"
    ]

    return msg, columns

##############################################################################################
# [국내선물옵션] 실시간시세 > 지수옵션 실시간체결가[실시간-014]
##############################################################################################

def index_option_realtime_conclusion(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    지수옵션 실시간체결가 API입니다.
    실시간 웹소켓 연결을 통해 지수옵션의 실시간 체결가 정보를 수신할 수 있습니다.
    옵션 현재가, 시고저가, 체결량, 누적거래량, 이론가 등의 기본 정보와 함께
    델타, 감마, 베가, 세타, 로우 등의 그리스 지표와 내재가치, 시간가치, 변동성 정보를 제공합니다.
    옵션 거래에 필수적인 전문 지표들을 포함하는 확장된 체결가 정보입니다.
    실전계좌만 지원되며 모의투자는 미지원됩니다.

    Args:
        tr_type (str): [필수] 구독 등록/해제 여부 (ex. "1": 구독, "2": 해제)
        tr_key (str): [필수] 코드 (ex. 201S11305)

    Returns:
        message (str): 메시지 데이터

    Example:
        >>> msg, columns = index_option_realtime_conclusion("1", "101W09")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0IOCNT0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "optn_shrn_iscd",
        "bsop_hour",
        "optn_prpr",
        "prdy_vrss_sign",
        "optn_prdy_vrss",
        "prdy_ctrt",
        "optn_oprc",
        "optn_hgpr",
        "optn_lwpr",
        "last_cnqn",
        "acml_vol",
        "acml_tr_pbmn",
        "hts_thpr",
        "hts_otst_stpl_qty",
        "otst_stpl_qty_icdc",
        "oprc_hour",
        "oprc_vrss_prpr_sign",
        "oprc_vrss_nmix_prpr",
        "hgpr_hour",
        "hgpr_vrss_prpr_sign",
        "hgpr_vrss_nmix_prpr",
        "lwpr_hour",
        "lwpr_vrss_prpr_sign",
        "lwpr_vrss_nmix_prpr",
        "shnu_rate",
        "prmm_val",
        "invl_val",
        "tmvl_val",
        "delta",
        "gama",
        "vega",
        "theta",
        "rho",
        "hts_ints_vltl",
        "esdg",
        "otst_stpl_rgbf_qty_icdc",
        "thpr_basis",
        "unas_hist_vltl",
        "cttr",
        "dprt",
        "mrkt_basis",
        "optn_askp1",
        "optn_bidp1",
        "askp_rsqn1",
        "bidp_rsqn1",
        "seln_cntg_csnu",
        "shnu_cntg_csnu",
        "ntby_cntg_csnu",
        "seln_cntg_smtn",
        "shnu_cntg_smtn",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "prdy_vol_vrss_acml_vol_rate",
        "avrg_vltl",
        "dscs_lrqn_vol",
        "dynm_mxpr",
        "dynm_llam",
        "dynm_prc_limt_yn"
    ]

    return msg, columns

##############################################################################################
# [국내선물옵션] 실시간시세 > 지수옵션 실시간호가[실시간-015]
##############################################################################################

def index_option_realtime_quote(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    지수옵션 실시간호가 API입니다.
    실시간 웹소켓 연결을 통해 지수옵션 매도/매수 호가 정보를 실시간으로 수신할 수 있습니다.
    실전계좌만 지원되며, 모의투자는 지원하지 않습니다.

    Args:
        tr_type (str): [필수] 구독 등록/해제 여부 (ex. "1": 구독, "2": 해제)
        tr_key (str): [필수] 코드 (ex. 201S11305)

    Returns:
        message (str): 메시지 데이터

    Example:
        >>> msg, columns = index_option_realtime_quote("1", "201S11305")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0IOASP0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "optn_shrn_iscd",
        "bsop_hour",
        "optn_askp1",
        "optn_askp2",
        "optn_askp3",
        "optn_askp4",
        "optn_askp5",
        "optn_bidp1",
        "optn_bidp2",
        "optn_bidp3",
        "optn_bidp4",
        "optn_bidp5",
        "askp_csnu1",
        "askp_csnu2",
        "askp_csnu3",
        "askp_csnu4",
        "askp_csnu5",
        "bidp_csnu1",
        "bidp_csnu2",
        "bidp_csnu3",
        "bidp_csnu4",
        "bidp_csnu5",
        "askp_rsqn1",
        "askp_rsqn2",
        "askp_rsqn3",
        "askp_rsqn4",
        "askp_rsqn5",
        "bidp_rsqn1",
        "bidp_rsqn2",
        "bidp_rsqn3",
        "bidp_rsqn4",
        "bidp_rsqn5",
        "total_askp_csnu",
        "total_bidp_csnu",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "total_askp_rsqn_icdc",
        "total_bidp_rsqn_icdc"
    ]

    return msg, columns

##############################################################################################
# [국내선물옵션] 실시간시세 > KRX야간선물 실시간호가 [실시간-065]
##############################################################################################

def krx_ngt_futures_asking_price(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    ※ 선물옵션 호가 데이터는 0.2초 필터링 옵션이 있습니다.
    필터링 사유는 순간적으로 데이터가 폭증할 경우 서버 뿐만아니라 클라이언트 환경에도 부하를 줄 수 있어 적용된 사항인 점 양해 부탁드립니다.

    [참고자료]
    종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = krx_ngt_futures_asking_price("1", "101W9000")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0MFASP0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "futs_shrn_iscd",
        "bsop_hour",
        "futs_askp1",
        "futs_askp2",
        "futs_askp3",
        "futs_askp4",
        "futs_askp5",
        "futs_bidp1",
        "futs_bidp2",
        "futs_bidp3",
        "futs_bidp4",
        "futs_bidp5",
        "askp_csnu1",
        "askp_csnu2",
        "askp_csnu3",
        "askp_csnu4",
        "askp_csnu5",
        "bidp_csnu1",
        "bidp_csnu2",
        "bidp_csnu3",
        "bidp_csnu4",
        "bidp_csnu5",
        "askp_rsqn1",
        "askp_rsqn2",
        "askp_rsqn3",
        "askp_rsqn4",
        "askp_rsqn5",
        "bidp_rsqn1",
        "bidp_rsqn2",
        "bidp_rsqn3",
        "bidp_rsqn4",
        "bidp_rsqn5",
        "total_askp_csnu",
        "total_bidp_csnu",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "total_askp_rsqn_icdc",
        "total_bidp_rsqn_icdc"
    ]

    return msg, columns

##############################################################################################
# [국내선물옵션] 실시간시세 > KRX야간선물 실시간종목체결 [실시간-064]
##############################################################################################

def krx_ngt_futures_ccnl(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    [참고자료]
    종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = krx_ngt_futures_ccnl("1", "101W9000")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0MFCNT0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "futs_shrn_iscd",
        "bsop_hour",
        "futs_prdy_vrss",
        "prdy_vrss_sign",
        "futs_prdy_ctrt",
        "futs_prpr",
        "futs_oprc",
        "futs_hgpr",
        "futs_lwpr",
        "last_cnqn",
        "acml_vol",
        "acml_tr_pbmn",
        "hts_thpr",
        "mrkt_basis",
        "dprt",
        "nmsc_fctn_stpl_prc",
        "fmsc_fctn_stpl_prc",
        "spead_prc",
        "hts_otst_stpl_qty",
        "otst_stpl_qty_icdc",
        "oprc_hour",
        "oprc_vrss_prpr_sign",
        "oprc_vrss_nmix_prpr",
        "hgpr_hour",
        "hgpr_vrss_prpr_sign",
        "hgpr_vrss_nmix_prpr",
        "lwpr_hour",
        "lwpr_vrss_prpr_sign",
        "lwpr_vrss_nmix_prpr",
        "shnu_rate",
        "cttr",
        "esdg",
        "otst_stpl_rgbf_qty_icdc",
        "thpr_basis",
        "futs_askp1",
        "futs_bidp1",
        "askp_rsqn1",
        "bidp_rsqn1",
        "seln_cntg_csnu",
        "shnu_cntg_csnu",
        "ntby_cntg_csnu",
        "seln_cntg_smtn",
        "shnu_cntg_smtn",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "prdy_vol_vrss_acml_vol_rate",
        "dynm_mxpr",
        "dynm_llam",
        "dynm_prc_limt_yn"
    ]

    return msg, columns

##############################################################################################
# [국내선물옵션] 실시간시세 > KRX야간선물 실시간체결통보 [실시간-066]
##############################################################################################

def krx_ngt_futures_ccnl_notice(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    [참고자료]
    종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = krx_ngt_futures_ccnl_notice("1", trenv.my_htsid)
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0MFCNI0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "cust_id",
        "acnt_no",
        "oder_no",
        "ooder_no",
        "seln_byov_cls",
        "rctf_cls",
        "oder_kind2",
        "stck_shrn_iscd",
        "cntg_qty",
        "cntg_unpr",
        "stck_cntg_hour",
        "rfus_yn",
        "cntg_yn",
        "acpt_yn",
        "brnc_no",
        "oder_qty",
        "acnt_name",
        "cntg_isnm",
        "oder_cond"
    ]

    return msg, columns

##############################################################################################
# [국내선물옵션] 실시간시세 > KRX야간옵션 실시간호가 [실시간-033]
##############################################################################################

def krx_ngt_option_asking_price(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    [참고자료]
    종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = krx_ngt_option_asking_price("1", "101W09")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0EUASP0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "optn_shrn_iscd",
        "bsop_hour",
        "optn_askp1",
        "optn_askp2",
        "optn_askp3",
        "optn_askp4",
        "optn_askp5",
        "optn_bidp1",
        "optn_bidp2",
        "optn_bidp3",
        "optn_bidp4",
        "optn_bidp5",
        "askp_csnu1",
        "askp_csnu2",
        "askp_csnu3",
        "askp_csnu4",
        "askp_csnu5",
        "bidp_csnu1",
        "bidp_csnu2",
        "bidp_csnu3",
        "bidp_csnu4",
        "bidp_csnu5",
        "askp_rsqn1",
        "askp_rsqn2",
        "askp_rsqn3",
        "askp_rsqn4",
        "askp_rsqn5",
        "bidp_rsqn1",
        "bidp_rsqn2",
        "bidp_rsqn3",
        "bidp_rsqn4",
        "bidp_rsqn5",
        "total_askp_csnu",
        "total_bidp_csnu",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "total_askp_rsqn_icdc",
        "total_bidp_rsqn_icdc"
    ]

    return msg, columns

##############################################################################################
# [국내선물옵션] 실시간시세 > KRX야간옵션 실시간체결가 [실시간-032]
##############################################################################################

def krx_ngt_option_ccnl(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    [참고자료]
    종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 선물단축종목코드

    Returns:
        message (str): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = krx_ngt_option_ccnl("1", "101W9000")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0EUCNT0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "optn_shrn_iscd",
        "bsop_hour",
        "optn_prpr",
        "prdy_vrss_sign",
        "optn_prdy_vrss",
        "prdy_ctrt",
        "optn_oprc",
        "optn_hgpr",
        "optn_lwpr",
        "last_cnqn",
        "acml_vol",
        "acml_tr_pbmn",
        "hts_thpr",
        "hts_otst_stpl_qty",
        "otst_stpl_qty_icdc",
        "oprc_hour",
        "oprc_vrss_prpr_sign",
        "oprc_vrss_nmix_prpr",
        "hgpr_hour",
        "hgpr_vrss_prpr_sign",
        "hgpr_vrss_nmix_prpr",
        "lwpr_hour",
        "lwpr_vrss_prpr_sign",
        "lwpr_vrss_nmix_prpr",
        "shnu_rate",
        "prmm_val",
        "invl_val",
        "tmvl_val",
        "delta",
        "gama",
        "vega",
        "theta",
        "rho",
        "hts_ints_vltl",
        "esdg",
        "otst_stpl_rgbf_qty_icdc",
        "thpr_basis",
        "unas_hist_vltl",
        "cttr",
        "dprt",
        "mrkt_basis",
        "optn_askp1",
        "optn_bidp1",
        "askp_rsqn1",
        "bidp_rsqn1",
        "seln_cntg_csnu",
        "shnu_cntg_csnu",
        "ntby_cntg_csnu",
        "seln_cntg_smtn",
        "shnu_cntg_smtn",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "prdy_vol_vrss_acml_vol_rate",
        "dynm_mxpr",
        "dynm_prc_limt_yn",
        "dynm_llam"
    ]

    return msg, columns

##############################################################################################
# [국내선물옵션] 실시간시세 > KRX야간옵션실시간예상체결 [실시간-034]
##############################################################################################

def krx_ngt_option_exp_ccnl(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    [국내선물옵션] 실시간시세 
    KRX야간옵션실시간예상체결 [실시간-034]
    
    [참고자료]
    종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 선물단축종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = krx_ngt_option_exp_ccnl("1", "101W9000")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0EUANC0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "optn_shrn_iscd",
        "bsop_hour",
        "antc_cnpr",
        "antc_cntg_vrss",
        "antc_cntg_vrss_sign",
        "antc_cntg_prdy_ctrt",
        "antc_mkop_cls_code",
        "antc_cnqn"
    ]

    return msg, columns

##############################################################################################
# [국내선물옵션] 실시간시세 > KRX야간옵션실시간체결통보 [실시간-067]
##############################################################################################

def krx_ngt_option_notice(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    [참고자료]
    종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 고객 ID

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = krx_ngt_option_notice("1", trenv.my_htsid)
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0EUCNI0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "cust_id",
        "acnt_no",
        "oder_no",
        "ooder_no",
        "seln_byov_cls",
        "rctf_cls",
        "oder_kind2",
        "stck_shrn_iscd",
        "cntg_qty",
        "cntg_unpr",
        "stck_cntg_hour",
        "rfus_yn",
        "cntg_yn",
        "acpt_yn",
        "brnc_no",
        "oder_qty",
        "acnt_name",
        "cntg_isnm",
        "oder_cond"
    ]

    return msg, columns

##############################################################################################
# [국내선물옵션] 실시간시세 > 주식옵션 실시간예상체결 [실시간-046]
##############################################################################################

def option_exp_ccnl(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    [국내선물옵션] 실시간시세 
    주식옵션 실시간예상체결 [실시간-046]

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = option_exp_ccnl("1", "101W9000")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0ZOANC0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "optn_shrn_iscd",
        "bsop_hour",
        "antc_cnpr",
        "antc_cntg_vrss",
        "antc_cntg_vrss_sign",
        "antc_cntg_prdy_ctrt",
        "antc_mkop_cls_code"
    ]

    return msg, columns

##############################################################################################
# [국내선물옵션] 실시간시세 > 주식선물 실시간체결가 [실시간-029]
##############################################################################################

def stock_futures_realtime_conclusion(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    주식선물 실시간체결가 API입니다.
    실시간 웹소켓 연결을 통해 주식선물의 실시간 체결가 정보를 수신할 수 있습니다.
    주식 현재가, 시고저가, 체결량, 누적거래량, 이론가, 베이시스, 괴리율 등의 상세 정보를 제공합니다.
    매도/매수 호가, 체결 건수, 미결제 약정 수량 등의 선물거래 필수 정보를 포함합니다.
    실전계좌만 지원되며 모의투자는 미지원됩니다.

    Args:
        tr_type (str): [필수] 구독 등록/해제 여부 (ex. "1": 구독, "2": 해제)
        tr_key (str): [필수] 종목코드 (ex. 101S12)

    Returns:
        message (str): 메시지 데이터

    Example:
        >>> msg, columns = stock_futures_realtime_conclusion("1", "101S12")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0ZFCNT0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "futs_shrn_iscd",
        "bsop_hour",
        "stck_prpr",
        "prdy_vrss_sign",
        "prdy_vrss",
        "futs_prdy_ctrt",
        "stck_oprc",
        "stck_hgpr",
        "stck_lwpr",
        "last_cnqn",
        "acml_vol",
        "acml_tr_pbmn",
        "hts_thpr",
        "mrkt_basis",
        "dprt",
        "nmsc_fctn_stpl_prc",
        "fmsc_fctn_stpl_prc",
        "spead_prc",
        "hts_otst_stpl_qty",
        "otst_stpl_qty_icdc",
        "oprc_hour",
        "oprc_vrss_prpr_sign",
        "oprc_vrss_prpr",
        "hgpr_hour",
        "hgpr_vrss_prpr_sign",
        "hgpr_vrss_prpr",
        "lwpr_hour",
        "lwpr_vrss_prpr_sign",
        "lwpr_vrss_prpr",
        "shnu_rate",
        "cttr",
        "esdg",
        "otst_stpl_rgbf_qty_icdc",
        "thpr_basis",
        "askp1",
        "bidp1",
        "askp_rsqn1",
        "bidp_rsqn1",
        "seln_cntg_csnu",
        "shnu_cntg_csnu",
        "ntby_cntg_csnu",
        "seln_cntg_smtn",
        "shnu_cntg_smtn",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "prdy_vol_vrss_acml_vol_rate",
        "dynm_mxpr",
        "dynm_llam",
        "dynm_prc_limt_yn"
    ]

    return msg, columns

##############################################################################################
# [국내선물옵션] 실시간시세 > 주식선물 실시간호가 [실시간-030]
##############################################################################################

def stock_futures_realtime_quote(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    주식선물 실시간호가 API입니다.
    실시간 웹소켓 연결을 통해 주식선물의 실시간 호가 정보를 수신할 수 있습니다.
    매도/매수 호가 1~10단계까지의 확장된 호가 정보를 제공하는 특별한 API입니다.
    호가별 건수, 호가별 잔량 등의 상세 정보를 포함합니다.
    선물옵션 호가 데이터는 0.2초 필터링 옵션이 적용됩니다.
    실전계좌만 지원되며 모의투자는 미지원됩니다.

    Args:
        tr_type (str): [필수] 구독 등록/해제 여부 (ex. "1": 구독, "2": 해제)
        tr_key (str): [필수] 종목코드 (ex. 101S12)

    Returns:
        message (str): 메시지 데이터

    Example:
        >>> msg, columns = stock_futures_realtime_quote("1", "101S12")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0ZFASP0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "futs_shrn_iscd",
        "bsop_hour",
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
        "askp_csnu1",
        "askp_csnu2",
        "askp_csnu3",
        "askp_csnu4",
        "askp_csnu5",
        "askp_csnu6",
        "askp_csnu7",
        "askp_csnu8",
        "askp_csnu9",
        "askp_csnu10",
        "bidp_csnu1",
        "bidp_csnu2",
        "bidp_csnu3",
        "bidp_csnu4",
        "bidp_csnu5",
        "bidp_csnu6",
        "bidp_csnu7",
        "bidp_csnu8",
        "bidp_csnu9",
        "bidp_csnu10",
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
        "total_askp_csnu",
        "total_bidp_csnu",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "total_askp_rsqn_icdc",
        "total_bidp_rsqn_icdc"
    ]

    return msg, columns

##############################################################################################
# [국내선물옵션] 실시간시세 > 주식옵션 실시간호가 [실시간-045]
##############################################################################################

def stock_option_asking_price(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    국내선물옵션 주식옵션 실시간호가 API입니다.

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 선물단축종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = stock_option_asking_price("1", "111W80")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0ZOASP0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "optn_shrn_iscd",
        "bsop_hour",
        "optn_askp1",
        "optn_askp2",
        "optn_askp3",
        "optn_askp4",
        "optn_askp5",
        "optn_bidp1",
        "optn_bidp2",
        "optn_bidp3",
        "optn_bidp4",
        "optn_bidp5",
        "askp_csnu1",
        "askp_csnu2",
        "askp_csnu3",
        "askp_csnu4",
        "askp_csnu5",
        "bidp_csnu1",
        "bidp_csnu2",
        "bidp_csnu3",
        "bidp_csnu4",
        "bidp_csnu5",
        "askp_rsqn1",
        "askp_rsqn2",
        "askp_rsqn3",
        "askp_rsqn4",
        "askp_rsqn5",
        "bidp_rsqn1",
        "bidp_rsqn2",
        "bidp_rsqn3",
        "bidp_rsqn4",
        "bidp_rsqn5",
        "total_askp_csnu",
        "total_bidp_csnu",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "total_askp_rsqn_icdc",
        "total_bidp_rsqn_icdc",
        "optn_askp6",
        "optn_askp7",
        "optn_askp8",
        "optn_askp9",
        "optn_askp10",
        "optn_bidp6",
        "optn_bidp7",
        "optn_bidp8",
        "optn_bidp9",
        "optn_bidp10",
        "askp_csnu6",
        "askp_csnu7",
        "askp_csnu8",
        "askp_csnu9",
        "askp_csnu10",
        "bidp_csnu6",
        "bidp_csnu7",
        "bidp_csnu8",
        "bidp_csnu9",
        "bidp_csnu10",
        "askp_rsqn6",
        "askp_rsqn7",
        "askp_rsqn8",
        "askp_rsqn9",
        "askp_rsqn10",
        "bidp_rsqn6",
        "bidp_rsqn7",
        "bidp_rsqn8",
        "bidp_rsqn9",
        "bidp_rsqn10"
    ]

    return msg, columns

##############################################################################################
# [국내선물옵션] 실시간시세 > 주식옵션 실시간체결가 [실시간-044]
##############################################################################################

def stock_option_ccnl(
        tr_type: str,
        tr_key: str,
) -> (dict, list[str]):
    """
    주식옵션 실시간체결가 API입니다.

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = stock_option_ccnl("1", "101W9000")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "H0ZOCNT0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "optn_shrn_iscd",
        "bsop_hour",
        "optn_prpr",
        "prdy_vrss_sign",
        "optn_prdy_vrss",
        "prdy_ctrt",
        "optn_oprc",
        "optn_hgpr",
        "optn_lwpr",
        "last_cnqn",
        "acml_vol",
        "acml_tr_pbmn",
        "hts_thpr",
        "hts_otst_stpl_qty",
        "otst_stpl_qty_icdc",
        "oprc_hour",
        "oprc_vrss_prpr_sign",
        "oprc_vrss_nmix_prpr",
        "hgpr_hour",
        "hgpr_vrss_prpr_sign",
        "hgpr_vrss_nmix_prpr",
        "lwpr_hour",
        "lwpr_vrss_prpr_sign",
        "lwpr_vrss_nmix_prpr",
        "shnu_rate",
        "prmm_val",
        "invl_val",
        "tmvl_val",
        "delta",
        "gama",
        "vega",
        "theta",
        "rho",
        "hts_ints_vltl",
        "esdg",
        "otst_stpl_rgbf_qty_icdc",
        "thpr_basis",
        "unas_hist_vltl",
        "cttr",
        "dprt",
        "mrkt_basis",
        "optn_askp1",
        "optn_bidp1",
        "askp_rsqn1",
        "bidp_rsqn1",
        "seln_cntg_csnu",
        "shnu_cntg_csnu",
        "ntby_cntg_csnu",
        "seln_cntg_smtn",
        "shnu_cntg_smtn",
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "prdy_vol_vrss_acml_vol_rate"
    ]

    return msg, columns

