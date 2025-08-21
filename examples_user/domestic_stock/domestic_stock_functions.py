import logging
import time
import sys
from typing import Optional, Tuple

import pandas as pd

sys.path.extend(['..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


##############################################################################################
# [국내주식] 기본시세 > 국내주식 시간외잔량 순위[v1_국내주식-093]
##############################################################################################

def after_hour_balance(
        fid_input_price_1: str,  # 입력 가격1
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_rank_sort_cls_code: str,  # 순위 정렬 구분 코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_trgt_exls_cls_code: str,  # 대상 제외 구분 코드
        fid_trgt_cls_code: str,  # 대상 구분 코드
        fid_vol_cnt: str,  # 거래량 수
        fid_input_price_2: str,  # 입력 가격2
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 시간외잔량 순위[v1_국내주식-093]
    국내주식 시간외잔량 순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_input_price_1 (str): 입력값 없을때 전체 (가격 ~)
        fid_cond_mrkt_div_code (str): 시장구분코드 (주식 J)
        fid_cond_scr_div_code (str): Unique key( 20176 )
        fid_rank_sort_cls_code (str): 1: 장전 시간외, 2: 장후 시간외, 3:매도잔량, 4:매수잔량
        fid_div_cls_code (str): 0 : 전체
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200
        fid_trgt_exls_cls_code (str): 0 : 전체
        fid_trgt_cls_code (str): 0 : 전체
        fid_vol_cnt (str): 입력값 없을때 전체 (거래량 ~)
        fid_input_price_2 (str): 입력값 없을때 전체 (~ 가격)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 시간외잔량 순위 데이터
        
    Example:
        >>> df = after_hour_balance(
        ...     fid_input_price_1="",
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_cond_scr_div_code="20176",
        ...     fid_rank_sort_cls_code="1",
        ...     fid_div_cls_code="0",
        ...     fid_input_iscd="0000",
        ...     fid_trgt_exls_cls_code="0",
        ...     fid_trgt_cls_code="0",
        ...     fid_vol_cnt="",
        ...     fid_input_price_2=""
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/after-hour-balance"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20176')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20176')")

    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '1')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '1')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0000')")
        raise ValueError("fid_input_iscd is required. (e.g. '0000')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # API 호출 URL 및 거래 ID 설정

    tr_id = "FHPST01760000"

    # API 요청 파라미터 설정
    params = {
        "fid_input_price_1": fid_input_price_1,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_rank_sort_cls_code": fid_rank_sort_cls_code,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_input_iscd": fid_input_iscd,
        "fid_trgt_exls_cls_code": fid_trgt_exls_cls_code,
        "fid_trgt_cls_code": fid_trgt_cls_code,
        "fid_vol_cnt": fid_vol_cnt,
        "fid_input_price_2": fid_input_price_2,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    # API 호출 성공 시 데이터 처리
    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        # 기존 데이터프레임과 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        # 다음 페이지 호출
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return after_hour_balance(
                fid_input_price_1,
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_rank_sort_cls_code,
                fid_div_cls_code,
                fid_input_iscd,
                fid_trgt_exls_cls_code,
                fid_trgt_cls_code,
                fid_vol_cnt,
                fid_input_price_2,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 호출 실패 시 에러 로그 출력
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 순위분석 > 국내주식 대량체결건수 상위[국내주식-107]
##############################################################################################

def bulk_trans_num(
        fid_aply_rang_prc_2: str,  # 적용 범위 가격2
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_rank_sort_cls_code: str,  # 순위 정렬 구분 코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_input_price_1: str,  # 입력 가격1
        fid_aply_rang_prc_1: str,  # 적용 범위 가격1
        fid_input_iscd_2: str,  # 입력 종목코드2
        fid_trgt_exls_cls_code: str,  # 대상 제외 구분 코드
        fid_trgt_cls_code: str,  # 대상 구분 코드
        fid_vol_cnt: str,  # 거래량 수
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 대량체결건수 상위[국내주식-107]
    국내주식 대량체결건수 상위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_aply_rang_prc_2 (str): ~ 가격
        fid_cond_mrkt_div_code (str): 시장구분코드 (J:KRX, NX:NXT)
        fid_cond_scr_div_code (str): Unique key(11909)
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100
        fid_rank_sort_cls_code (str): 0:매수상위, 1:매도상위
        fid_div_cls_code (str): 0:전체
        fid_input_price_1 (str): 건별금액 ~
        fid_aply_rang_prc_1 (str): 가격 ~
        fid_input_iscd_2 (str): 공백:전체종목, 개별종목 조회시 종목코드 (000660)
        fid_trgt_exls_cls_code (str): 0:전체
        fid_trgt_cls_code (str): 0:전체
        fid_vol_cnt (str): 거래량 ~
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 대량체결건수 상위 데이터
        
    Example:
        >>> df = bulk_trans_num(
                fid_aply_rang_prc_2="100000",
                fid_cond_mrkt_div_code="J",
                fid_cond_scr_div_code="11909",
                fid_input_iscd="0000",
                fid_rank_sort_cls_code="0",
                fid_div_cls_code="0",
                fid_input_price_1="50000",
                fid_aply_rang_prc_1="200000",
                fid_input_iscd_2="",
                fid_trgt_exls_cls_code="0",
                fid_trgt_cls_code="0",
                fid_vol_cnt="1000"
            )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/bulk-trans-num"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '11909')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '11909')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0000')")
        raise ValueError("fid_input_iscd is required. (e.g. '0000')")

    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '0')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '0')")

    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")

    if not fid_trgt_exls_cls_code:
        logger.error("fid_trgt_exls_cls_code is required. (e.g. '0')")
        raise ValueError("fid_trgt_exls_cls_code is required. (e.g. '0')")

    if not fid_trgt_cls_code:
        logger.error("fid_trgt_cls_code is required. (e.g. '0')")
        raise ValueError("fid_trgt_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHKST190900C0"

    params = {
        "fid_aply_rang_prc_2": fid_aply_rang_prc_2,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_input_iscd": fid_input_iscd,
        "fid_rank_sort_cls_code": fid_rank_sort_cls_code,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_input_price_1": fid_input_price_1,
        "fid_aply_rang_prc_1": fid_aply_rang_prc_1,
        "fid_input_iscd_2": fid_input_iscd_2,
        "fid_trgt_exls_cls_code": fid_trgt_exls_cls_code,
        "fid_trgt_cls_code": fid_trgt_cls_code,
        "fid_vol_cnt": fid_vol_cnt,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 다음 페이지 여부 확인
        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return bulk_trans_num(
                fid_aply_rang_prc_2,
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_rank_sort_cls_code,
                fid_div_cls_code,
                fid_input_price_1,
                fid_aply_rang_prc_1,
                fid_input_iscd_2,
                fid_trgt_exls_cls_code,
                fid_trgt_cls_code,
                fid_vol_cnt,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 호출 실패 시 에러 로그
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 국내주식 상하한가 포착 [국내주식-190]
##############################################################################################

def capture_uplowprice(
        fid_cond_mrkt_div_code: str,  # [필수] 조건시장분류코드 (ex. J:주식)
        fid_cond_scr_div_code: str,  # [필수] 조건화면분류코드 (ex. 11300)
        fid_prc_cls_code: str,  # [필수] 상하한가 구분코드 (ex. 0:상한가, 1:하한가)
        fid_div_cls_code: str,
        # [필수] 분류구분코드 (ex. 0:상하한가종목, 6:8%상하한가 근접, 5:10%상하한가 근접, 1:15%상하한가 근접, 2:20%상하한가 근접, 3:25%상하한가 근접)
        fid_input_iscd: str,  # [필수] 입력종목코드 (ex. 0000:전체, 0001:코스피, 1001:코스닥)
        fid_trgt_cls_code: str = "",  # 대상구분코드
        fid_trgt_exls_cls_code: str = "",  # 대상제외구분코드
        fid_input_price_1: str = "",  # 입력가격1
        fid_input_price_2: str = "",  # 입력가격2
        fid_vol_cnt: str = ""  # 거래량수
) -> pd.DataFrame:
    """
    국내주식 상하한가 포착 API입니다.
    한국투자 HTS(eFriend Plus) > [0917] 실시간 상하한가 포착 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건시장분류코드 (ex. J:주식)
        fid_cond_scr_div_code (str): [필수] 조건화면분류코드 (ex. 11300)
        fid_prc_cls_code (str): [필수] 상하한가 구분코드 (ex. 0:상한가, 1:하한가)
        fid_div_cls_code (str): [필수] 분류구분코드 (ex. 0:상하한가종목, 6:8%상하한가 근접, 5:10%상하한가 근접, 1:15%상하한가 근접, 2:20%상하한가 근접, 3:25%상하한가 근접)
        fid_input_iscd (str): [필수] 입력종목코드 (ex. 0000:전체, 0001:코스피, 1001:코스닥)
        fid_trgt_cls_code (str): 대상구분코드
        fid_trgt_exls_cls_code (str): 대상제외구분코드
        fid_input_price_1 (str): 입력가격1
        fid_input_price_2 (str): 입력가격2
        fid_vol_cnt (str): 거래량수

    Returns:
        pd.DataFrame: 상하한가 포착 데이터
        
    Example:
        >>> df = capture_uplowprice("J", "11300", "0", "0", "0000")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/capture-uplowprice"

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")

    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '11300')")

    if fid_prc_cls_code == "":
        raise ValueError("fid_prc_cls_code is required (e.g. '0', '1')")

    if fid_div_cls_code == "":
        raise ValueError("fid_div_cls_code is required (e.g. '0', '6', '5', '1', '2', '3')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '0000', '0001', '1001')")

    tr_id = "FHKST130000C0"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_PRC_CLS_CODE": fid_prc_cls_code,
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_TRGT_CLS_CODE": fid_trgt_cls_code,
        "FID_TRGT_EXLS_CLS_CODE": fid_trgt_exls_cls_code,
        "FID_INPUT_PRICE_1": fid_input_price_1,
        "FID_INPUT_PRICE_2": fid_input_price_2,
        "FID_VOL_CNT": fid_vol_cnt
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        return pd.DataFrame(res.getBody().output)
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 업종/기타 > 국내휴장일조회[국내주식-040]
##############################################################################################

def chk_holiday(
        bass_dt: str,  # 기준일자 (YYYYMMDD)
        NK100: str = "",  # 연속조회키
        FK100: str = "",  # 연속조회검색조건
        tr_cont: str = "",  # 연속거래여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 내부 재귀깊이 (자동관리)
        max_depth: int = 10  # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    (★중요) 국내휴장일조회(TCA0903R) 서비스는 당사 원장서비스와 연관되어 있어 
    단시간 내 다수 호출시 서비스에 영향을 줄 수 있어 가급적 1일 1회 호출 부탁드립니다.

    국내휴장일조회 API입니다.
    영업일, 거래일, 개장일, 결제일 여부를 조회할 수 있습니다.
    주문을 넣을 수 있는지 확인하고자 하실 경우 개장일여부(opnd_yn)을 사용하시면 됩니다.
    
    Args:
        bass_dt (str): [필수] 기준일자 (ex. YYYYMMDD)
        NK100 (str): 연속조회키
        FK100 (str): 연속조회검색조건
        tr_cont (str): 연속거래여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        pd.DataFrame: 국내휴장일조회 데이터
        
    Example:
        >>> df = chk_holiday(bass_dt="20250630")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/chk-holiday"

    if bass_dt == "":
        raise ValueError("bass_dt is required (e.g. 'YYYYMMDD')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    tr_id = "CTCA0903R"  # 국내휴장일조회

    params = {
        "BASS_DT": bass_dt,
        "CTX_AREA_FK": FK100,
        "CTX_AREA_NK": NK100
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont
        FK100 = res.getBody().ctx_area_fk
        NK100 = res.getBody().ctx_area_nk

        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return chk_holiday(
                bass_dt, NK100, FK100, "N", dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 업종/기타 > 금리 종합(국내채권_금리)[국내주식-155]
##############################################################################################

def comp_interest(
        fid_cond_mrkt_div_code: str,  # 조건시장분류코드
        fid_cond_scr_div_code: str,  # 조건화면분류코드
        fid_div_cls_code: str,  # 분류구분코드
        fid_div_cls_code1: str,  # 분류구분코드
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        tr_cont: str = "",
        depth: int = 0,
        max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 업종/기타 
    금리 종합(국내채권_금리)[국내주식-155]
    금리 종합(국내채권_금리) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건시장분류코드 (필수)
        fid_cond_scr_div_code (str): 조건화면분류코드 (필수)
        fid_div_cls_code (str): 분류구분코드 (필수)
        fid_div_cls_code1 (str): 분류구분코드 (공백 허용)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 금리 종합(국내채권_금리) 데이터
        
    Example:
        >>> df1, df2 = comp_interest('01', '20702', '1', '')
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/comp-interest"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. '01')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. '01')")

    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20702')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20702')")

    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '1')")
        raise ValueError("fid_div_cls_code is required. (e.g. '1')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()

    tr_id = "FHPST07020000"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_DIV_CLS_CODE1": fid_div_cls_code1,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                current_data1 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe1 = pd.concat([dataframe1, current_data1],
                                       ignore_index=True) if dataframe1 is not None else current_data1
            else:
                dataframe1 = dataframe1 if dataframe1 is not None else pd.DataFrame()

        # output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                current_data2 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe2 = pd.concat([dataframe2, current_data2],
                                       ignore_index=True) if dataframe2 is not None else current_data2
            else:
                dataframe2 = dataframe2 if dataframe2 is not None else pd.DataFrame()

        tr_cont = res.getHeader().tr_cont

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return comp_interest(
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_div_cls_code,
                fid_div_cls_code1,
                "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 프로그램매매 종합현황(일별)[국내주식-115]
##############################################################################################

def comp_program_trade_daily(
        fid_cond_mrkt_div_code: str,  # [필수] 조건시장분류코드 (ex. J:주식,NX:NXT,UN:통합)
        fid_mrkt_cls_code: str,  # [필수] 시장구분코드 (ex. K:코스피,Q:코스닥)
        fid_input_date_1: str = "",  # 검색시작일
        fid_input_date_2: str = ""  # 검색종료일
) -> pd.DataFrame:
    """
    프로그램매매 종합현황(일별) API입니다. 
    한국투자 HTS(eFriend Plus) > [0460] 프로그램매매 종합현황 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건시장분류코드 (ex. J:주식,NX:NXT,UN:통합)
        fid_mrkt_cls_code (str): [필수] 시장구분코드 (ex. K:코스피,Q:코스닥)
        fid_input_date_1 (str): 검색시작일
        fid_input_date_2 (str): 검색종료일

    Returns:
        pd.DataFrame: 프로그램매매 종합현황(일별) 데이터
        
    Example:
        >>> df = comp_program_trade_daily("J", "K", "20250101", "20250617")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/comp-program-trade-daily"

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:주식,NX:NXT,UN:통합')")

    if fid_mrkt_cls_code == "":
        raise ValueError("fid_mrkt_cls_code is required (e.g. 'K:코스피,Q:코스닥')")

    tr_id = "FHPPG04600001"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_MRKT_CLS_CODE": fid_mrkt_cls_code,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_DATE_2": fid_input_date_2
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        return pd.DataFrame(res.getBody().output)
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 프로그램매매 종합현황(시간) [국내주식-114]
##############################################################################################

def comp_program_trade_today(
        fid_cond_mrkt_div_code: str,  # [필수] 시장 구분 코드 (J:KRX,NX:NXT,UN:통합)
        fid_mrkt_cls_code: str,  # [필수] 시장구분코드 (K:코스피, Q:코스닥)
        fid_sctn_cls_code: str = "",  # 구간 구분 코드
        fid_input_iscd: str = "",  # 입력종목코드
        fid_cond_mrkt_div_code1: str = "",  # 시장분류코드
        fid_input_hour_1: str = ""  # 입력시간
) -> pd.DataFrame:
    """
    프로그램매매 종합현황(시간) API입니다. 
    한국투자 HTS(eFriend Plus) > [0460] 프로그램매매 종합현황 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

    ※ 장시간(09:00~15:30) 동안의 최근 30분간의 데이터 확인이 가능하며, 다음조회가 불가합니다.
    ※ 장시간(09:00~15:30) 이후에는 bsop_hour 에 153000 ~ 170000 까지의 시간데이터가 출력되지만 데이터는 모두 동일한 장마감 데이터인 점 유의 부탁드립니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 시장 구분 코드 (ex. J:KRX,NX:NXT,UN:통합)
        fid_mrkt_cls_code (str): [필수] 시장구분코드 (ex. K:코스피, Q:코스닥)
        fid_sctn_cls_code (str): 구간 구분 코드
        fid_input_iscd (str): 입력종목코드
        fid_cond_mrkt_div_code1 (str): 시장분류코드
        fid_input_hour_1 (str): 입력시간
        
    Returns:
        pd.DataFrame: 프로그램매매 종합현황 데이터
        
    Example:
        >>> df = comp_program_trade_today("J", "K")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/comp-program-trade-today"

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:KRX,NX:NXT,UN:통합')")

    if fid_mrkt_cls_code == "":
        raise ValueError("fid_mrkt_cls_code is required (e.g. 'K:코스피, Q:코스닥')")

    tr_id = "FHPPG04600101"  # 프로그램매매 종합현황(시간)

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,  # 시장 구분 코드
        "FID_MRKT_CLS_CODE": fid_mrkt_cls_code,  # 시장구분코드
        "FID_SCTN_CLS_CODE": fid_sctn_cls_code,  # 구간 구분 코드
        "FID_INPUT_ISCD": fid_input_iscd,  # 입력종목코드
        "FID_COND_MRKT_DIV_CODE1": fid_cond_mrkt_div_code1,  # 시장분류코드
        "FID_INPUT_HOUR_1": fid_input_hour_1  # 입력시간
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        # array 타입이므로 DataFrame으로 반환
        current_data = pd.DataFrame(res.getBody().output)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 순위분석 > 국내주식 신용잔고 상위 [국내주식-109]
##############################################################################################

def credit_balance(
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_option: str,  # 증가율기간
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_rank_sort_cls_code: str,  # 순위 정렬 구분 코드
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        tr_cont: str = "",
        depth: int = 0,
        max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 신용잔고 상위[국내주식-109]
    국내주식 신용잔고 상위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_scr_div_code (str): Unique key(11701)
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200,
        fid_option (str): 2~999
        fid_cond_mrkt_div_code (str): 시장구분코드 (주식 J)
        fid_rank_sort_cls_code (str): '(융자)0:잔고비율 상위, 1: 잔고수량 상위, 2: 잔고금액 상위, 3: 잔고비율 증가상위, 4: 잔고비율 감소상위  (대주)5:잔고비율 상위, 6: 잔고수량 상위, 7: 잔고금액 상위, 8: 잔고비율 증가상위, 9: 잔고비율 감소상위 '
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 국내주식 신용잔고 상위 데이터
        
    Example:
        >>> df1, df2 = credit_balance('11701', '0000', '2', 'J', '0')
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/credit-balance"
    # 필수 파라미터 검증
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '11701')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '11701')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0000')")
        raise ValueError("fid_input_iscd is required. (e.g. '0000')")

    if not fid_option:
        logger.error("fid_option is required. (e.g. '2')")
        raise ValueError("fid_option is required. (e.g. '2')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    if fid_rank_sort_cls_code not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '0')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()

    tr_id = "FHKST17010000"

    params = {
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_OPTION": fid_option,
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                # output1은 단일 객체, output2는 배열일 수 있음
                if isinstance(output_data, list):
                    current_data1 = pd.DataFrame(output_data)
                else:
                    # 단일 객체인 경우 리스트로 감싸서 DataFrame 생성
                    current_data1 = pd.DataFrame([output_data])

                if dataframe1 is not None:
                    dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
                else:
                    dataframe1 = current_data1
            else:
                if dataframe1 is None:
                    dataframe1 = pd.DataFrame()
        else:
            if dataframe1 is None:
                dataframe1 = pd.DataFrame()
        # output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                # output1은 단일 객체, output2는 배열일 수 있음
                if isinstance(output_data, list):
                    current_data2 = pd.DataFrame(output_data)
                else:
                    # 단일 객체인 경우 리스트로 감싸서 DataFrame 생성
                    current_data2 = pd.DataFrame([output_data])

                if dataframe2 is not None:
                    dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
                else:
                    dataframe2 = current_data2
            else:
                if dataframe2 is None:
                    dataframe2 = pd.DataFrame()
        else:
            if dataframe2 is None:
                dataframe2 = pd.DataFrame()
        tr_cont = res.getHeader().tr_cont

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return credit_balance(
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_option,
                fid_cond_mrkt_div_code,
                fid_rank_sort_cls_code,
                "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 국내주식 당사 신용가능종목[국내주식-111]
##############################################################################################

def credit_by_company(
        fid_rank_sort_cls_code: str,  # 순위 정렬 구분 코드
        fid_slct_yn: str,  # 선택 여부
        fid_input_iscd: str,  # 입력 종목코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    국내주식 당사 신용가능종목[국내주식-111]
    국내주식 당사 신용가능종목 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_rank_sort_cls_code (str): 0:코드순, 1:이름순
        fid_slct_yn (str): 0:신용주문가능, 1: 신용주문불가
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100
        fid_cond_scr_div_code (str): Unique key(20477)
        fid_cond_mrkt_div_code (str): 시장구분코드 (주식 J)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 당사 신용가능종목 데이터
        
    Example:
        >>> df = credit_by_company(
        ...     fid_rank_sort_cls_code="1",
        ...     fid_slct_yn="0",
        ...     fid_input_iscd="0000",
        ...     fid_cond_scr_div_code="20477",
        ...     fid_cond_mrkt_div_code="J"
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/credit-by-company"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '1')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '1')")

    if not fid_slct_yn:
        logger.error("fid_slct_yn is required. (e.g. '0')")
        raise ValueError("fid_slct_yn is required. (e.g. '0')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0000')")
        raise ValueError("fid_input_iscd is required. (e.g. '0000')")

    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20477')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20477')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # API 호출 URL 및 ID 설정

    tr_id = "FHPST04770000"

    # 요청 파라미터 설정
    params = {
        "fid_rank_sort_cls_code": fid_rank_sort_cls_code,
        "fid_slct_yn": fid_slct_yn,
        "fid_input_iscd": fid_input_iscd,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    # API 호출 성공 시 데이터 처리
    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        # 기존 데이터프레임과 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        # 다음 페이지 호출
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return credit_by_company(
                fid_rank_sort_cls_code,
                fid_slct_yn,
                fid_input_iscd,
                fid_cond_scr_div_code,
                fid_cond_mrkt_div_code,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 호출 실패 시 에러 로그 출력
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 국내주식 신용잔고 일별추이[국내주식-110]
##############################################################################################

def daily_credit_balance(
        fid_cond_mrkt_div_code: str,  # [필수] 시장 분류 코드
        fid_cond_scr_div_code: str,  # [필수] 화면 분류 코드
        fid_input_iscd: str,  # [필수] 종목코드
        fid_input_date_1: str,  # [필수] 결제일자
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 내부 재귀깊이 (자동관리)
        max_depth: int = 10  # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    국내주식 신용잔고 일별추이 API입니다.
    한국투자 HTS(eFriend Plus) > [0476] 국내주식 신용잔고 일별추이 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    한 번의 호출에 최대 30건 확인 가능하며, fid_input_date_1 을 입력하여 다음 조회가 가능합니다.
    
    ※ 상환수량은 "매도상환수량+현금상환수량"의 합계 수치입니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 시장 분류 코드 (ex. J: 주식)
        fid_cond_scr_div_code (str): [필수] 화면 분류 코드 (ex. 20476)
        fid_input_iscd (str): [필수] 종목코드 (ex. 005930)
        fid_input_date_1 (str): [필수] 결제일자 (ex. 20240313)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        pd.DataFrame: 국내주식 신용잔고 일별추이 데이터
        
    Example:
        >>> df = daily_credit_balance("J", "20476", "005930", "20240313")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/daily-credit-balance"

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")

    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '20476')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '005930')")

    if fid_input_date_1 == "":
        raise ValueError("fid_input_date_1 is required (e.g. '20240313')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    tr_id = "FHPST04760000"  # 국내주식 신용잔고 일별추이

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,  # 시장 분류 코드
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,  # 화면 분류 코드
        "FID_INPUT_ISCD": fid_input_iscd,  # 종목코드
        "FID_INPUT_DATE_1": fid_input_date_1  # 결제일자
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return daily_credit_balance(
                fid_cond_mrkt_div_code, fid_cond_scr_div_code, fid_input_iscd, fid_input_date_1, "N", dataframe,
                depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 종목별 일별 대차거래추이 [국내주식-135]
##############################################################################################

def daily_loan_trans(
        mrkt_div_cls_code: str,  # [필수] 조회구분 (ex. 1:코스피,2:코스닥,3:종목)
        mksc_shrn_iscd: str,  # [필수] 종목코드 (ex. 123456)
        start_date: str = "",  # 시작일자
        end_date: str = "",  # 종료일자
        cts: str = ""  # 이전조회KEY
) -> pd.DataFrame:
    """
    종목별 일별 대차거래추이 API입니다.
    한 번의 조회에 최대 100건까지 조회 가능하며, start_date, end_date 를 수정하여 다음 조회가 가능합니다.
    
    Args:
        mrkt_div_cls_code (str): [필수] 조회구분 (ex. 1:코스피,2:코스닥,3:종목)
        mksc_shrn_iscd (str): [필수] 종목코드 (ex. 123456)
        start_date (str): 시작일자
        end_date (str): 종료일자
        cts (str): 이전조회KEY

    Returns:
        pd.DataFrame: 종목별 일별 대차거래추이 데이터
        
    Example:
        >>> df = daily_loan_trans(mrkt_div_cls_code="1", mksc_shrn_iscd="005930")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/daily-loan-trans"

    # 필수 파라미터 검증
    if mrkt_div_cls_code == "":
        raise ValueError("mrkt_div_cls_code is required (e.g. '1', '2', '3')")

    if mksc_shrn_iscd == "":
        raise ValueError("mksc_shrn_iscd is required (e.g. '123456')")

    tr_id = "HHPST074500C0"

    params = {
        "MRKT_DIV_CLS_CODE": mrkt_div_cls_code,
        "MKSC_SHRN_ISCD": mksc_shrn_iscd,
        "START_DATE": start_date,
        "END_DATE": end_date,
        "CTS": cts
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        result_data = pd.DataFrame(res.getBody().output1)
        return result_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 국내주식 공매도 일별추이[국내주식-134]
##############################################################################################

def daily_short_sale(
        fid_cond_mrkt_div_code: str,  # [필수] 시장분류코드 (ex. J:주식)
        fid_input_iscd: str,  # [필수] 종목코드 (ex. 123456)
        fid_input_date_1: str = "",  # 시작일자
        fid_input_date_2: str = ""  # 종료일자
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    국내주식 공매도 일별추이를 조회합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 시장분류코드 (ex. J:주식)
        fid_input_iscd (str): [필수] 종목코드 (ex. 123456)
        fid_input_date_1 (str): 시작일자
        fid_input_date_2 (str): 종료일자

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 데이터프레임 쌍
        
    Example:
        >>> df1, df2 = daily_short_sale("J", "005930", "20240301", "20240328")
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/daily-short-sale"

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:주식')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '123456')")

    tr_id = "FHPST04830000"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_DATE_2": fid_input_date_2
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        # output1 처리 (object 타입 -> DataFrame)
        output1_data = pd.DataFrame(res.getBody().output1, index=[0])

        # output2 처리 (array 타입 -> DataFrame)
        output2_data = pd.DataFrame(res.getBody().output2)

        return output1_data, output2_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 순위분석 > 국내주식 이격도 순위 [v1_국내주식-095]
##############################################################################################

def disparity(
        fid_input_price_2: str,  # 입력 가격2
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_rank_sort_cls_code: str,  # 순위 정렬 구분 코드
        fid_hour_cls_code: str,  # 시간 구분 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_trgt_cls_code: str,  # 대상 구분 코드
        fid_trgt_exls_cls_code: str,  # 대상 제외 구분 코드
        fid_input_price_1: str,  # 입력 가격1
        fid_vol_cnt: str,  # 거래량 수
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 이격도 순위[v1_국내주식-095]
    국내주식 이격도 순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_input_price_2 (str): 입력값 없을때 전체 (~ 가격)
        fid_cond_mrkt_div_code (str): 시장구분코드 (ex. J:KRX, NX:NXT)
        fid_cond_scr_div_code (str): Unique key( 20178 )
        fid_div_cls_code (str): 0: 전체, 1:관리종목, 2:투자주의, 3:투자경고, 4:투자위험예고, 5:투자위험, 6:보톧주, 7:우선주
        fid_rank_sort_cls_code (str): 0: 이격도상위순, 1:이격도하위순
        fid_hour_cls_code (str): 5:이격도5, 10:이격도10, 20:이격도20, 60:이격도60, 120:이격도120
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200
        fid_trgt_cls_code (str): 0 : 전체
        fid_trgt_exls_cls_code (str): 0 : 전체
        fid_input_price_1 (str): 입력값 없을때 전체 (가격 ~)
        fid_vol_cnt (str): 입력값 없을때 전체 (거래량 ~)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 이격도 순위 데이터
        
    Example:
        >>> df = disparity(
        ...     fid_input_price_2="",
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_cond_scr_div_code="20178",
        ...     fid_div_cls_code="0",
        ...     fid_rank_sort_cls_code="0",
        ...     fid_hour_cls_code="5",
        ...     fid_input_iscd="0000",
        ...     fid_trgt_cls_code="0",
        ...     fid_trgt_exls_cls_code="0",
        ...     fid_input_price_1="",
        ...     fid_vol_cnt=""
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/disparity"
    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20178')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20178')")

    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")

    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '0')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '0')")

    if not fid_hour_cls_code:
        logger.error("fid_hour_cls_code is required. (e.g. '5')")
        raise ValueError("fid_hour_cls_code is required. (e.g. '5')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0000')")
        raise ValueError("fid_input_iscd is required. (e.g. '0000')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHPST01780000"

    params = {
        "fid_input_price_2": fid_input_price_2,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_rank_sort_cls_code": fid_rank_sort_cls_code,
        "fid_hour_cls_code": fid_hour_cls_code,
        "fid_input_iscd": fid_input_iscd,
        "fid_trgt_cls_code": fid_trgt_cls_code,
        "fid_trgt_exls_cls_code": fid_trgt_exls_cls_code,
        "fid_input_price_1": fid_input_price_1,
        "fid_vol_cnt": fid_vol_cnt,
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return disparity(
                fid_input_price_2,
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_div_cls_code,
                fid_rank_sort_cls_code,
                fid_hour_cls_code,
                fid_input_iscd,
                fid_trgt_cls_code,
                fid_trgt_exls_cls_code,
                fid_input_price_1,
                fid_vol_cnt,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 순위분석 > 국내주식 배당률 상위[국내주식-106]
##############################################################################################

def dividend_rate(
        cts_area: str,  # CTS_AREA
        gb1: str,  # KOSPI
        upjong: str,  # 업종구분
        gb2: str,  # 종목선택
        gb3: str,  # 배당구분
        f_dt: str,  # 기준일From
        t_dt: str,  # 기준일To
        gb4: str,  # 결산/중간배당
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 배당률 상위[국내주식-106]
    국내주식 배당률 상위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cts_area (str): 공백
        gb1 (str): 0:전체, 1:코스피,  2: 코스피200, 3: 코스닥,
        upjong (str): '코스피(0001:종합, 0002:대형주.…0027:제조업 ),  코스닥(1001:종합, …. 1041:IT부품 코스피200 (2001:KOSPI200, 2007:KOSPI100, 2008:KOSPI50)'
        gb2 (str): 0:전체, 6:보통주, 7:우선주
        gb3 (str): 1:주식배당, 2: 현금배당
        f_dt (str): 기준일 시작
        t_dt (str): 기준일 종료
        gb4 (str): 0:전체, 1:결산배당, 2:중간배당
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 배당률 상위 데이터
        
    Example:
        >>> df = dividend_rate(
        ...     cts_area=" ",
        ...     gb1="1",
        ...     upjong="0001",
        ...     gb2="0",
        ...     gb3="1",
        ...     f_dt="20230101",
        ...     t_dt="20231231",
        ...     gb4="0"
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/dividend-rate"
    # 필수 파라미터 검증
    if not gb1:
        logger.error("gb1 is required. (e.g. '1')")
        raise ValueError("gb1 is required. (e.g. '1')")

    if not upjong:
        logger.error("upjong is required. (e.g. '0001')")
        raise ValueError("upjong is required. (e.g. '0001')")

    if not gb2:
        logger.error("gb2 is required. (e.g. '0')")
        raise ValueError("gb2 is required. (e.g. '0')")

    if not gb3:
        logger.error("gb3 is required. (e.g. '1')")
        raise ValueError("gb3 is required. (e.g. '1')")

    if not f_dt:
        logger.error("f_dt is required. (e.g. '20230101')")
        raise ValueError("f_dt is required. (e.g. '20230101')")

    if not t_dt:
        logger.error("t_dt is required. (e.g. '20231231')")
        raise ValueError("t_dt is required. (e.g. '20231231')")

    if not gb4:
        logger.error("gb4 is required. (e.g. '0')")
        raise ValueError("gb4 is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "HHKDB13470100"

    params = {
        "CTS_AREA": cts_area,
        "GB1": gb1,
        "UPJONG": upjong,
        "GB2": gb2,
        "GB3": gb3,
        "F_DT": f_dt,
        "T_DT": t_dt,
        "GB4": gb4,
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return dividend_rate(
                cts_area,
                gb1,
                upjong,
                gb2,
                gb3,
                f_dt,
                t_dt,
                gb4,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 국내주식 종목추정실적[국내주식-187]
##############################################################################################

def estimate_perform(
        sht_cd: str,  # 종목코드
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        dataframe3: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output3)
        dataframe4: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output4)
        tr_cont: str = "",
        depth: int = 0,
        max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 종목정보 
    국내주식 종목추정실적[국내주식-187]
    국내주식 종목추정실적 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        sht_cd (str): 종목코드 (예: 265520)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        dataframe3 (Optional[pd.DataFrame]): 누적 데이터프레임 (output3)
        dataframe4 (Optional[pd.DataFrame]): 누적 데이터프레임 (output4)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]: 국내주식 종목추정실적 데이터
        
    Example:
        >>> df1, df2, df3, df4 = estimate_perform("265520")
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/estimate-perform"
    # 필수 파라미터 검증
    if not sht_cd:
        logger.error("sht_cd is required. (e.g. '265520')")
        raise ValueError("sht_cd is required. (e.g. '265520')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return (
            dataframe1 if dataframe1 is not None else pd.DataFrame(),
            dataframe2 if dataframe2 is not None else pd.DataFrame(),
            dataframe3 if dataframe3 is not None else pd.DataFrame(),
            dataframe4 if dataframe4 is not None else pd.DataFrame()
        )

    tr_id = "HHKST668300C0"

    params = {
        "SHT_CD": sht_cd,
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                current_data1 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe1 = pd.concat([dataframe1, current_data1],
                                       ignore_index=True) if dataframe1 is not None else current_data1
            else:
                dataframe1 = pd.DataFrame() if dataframe1 is None else dataframe1

        # output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                current_data2 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe2 = pd.concat([dataframe2, current_data2],
                                       ignore_index=True) if dataframe2 is not None else current_data2
            else:
                dataframe2 = pd.DataFrame() if dataframe2 is None else dataframe2

        # output3 처리
        if hasattr(res.getBody(), 'output3'):
            output_data = res.getBody().output3
            if output_data:
                current_data3 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe3 = pd.concat([dataframe3, current_data3],
                                       ignore_index=True) if dataframe3 is not None else current_data3
            else:
                dataframe3 = pd.DataFrame() if dataframe3 is None else dataframe3

        # output4 처리
        if hasattr(res.getBody(), 'output4'):
            output_data = res.getBody().output4
            if output_data:
                current_data4 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe4 = pd.concat([dataframe4, current_data4],
                                       ignore_index=True) if dataframe4 is not None else current_data4
            else:
                dataframe4 = pd.DataFrame() if dataframe4 is None else dataframe4

        tr_cont = res.getHeader().tr_cont

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return estimate_perform(
                sht_cd, dataframe1, dataframe2, dataframe3, dataframe4, "N", depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2, dataframe3, dataframe4
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 국내주식 장마감 예상체결가[국내주식-120]
##############################################################################################

def exp_closing_price(
        fid_cond_mrkt_div_code: str,  # [필수] 조건시장분류코드 (ex. J:주식)
        fid_input_iscd: str,  # [필수] 입력종목코드 (ex. 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100)
        fid_rank_sort_cls_code: str,  # [필수] 순위정렬구분코드 (ex. 0:전체, 1:상한가마감예상, 2:하한가마감예상, 3:직전대비상승률상위, 4:직전대비하락률상위)
        fid_cond_scr_div_code: str,  # [필수] 조건화면분류코드 (ex. 11173)
        fid_blng_cls_code: str  # [필수] 소속구분코드 (ex. 0:전체, 1:종가범위연장)
) -> pd.DataFrame:
    """
    국내주식 장마감 예상체결가 API입니다. 
    한국투자 HTS(eFriend Plus) > [0183] 장마감 예상체결가 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건시장분류코드 (ex. J:주식)
        fid_input_iscd (str): [필수] 입력종목코드 (ex. 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100)
        fid_rank_sort_cls_code (str): [필수] 순위정렬구분코드 (ex. 0:전체, 1:상한가마감예상, 2:하한가마감예상, 3:직전대비상승률상위, 4:직전대비하락률상위)
        fid_cond_scr_div_code (str): [필수] 조건화면분류코드 (ex. 11173)
        fid_blng_cls_code (str): [필수] 소속구분코드 (ex. 0:전체, 1:종가범위연장)

    Returns:
        pd.DataFrame: 국내주식 장마감 예상체결가 데이터
        
    Example:
        >>> df = exp_closing_price("J", "0001", "0", "11173", "0")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/exp-closing-price"

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '0000', '0001', '1001', '2001', '4001')")

    if fid_rank_sort_cls_code == "":
        raise ValueError("fid_rank_sort_cls_code is required (e.g. '0', '1', '2', '3', '4')")

    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '11173')")

    if fid_blng_cls_code == "":
        raise ValueError("fid_blng_cls_code is required (e.g. '0', '1')")

    tr_id = "FHKST117300C0"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_BLNG_CLS_CODE": fid_blng_cls_code
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        return pd.DataFrame(res.getBody().output)
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 업종/기타 > 국내주식 예상체결지수 추이[국내주식-121]
##############################################################################################

def exp_index_trend(
        fid_mkop_cls_code: str,  # 장운영 구분 코드
        fid_input_hour_1: str,  # 입력 시간1
        fid_input_iscd: str,  # 입력 종목코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 업종/기타 
    국내주식 예상체결지수 추이[국내주식-121]
    국내주식 예상체결지수 추이 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_mkop_cls_code (str): 1: 장시작전, 2: 장마감
        fid_input_hour_1 (str): 10(10초), 30(30초), 60(1분), 600(10분)
        fid_input_iscd (str): 0000:전체, 0001:코스피, 1001:코스닥, 2001:코스피200, 4001: KRX100
        fid_cond_mrkt_div_code (str): 시장구분코드 (주식 U)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 예상체결지수 추이 데이터
        
    Example:
        >>> df = exp_index_trend('1', '10', '0000', 'U')
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/exp-index-trend"
    # 필수 파라미터 검증
    if not fid_mkop_cls_code:
        logger.error("fid_mkop_cls_code is required. (e.g. '1')")
        raise ValueError("fid_mkop_cls_code is required. (e.g. '1')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0000')")
        raise ValueError("fid_input_iscd is required. (e.g. '0000')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'U')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'U')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHPST01840000"

    params = {
        "FID_MKOP_CLS_CODE": fid_mkop_cls_code,
        "FID_INPUT_HOUR_1": fid_input_hour_1,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return exp_index_trend(
                fid_mkop_cls_code,
                fid_input_hour_1,
                fid_input_iscd,
                fid_cond_mrkt_div_code,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 국내주식 예상체결가 추이[국내주식-118]
##############################################################################################

def exp_price_trend(
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드 (ex. J)
        fid_input_iscd: str,  # 입력 종목코드 (ex. 123456)
        fid_mkop_cls_code: str  # (ex. 0:전체, 4:체결량 0 제외)
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    국내주식 예상체결가 추이 API입니다.
    한국투자 HTS(eFriend Plus) > [0184] 예상체결지수 추이 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    최대 30건 확인 가능하며, 다음 조회가 불가합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 123456)
        fid_mkop_cls_code (str): [필수]  (ex. 0:전체, 4:체결량 0 제외)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 데이터

    Example:
        >>> output1, output2 = exp_price_trend("J", "005930", "0")
        >>> print(output1)
        >>> print(output2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/exp-price-trend"

    if not fid_cond_mrkt_div_code:
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")

    if not fid_input_iscd:
        raise ValueError("fid_input_iscd is required (e.g. '123456')")

    if not fid_mkop_cls_code:
        raise ValueError("fid_mkop_cls_code is required (e.g. '0')")

    tr_id = "FHPST01810000"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_MKOP_CLS_CODE": fid_mkop_cls_code,
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        output1_data = pd.DataFrame([res.getBody().output1])
        output2_data = pd.DataFrame(res.getBody().output2)

        logging.info("Data fetch complete.")
        return output1_data, output2_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 업종/기타 > 국내주식 예상체결 전체지수[국내주식-122]
##############################################################################################

def exp_total_index(
        fid_mrkt_cls_code: str,  # 시장 구분 코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_mkop_cls_code: str,  # 장운영 구분 코드
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        tr_cont: str = "",
        depth: int = 0,
        max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 업종/기타 
    국내주식 예상체결 전체지수[국내주식-122]
    국내주식 예상체결 전체지수 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_mrkt_cls_code (str): 0:전체 K:거래소 Q:코스닥
        fid_cond_mrkt_div_code (str): 시장구분코드 (업종 U)
        fid_cond_scr_div_code (str): Unique key(11175)
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100
        fid_mkop_cls_code (str): 1:장시작전, 2:장마감
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 국내주식 예상체결 전체지수 데이터
        
    Example:
        >>> df1, df2 = exp_total_index(
        ...     fid_mrkt_cls_code="K",
        ...     fid_cond_mrkt_div_code="U",
        ...     fid_cond_scr_div_code="11175",
        ...     fid_input_iscd="1001",
        ...     fid_mkop_cls_code="1"
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/exp-total-index"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_mrkt_cls_code:
        logger.error("fid_mrkt_cls_code is required. (e.g. 'K')")
        raise ValueError("fid_mrkt_cls_code is required. (e.g. 'K')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'U')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'U')")

    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '11175')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '11175')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '1001')")
        raise ValueError("fid_input_iscd is required. (e.g. '1001')")

    if not fid_mkop_cls_code:
        logger.error("fid_mkop_cls_code is required. (e.g. '1')")
        raise ValueError("fid_mkop_cls_code is required. (e.g. '1')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()

    tr_id = "FHKUP11750000"

    params = {
        "fid_mrkt_cls_code": fid_mrkt_cls_code,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_input_iscd": fid_input_iscd,
        "fid_mkop_cls_code": fid_mkop_cls_code,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                current_data1 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe1 = pd.concat([dataframe1, current_data1],
                                       ignore_index=True) if dataframe1 is not None else current_data1
            else:
                dataframe1 = pd.DataFrame() if dataframe1 is None else dataframe1
        else:
            dataframe1 = pd.DataFrame() if dataframe1 is None else dataframe1

        # output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                current_data2 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe2 = pd.concat([dataframe2, current_data2],
                                       ignore_index=True) if dataframe2 is not None else current_data2
            else:
                dataframe2 = pd.DataFrame() if dataframe2 is None else dataframe2
        else:
            dataframe2 = pd.DataFrame() if dataframe2 is None else dataframe2

        tr_cont = res.getHeader().tr_cont

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return exp_total_index(
                fid_mrkt_cls_code,
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_mkop_cls_code,
                "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 순위분석 > 국내주식 예상체결 상승_하락상위[v1_국내주식-103]
##############################################################################################

def exp_trans_updown(
        fid_rank_sort_cls_code: str,  # 순위 정렬 구분 코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_aply_rang_prc_1: str,  # 적용 범위 가격1
        fid_vol_cnt: str,  # 거래량 수
        fid_pbmn: str,  # 거래대금
        fid_blng_cls_code: str,  # 소속 구분 코드
        fid_mkop_cls_code: str,  # 장운영 구분 코드
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 예상체결 상승_하락상위[v1_국내주식-103]
    국내주식 예상체결 상승_하락상위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_rank_sort_cls_code (str): 0:상승률1:상승폭2:보합3:하락율4:하락폭5:체결량6:거래대금
        fid_cond_mrkt_div_code (str): 시장구분코드 (주식 J)
        fid_cond_scr_div_code (str): Unique key(20182)
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100
        fid_div_cls_code (str): 0:전체 1:보통주 2:우선주
        fid_aply_rang_prc_1 (str): 입력값 없을때 전체 (가격 ~)
        fid_vol_cnt (str): 입력값 없을때 전체 (거래량 ~)
        fid_pbmn (str): 입력값 없을때 전체 (거래대금 ~) 천원단위
        fid_blng_cls_code (str): 0: 전체
        fid_mkop_cls_code (str): 0:장전예상1:장마감예상
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 예상체결 상승_하락상위 데이터
        
    Example:
        >>> df = exp_trans_updown(
        ...     fid_rank_sort_cls_code="0",
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_cond_scr_div_code="20182",
        ...     fid_input_iscd="0000",
        ...     fid_div_cls_code="0",
        ...     fid_aply_rang_prc_1="",
        ...     fid_vol_cnt="",
        ...     fid_pbmn="",
        ...     fid_blng_cls_code="0",
        ...     fid_mkop_cls_code="0"
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/exp-trans-updown"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '0')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '0')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20182')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20182')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0000')")
        raise ValueError("fid_input_iscd is required. (e.g. '0000')")

    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")

    if not fid_blng_cls_code:
        logger.error("fid_blng_cls_code is required. (e.g. '0')")
        raise ValueError("fid_blng_cls_code is required. (e.g. '0')")

    if not fid_mkop_cls_code:
        logger.error("fid_mkop_cls_code is required. (e.g. '0')")
        raise ValueError("fid_mkop_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHPST01820000"

    params = {
        "fid_rank_sort_cls_code": fid_rank_sort_cls_code,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_input_iscd": fid_input_iscd,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_aply_rang_prc_1": fid_aply_rang_prc_1,
        "fid_vol_cnt": fid_vol_cnt,
        "fid_pbmn": fid_pbmn,
        "fid_blng_cls_code": fid_blng_cls_code,
        "fid_mkop_cls_code": fid_mkop_cls_code,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return exp_trans_updown(
                fid_rank_sort_cls_code,
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_div_cls_code,
                fid_aply_rang_prc_1,
                fid_vol_cnt,
                fid_pbmn,
                fid_blng_cls_code,
                fid_mkop_cls_code,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 국내주식 대차대조표 [v1_국내주식-078]
##############################################################################################

def finance_balance_sheet(
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    국내주식 대차대조표[v1_국내주식-078]
    국내주식 대차대조표 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_div_cls_code (str): 0: 년, 1: 분기
        fid_cond_mrkt_div_code (str): J
        fid_input_iscd (str): 000660 : 종목코드
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 대차대조표 데이터
        
    Example:
        >>> df = finance_balance_sheet("0", "J", "000660")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/finance/balance-sheet"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '000660')")
        raise ValueError("fid_input_iscd is required. (e.g. '000660')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHKST66430100"

    params = {
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_input_iscd": fid_input_iscd,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return finance_balance_sheet(
                fid_div_cls_code,
                fid_cond_mrkt_div_code,
                fid_input_iscd,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 에러 처리
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 국내주식 재무비율 [v1_국내주식-080]
##############################################################################################

def finance_financial_ratio(
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    국내주식 재무비율[v1_국내주식-080]
    국내주식 재무비율 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_div_cls_code (str): 0: 년, 1: 분기
        fid_cond_mrkt_div_code (str): J
        fid_input_iscd (str): 000660 : 종목코드
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 재무비율 데이터
        
    Example:
        >>> df = finance_financial_ratio("0", "J", "000660")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/finance/financial-ratio"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '000660')")
        raise ValueError("fid_input_iscd is required. (e.g. '000660')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHKST66430300"

    params = {
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_input_iscd": fid_input_iscd,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return finance_financial_ratio(
                fid_div_cls_code,
                fid_cond_mrkt_div_code,
                fid_input_iscd,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 국내주식 성장성비율 [v1_국내주식-085]
##############################################################################################

def finance_growth_ratio(
        fid_input_iscd: str,  # 입력 종목코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    국내주식 성장성비율[v1_국내주식-085]
    국내주식 성장성비율 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_input_iscd (str): 입력 종목코드 (예: '000660')
        fid_div_cls_code (str): 분류 구분 코드 (0: 년, 1: 분기)
        fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (예: 'J')
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 성장성비율 데이터
        
    Example:
        >>> df = finance_growth_ratio('005930', '1', 'J')
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/finance/growth-ratio"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '000660')")
        raise ValueError("fid_input_iscd is required. (e.g. '000660')")

    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0' or '1')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0' or '1')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # API URL 및 거래 ID 설정
    tr_id = "FHKST66430800"

    # 요청 파라미터 설정
    params = {
        "fid_input_iscd": fid_input_iscd,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    # API 응답 처리
    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return finance_growth_ratio(
                fid_input_iscd,
                fid_div_cls_code,
                fid_cond_mrkt_div_code,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 국내주식 손익계산서 [v1_국내주식-079]
##############################################################################################

def finance_income_statement(
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    국내주식 손익계산서 API를 호출하여 DataFrame으로 반환합니다.

    Args:
        fid_div_cls_code (str): 분류 구분 코드 (0: 년, 1: 분기)
        fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (예: 'J')
        fid_input_iscd (str): 입력 종목코드 (예: '000660')
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)

    Returns:
        Optional[pd.DataFrame]: 국내주식 손익계산서 데이터

    Example:
        >>> df = finance_income_statement('1', 'J', '005930')
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/finance/income-statement"
    # 필수 파라미터 검증
    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0' or '1')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0' or '1')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '000660')")
        raise ValueError("fid_input_iscd is required. (e.g. '000660')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHKST66430200"

    params = {
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_input_iscd": fid_input_iscd,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return finance_income_statement(
                fid_div_cls_code,
                fid_cond_mrkt_div_code,
                fid_input_iscd,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 국내주식 기타주요비율[v1_국내주식-082]
##############################################################################################

def finance_other_major_ratios(
        fid_input_iscd: str,  # 입력 종목코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    국내주식 기타주요비율[v1_국내주식-082]
    국내주식 기타주요비율 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_input_iscd (str): 종목코드 (예: '000660')
        fid_div_cls_code (str): 분류 구분 코드 (예: '0' - 년, '1' - 분기)
        fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (예: 'J')
        tr_cont (str): 연속 거래 여부 (기본값: 공백)
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (기본값: None)
        depth (int): 현재 재귀 깊이 (기본값: 0)
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 기타주요비율 데이터
        
    Example:
        >>> df = finance_other_major_ratios('005930', '1', 'J')
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/finance/other-major-ratios"
    # 필수 파라미터 검증
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '000660')")
        raise ValueError("fid_input_iscd is required. (e.g. '000660')")

    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0' or '1')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0' or '1')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHKST66430500"

    params = {
        "fid_input_iscd": fid_input_iscd,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return finance_other_major_ratios(
                fid_input_iscd,
                fid_div_cls_code,
                fid_cond_mrkt_div_code,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 국내주식 수익성비율[v1_국내주식-081]
##############################################################################################

def finance_profit_ratio(
        fid_input_iscd: str,  # 입력 종목코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    국내주식 수익성비율[v1_국내주식-081]
    국내주식 수익성비율 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_input_iscd (str): 입력 종목코드 (예: '000660')
        fid_div_cls_code (str): 분류 구분 코드 (0: 년, 1: 분기)
        fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (예: 'J')
        tr_cont (str): 연속 거래 여부 (기본값: 공백)
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 수익성비율 데이터
        
    Example:
        >>> df = finance_profit_ratio('005930', '1', 'J')
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/finance/profit-ratio"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '000660')")
        raise ValueError("fid_input_iscd is required. (e.g. '000660')")

    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHKST66430400"

    params = {
        "fid_input_iscd": fid_input_iscd,
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return finance_profit_ratio(
                fid_input_iscd,
                fid_div_cls_code,
                fid_cond_mrkt_div_code,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 호출 실패 시 에러 로그
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 순위분석 > 국내주식 재무비율 순위[v1_국내주식-092]
##############################################################################################

def finance_ratio(
        fid_trgt_cls_code: str,  # 대상 구분 코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_input_price_1: str,  # 입력 가격1
        fid_input_price_2: str,  # 입력 가격2
        fid_vol_cnt: str,  # 거래량 수
        fid_input_option_1: str,  # 입력 옵션1
        fid_input_option_2: str,  # 입력 옵션2
        fid_rank_sort_cls_code: str,  # 순위 정렬 구분 코드
        fid_blng_cls_code: str,  # 소속 구분 코드
        fid_trgt_exls_cls_code: str,  # 대상 제외 구분 코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None  # 누적 데이터프레임
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 재무비율 순위[v1_국내주식-092]
    국내주식 재무비율 순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_trgt_cls_code (str): 대상 구분 코드 (0 : 전체)
        fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (J:KRX, NX:NXT)
        fid_cond_scr_div_code (str): 조건 화면 분류 코드 (Unique key, 20175)
        fid_input_iscd (str): 입력 종목코드 (0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200)
        fid_div_cls_code (str): 분류 구분 코드 (0 : 전체)
        fid_input_price_1 (str): 입력 가격1 (입력값 없을때 전체, 가격 ~)
        fid_input_price_2 (str): 입력 가격2 (입력값 없을때 전체, ~ 가격)
        fid_vol_cnt (str): 거래량 수 (입력값 없을때 전체, 거래량 ~)
        fid_input_option_1 (str): 입력 옵션1 (회계년도 입력, ex 2023)
        fid_input_option_2 (str): 입력 옵션2 (0: 1/4분기, 1: 반기, 2: 3/4분기, 3: 결산)
        fid_rank_sort_cls_code (str): 순위 정렬 구분 코드 (7: 수익성 분석, 11: 안정성 분석, 15: 성장성 분석, 20: 활동성 분석)
        fid_blng_cls_code (str): 소속 구분 코드 (0)
        fid_trgt_exls_cls_code (str): 대상 제외 구분 코드 (0 : 전체)
        tr_cont (str): 연속 거래 여부 (공백 : 초기 조회, N : 다음 데이터 조회)
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 재무비율 순위 데이터
        
    Example:
        >>> df = finance_ratio(
        ...     fid_trgt_cls_code="0",
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_cond_scr_div_code="20175",
        ...     fid_input_iscd="0000",
        ...     fid_div_cls_code="0",
        ...     fid_input_price_1="",
        ...     fid_input_price_2="",
        ...     fid_vol_cnt="",
        ...     fid_input_option_1="2023",
        ...     fid_input_option_2="3",
        ...     fid_rank_sort_cls_code="7",
        ...     fid_blng_cls_code="0",
        ...     fid_trgt_exls_cls_code="0"
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/finance-ratio"
    # 필수 파라미터 검증
    if fid_trgt_cls_code == "":
        raise ValueError("대상 구분 코드 확인요망!!!")
    if fid_cond_mrkt_div_code != "J":
        raise ValueError("조건 시장 분류 코드 확인요망!!!")
    if fid_cond_scr_div_code != "20175":
        raise ValueError("조건 화면 분류 코드 확인요망!!!")
    if fid_input_iscd not in ["0000", "0001", "1001", "2001"]:
        raise ValueError("입력 종목코드 확인요망!!!")
    if fid_div_cls_code != "0":
        raise ValueError("분류 구분 코드 확인요망!!!")
    if fid_input_option_2 not in ["0", "1", "2", "3"]:
        raise ValueError("입력 옵션2 확인요망!!!")
    if fid_rank_sort_cls_code not in ["7", "11", "15", "20"]:
        raise ValueError("순위 정렬 구분 코드 확인요망!!!")
    if fid_blng_cls_code != "0":
        raise ValueError("소속 구분 코드 확인요망!!!")
    if fid_trgt_exls_cls_code != "0":
        raise ValueError("대상 제외 구분 코드 확인요망!!!")

    tr_id = "FHPST01750000"

    params = {
        "fid_trgt_cls_code": fid_trgt_cls_code,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_input_iscd": fid_input_iscd,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_input_price_1": fid_input_price_1,
        "fid_input_price_2": fid_input_price_2,
        "fid_vol_cnt": fid_vol_cnt,
        "fid_input_option_1": fid_input_option_1,
        "fid_input_option_2": fid_input_option_2,
        "fid_rank_sort_cls_code": fid_rank_sort_cls_code,
        "fid_blng_cls_code": fid_blng_cls_code,
        "fid_trgt_exls_cls_code": fid_trgt_exls_cls_code,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            print("Call Next")
            ka.smart_sleep()
            return finance_ratio(
                fid_trgt_cls_code,
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_div_cls_code,
                fid_input_price_1,
                fid_input_price_2,
                fid_vol_cnt,
                fid_input_option_1,
                fid_input_option_2,
                fid_rank_sort_cls_code,
                fid_blng_cls_code,
                fid_trgt_exls_cls_code,
                "N", dataframe
            )
        else:
            print("The End")
            return dataframe
    else:
        # 오류 처리
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 국내주식 안정성비율[v1_국내주식-083]
##############################################################################################

def finance_stability_ratio(
        fid_input_iscd: str,  # 입력 종목코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    국내주식 안정성비율[v1_국내주식-083]
    국내주식 안정성비율 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_input_iscd (str): 종목코드 (예: '000660')
        fid_div_cls_code (str): 분류 구분 코드 (예: '0' - 년, '1' - 분기)
        fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (예: 'J')
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (기본값: None)
        depth (int): 현재 재귀 깊이 (기본값: 0)
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 안정성비율 데이터
        
    Example:
        >>> df = finance_stability_ratio('005930', '1', 'J')
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/finance/stability-ratio"
    # 필수 파라미터 검증
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '000660')")
        raise ValueError("fid_input_iscd is required. (e.g. '000660')")

    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0' or '1')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0' or '1')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHKST66430600"

    params = {
        "fid_input_iscd": fid_input_iscd,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return finance_stability_ratio(
                fid_input_iscd,
                fid_div_cls_code,
                fid_cond_mrkt_div_code,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 순위분석 > 등락률 순위[v1_국내주식-088]
##############################################################################################

def fluctuation(
        fid_cond_mrkt_div_code: str,  # 필수, 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 필수, 조건 화면 분류 코드
        fid_input_iscd: str,  # 필수, 입력 종목코드
        fid_rank_sort_cls_code: str,  # 필수, 순위 정렬 구분 코드
        fid_input_cnt_1: str,  # 필수, 입력 수1
        fid_prc_cls_code: str,  # 필수, 가격 구분 코드
        fid_input_price_1: str,  # 필수, 입력 가격1
        fid_input_price_2: str,  # 필수, 입력 가격2
        fid_vol_cnt: str,  # 필수, 거래량 수
        fid_trgt_cls_code: str,  # 필수, 대상 구분 코드
        fid_trgt_exls_cls_code: str,  # 필수, 대상 제외 구분 코드
        fid_div_cls_code: str,  # 필수, 분류 구분 코드
        fid_rsfl_rate1: str,  # 필수, 등락 비율1
        fid_rsfl_rate2: str,  # 필수, 등락 비율2
        tr_cont: str = "",  # 선택, 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None  # 선택, 누적 데이터프레임
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석
    등락률 순위[v1_국내주식-088]
    국내주식 등락률 순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (J:KRX, NX:NXT)
        fid_cond_scr_div_code (str): 조건 화면 분류 코드 (20170: 등락률)
        fid_input_iscd (str): 입력 종목코드 (0000: 전체)
        fid_rank_sort_cls_code (str): 순위 정렬 구분 코드 (0000: 등락률순)
        fid_input_cnt_1 (str): 입력 수1 (조회할 종목 수)
        fid_prc_cls_code (str): 가격 구분 코드 (0: 전체)
        fid_input_price_1 (str): 입력 가격1 (하한가)
        fid_input_price_2 (str): 입력 가격2 (상한가)
        fid_vol_cnt (str): 거래량 수 (최소 거래량)
        fid_trgt_cls_code (str): 대상 구분 코드 (9자리, "1" or "0", 증거금30% 40% 50% 60% 100% 신용보증금30% 40% 50% 60%)
        fid_trgt_exls_cls_code (str): 대상 제외 구분 코드 (10자리, "1" or "0", 투자위험/경고/주의 관리종목 정리매매 불성실공시 우선주 거래정지 ETF ETN 신용주문불가 SPAC)
        fid_div_cls_code (str): 분류 구분 코드 (0: 전체)
        fid_rsfl_rate1 (str): 등락 비율1 (하락률 하한)
        fid_rsfl_rate2 (str): 등락 비율2 (상승률 상한)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        
    Returns:
        Optional[pd.DataFrame]: API 응답 데이터
        
    Example:
        >>> df = fluctuation(fid_rsfl_rate2="10", fid_cond_mrkt_div_code="J", fid_cond_scr_div_code="20170", fid_input_iscd="0000", fid_rank_sort_cls_code="0000", fid_input_cnt_1="10", fid_prc_cls_code="0", fid_input_price_1="0", fid_input_price_2="1000000", fid_vol_cnt="100000", fid_trgt_cls_code="0", fid_trgt_exls_cls_code="0", fid_div_cls_code="0", fid_rsfl_rate1="0")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/fluctuation"
    if fid_cond_mrkt_div_code not in ["J", "W", "Q"]:
        raise ValueError("조건 시장 분류 코드 확인요망!!!")

    if fid_cond_scr_div_code != "20170":
        raise ValueError("조건 화면 분류 코드 확인요망!!!")

    tr_id = "FHPST01700000"  # 국내주식 등락률 순위

    params = {
        "fid_rsfl_rate2": fid_rsfl_rate2,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_input_iscd": fid_input_iscd,
        "fid_rank_sort_cls_code": fid_rank_sort_cls_code,
        "fid_input_cnt_1": fid_input_cnt_1,
        "fid_prc_cls_code": fid_prc_cls_code,
        "fid_input_price_1": fid_input_price_1,
        "fid_input_price_2": fid_input_price_2,
        "fid_vol_cnt": fid_vol_cnt,
        "fid_trgt_cls_code": fid_trgt_cls_code,
        "fid_trgt_exls_cls_code": fid_trgt_exls_cls_code,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_rsfl_rate1": fid_rsfl_rate1
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":  # 다음 페이지 존재
            print("Call Next")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return fluctuation(
                fid_rsfl_rate2, fid_cond_mrkt_div_code, fid_cond_scr_div_code,
                fid_input_iscd, fid_rank_sort_cls_code, fid_input_cnt_1,
                fid_prc_cls_code, fid_input_price_1, fid_input_price_2,
                fid_vol_cnt, fid_trgt_cls_code, fid_trgt_exls_cls_code,
                fid_div_cls_code, fid_rsfl_rate1, "N", dataframe
            )
        else:
            print("The End")
            return dataframe
    else:
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 국내기관_외국인 매매종목가집계[국내주식-037]
##############################################################################################

def foreign_institution_total(
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건화면분류코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_div_cls_code: str,  # 분류구분코드
        fid_rank_sort_cls_code: str,  # 순위정렬구분코드
        fid_etc_cls_code: str  # 기타구분정렬
) -> pd.DataFrame:
    """
    국내기관_외국인 매매종목가집계 API입니다.

    HTS(efriend Plus) [0440] 외국인/기관 매매종목 가집계 화면을 API로 구현한 사항으로 화면을 함께 보시면 기능 이해가 쉽습니다.

    증권사 직원이 장중에 집계/입력한 자료를 단순 누계한 수치로서, 
    입력시간은 외국인 09:30, 11:20, 13:20, 14:30 / 기관종합 10:00, 11:20, 13:20, 14:30 이며, 
    입력한 시간은 ±10분정도 차이가 발생할 수 있으며, 장운영 사정에 다라 변동될 수 있습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. V)
        fid_cond_scr_div_code (str): [필수] 조건화면분류코드 (ex. 16449)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 0000:전체,0001:코스피,1001:코스닥,...,FAQ 종목정보 다운로드(국내) - 업종코드 참조 )
        fid_div_cls_code (str): [필수] 분류구분코드 (ex. 0:수량정열, 1:금액정열)
        fid_rank_sort_cls_code (str): [필수] 순위정렬구분코드 (ex. 0:순매수상위,1:순매도상위)
        fid_etc_cls_code (str): [필수] 기타구분정렬 (ex. 0:전체,1:외국인,2:기관계,3:기타)

    Returns:
        pd.DataFrame: 국내기관_외국인 매매종목가집계 데이터
        
    Example:
        >>> df = foreign_institution_total("V", "16449", "0000", "0", "0", "0")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/foreign-institution-total"

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'V')")

    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '16449')")

    if fid_input_iscd == "":
        raise ValueError(
            "fid_input_iscd is required (e.g. '0000:전체,0001:코스피,1001:코스닥,...,FAQ 종목정보 다운로드(국내) - 업종코드 참조 ')")

    if fid_div_cls_code == "":
        raise ValueError("fid_div_cls_code is required (e.g. '0:수량정열, 1:금액정열')")

    if fid_rank_sort_cls_code == "":
        raise ValueError("fid_rank_sort_cls_code is required (e.g. '0:순매수상위,1:순매도상위')")

    if fid_etc_cls_code == "":
        raise ValueError("fid_etc_cls_code is required (e.g. '0:전체,1:외국인,2:기관계,3:기타')")

    tr_id = "FHPTJ04400000"  # 국내기관_외국인 매매종목가집계

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,  # 조건 시장 분류 코드
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,  # 조건화면분류코드
        "FID_INPUT_ISCD": fid_input_iscd,  # 입력 종목코드
        "FID_DIV_CLS_CODE": fid_div_cls_code,  # 분류구분코드
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,  # 순위정렬구분코드
        "FID_ETC_CLS_CODE": fid_etc_cls_code  # 기타구분정렬
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)

        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 종목별 외국계 순매수추이 [국내주식-164]
##############################################################################################

def frgnmem_pchs_trend(
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드 (ex. J)
        fid_input_iscd: str,  # 입력 종목코드 (ex. 123456)
        fid_input_iscd_2: str  # 입력 종목코드 (ex. 99999)
) -> pd.DataFrame:
    """
    종목별 외국계 순매수추이 API입니다.
    한국투자 HTS(eFriend Plus) > [0433] 종목별 외국계 순매수추이 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 123456)
        fid_input_iscd_2 (str): [필수] 입력 종목코드 (ex. 99999)

    Returns:
        pd.DataFrame: 종목별 외국계 순매수추이 데이터

    Example:
        >>> df = frgnmem_pchs_trend("J", "005930", "99999")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/frgnmem-pchs-trend"

    if not fid_cond_mrkt_div_code:
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")

    if not fid_input_iscd:
        raise ValueError("fid_input_iscd is required (e.g. '123456')")

    if not fid_input_iscd_2:
        raise ValueError("fid_input_iscd_2 is required (e.g. '99999')")

    tr_id = "FHKST644400C0"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_ISCD_2": fid_input_iscd_2,
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        output_data = pd.DataFrame(res.getBody().output)

        logging.info("Data fetch complete.")
        return output_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 외국계 매매종목 가집계 [국내주식-161]
##############################################################################################

def frgnmem_trade_estimate(
        fid_cond_mrkt_div_code: str,
        fid_cond_scr_div_code: str,
        fid_input_iscd: str,
        fid_rank_sort_cls_code: str,
        fid_rank_sort_cls_code_2: str
) -> pd.DataFrame:
    """
    외국계 매매종목 가집계 API입니다.
    한국투자 HTS(eFriend Plus) > [0430] 외국계 매매종목 가집계 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건시장분류코드 (ex. J)
        fid_cond_scr_div_code (str): [필수] 조건화면분류코드 (ex. 16441)
        fid_input_iscd (str): [필수] 입력종목코드 (ex. 0000:전체, 1001:코스피, 2001:코스닥)
        fid_rank_sort_cls_code (str): [필수] 순위정렬구분코드 (ex. 0:금액순, 1:수량순)
        fid_rank_sort_cls_code_2 (str): [필수] 순위정렬구분코드2 (ex. 0:매수순, 1:매도순)
        
    Returns:
        pd.DataFrame: 외국계 매매종목 가집계 데이터
        
    Example:
        >>> df = frgnmem_trade_estimate("J", "16441", "0000", "0", "0")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/frgnmem-trade-estimate"

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")

    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '16441')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '0000')")

    if fid_rank_sort_cls_code == "":
        raise ValueError("fid_rank_sort_cls_code is required (e.g. '0')")

    if fid_rank_sort_cls_code_2 == "":
        raise ValueError("fid_rank_sort_cls_code_2 is required (e.g. '0')")

    tr_id = "FHKST644100C0"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_RANK_SORT_CLS_CODE_2": fid_rank_sort_cls_code_2
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 회원사 실 시간 매매동향(틱)[국내주식-163]
##############################################################################################

def frgnmem_trade_trend(
        fid_cond_scr_div_code: str,  # 화면분류코드
        fid_cond_mrkt_div_code: str,  # 조건시장구분코드
        fid_input_iscd: str,  # 종목코드
        fid_input_iscd_2: str,  # 회원사코드
        fid_mrkt_cls_code: str,  # 시장구분코드
        fid_vol_cnt: str,  # 거래량
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        tr_cont: str = "",
        depth: int = 0,
        max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 시세분석 
    회원사 실 시간 매매동향(틱)[국내주식-163]
    회원사 실 시간 매매동향(틱) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_scr_div_code (str): 20432(primary key)
        fid_cond_mrkt_div_code (str): J 고정입력
        fid_input_iscd (str): ex. 005930(삼성전자)   ※ FID_INPUT_ISCD(종목코드) 혹은 FID_MRKT_CLS_CODE(시장구분코드) 둘 중 하나만 입력
        fid_input_iscd_2 (str): ex. 99999(전체)  ※ 회원사코드 (kis developers 포탈 사이트 포럼-> FAQ -> 종목정보 다운로드(국내) 참조)
        fid_mrkt_cls_code (str): A(전체),K(코스피), Q(코스닥), K2(코스피200), W(ELW)  ※ FID_INPUT_ISCD(종목코드) 혹은 FID_MRKT_CLS_CODE(시장구분코드) 둘 중 하나만 입력
        fid_vol_cnt (str): 거래량 ~
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 회원사 실 시간 매매동향(틱) 데이터
        
    Example:
        >>> df1, df2 = frgnmem_trade_trend(
        ...     fid_cond_scr_div_code="20432",
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_input_iscd="005930",
        ...     fid_input_iscd_2="99999",
        ...     fid_mrkt_cls_code="A",
        ...     fid_vol_cnt="1000"
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/frgnmem-trade-trend"
    # [필수 파라미터 검증]
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20432')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20432')")
    if not fid_cond_mrkt_div_code or fid_cond_mrkt_div_code != "J":
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '005930')")
        raise ValueError("fid_input_iscd is required. (e.g. '005930')")
    if not fid_input_iscd_2:
        logger.error("fid_input_iscd_2 is required. (e.g. '99999')")
        raise ValueError("fid_input_iscd_2 is required. (e.g. '99999')")
    if not fid_mrkt_cls_code:
        logger.error("fid_mrkt_cls_code is required. (e.g. 'A')")
        raise ValueError("fid_mrkt_cls_code is required. (e.g. 'A')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()

    tr_id = "FHPST04320000"

    params = {
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_ISCD_2": fid_input_iscd_2,
        "FID_MRKT_CLS_CODE": fid_mrkt_cls_code,
        "FID_VOL_CNT": fid_vol_cnt,
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                # output1은 단일 객체, output2는 배열일 수 있음
                if isinstance(output_data, list):
                    current_data1 = pd.DataFrame(output_data)
                else:
                    # 단일 객체인 경우 리스트로 감싸서 DataFrame 생성
                    current_data1 = pd.DataFrame([output_data])

                if dataframe1 is not None:
                    dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
                else:
                    dataframe1 = current_data1
            else:
                if dataframe1 is None:
                    dataframe1 = pd.DataFrame()
        else:
            if dataframe1 is None:
                dataframe1 = pd.DataFrame()
        # output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                # output1은 단일 객체, output2는 배열일 수 있음
                if isinstance(output_data, list):
                    current_data2 = pd.DataFrame(output_data)
                else:
                    # 단일 객체인 경우 리스트로 감싸서 DataFrame 생성
                    current_data2 = pd.DataFrame([output_data])

                if dataframe2 is not None:
                    dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
                else:
                    dataframe2 = current_data2
            else:
                if dataframe2 is None:
                    dataframe2 = pd.DataFrame()
        else:
            if dataframe2 is None:
                dataframe2 = pd.DataFrame()
        tr_cont = res.getHeader().tr_cont

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return frgnmem_trade_trend(
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_input_iscd_2,
                fid_mrkt_cls_code,
                fid_vol_cnt,
                "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 순위분석 > HTS조회상위20종목[국내주식-214]
##############################################################################################

def hts_top_view(
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    HTS조회상위20종목[국내주식-214]
    HTS조회상위20종목 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        tr_cont (str): 연속 거래 여부 ("공백": 초기 조회, "N": 다음 데이터 조회)
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: HTS조회상위20종목 데이터
        
    Example:
        >>> df = hts_top_view(tr_cont="", dataframe=None, depth=0, max_depth=10)
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/hts-top-view"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "HHMCM000100C0"

    # Request Query Parameter가 없으므로 빈 딕셔너리로 유지
    params = {}

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
        if hasattr(res.getBody(), 'output1'):
            current_data = pd.DataFrame(res.getBody().output1)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 다음 페이지 호출 여부 결정
        tr_cont = res.getHeader().tr_cont
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return hts_top_view(
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 호출 실패 시 에러 로그 출력
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 투자계좌자산현황조회[v1_국내주식-048]
##############################################################################################

def inquire_account_balance(
        cano: str,  # [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 19 or 21)
        inqr_dvsn_1: str = "",  # 조회구분1
        bspr_bf_dt_aply_yn: str = ""  # 기준가이전일자적용여부
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    투자계좌자산현황조회 API입니다.

    output1은 한국투자 HTS(eFriend Plus) > [0891] 계좌 자산비중(결제기준) 화면 아래 테이블의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 19 or 21)
        inqr_dvsn_1 (str): 조회구분1
        bspr_bf_dt_aply_yn (str): 기준가이전일자적용여부
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터프레임, output2 데이터프레임)
        
    Example:
        >>> df1, df2 = inquire_account_balance("12345678", "21")
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/trading/inquire-account-balance"

    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '19' or '21')")

    tr_id = "CTRP6548R"  # 투자계좌자산현황조회

    params = {
        "CANO": cano,  # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "INQR_DVSN_1": inqr_dvsn_1,  # 조회구분1
        "BSPR_BF_DT_APLY_YN": bspr_bf_dt_aply_yn  # 기준가이전일자적용여부
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        # output1 - array 타입
        df1 = pd.DataFrame(res.getBody().output1)

        # output2 - object 타입 (단일 객체를 DataFrame으로 변환)
        df2 = pd.DataFrame([res.getBody().output2])

        logging.info("Data fetch complete.")
        return df1, df2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 주식현재가 호가/예상체결[v1_국내주식-011]
##############################################################################################

def inquire_asking_price_exp_ccn(
        env_dv: str,  # 실전모의구분 (real:실전, demo:모의)
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드 (J:KRX, NX:NXT, UN:통합)
        fid_input_iscd: str  # 입력 종목코드 (123456)
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    주식현재가 호가 예상체결 API입니다. 매수 매도 호가를 확인하실 수 있습니다. 실시간 데이터를 원하신다면 웹소켓 API를 활용하세요.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 123456)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (호가정보, 예상체결정보) 데이터
        
    Example:
        >>> result1, result2 = inquire_asking_price_exp_ccn(env_dv="real", fid_cond_mrkt_div_code="J", fid_input_iscd="005930")
        >>> print(result1)  # 호가정보
        >>> print(result2)  # 예상체결정보
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn"

    # 필수 파라미터 검증
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:KRX, NX:NXT, UN:통합')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '123456')")

    # TR_ID 설정
    if env_dv == "real":
        tr_id = "FHKST01010200"
    elif env_dv == "demo":
        tr_id = "FHKST01010200"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,  # 조건 시장 분류 코드
        "FID_INPUT_ISCD": fid_input_iscd  # 입력 종목코드
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        # output1 (object) -> 호가정보
        output1_data = pd.DataFrame([res.getBody().output1])

        # output2 (array) -> 예상체결정보
        output2_data = pd.DataFrame([res.getBody().output2])

        return output1_data, output2_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 주식잔고조회[v1_국내주식-006]
##############################################################################################

def inquire_balance(
        env_dv: str,  # 실전모의구분
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        afhr_flpr_yn: str,  # 시간외단일가·거래소여부
        inqr_dvsn: str,  # 조회구분
        unpr_dvsn: str,  # 단가구분
        fund_sttl_icld_yn: str,  # 펀드결제분포함여부
        fncg_amt_auto_rdpt_yn: str,  # 융자금액자동상환여부
        prcs_dvsn: str,  # 처리구분
        FK100: str = "",  # 연속조회검색조건100
        NK100: str = "",  # 연속조회키100
        tr_cont: str = "",  # 연속거래여부
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
        depth: int = 0,  # 내부 재귀깊이 (자동관리)
        max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    주식 잔고조회 API입니다. 
    실전계좌의 경우, 한 번의 호출에 최대 50건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다. 
    모의계좌의 경우, 한 번의 호출에 최대 20건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다. 

    * 당일 전량매도한 잔고도 보유수량 0으로 보여질 수 있으나, 해당 보유수량 0인 잔고는 최종 D-2일 이후에는 잔고에서 사라집니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        cano (str): [필수] 종합계좌번호 (ex. 계좌번호 체계(8-2)의 앞 8자리)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 계좌번호 체계(8-2)의 뒤 2자리)
        afhr_flpr_yn (str): [필수] 시간외단일가·거래소여부 (ex. N:기본값, Y:시간외단일가, X:NXT)
        inqr_dvsn (str): [필수] 조회구분 (ex. 01 – 대출일별 | 02 – 종목별)
        unpr_dvsn (str): [필수] 단가구분 (ex. 01)
        fund_sttl_icld_yn (str): [필수] 펀드결제분포함여부 (ex. N, Y)
        fncg_amt_auto_rdpt_yn (str): [필수] 융자금액자동상환여부 (ex. N)
        prcs_dvsn (str): [필수] 처리구분 (ex. 00: 전일매매포함, 01:전일매매미포함)
        FK100 (str): 연속조회검색조건100
        NK100 (str): 연속조회키100
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 주식잔고조회 데이터 (output1, output2)
        
    Example:
        >>> df1, df2 = inquire_balance(env_dv="real", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, afhr_flpr_yn="N", inqr_dvsn="01", unpr_dvsn="01", fund_sttl_icld_yn="N", fncg_amt_auto_rdpt_yn="N", prcs_dvsn="00")
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/trading/inquire-balance"

    # 필수 파라미터 검증
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")

    if cano == "":
        raise ValueError("cano is required (e.g. '계좌번호 체계(8-2)의 앞 8자리')")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '계좌번호 체계(8-2)의 뒤 2자리')")

    if afhr_flpr_yn == "":
        raise ValueError("afhr_flpr_yn is required (e.g. 'N:기본값, Y:시간외단일가, X:NXT')")

    if inqr_dvsn == "":
        raise ValueError("inqr_dvsn is required (e.g. '01 – 대출일별 | 02 – 종목별')")

    if unpr_dvsn == "":
        raise ValueError("unpr_dvsn is required (e.g. '01')")

    if fund_sttl_icld_yn == "":
        raise ValueError("fund_sttl_icld_yn is required (e.g. 'N, Y')")

    if fncg_amt_auto_rdpt_yn == "":
        raise ValueError("fncg_amt_auto_rdpt_yn is required (e.g. 'N')")

    if prcs_dvsn == "":
        raise ValueError("prcs_dvsn is required (e.g. '00: 전일매매포함, 01:전일매매미포함')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    # tr_id 설정
    if env_dv == "real":
        tr_id = "TTTC8434R"
    elif env_dv == "demo":
        tr_id = "VTTC8434R"
    else:
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "AFHR_FLPR_YN": afhr_flpr_yn,
        "OFL_YN": "",
        "INQR_DVSN": inqr_dvsn,
        "UNPR_DVSN": unpr_dvsn,
        "FUND_STTL_ICLD_YN": fund_sttl_icld_yn,
        "FNCG_AMT_AUTO_RDPT_YN": fncg_amt_auto_rdpt_yn,
        "PRCS_DVSN": prcs_dvsn,
        "CTX_AREA_FK100": FK100,
        "CTX_AREA_NK100": NK100
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        current_data1 = pd.DataFrame(res.getBody().output1)
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1

        # output2 처리
        current_data2 = pd.DataFrame(res.getBody().output2)
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2

        tr_cont = res.getHeader().tr_cont
        FK100 = res.getBody().ctx_area_fk100
        NK100 = res.getBody().ctx_area_nk100

        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_balance(
                env_dv, cano, acnt_prdt_cd, afhr_flpr_yn, inqr_dvsn, unpr_dvsn,
                fund_sttl_icld_yn, fncg_amt_auto_rdpt_yn, prcs_dvsn, FK100, NK100,
                "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 주식잔고조회_실현손익[v1_국내주식-041]
##############################################################################################

def inquire_balance_rlz_pl(
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        afhr_flpr_yn: str,  # 시간외단일가여부
        inqr_dvsn: str,  # 조회구분
        unpr_dvsn: str,  # 단가구분
        fund_sttl_icld_yn: str,  # 펀드결제포함여부
        fncg_amt_auto_rdpt_yn: str,  # 융자금액자동상환여부
        prcs_dvsn: str,  # PRCS_DVSN
        ofl_yn: str = "",  # 오프라인여부
        cost_icld_yn: str = "",  # 비용포함여부
        FK100: str = "",  # 연속조회검색조건100
        NK100: str = "",  # 연속조회키100
        tr_cont: str = "",  # 연속거래여부
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
        depth: int = 0,  # 내부 재귀깊이 (자동관리)
        max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    주식잔고조회_실현손익 API입니다.
    한국투자 HTS(eFriend Plus) [0800] 국내 체결기준잔고 화면을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    (참고: 포럼 - 공지사항 - 신규 API 추가 안내(주식잔고조회_실현손익 외 1건))
    
    Args:
        cano (str): [필수] 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        afhr_flpr_yn (str): [필수] 시간외단일가여부 (N:기본값, Y:시간외단일가)
        inqr_dvsn (str): [필수] 조회구분 (00:전체)
        unpr_dvsn (str): [필수] 단가구분 (01:기본값)
        fund_sttl_icld_yn (str): [필수] 펀드결제포함여부 (N:포함하지 않음, Y:포함)
        fncg_amt_auto_rdpt_yn (str): [필수] 융자금액자동상환여부 (N:기본값)
        prcs_dvsn (str): [필수] PRCS_DVSN (00:전일매매포함, 01:전일매매미포함)
        ofl_yn (str): 오프라인여부
        cost_icld_yn (str): 비용포함여부
        FK100 (str): 연속조회검색조건100
        NK100 (str): 연속조회키100
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 주식잔고조회_실현손익 데이터 (output1, output2)
        
    Example:
        >>> df1, df2 = inquire_balance_rlz_pl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, afhr_flpr_yn="N", inqr_dvsn="02", unpr_dvsn="01", fund_sttl_icld_yn="N", fncg_amt_auto_rdpt_yn="N", prcs_dvsn="01")
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/trading/inquire-balance-rlz-pl"

    # 필수 파라미터 검증
    if cano == "":
        raise ValueError("cano is required (e.g. '계좌번호 체계(8-2)의 앞 8자리')")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '계좌번호 체계(8-2)의 뒤 2자리')")

    if afhr_flpr_yn == "":
        raise ValueError("afhr_flpr_yn is required (e.g. 'N:기본값, Y:시간외단일가')")

    if inqr_dvsn == "":
        raise ValueError("inqr_dvsn is required (e.g. '00:전체')")

    if unpr_dvsn == "":
        raise ValueError("unpr_dvsn is required (e.g. '01:기본값')")

    if fund_sttl_icld_yn == "":
        raise ValueError("fund_sttl_icld_yn is required (e.g. 'N:포함하지 않음, Y:포함')")

    if fncg_amt_auto_rdpt_yn == "":
        raise ValueError("fncg_amt_auto_rdpt_yn is required (e.g. 'N:기본값')")

    if prcs_dvsn == "":
        raise ValueError("prcs_dvsn is required (e.g. '00:전일매매포함, 01:전일매매미포함')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "TTTC8494R"  # 주식잔고조회_실현손익

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "AFHR_FLPR_YN": afhr_flpr_yn,
        "OFL_YN": ofl_yn,
        "INQR_DVSN": inqr_dvsn,
        "UNPR_DVSN": unpr_dvsn,
        "FUND_STTL_ICLD_YN": fund_sttl_icld_yn,
        "FNCG_AMT_AUTO_RDPT_YN": fncg_amt_auto_rdpt_yn,
        "PRCS_DVSN": prcs_dvsn,
        "COST_ICLD_YN": cost_icld_yn,
        "CTX_AREA_FK100": FK100,
        "CTX_AREA_NK100": NK100
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        current_data1 = pd.DataFrame(res.getBody().output1)
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1

        # output2 처리  
        current_data2 = pd.DataFrame(res.getBody().output2)
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2

        tr_cont = res.getHeader().tr_cont
        FK100 = res.getBody().ctx_area_fk100
        NK100 = res.getBody().ctx_area_nk100

        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_balance_rlz_pl(
                cano, acnt_prdt_cd, afhr_flpr_yn, inqr_dvsn, unpr_dvsn,
                fund_sttl_icld_yn, fncg_amt_auto_rdpt_yn, prcs_dvsn,
                ofl_yn, cost_icld_yn, FK100, NK100, "N",
                dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 주식현재가 체결[v1_국내주식-009]
##############################################################################################

def inquire_ccnl(
        env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
        fid_input_iscd: str  # [필수] 입력 종목코드 (ex. 123456)
) -> pd.DataFrame:
    """
    국내현재가 체결 API 입니다. 종목의 체결 정보를 확인할 수 있습니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 123456)

    Returns:
        pd.DataFrame: 주식현재가 체결 데이터
        
    Example:
        >>> df = inquire_ccnl("real", "J", "005930")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-ccnl"

    # 필수 파라미터 검증
    if env_dv == "" or env_dv is None:
        raise ValueError("env_dv is required (e.g. 'real:실전', 'demo:모의')")

    if fid_cond_mrkt_div_code == "" or fid_cond_mrkt_div_code is None:
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:KRX', 'NX:NXT', 'UN:통합')")

    if fid_input_iscd == "" or fid_input_iscd is None:
        raise ValueError("fid_input_iscd is required (e.g. '123456')")

    # tr_id 설정
    if env_dv == "real":
        tr_id = "FHKST01010300"
    elif env_dv == "demo":
        tr_id = "FHKST01010300"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 신용매수가능조회[v1_국내주식-042]
##############################################################################################

def inquire_credit_psamount(
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        pdno: str,  # 종목코드
        ord_dvsn: str,  # 주문구분
        crdt_type: str,  # 신용유형
        cma_evlu_amt_icld_yn: str,  # CMA평가금액포함여부
        ovrs_icld_yn: str,  # 해외포함여부
        ord_unpr: str = ""  # 주문단가
) -> pd.DataFrame:
    """
    신용매수가능조회 API입니다.
    신용매수주문 시 주문가능수량과 금액을 확인하실 수 있습니다.
    
    Args:
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드
        pdno (str): [필수] 종목코드
        ord_dvsn (str): [필수] 주문구분 (ex. 00 : 지정가, 01 : 시장가, 02 : 조건부지정가, 03 : 최유리지정가, 04 : 최우선지정가, 05 : 장전 시간외, 06 : 장후 시간외, 07 : 시간외 단일가 등)
        crdt_type (str): [필수] 신용유형 (ex. 21 : 자기융자신규, 23 : 유통융자신규, 26 : 유통대주상환, 28 : 자기대주상환, 25 : 자기융자상환, 27 : 유통융자상환, 22 : 유통대주신규, 24 : 자기대주신규)
        cma_evlu_amt_icld_yn (str): [필수] CMA평가금액포함여부
        ovrs_icld_yn (str): [필수] 해외포함여부
        ord_unpr (str): 주문단가 (ex. 1주당 가격. 장전/장후 시간외, 시장가의 경우 "0" 입력 권고)

    Returns:
        pd.DataFrame: 신용매수가능조회 데이터
        
    Example:
        >>> df = inquire_credit_psamount(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, pdno="005930", ord_dvsn="00", crdt_type="21", cma_evlu_amt_icld_yn="N", ovrs_icld_yn="N")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/trading/inquire-credit-psamount"

    # 필수 파라미터 검증
    if cano == "" or cano is None:
        raise ValueError("cano is required")

    if acnt_prdt_cd == "" or acnt_prdt_cd is None:
        raise ValueError("acnt_prdt_cd is required")

    if pdno == "" or pdno is None:
        raise ValueError("pdno is required")

    if ord_dvsn == "" or ord_dvsn is None:
        raise ValueError(
            "ord_dvsn is required (e.g. '00 : 지정가, 01 : 시장가, 02 : 조건부지정가, 03 : 최유리지정가, 04 : 최우선지정가, 05 : 장전 시간외, 06 : 장후 시간외, 07 : 시간외 단일가 등')")

    if crdt_type == "" or crdt_type is None:
        raise ValueError(
            "crdt_type is required (e.g. '21 : 자기융자신규, 23 : 유통융자신규, 26 : 유통대주상환, 28 : 자기대주상환, 25 : 자기융자상환, 27 : 유통융자상환, 22 : 유통대주신규, 24 : 자기대주신규')")

    if cma_evlu_amt_icld_yn == "" or cma_evlu_amt_icld_yn is None:
        raise ValueError("cma_evlu_amt_icld_yn is required")

    if ovrs_icld_yn == "" or ovrs_icld_yn is None:
        raise ValueError("ovrs_icld_yn is required")

    tr_id = "TTTC8909R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "ORD_DVSN": ord_dvsn,
        "CRDT_TYPE": crdt_type,
        "CMA_EVLU_AMT_ICLD_YN": cma_evlu_amt_icld_yn,
        "OVRS_ICLD_YN": ovrs_icld_yn,
        "ORD_UNPR": ord_unpr
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output, index=[0])
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 주식일별주문체결조회[v1_국내주식-005]
##############################################################################################

def inquire_daily_ccld(
        env_dv: str,  # [필수] 실전모의구분 (real:실전, demo:모의)
        pd_dv: str,  # [필수] 3개월이전이내구분 (before:이전, inner:이내)
        cano: str,  # [필수] 종합계좌번호
        acnt_prdt_cd: str,  # [필수] 계좌상품코드
        inqr_strt_dt: str,  # [필수] 조회시작일자
        inqr_end_dt: str,  # [필수] 조회종료일자
        sll_buy_dvsn_cd: str,  # [필수] 매도매수구분코드 (00 : 전체 / 01 : 매도 / 02 : 매수)
        ccld_dvsn: str,  # [필수] 체결구분 (00 전체 / 01 체결 / 02 미체결)
        inqr_dvsn: str,  # [필수] 조회구분 (00 역순 / 01 정순)
        inqr_dvsn_3: str,  # [필수] 조회구분3 (00 전체 / 01 현금 / 02 신용 / 03 담보 / 04 대주 / 05 대여 / 06 자기융자신규/상환 / 07 유통융자신규/상환)
        pdno: str = "",  # 상품번호
        ord_gno_brno: str = "",  # 주문채번지점번호
        odno: str = "",  # 주문번호 (주문시 한국투자증권 시스템에서 채번된 주문번호)
        inqr_dvsn_1: str = "",  # 조회구분1 (없음: 전체 / 1: ELW / 2: 프리보드)
        FK100: str = "",  # 연속조회검색조건100 (공란: 최초 조회 / 이전 조회 Output 사용)
        NK100: str = "",  # 연속조회키100 (공란: 최초 조회 / 이전 조회 Output 사용)
        tr_cont: str = "",  # 연속거래여부
        excg_id_dvsn_cd: Optional[str] = "KRX",  # 거래소ID구분코드 (KRX / NXT / SOR / ALL)
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        depth: int = 0,  # 내부 재귀깊이 (자동관리)
        max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    주식일별주문체결조회 API입니다. 
    실전계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다. 
    모의계좌의 경우, 한 번의 호출에 최대 15건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다. 

    * 다만, 3개월 이전 체결내역 조회(CTSC9115R) 의 경우, 
    장중에는 많은 거래량으로 인해 순간적으로 DB가 밀렸거나 응답을 늦게 받거나 하는 등의 이슈가 있을 수 있어
    ① 가급적 장 종료 이후(15:30 이후) 조회하시고 
    ② 조회기간(INQR_STRT_DT와 INQR_END_DT 사이의 간격)을 보다 짧게 해서 조회하는 것을
    권유드립니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        pd_dv (str): [필수] 3개월이전이내구분 (ex. before:이전, inner:이내)
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드
        inqr_strt_dt (str): [필수] 조회시작일자
        inqr_end_dt (str): [필수] 조회종료일자
        sll_buy_dvsn_cd (str): [필수] 매도매수구분코드 (ex. 00 : 전체 / 01 : 매도 / 02 : 매수)
        pdno (str): 상품번호
        ccld_dvsn (str): [필수] 체결구분 (ex. 00 전체 / 01 체결 / 02 미체결)
        inqr_dvsn (str): [필수] 조회구분 (ex. 00 역순 / 01 정순)
        inqr_dvsn_3 (str): [필수] 조회구분3 (ex. 00 전체 / 01 현금 / 02 신용 / 03 담보 / 04 대주 / 05 대여 / 06 자기융자신규/상환 / 07 유통융자신규/상환)
        ord_gno_brno (str): 주문채번지점번호
        odno (str): 주문번호 (ex. 주문시 한국투자증권 시스템에서 채번된 주문번호)
        inqr_dvsn_1 (str): 조회구분1 (ex. 없음: 전체 / 1: ELW / 2: 프리보드)
        FK100 (str): 연속조회검색조건100 (ex. 공란: 최초 조회 / 이전 조회 Output 사용)
        NK100 (str): 연속조회키100 (ex. 공란: 최초 조회 / 이전 조회 Output 사용)
        tr_cont (str): 연속거래여부
        excg_id_dvsn_cd (Optional[str]): 거래소ID구분코드 (ex. KRX / NXT / SOR / ALL)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터프레임, output2 데이터프레임)
        
    Example:
        >>> df1, df2 = inquire_daily_ccld(
        ...     env_dv="real", pd_dv="inner", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod,
        ...     inqr_strt_dt="20220810", inqr_end_dt="20220810", 
        ...     sll_buy_dvsn_cd="00", pdno="005930", ccld_dvsn="00", 
        ...     inqr_dvsn="00", inqr_dvsn_3="00"
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/trading/inquire-daily-ccld"

    # 필수 파라미터 검증
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real:실전', 'demo:모의')")

    if pd_dv == "":
        raise ValueError("pd_dv is required (e.g. 'before:이전', 'inner:이내')")

    if cano == "":
        raise ValueError("cano is required")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required")

    if inqr_strt_dt == "":
        raise ValueError("inqr_strt_dt is required")

    if inqr_end_dt == "":
        raise ValueError("inqr_end_dt is required")

    if sll_buy_dvsn_cd == "":
        raise ValueError("sll_buy_dvsn_cd is required (e.g. '00 : 전체 / 01 : 매도 / 02 : 매수')")

    if ccld_dvsn == "":
        raise ValueError("ccld_dvsn is required (e.g. '00 전체 / 01 체결 / 02 미체결')")

    if inqr_dvsn == "":
        raise ValueError("inqr_dvsn is required (e.g. '00 역순 / 01 정순')")

    if inqr_dvsn_3 == "":
        raise ValueError(
            "inqr_dvsn_3 is required (e.g. '00 전체 / 01 현금 / 02 신용 / 03 담보 / 04 대주 / 05 대여 / 06 자기융자신규/상환 / 07 유통융자신규/상환')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    # tr_id 설정
    if env_dv == "real":
        if pd_dv == "before":
            tr_id = "CTSC9215R"
        elif pd_dv == "inner":
            tr_id = "TTTC0081R"
        else:
            raise ValueError("pd_dv can only be 'before' or 'inner'")
    elif env_dv == "demo":
        if pd_dv == "before":
            tr_id = "VTSC9215R"
        elif pd_dv == "inner":
            tr_id = "VTTC0081R"
        else:
            raise ValueError("pd_dv can only be 'before' or 'inner'")
    else:
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "INQR_STRT_DT": inqr_strt_dt,
        "INQR_END_DT": inqr_end_dt,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "PDNO": pdno,
        "CCLD_DVSN": ccld_dvsn,
        "INQR_DVSN": inqr_dvsn,
        "INQR_DVSN_3": inqr_dvsn_3,
        "ORD_GNO_BRNO": ord_gno_brno,
        "ODNO": odno,
        "INQR_DVSN_1": inqr_dvsn_1,
        "CTX_AREA_FK100": FK100,
        "CTX_AREA_NK100": NK100
    }

    if excg_id_dvsn_cd is not None:
        params["EXCG_ID_DVSN_CD"] = excg_id_dvsn_cd

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # output1 (array) 처리
        current_data1 = pd.DataFrame(res.getBody().output1)
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1

        # output2 (object) 처리
        current_data2 = pd.DataFrame([res.getBody().output2])
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2

        tr_cont = res.getHeader().tr_cont
        FK100 = res.getBody().ctx_area_fk100
        NK100 = res.getBody().ctx_area_nk100

        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_daily_ccld(
                env_dv, pd_dv, cano, acnt_prdt_cd, inqr_strt_dt, inqr_end_dt,
                sll_buy_dvsn_cd, pdno, ccld_dvsn, inqr_dvsn, inqr_dvsn_3,
                ord_gno_brno, odno, inqr_dvsn_1, FK100, NK100, "N",
                excg_id_dvsn_cd, dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 국내주식업종기간별시세(일_주_월_년)[v1_국내주식-021]
##############################################################################################

def inquire_daily_indexchartprice(
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_input_iscd: str,  # 업종 상세코드
        fid_input_date_1: str,  # 조회 시작일자
        fid_input_date_2: str,  # 조회 종료일자
        fid_period_div_code: str,  # 기간분류코드
        env_dv: str = "real",  # [추가] 실전모의구분 (real:실전, demo:모의)
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        tr_cont: str = "",
        depth: int = 0,
        max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 업종/기타 
    국내주식업종기간별시세(일_주_월_년)[v1_국내주식-021]
    국내주식업종기간별시세(일_주_월_년) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 업종 : U
        fid_input_iscd (str): 0001 : 종합 0002 : 대형주 ... 포탈 (FAQ : 종목정보 다운로드(국내) - 업종코드 참조)
        fid_input_date_1 (str): 조회 시작일자 (ex. 20220501)
        fid_input_date_2 (str): 조회 종료일자 (ex. 20220530)
        fid_period_div_code (str): D:일봉 W:주봉, M:월봉, Y:년봉
        env_dv (str): [추가] 실전모의구분 (real:실전, demo:모의, 기본값: 'real')
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 국내주식업종기간별시세(일_주_월_년) 데이터
        
    Example:
        >>> df1, df2 = inquire_daily_indexchartprice(
        ...     fid_cond_mrkt_div_code="U",
        ...     fid_input_iscd="0001",
        ...     fid_input_date_1="20220501",
        ...     fid_input_date_2="20220530",
        ...     fid_period_div_code="D",
        ...     env_dv="real"  # 실전투자
        ... )
        >>> df1, df2 = inquire_daily_indexchartprice(
        ...     fid_cond_mrkt_div_code="U",
        ...     fid_input_iscd="0001",
        ...     fid_input_date_1="20220501",
        ...     fid_input_date_2="20220530",
        ...     fid_period_div_code="D",
        ...     env_dv="demo"  # 모의투자
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-daily-indexchartprice"
    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'U')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'U')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0001')")
        raise ValueError("fid_input_iscd is required. (e.g. '0001')")

    if not fid_input_date_1:
        logger.error("fid_input_date_1 is required. (e.g. '20220501')")
        raise ValueError("fid_input_date_1 is required. (e.g. '20220501')")

    if not fid_input_date_2:
        logger.error("fid_input_date_2 is required. (e.g. '20220530')")
        raise ValueError("fid_input_date_2 is required. (e.g. '20220530')")

    if not fid_period_div_code:
        logger.error("fid_period_div_code is required. (e.g. 'D')")
        raise ValueError("fid_period_div_code is required. (e.g. 'D')")

    # env_dv 파라미터 검증 (모의투자 지원 로직)
    if env_dv not in ["real", "demo"]:
        logger.error("env_dv must be 'real' or 'demo'")
        raise ValueError("env_dv must be 'real' or 'demo'")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()

    # API 호출 URL 설정

    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real" or env_dv == "demo":
        tr_id = "FHKUP03500100"  # 실전투자용 TR ID
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_DATE_2": fid_input_date_2,
        "FID_PERIOD_DIV_CODE": fid_period_div_code,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                current_data1 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe1 = pd.concat([dataframe1, current_data1],
                                       ignore_index=True) if dataframe1 is not None else current_data1
            else:
                dataframe1 = dataframe1 if dataframe1 is not None else pd.DataFrame()
        else:
            dataframe1 = dataframe1 if dataframe1 is not None else pd.DataFrame()

        # output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                current_data2 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe2 = pd.concat([dataframe2, current_data2],
                                       ignore_index=True) if dataframe2 is not None else current_data2
            else:
                dataframe2 = dataframe2 if dataframe2 is not None else pd.DataFrame()
        else:
            dataframe2 = dataframe2 if dataframe2 is not None else pd.DataFrame()

        tr_cont = res.getHeader().tr_cont

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_daily_indexchartprice(
                fid_cond_mrkt_div_code,
                fid_input_iscd,
                fid_input_date_1,
                fid_input_date_2,
                fid_period_div_code,
                env_dv,  # env_dv 파라미터 추가
                dataframe1,
                dataframe2,
                "N", depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 국내주식기간별시세(일/주/월/년)[v1_국내주식-016]
##############################################################################################

def inquire_daily_itemchartprice(
        env_dv: str,  # 실전모의구분
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_input_date_1: str,  # 입력 날짜 1
        fid_input_date_2: str,  # 입력 날짜 2
        fid_period_div_code: str,  # 기간분류코드
        fid_org_adj_prc: str  # 수정주가 원주가 가격 여부
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    국내주식기간별시세(일/주/월/년) API입니다.
    실전계좌/모의계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능합니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 종목코드 (ex 005930 삼성전자))
        fid_input_date_1 (str): [필수] 입력 날짜 1 (ex. 조회 시작일자)
        fid_input_date_2 (str): [필수] 입력 날짜 2 (ex. 조회 종료일자 (최대 100개))
        fid_period_div_code (str): [필수] 기간분류코드 (ex. D:일봉 W:주봉, M:월봉, Y:년봉)
        fid_org_adj_prc (str): [필수] 수정주가 원주가 가격 여부 (ex. 0:수정주가 1:원주가)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> df1, df2 = inquire_daily_itemchartprice("real", "J", "005930", "20220101", "20220809", "D", "1")
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"

    # 필수 파라미터 검증
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:KRX, NX:NXT, UN:통합')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '종목코드 (ex 005930 삼성전자)')")

    if fid_input_date_1 == "":
        raise ValueError("fid_input_date_1 is required (e.g. '조회 시작일자')")

    if fid_input_date_2 == "":
        raise ValueError("fid_input_date_2 is required (e.g. '조회 종료일자 (최대 100개)')")

    if fid_period_div_code == "":
        raise ValueError("fid_period_div_code is required (e.g. 'D:일봉 W:주봉, M:월봉, Y:년봉')")

    if fid_org_adj_prc == "":
        raise ValueError("fid_org_adj_prc is required (e.g. '0:수정주가 1:원주가')")

    # TR_ID 설정
    if env_dv == "real":
        tr_id = "FHKST03010100"
    elif env_dv == "demo":
        tr_id = "FHKST03010100"
    else:
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_DATE_2": fid_input_date_2,
        "FID_PERIOD_DIV_CODE": fid_period_div_code,
        "FID_ORG_ADJ_PRC": fid_org_adj_prc
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        # output1 처리 (object 타입이므로 DataFrame)
        output1_data = pd.DataFrame([res.getBody().output1])

        # output2 처리 (array 타입이므로 DataFrame)
        output2_data = pd.DataFrame(res.getBody().output2)

        return (output1_data, output2_data)
    else:
        res.printError(url=api_url)
        return (pd.DataFrame(), pd.DataFrame())


##############################################################################################
# [국내주식] 기본시세 > 주식현재가 시간외일자별주가[v1_국내주식-026]
##############################################################################################

def inquire_daily_overtimeprice(
        env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J)
        fid_input_iscd: str  # [필수] 입력 종목코드
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    주식현재가 시간외일자별주가 API입니다.  (최근일 30건만 조회 가능)
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J)
        fid_input_iscd (str): [필수] 입력 종목코드

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 데이터프레임 튜플
        
    Example:
        >>> result1, result2 = inquire_daily_overtimeprice("real", "J", "005930")
        >>> print(result1)
        >>> print(result2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-daily-overtimeprice"

    # 필수 파라미터 검증
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required")

    # TR_ID 설정
    if env_dv == "real":
        tr_id = "FHPST02320000"
    elif env_dv == "demo":
        tr_id = "FHPST02320000"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        # output1 (object) -> DataFrame
        output1_data = pd.DataFrame(res.getBody().output1, index=[0])

        # output2 (array) -> DataFrame  
        output2_data = pd.DataFrame(res.getBody().output2)

        return output1_data, output2_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 주식현재가 일자별[v1_국내주식-010]
##############################################################################################

def inquire_daily_price(
        env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
        fid_input_iscd: str,  # [필수] 입력 종목코드 (ex. 종목코드 (ex 005930 삼성전자))
        fid_period_div_code: str,  # [필수] 기간 분류 코드 (ex. D:(일)최근 30거래일, W:(주)최근 30주, M:(월)최근 30개월)
        fid_org_adj_prc: str
        # [필수] 수정주가 원주가 가격 (ex. 0:수정주가미반영, 1:수정주가반영, *수정주가는 액면분할/액면병합 등 권리 발생 시 과거 시세를 현재 주가에 맞게 보정한 가격)
) -> pd.DataFrame:
    """
    주식현재가 일자별 API입니다. 일/주/월별 주가를 확인할 수 있으며 최근 30일(주,별)로 제한되어 있습니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)  
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 종목코드 (ex 005930 삼성전자))
        fid_period_div_code (str): [필수] 기간 분류 코드 (ex. D:(일)최근 30거래일, W:(주)최근 30주, M:(월)최근 30개월)
        fid_org_adj_prc (str): [필수] 수정주가 원주가 가격 (ex. 0:수정주가미반영, 1:수정주가반영, *수정주가는 액면분할/액면병합 등 권리 발생 시 과거 시세를 현재 주가에 맞게 보정한 가격)

    Returns:
        pd.DataFrame: 주식현재가 일자별 데이터
        
    Raises:
        ValueError: 필수 파라미터가 누락된 경우
        
    Example:
        >>> df = inquire_daily_price("real", "J", "005930", "D", "1")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-daily-price"

    # 필수 파라미터 검증
    if env_dv == "" or env_dv is None:
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")

    if fid_cond_mrkt_div_code == "" or fid_cond_mrkt_div_code is None:
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:KRX, NX:NXT, UN:통합')")

    if fid_input_iscd == "" or fid_input_iscd is None:
        raise ValueError("fid_input_iscd is required (e.g. '종목코드 (ex 005930 삼성전자)')")

    if fid_period_div_code == "" or fid_period_div_code is None:
        raise ValueError("fid_period_div_code is required (e.g. 'D:(일)최근 30거래일, W:(주)최근 30주, M:(월)최근 30개월')")

    if fid_org_adj_prc == "" or fid_org_adj_prc is None:
        raise ValueError(
            "fid_org_adj_prc is required (e.g. '0:수정주가미반영, 1:수정주가반영, *수정주가는 액면분할/액면병합 등 권리 발생 시 과거 시세를 현재 주가에 맞게 보정한 가격')")

    # tr_id 설정 (실전/모의 모두 동일)
    if env_dv == "real":
        tr_id = "FHKST01010400"
    elif env_dv == "demo":
        tr_id = "FHKST01010400"
    else:
        raise ValueError("env_dv can only be real or demo")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_PERIOD_DIV_CODE": fid_period_div_code,
        "FID_ORG_ADJ_PRC": fid_org_adj_prc
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        # output은 array 자료형이므로 DataFrame으로 변환
        current_data = pd.DataFrame(res.getBody().output)
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 종목별일별매수매도체결량 [v1_국내주식-056]
##############################################################################################

def inquire_daily_trade_volume(
        fid_cond_mrkt_div_code: str,  # FID 조건 시장 분류 코드
        fid_input_iscd: str,  # FID 입력 종목코드
        fid_period_div_code: str,  # FID 기간 분류 코드
        fid_input_date_1: str = "",  # FID 입력 날짜1
        fid_input_date_2: str = ""  # FID 입력 날짜2
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    종목별일별매수매도체결량 API입니다. 실전계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능합니다.
    국내주식 종목의 일별 매수체결량, 매도체결량 데이터를 확인할 수 있습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] FID 조건 시장 분류 코드 (J:KRX, NX:NXT, UN:통합)
        fid_input_iscd (str): [필수] FID 입력 종목코드 (ex. 123456)
        fid_period_div_code (str): [필수] FID 기간 분류 코드 (ex. D)
        fid_input_date_1 (str): FID 입력 날짜1
        fid_input_date_2 (str): FID 입력 날짜2

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터프레임, output2 데이터프레임)
        
    Example:
        >>> df1, df2 = inquire_daily_trade_volume("J", "005930", "D")
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-daily-trade-volume"

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '005930')")

    if fid_period_div_code == "":
        raise ValueError("fid_period_div_code is required (e.g. 'D')")

    tr_id = "FHKST03010800"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_PERIOD_DIV_CODE": fid_period_div_code,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_DATE_2": fid_input_date_2
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        # output1 (object) - 단일 레코드
        output1_data = pd.DataFrame([res.getBody().output1])

        # output2 (array) - 배열 데이터
        output2_data = pd.DataFrame(res.getBody().output2)

        return output1_data, output2_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] ELW시세 > ELW 현재가 시세 [v1_국내주식-014]
##############################################################################################

def inquire_elw_price(
        fid_cond_mrkt_div_code: str,  # FID 조건 시장 분류 코드
        fid_input_iscd: str,  # FID 입력 종목코드
        env_dv: str = "real",  # 실전모의구분 (real:실전, demo:모의)
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 현재가 시세[v1_국내주식-014]
    ELW 현재가 시세 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): FID 조건 시장 분류 코드 (예: 'W')
        fid_input_iscd (str): FID 입력 종목코드 (예: '000660')
        env_dv (str): [추가] 실전모의구분 (real:실전, demo:모의, 기본값: 'real')
        tr_cont (str): 연속 거래 여부 (기본값: '')
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (기본값: None)
        depth (int): 현재 재귀 깊이 (기본값: 0)
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 현재가 시세 데이터
        
    Example:
        >>> df = inquire_elw_price('W', '000660', env_dv='real')  # 실전투자
        >>> df = inquire_elw_price('W', '000660', env_dv='demo')  # 모의투자
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-elw-price"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '000660')")
        raise ValueError("fid_input_iscd is required. (e.g. '000660')")

    # env_dv 파라미터 검증 (모의투자 지원 로직)
    if env_dv not in ["real", "demo"]:
        logger.error("env_dv must be 'real' or 'demo'")
        raise ValueError("env_dv must be 'real' or 'demo'")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # API 호출 URL 설정

    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real" or env_dv == "demo":
        tr_id = "FHKEW15010000"  # 실전투자용 TR ID

    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    # 요청 파라미터 설정
    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    # API 응답 처리
    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_elw_price(
                fid_cond_mrkt_div_code,
                fid_input_iscd,
                env_dv,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 업종/기타 > 국내업종 구분별전체시세[v1_국내주식-066]
##############################################################################################

def inquire_index_category_price(
        fid_cond_mrkt_div_code: str,  # FID 조건 시장 분류 코드
        fid_input_iscd: str,  # FID 입력 종목코드
        fid_cond_scr_div_code: str,  # FID 조건 화면 분류 코드
        fid_mrkt_cls_code: str,  # FID 시장 구분 코드
        fid_blng_cls_code: str,  # FID 소속 구분 코드
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        tr_cont: str = "",
        depth: int = 0,
        max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 업종/기타 
    국내업종 구분별전체시세[v1_국내주식-066]
    국내업종 구분별전체시세 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 시장구분코드 (업종 U)
        fid_input_iscd (str): 코스피(0001), 코스닥(1001), 코스피200(2001) ... 포탈 (FAQ : 종목정보 다운로드(국내) - 업종코드 참조)
        fid_cond_scr_div_code (str): Unique key( 20214 )
        fid_mrkt_cls_code (str): 시장구분코드(K:거래소, Q:코스닥, K2:코스피200)
        fid_blng_cls_code (str): 시장구분코드에 따라 아래와 같이 입력 시장구분코드(K:거래소) 0:전업종, 1:기타구분, 2:자본금구분 3:상업별구분 시장구분코드(Q:코스닥) 0:전업종, 1:기타구분, 2:벤처구분 3:일반구분 시장구분코드(K2:코스닥) 0:전업종
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 국내업종 구분별전체시세 데이터
        
    Example:
        >>> df1, df2 = inquire_index_category_price(
        ...     fid_cond_mrkt_div_code='U',
        ...     fid_input_iscd='0001',
        ...     fid_cond_scr_div_code='20214',
        ...     fid_mrkt_cls_code='K',
        ...     fid_blng_cls_code='0'
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-index-category-price"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'U')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'U')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0001')")
        raise ValueError("fid_input_iscd is required. (e.g. '0001')")

    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20214')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20214')")

    if not fid_mrkt_cls_code:
        logger.error("fid_mrkt_cls_code is required. (e.g. 'K')")
        raise ValueError("fid_mrkt_cls_code is required. (e.g. 'K')")

    if not fid_blng_cls_code:
        logger.error("fid_blng_cls_code is required. (e.g. '0')")
        raise ValueError("fid_blng_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()

    tr_id = "FHPUP02140000"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_MRKT_CLS_CODE": fid_mrkt_cls_code,
        "FID_BLNG_CLS_CODE": fid_blng_cls_code,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                current_data1 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe1 = pd.concat([dataframe1, current_data1],
                                       ignore_index=True) if dataframe1 is not None else current_data1
            else:
                dataframe1 = dataframe1 if dataframe1 is not None else pd.DataFrame()

        # output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                current_data2 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe2 = pd.concat([dataframe2, current_data2],
                                       ignore_index=True) if dataframe2 is not None else current_data2
            else:
                dataframe2 = dataframe2 if dataframe2 is not None else pd.DataFrame()

        tr_cont = res.getHeader().tr_cont

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_index_category_price(
                fid_cond_mrkt_div_code,
                fid_input_iscd,
                fid_cond_scr_div_code,
                fid_mrkt_cls_code,
                fid_blng_cls_code,
                "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 업종/기타 > 국내업종 일자별지수 [v1_국내주식-065]
##############################################################################################

def inquire_index_daily_price(
        fid_period_div_code: str,  # FID 기간 분류 코드
        fid_cond_mrkt_div_code: str,  # FID 조건 시장 분류 코드
        fid_input_iscd: str,  # FID 입력 종목코드
        fid_input_date_1: str,  # FID 입력 날짜1
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        tr_cont: str = "",
        depth: int = 0,
        max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 업종/기타 
    국내업종 일자별지수[v1_국내주식-065]
    국내업종 일자별지수 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_period_div_code (str): 일/주/월 구분코드 ( D:일별 , W:주별, M:월별 )
        fid_cond_mrkt_div_code (str): 시장구분코드 (업종 U)
        fid_input_iscd (str): 코스피(0001), 코스닥(1001), 코스피200(2001) ... 포탈 (FAQ : 종목정보 다운로드(국내) - 업종코드 참조)
        fid_input_date_1 (str): 입력 날짜(ex. 20240223)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 국내업종 일자별지수 데이터
        
    Example:
        >>> df1, df2 = inquire_index_daily_price('D', 'U', '0001', '20240223')
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-index-daily-price"
    # 필수 파라미터 검증
    if not fid_period_div_code:
        logger.error("fid_period_div_code is required. (e.g. 'D')")
        raise ValueError("fid_period_div_code is required. (e.g. 'D')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'U')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'U')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0001')")
        raise ValueError("fid_input_iscd is required. (e.g. '0001')")

    if not fid_input_date_1:
        logger.error("fid_input_date_1 is required. (e.g. '20240223')")
        raise ValueError("fid_input_date_1 is required. (e.g. '20240223')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()

    tr_id = "FHPUP02120000"

    params = {
        "FID_PERIOD_DIV_CODE": fid_period_div_code,
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_DATE_1": fid_input_date_1,
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                current_data1 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe1 = pd.concat([dataframe1, current_data1],
                                       ignore_index=True) if dataframe1 is not None else current_data1
            else:
                dataframe1 = pd.DataFrame() if dataframe1 is None else dataframe1

        # output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                current_data2 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe2 = pd.concat([dataframe2, current_data2],
                                       ignore_index=True) if dataframe2 is not None else current_data2
            else:
                dataframe2 = pd.DataFrame() if dataframe2 is None else dataframe2

        tr_cont = res.getHeader().tr_cont

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_index_daily_price(
                fid_period_div_code,
                fid_cond_mrkt_div_code,
                fid_input_iscd,
                fid_input_date_1,
                "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 업종/기타 > 국내업종 현재지수 [v1_국내주식-063]
##############################################################################################

def inquire_index_price(
        fid_cond_mrkt_div_code: str,  # FID 조건 시장 분류 코드
        fid_input_iscd: str,  # FID 입력 종목코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 업종/기타 
    국내업종 현재지수[v1_국내주식-063]
    국내업종 현재지수 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 업종(U)
        fid_input_iscd (str): 코스피(0001), 코스닥(1001), 코스피200(2001) ... 포탈 (FAQ : 종목정보 다운로드(국내) - 업종코드 참조)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내업종 현재지수 데이터
        
    Example:
        >>> df = inquire_index_price("U", "0001")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-index-price"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'U')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'U')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0001')")
        raise ValueError("fid_input_iscd is required. (e.g. '0001')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # API 호출 URL 및 거래 ID 설정
    tr_id = "FHPUP02100000"

    # 요청 파라미터 설정
    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    # API 호출 성공 시 데이터 처리
    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        # 기존 데이터프레임과 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_index_price(
                fid_cond_mrkt_div_code,
                fid_input_iscd,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 호출 실패 시 에러 로그 출력
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 업종/기타 > 국내업종 시간별지수(초)[국내주식-064]
##############################################################################################

def inquire_index_tickprice(
        fid_input_iscd: str,  # 입력 종목코드
        fid_cond_mrkt_div_code: str,  # 시장 분류 코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 업종/기타 
    국내업종 시간별지수(초)[국내주식-064]
    국내업종 시간별지수(초) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_input_iscd (str): 0001:거래소, 1001:코스닥, 2001:코스피200, 3003:KSQ150
        fid_cond_mrkt_div_code (str): 시장구분코드 (업종 U)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내업종 시간별지수(초) 데이터
        
    Example:
        >>> df = inquire_index_tickprice('0001', 'U')
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-index-tickprice"
    # 필수 파라미터 검증
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0001')")
        raise ValueError("fid_input_iscd is required. (e.g. '0001')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'U')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'U')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHPUP02110100"

    params = {
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_index_tickprice(
                fid_input_iscd,
                fid_cond_mrkt_div_code,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 에러 처리
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 업종/기타 > 국내업종 시간별지수(분)[국내주식-119]
##############################################################################################

def inquire_index_timeprice(
        fid_input_hour_1: str,  # ?입력 시간1
        fid_input_iscd: str,  # 입력 종목코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 업종/기타 
    국내업종 시간별지수(분)[국내주식-119]
    국내업종 시간별지수(분) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_input_hour_1 (str): 초단위, 60(1분), 300(5분), 600(10분)
        fid_input_iscd (str): 0001:거래소, 1001:코스닥, 2001:코스피200, 3003:KSQ150
        fid_cond_mrkt_div_code (str): 시장구분코드 (업종 U)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내업종 시간별지수(분) 데이터
        
    Example:
        >>> df = inquire_index_timeprice("60", "0001", "U")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-index-timeprice"
    # 필수 파라미터 검증
    if not fid_input_hour_1:
        logger.error("fid_input_hour_1 is required. (e.g. '60')")
        raise ValueError("fid_input_hour_1 is required. (e.g. '60')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0001')")
        raise ValueError("fid_input_iscd is required. (e.g. '0001')")

    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'U')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'U')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHPUP02110200"

    params = {
        "FID_INPUT_HOUR_1": fid_input_hour_1,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_index_timeprice(
                fid_input_hour_1,
                fid_input_iscd,
                fid_cond_mrkt_div_code,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 주식현재가 투자자[v1_국내주식-012]
##############################################################################################

def inquire_investor(
        env_dv: str,  # [필수] 실전모의구분
        fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드
        fid_input_iscd: str  # [필수] 입력 종목코드
) -> pd.DataFrame:
    """
    주식현재가 투자자 API입니다. 개인, 외국인, 기관 등 투자 정보를 확인할 수 있습니다.

    [유의사항]
    - 외국인은 외국인(외국인투자등록 고유번호가 있는 경우)+기타 외국인을 지칭합니다.
    - 당일 데이터는 장 종료 후 제공됩니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 123456)

    Returns:
        pd.DataFrame: 주식현재가 투자자 데이터
        
    Example:
        >>> df = inquire_investor(env_dv="real", fid_cond_mrkt_div_code="J", fid_input_iscd="005930")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-investor"

    # 필수 파라미터 검증
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:KRX')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '123456')")

    # tr_id 설정
    if env_dv == "real":
        tr_id = "FHKST01010900"
    elif env_dv == "demo":
        tr_id = "FHKST01010900"
    else:
        raise ValueError("env_dv can only be real or demo")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        return pd.DataFrame(res.getBody().output)
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 시장별 투자자매매동향(일별) [국내주식-075]
##############################################################################################

def inquire_investor_daily_by_market(
        fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. U:업종)
        fid_input_iscd: str,  # [필수] 입력 종목코드 (ex. 0001)
        fid_input_date_1: str,  # [필수] 입력 날짜1 (ex. 20250701)
        fid_input_iscd_1: str,  # [필수] 입력 종목코드 (ex. KSP:코스피, KSQ:코스닥)
        fid_input_date_2: str,  # [필수] 입력 날짜1과 동일날짜 입력
        fid_input_iscd_2: str,  # [필수] 입력 종목코드 (ex. 업종분류코드)

) -> pd.DataFrame:
    """
    시장별 투자자매매동향(일별) API입니다.
    한국투자 HTS(eFriend Plus) > [0404] 시장별 일별동향 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. U:업종)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 0001)
        fid_input_date_1 (str): [필수] 입력 날짜1 (ex. 20250701)
        fid_input_iscd_1 (str): [필수] 입력 종목코드 (ex. KSP:코스피, KSQ:코스닥)
        fid_input_date_2 (str): [필수] 입력 날짜1과 동일날짜 입력
        fid_input_iscd_2 (str): [필수] 입력 종목코드 (ex. 업종분류코드)

    Returns:
        pd.DataFrame: 시장별 투자자매매동향(일별) 데이터
        
    Example:
        >>> df = inquire_investor_daily_by_market("U", "0001", "20250701", "KSP", "20250701", "0001")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-investor-daily-by-market"

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'U')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '0001')")

    if fid_input_date_1 == "":
        raise ValueError("fid_input_date_1 is required (e.g. '20250701')")

    if fid_input_iscd_1 == "":
        raise ValueError("fid_input_iscd_1 is required (e.g. 'KSP')")

    if fid_input_date_2 == "":
        raise ValueError("fid_input_date_2 is required (e.g. '20250701')")

    if fid_input_iscd_2 == "":
        raise ValueError("fid_input_iscd_2 is required (e.g. 업종분류코드')")

    tr_id = "FHPTJ04040000"  # 시장별 투자자매매동향(일별)

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,  # 조건 시장 분류 코드
        "FID_INPUT_ISCD": fid_input_iscd,  # 입력 종목코드
        "FID_INPUT_DATE_1": fid_input_date_1,  # 입력 날짜1
        "FID_INPUT_ISCD_1": fid_input_iscd_1,  # 입력 종목코드
        "FID_INPUT_DATE_2": fid_input_date_2,  # 입력 날짜2
        "FID_INPUT_ISCD_2": fid_input_iscd_2,  # 입력 종목코드
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 시장별 투자자매매동향(시세)[v1_국내주식-074]
##############################################################################################

def inquire_investor_time_by_market(
        fid_input_iscd: str,  # [필수] 시장구분
        fid_input_iscd_2: str  # [필수] 업종구분
) -> pd.DataFrame:
    """
    시장별 투자자매매동향(시세성) API입니다.
    한국투자 HTS(eFriend Plus) > [0403] 시장별 시간동향 의 상단 표 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_input_iscd (str): [필수] 시장구분
        fid_input_iscd_2 (str): [필수] 업종구분
        
    Returns:
        pd.DataFrame: 시장별 투자자매매동향 데이터
        
    Example:
        >>> df = inquire_investor_time_by_market(fid_input_iscd="999", fid_input_iscd_2="S001")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-investor-time-by-market"

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required")

    if fid_input_iscd_2 == "":
        raise ValueError("fid_input_iscd_2 is required")

    tr_id = "FHPTJ04030000"

    params = {
        "FID_INPUT_ISCD": fid_input_iscd,  # 시장구분
        "FID_INPUT_ISCD_2": fid_input_iscd_2  # 업종구분
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 주식현재가 회원사[v1_국내주식-013]
##############################################################################################

def inquire_member(
        env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J:KRX)
        fid_input_iscd: str,  # [필수] 입력 종목코드 (ex. 123456)
) -> pd.DataFrame:
    """
    주식 현재가 회원사 API입니다. 회원사의 투자 정보를 확인할 수 있습니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 123456)

    Returns:
        pd.DataFrame: 주식현재가 회원사 데이터
        
    Example:
        >>> df = inquire_member(env_dv="real", fid_cond_mrkt_div_code="J", fid_input_iscd="005930")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-member"

    # 필수 파라미터 검증
    if env_dv == "" or env_dv is None:
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")

    if fid_cond_mrkt_div_code == "" or fid_cond_mrkt_div_code is None:
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:KRX')")

    if fid_input_iscd == "" or fid_input_iscd is None:
        raise ValueError("fid_input_iscd is required (e.g. '123456')")

    # tr_id 설정
    if env_dv == "real":
        tr_id = "FHKST01010600"
    elif env_dv == "demo":
        tr_id = "FHKST01010600"
    else:
        raise ValueError("env_dv can only be real or demo")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame([res.getBody().output])
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 주식현재가 회원사 종목매매동향 [국내주식-197]
##############################################################################################

def inquire_member_daily(
        fid_cond_mrkt_div_code: str,  # [필수] 조건시장분류코드 (ex. 주식J)
        fid_input_iscd: str,  # [필수] 입력종목코드 (ex. 123456)
        fid_input_iscd_2: str,  # [필수] 회원사코드 (ex. 회원사코드 FAQ 종목정보 다운로드(국내) > 회원사 참조)
        fid_input_date_1: str,  # [필수] 입력날짜1
        fid_input_date_2: str,  # [필수] 입력날짜2
        fid_sctn_cls_code: str = ""  # 데이터 순위 (초기값: "")
) -> pd.DataFrame:
    """
    주식현재가 회원사 종목매매동향 API입니다.
    한국투자 HTS(eFriend Plus) > [0454] 증권사 종목매매동향 화면을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건시장분류코드 (ex. J:KRX, NX:NXT)
        fid_input_iscd (str): [필수] 입력종목코드 (ex. 123456)  
        fid_input_iscd_2 (str): [필수] 회원사코드 (ex. 회원사코드 FAQ 종목정보 다운로드(국내) > 회원사 참조)
        fid_input_date_1 (str): [필수] 입력날짜1
        fid_input_date_2 (str): [필수] 입력날짜2
        fid_sctn_cls_code (str): 데이터 순위 (초기값: "")

    Returns:
        pd.DataFrame: 주식현재가 회원사 종목매매동향 데이터
        
    Example:
        >>> df = inquire_member_daily(
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_input_iscd="005930", 
        ...     fid_input_iscd_2="00003",
        ...     fid_input_date_1="20240501",
        ...     fid_input_date_2="20240624"
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-member-daily"

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '123456')")

    if fid_input_iscd_2 == "":
        raise ValueError("fid_input_iscd_2 is required (e.g. '00003')")

    if fid_input_date_1 == "":
        raise ValueError("fid_input_date_1 is required")

    if fid_input_date_2 == "":
        raise ValueError("fid_input_date_2 is required")

    tr_id = "FHPST04540000"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_ISCD_2": fid_input_iscd_2,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_DATE_2": fid_input_date_2,
        "FID_SCTN_CLS_CODE": fid_sctn_cls_code
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 국내주식 시간외호가[국내주식-077]
##############################################################################################

def inquire_overtime_asking_price(
        fid_cond_mrkt_div_code: str,  # [필수] 시장 분류 코드 (ex. J:주식)
        fid_input_iscd: str,  # [필수] 종목코드 (ex. 123456)
) -> pd.DataFrame:
    """
    국내주식 시간외호가 API입니다. 
    한국투자 HTS(eFriend Plus) > [0230] 시간외 현재가 화면의 '호가' 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 시장 분류 코드 (ex. J:주식)
        fid_input_iscd (str): [필수] 종목코드 (ex. 123456)

    Returns:
        pd.DataFrame: 국내주식 시간외호가 데이터
        
    Example:
        >>> df = inquire_overtime_asking_price("J", "005930")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-overtime-asking-price"

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '123456')")

    tr_id = "FHPST02300400"  # 국내주식 시간외호가

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,  # 시장 분류 코드
        "FID_INPUT_ISCD": fid_input_iscd,  # 종목코드
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame([res.getBody().output])
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 국내주식 시간외현재가[국내주식-076]
##############################################################################################

def inquire_overtime_price(
        fid_cond_mrkt_div_code: str,  # [필수] 시장 분류 코드 (ex. J: 주식)
        fid_input_iscd: str  # [필수] 종목코드 (ex. 005930)
) -> pd.DataFrame:
    """
    국내주식 시간외현재가 API입니다. 
    한국투자 HTS(eFriend Plus) > [0230] 시간외 현재가 화면의 좌측 상단기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 시장 분류 코드 (ex. J: 주식)
        fid_input_iscd (str): [필수] 종목코드 (ex. 005930)

    Returns:
        pd.DataFrame: 시간외현재가 데이터
        
    Example:
        >>> df = inquire_overtime_price("J", "005930")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-overtime-price"

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '005930')")

    tr_id = "FHPST02300000"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output, index=[0])
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 기간별손익일별합산조회[v1_국내주식-052]
##############################################################################################

def inquire_period_profit(
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        inqr_strt_dt: str,  # 조회시작일자
        inqr_end_dt: str,  # 조회종료일자
        sort_dvsn: str,  # 정렬구분 (ex. 00: 최근 순, 01: 과거 순, 02: 최근 순)
        inqr_dvsn: str,  # 조회구분 (ex. 00)
        cblc_dvsn: str,  # 잔고구분 (ex. 00: 전체)
        pdno: str = "",  # 상품번호
        NK100: str = "",  # 연속조회키100
        FK100: str = "",  # 연속조회검색조건100
        tr_cont: str = "",  # 연속거래여부
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
        depth: int = 0,  # 내부 재귀깊이 (자동관리)
        max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    기간별손익일별합산조회 API입니다.
    한국투자 HTS(eFriend Plus) > [0856] 기간별 매매손익 화면 에서 "일별" 클릭 시의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드
        inqr_strt_dt (str): [필수] 조회시작일자
        inqr_end_dt (str): [필수] 조회종료일자
        sort_dvsn (str): [필수] 정렬구분 (00: 최근 순, 01: 과거 순, 02: 최근 순)
        inqr_dvsn (str): [필수] 조회구분 (00)
        cblc_dvsn (str): [필수] 잔고구분 (00: 전체)
        pdno (str): 상품번호
        NK100 (str): 연속조회키100
        FK100 (str): 연속조회검색조건100
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 기간별손익일별합산조회 데이터 (output1, output2)
        
    Example:
        >>> df1, df2 = inquire_period_profit(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, inqr_strt_dt="20230101", inqr_end_dt="20240301", sort_dvsn="00", inqr_dvsn="00", cblc_dvsn="00")
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/trading/inquire-period-profit"

    # 필수 파라미터 검증
    if cano == "":
        raise ValueError("cano is required")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required")

    if inqr_strt_dt == "":
        raise ValueError("inqr_strt_dt is required")

    if inqr_end_dt == "":
        raise ValueError("inqr_end_dt is required")

    if sort_dvsn == "":
        raise ValueError("sort_dvsn is required (e.g. '00', '01', '02')")

    if inqr_dvsn == "":
        raise ValueError("inqr_dvsn is required (e.g. '00')")

    if cblc_dvsn == "":
        raise ValueError("cblc_dvsn is required (e.g. '00')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "TTTC8708R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "INQR_STRT_DT": inqr_strt_dt,
        "INQR_END_DT": inqr_end_dt,
        "SORT_DVSN": sort_dvsn,
        "INQR_DVSN": inqr_dvsn,
        "CBLC_DVSN": cblc_dvsn,
        "PDNO": pdno,
        "CTX_AREA_FK100": FK100,
        "CTX_AREA_NK100": NK100
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리 (array)
        current_data1 = pd.DataFrame(res.getBody().output1)
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1

        # output2 처리 (object)
        current_data2 = pd.DataFrame(res.getBody().output2, index=[0])
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2

        tr_cont = res.getHeader().tr_cont
        FK100 = res.getBody().ctx_area_fk100
        NK100 = res.getBody().ctx_area_nk100

        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_period_profit(
                cano, acnt_prdt_cd, inqr_strt_dt, inqr_end_dt, sort_dvsn, inqr_dvsn, cblc_dvsn,
                pdno, NK100, FK100, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 기간별매매손익현황조회[v1_국내주식-060]
##############################################################################################

def inquire_period_trade_profit(
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        sort_dvsn: str,  # 정렬구분 (00: 최근, 01:과거, 02:최근)
        inqr_strt_dt: str,  # 조회시작일자
        inqr_end_dt: str,  # 조회종료일자
        cblc_dvsn: str,  # 잔고구분 (00: 전체)
        pdno: str = "",  # 상품번호
        NK100: str = "",  # 연속조회키100
        FK100: str = "",  # 연속조회검색조건100
        tr_cont: str = "",  # 연속거래여부
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
        depth: int = 0,  # 내부 재귀깊이 (자동관리)
        max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    기간별매매손익현황조회 API입니다.
    한국투자 HTS(eFriend Plus) > [0856] 기간별 매매손익 화면 에서 "종목별" 클릭 시의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드
        sort_dvsn (str): [필수] 정렬구분 (ex. 00: 최근, 01:과거, 02:최근)
        inqr_strt_dt (str): [필수] 조회시작일자
        inqr_end_dt (str): [필수] 조회종료일자
        cblc_dvsn (str): [필수] 잔고구분 (ex. 00: 전체)
        pdno (str): 상품번호
        NK100 (str): 연속조회키100
        FK100 (str): 연속조회검색조건100
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 기간별매매손익현황 데이터 (output1, output2)
        
    Example:
        >>> df1, df2 = inquire_period_trade_profit(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, sort_dvsn="02", inqr_strt_dt="20230216", inqr_end_dt="20240301", cblc_dvsn="00")
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/trading/inquire-period-trade-profit"

    if cano == "":
        raise ValueError("cano is required")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required")

    if sort_dvsn == "":
        raise ValueError("sort_dvsn is required (e.g. '00', '01', '02')")

    if inqr_strt_dt == "":
        raise ValueError("inqr_strt_dt is required")

    if inqr_end_dt == "":
        raise ValueError("inqr_end_dt is required")

    if cblc_dvsn == "":
        raise ValueError("cblc_dvsn is required (e.g. '00')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "TTTC8715R"  # 기간별매매손익현황조회

    params = {
        "CANO": cano,  # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "SORT_DVSN": sort_dvsn,  # 정렬구분
        "INQR_STRT_DT": inqr_strt_dt,  # 조회시작일자
        "INQR_END_DT": inqr_end_dt,  # 조회종료일자
        "CBLC_DVSN": cblc_dvsn,  # 잔고구분
        "PDNO": pdno,  # 상품번호
        "CTX_AREA_FK100": FK100,  # 연속조회검색조건100
        "CTX_AREA_NK100": NK100  # 연속조회키100
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        current_data1 = pd.DataFrame(res.getBody().output1)
        current_data2 = pd.DataFrame(res.getBody().output2, index=[0])

        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1

        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2

        tr_cont = res.getHeader().tr_cont
        FK100 = res.getBody().ctx_area_fk100
        NK100 = res.getBody().ctx_area_nk100

        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_period_trade_profit(
                cano, acnt_prdt_cd, sort_dvsn, inqr_strt_dt, inqr_end_dt, cblc_dvsn,
                pdno, NK100, FK100, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 주식현재가 시세[v1_국내주식-008]
##############################################################################################

def inquire_price(
        env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
        fid_input_iscd: str  # [필수] 입력 종목코드 (ex. 종목코드 (ex 005930 삼성전자), ETN은 종목코드 6자리 앞에 Q 입력 필수)
) -> pd.DataFrame:
    """
    주식 현재가 시세 API입니다. 실시간 시세를 원하신다면 웹소켓 API를 활용하세요.

    ※ 종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 종목코드 (ex 005930 삼성전자), ETN은 종목코드 6자리 앞에 Q 입력 필수)

    Returns:
        pd.DataFrame: 주식 현재가 시세 데이터
        
    Example:
        >>> df = inquire_price("real", "J", "005930")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-price"

    # 필수 파라미터 검증
    if env_dv == "" or env_dv is None:
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")

    if fid_cond_mrkt_div_code == "" or fid_cond_mrkt_div_code is None:
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:KRX, NX:NXT, UN:통합')")

    if fid_input_iscd == "" or fid_input_iscd is None:
        raise ValueError("fid_input_iscd is required (e.g. '종목코드 (ex 005930 삼성전자), ETN은 종목코드 6자리 앞에 Q 입력 필수')")

    # tr_id 설정
    if env_dv == "real":
        tr_id = "FHKST01010100"
    elif env_dv == "demo":
        tr_id = "FHKST01010100"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output, index=[0])
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 주식현재가 시세2[v1_국내주식-054]
##############################################################################################

def inquire_price_2(
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
) -> pd.DataFrame:
    """
    주식현재가 시세2 API입니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
        fid_input_iscd (str): [필수] 입력 종목코드
        
    Returns:
        pd.DataFrame: 주식현재가 시세2 데이터
        
    Example:
        >>> df = inquire_price_2("J", "005930")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-price-2"

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required")

    tr_id = "FHPST01010000"  # 주식현재가 시세2

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,  # 조건 시장 분류 코드
        "FID_INPUT_ISCD": fid_input_iscd,  # 입력 종목코드
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        return pd.DataFrame(res.getBody().output, index=[0])
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 매수가능조회[v1_국내주식-007]
##############################################################################################

def inquire_psbl_order(
        env_dv: str,  # 실전모의구분
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        pdno: str,  # 상품번호
        ord_unpr: str,  # 주문단가
        ord_dvsn: str,  # 주문구분
        cma_evlu_amt_icld_yn: str,  # CMA평가금액포함여부
        ovrs_icld_yn: str  # 해외포함여부
) -> pd.DataFrame:
    """
    매수가능 조회 API입니다. 
    실전계좌/모의계좌의 경우, 한 번의 호출에 최대 1건까지 확인 가능합니다.

    1) 매수가능금액 확인
    . 미수 사용 X: nrcvb_buy_amt(미수없는매수금액) 확인
    . 미수 사용 O: max_buy_amt(최대매수금액) 확인

    2) 매수가능수량 확인
    . 특정 종목 전량매수 시 가능수량을 확인하실 경우 ORD_DVSN:00(지정가)는 종목증거금율이 반영되지 않습니다. 
    따라서 "반드시" ORD_DVSN:01(시장가)로 지정하여 종목증거금율이 반영된 가능수량을 확인하시기 바랍니다. 

    (다만, 조건부지정가 등 특정 주문구분(ex.IOC)으로 주문 시 가능수량을 확인할 경우 주문 시와 동일한 주문구분(ex.IOC) 입력하여 가능수량 확인)

    . 미수 사용 X: ORD_DVSN:01(시장가) or 특정 주문구분(ex.IOC)로 지정하여 nrcvb_buy_qty(미수없는매수수량) 확인
    . 미수 사용 O: ORD_DVSN:01(시장가) or 특정 주문구분(ex.IOC)로 지정하여 max_buy_qty(최대매수수량) 확인
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        cano (str): [필수] 종합계좌번호 (ex. 계좌번호 체계(8-2)의 앞 8자리)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 계좌번호 체계(8-2)의 뒤 2자리)
        pdno (str): [필수] 상품번호 (ex. 종목번호(6자리))
        ord_unpr (str): [필수] 주문단가 (ex. 1주당 가격)
        ord_dvsn (str): [필수] 주문구분 (ex. 01 : 시장가)
        cma_evlu_amt_icld_yn (str): [필수] CMA평가금액포함여부 (ex. Y)
        ovrs_icld_yn (str): [필수] 해외포함여부 (ex. N)

    Returns:
        pd.DataFrame: 매수가능조회 데이터
        
    Example:
        >>> df = inquire_psbl_order(env_dv="real", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, pdno="005930", ord_unpr="55000", ord_dvsn="01", cma_evlu_amt_icld_yn="N", ovrs_icld_yn="N")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/trading/inquire-psbl-order"

    # 필수 파라미터 검증
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")

    if cano == "":
        raise ValueError("cano is required (e.g. '계좌번호 체계(8-2)의 앞 8자리')")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '계좌번호 체계(8-2)의 뒤 2자리')")

    if pdno == "":
        raise ValueError("pdno is required (e.g. '종목번호(6자리)')")

    if ord_unpr == "":
        raise ValueError("ord_unpr is required (e.g. '1주당 가격')")

    if ord_dvsn == "":
        raise ValueError("ord_dvsn is required (e.g. '01 : 시장가')")

    if cma_evlu_amt_icld_yn == "":
        raise ValueError("cma_evlu_amt_icld_yn is required (e.g. 'Y')")

    if ovrs_icld_yn == "":
        raise ValueError("ovrs_icld_yn is required (e.g. 'N')")

    # tr_id 설정
    if env_dv == "real":
        tr_id = "TTTC8908R"
    elif env_dv == "demo":
        tr_id = "VTTC8908R"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "ORD_UNPR": ord_unpr,
        "ORD_DVSN": ord_dvsn,
        "CMA_EVLU_AMT_ICLD_YN": cma_evlu_amt_icld_yn,
        "OVRS_ICLD_YN": ovrs_icld_yn
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        return pd.DataFrame(res.getBody().output, index=[0])
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 주식정정취소가능주문조회[v1_국내주식-004]
##############################################################################################

def inquire_psbl_rvsecncl(
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        inqr_dvsn_1: str,  # 조회구분1
        inqr_dvsn_2: str,  # 조회구분2
        FK100: str = "",  # 연속조회검색조건100
        NK100: str = "",  # 연속조회키100
        tr_cont: str = "",  # 연속거래여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 내부 재귀깊이 (자동관리)
        max_depth: int = 10  # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    주식정정취소가능주문조회 API입니다. 한 번의 호출에 최대 50건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.

    ※ 주식주문(정정취소) 호출 전에 반드시 주식정정취소가능주문조회 호출을 통해 정정취소가능수량(output > psbl_qty)을 확인하신 후 정정취소주문 내시기 바랍니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. 계좌번호 체계(8-2)의 앞 8자리)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 계좌번호 체계(8-2)의 뒤 2자리)
        inqr_dvsn_1 (str): [필수] 조회구분1 (ex. 0: 주문, 1: 종목)
        inqr_dvsn_2 (str): [필수] 조회구분2 (ex. 0: 전체, 1: 매도, 2: 매수)
        FK100 (str): 연속조회검색조건100
        NK100 (str): 연속조회키100
        tr_cont (str): 연속거래여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        pd.DataFrame: 주식정정취소가능주문조회 데이터
        
    Example:
        >>> df = inquire_psbl_rvsecncl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, inqr_dvsn_1="1", inqr_dvsn_2="0")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/trading/inquire-psbl-rvsecncl"

    if cano == "":
        raise ValueError("cano is required (e.g. '계좌번호 체계(8-2)의 앞 8자리')")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '계좌번호 체계(8-2)의 뒤 2자리')")

    if inqr_dvsn_1 == "":
        raise ValueError("inqr_dvsn_1 is required (e.g. '0: 주문, 1: 종목')")

    if inqr_dvsn_2 == "":
        raise ValueError("inqr_dvsn_2 is required (e.g. '0: 전체, 1: 매도, 2: 매수')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    tr_id = "TTTC0084R"  # 주식정정취소가능주문조회

    params = {
        "CANO": cano,  # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "INQR_DVSN_1": inqr_dvsn_1,  # 조회구분1
        "INQR_DVSN_2": inqr_dvsn_2,  # 조회구분2
        "CTX_AREA_FK100": FK100,  # 연속조회검색조건100
        "CTX_AREA_NK100": NK100  # 연속조회키100
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont
        FK100 = res.getBody().ctx_area_fk100
        NK100 = res.getBody().ctx_area_nk100

        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_psbl_rvsecncl(
                cano, acnt_prdt_cd, inqr_dvsn_1, inqr_dvsn_2, FK100, NK100, "N", dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 매도가능수량조회 [국내주식-165]
##############################################################################################

def inquire_psbl_sell(
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        pdno: str,  # 종목번호
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 주문/계좌 
    매도가능수량조회[국내주식-165]
    매도가능수량조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 종합계좌번호
        acnt_prdt_cd (str): 계좌상품코드
        pdno (str): 보유종목 코드 ex)000660
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 매도가능수량조회 데이터
        
    Example:
        >>> df = inquire_psbl_sell("12345678", "01", "000660")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/trading/inquire-psbl-sell"
    # 필수 파라미터 검증
    if not cano:
        logger.error("cano is required. (e.g. '12345678')")
        raise ValueError("cano is required. (e.g. '12345678')")

    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")

    if not pdno:
        logger.error("pdno is required. (e.g. '000660')")
        raise ValueError("pdno is required. (e.g. '000660')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "TTTC8408R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_psbl_sell(
                cano,
                acnt_prdt_cd,
                pdno,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 주식일별분봉조회 [국내주식-213]
##############################################################################################

def inquire_time_dailychartprice(
        fid_cond_mrkt_div_code: str,  # 시장 분류 코드
        fid_input_iscd: str,  # 종목코드
        fid_input_hour_1: str,  # 입력 시간1
        fid_input_date_1: str,  # 입력 날짜1
        fid_pw_data_incu_yn: str = "N",  # 과거 데이터 포함 여부
        fid_fake_tick_incu_yn: str = ""  # 허봉 포함 여부
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    주식일별분봉조회 API입니다. 

    실전계좌의 경우, 한 번의 호출에 최대 120건까지 확인 가능하며, 
    FID_INPUT_DATE_1, FID_INPUT_HOUR_1 이용하여 과거일자 분봉조회 가능합니다.

    ※ 과거 분봉 조회 시, 당사 서버에서 보관하고 있는 만큼의 데이터만 확인이 가능합니다. (최대 1년 분봉 보관)
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 시장 분류 코드 (ex. J:주식,NX:NXT,UN:통합)
        fid_input_iscd (str): [필수] 종목코드 (ex. 123456)
        fid_input_hour_1 (str): [필수] 입력 시간1 (ex. 130000)
        fid_input_date_1 (str): [필수] 입력 날짜1 (ex. 20241023)
        fid_pw_data_incu_yn (str): 과거 데이터 포함 여부 (기본값: "N")
        fid_fake_tick_incu_yn (str): 허봉 포함 여부 (기본값: "")

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> output1, output2 = inquire_time_dailychartprice("J", "005930", "130000", "20241023")
        >>> print(output1)
        >>> print(output2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-time-dailychartprice"

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J', 'NX', 'UN')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '123456')")

    if fid_input_hour_1 == "":
        raise ValueError("fid_input_hour_1 is required (e.g. '130000')")

    if fid_input_date_1 == "":
        raise ValueError("fid_input_date_1 is required (e.g. '20241023')")

    tr_id = "FHKST03010230"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_HOUR_1": fid_input_hour_1,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_PW_DATA_INCU_YN": fid_pw_data_incu_yn,
        "FID_FAKE_TICK_INCU_YN": fid_fake_tick_incu_yn
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        # output1 (object) -> DataFrame
        output1 = pd.DataFrame([res.getBody().output1])

        # output2 (array) -> DataFrame  
        output2 = pd.DataFrame(res.getBody().output2)

        return output1, output2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 업종 분봉조회[v1_국내주식-045]
##############################################################################################

def inquire_time_indexchartprice(
        fid_cond_mrkt_div_code: str,  # FID 조건 시장 분류 코드
        fid_etc_cls_code: str,  # FID 기타 구분 코드
        fid_input_iscd: str,  # FID 입력 종목코드
        fid_input_hour_1: str,  # FID 입력 시간1
        fid_pw_data_incu_yn: str,  # FID 과거 데이터 포함 여부
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        tr_cont: str = "",
        depth: int = 0,
        max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 업종/기타 
    업종 분봉조회[v1_국내주식-045]
    업종 분봉조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): FID 조건 시장 분류 코드 (예: 'U')
        fid_etc_cls_code (str): FID 기타 구분 코드 (예: '0' 기본, '1' 장마감, 시간외 제외)
        fid_input_iscd (str): FID 입력 종목코드 (예: '0001' 종합, '0002' 대형주)
        fid_input_hour_1 (str): FID 입력 시간1 (예: '30', '60', '600', '3600')
        fid_pw_data_incu_yn (str): FID 과거 데이터 포함 여부 (예: 'Y' 과거, 'N' 당일)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 업종 분봉조회 데이터
        
    Example:
        >>> df1, df2 = inquire_time_indexchartprice(
        ...     fid_cond_mrkt_div_code='U',
        ...     fid_etc_cls_code='0',
        ...     fid_input_iscd='0001',
        ...     fid_input_hour_1='30',
        ...     fid_pw_data_incu_yn='Y'
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-time-indexchartprice"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'U')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'U')")

    if not fid_etc_cls_code:
        logger.error("fid_etc_cls_code is required. (e.g. '0')")
        raise ValueError("fid_etc_cls_code is required. (e.g. '0')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0001')")
        raise ValueError("fid_input_iscd is required. (e.g. '0001')")

    if not fid_input_hour_1:
        logger.error("fid_input_hour_1 is required. (e.g. '30')")
        raise ValueError("fid_input_hour_1 is required. (e.g. '30')")

    if not fid_pw_data_incu_yn:
        logger.error("fid_pw_data_incu_yn is required. (e.g. 'Y')")
        raise ValueError("fid_pw_data_incu_yn is required. (e.g. 'Y')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()

    tr_id = "FHKUP03500200"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_ETC_CLS_CODE": fid_etc_cls_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_HOUR_1": fid_input_hour_1,
        "FID_PW_DATA_INCU_YN": fid_pw_data_incu_yn,
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # Output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                # output1은 단일 객체, output2는 배열일 수 있음
                if isinstance(output_data, list):
                    current_data1 = pd.DataFrame(output_data)
                else:
                    # 단일 객체인 경우 리스트로 감싸서 DataFrame 생성
                    current_data1 = pd.DataFrame([output_data])

                if dataframe1 is not None:
                    dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
                else:
                    dataframe1 = current_data1
            else:
                if dataframe1 is None:
                    dataframe1 = pd.DataFrame()
        else:
            if dataframe1 is None:
                dataframe1 = pd.DataFrame()
        # Output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                # output1은 단일 객체, output2는 배열일 수 있음
                if isinstance(output_data, list):
                    current_data2 = pd.DataFrame(output_data)
                else:
                    # 단일 객체인 경우 리스트로 감싸서 DataFrame 생성
                    current_data2 = pd.DataFrame([output_data])

                if dataframe2 is not None:
                    dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
                else:
                    dataframe2 = current_data2
            else:
                if dataframe2 is None:
                    dataframe2 = pd.DataFrame()
        else:
            if dataframe2 is None:
                dataframe2 = pd.DataFrame()
        tr_cont = res.getHeader().tr_cont

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_time_indexchartprice(
                fid_cond_mrkt_div_code,
                fid_etc_cls_code,
                fid_input_iscd,
                fid_input_hour_1,
                fid_pw_data_incu_yn,
                "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 주식당일분봉조회[v1_국내주식-022]
##############################################################################################

def inquire_time_itemchartprice(
        env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
        fid_input_iscd: str,  # [필수] 입력 종목코드 (ex. 123456)
        fid_input_hour_1: str,  # [필수] 입력 시간1 (ex. 입력시간)
        fid_pw_data_incu_yn: str,  # [필수] 과거 데이터 포함 여부
        fid_etc_cls_code: str = ""  # [필수] 기타 구분 코드
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    주식당일분봉조회 API입니다. 
    실전계좌/모의계좌의 경우, 한 번의 호출에 최대 30건까지 확인 가능합니다.

    ※ 당일 분봉 데이터만 제공됩니다. (전일자 분봉 미제공)

    ※ input > FID_INPUT_HOUR_1 에 미래일시 입력 시에 현재가로 조회됩니다.
    ex) 오전 10시에 113000 입력 시에 오전 10시~11시30분 사이의 데이터가 오전 10시 값으로 조회됨

    ※ output2의 첫번째 배열의 체결량(cntg_vol)은 첫체결이 발생되기 전까지는 이전 분봉의 체결량이 해당 위치에 표시됩니다. 
    해당 분봉의 첫 체결이 발생되면 해당 이전분 체결량이 두번째 배열로 이동되면서 새로운 체결량으로 업데이트됩니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 123456)
        fid_input_hour_1 (str): [필수] 입력 시간1 (ex. 입력시간)
        fid_pw_data_incu_yn (str): [필수] 과거 데이터 포함 여부
        fid_etc_cls_code (str): [필수] 기타 구분 코드

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> output1, output2 = inquire_time_itemchartprice(env_dv="real", fid_cond_mrkt_div_code="J", fid_input_iscd="005930", fid_input_hour_1="093000", fid_pw_data_incu_yn="Y")
        >>> print(output1)
        >>> print(output2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"

    # 필수 파라미터 검증
    if env_dv == "" or env_dv is None:
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")

    if fid_cond_mrkt_div_code == "" or fid_cond_mrkt_div_code is None:
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:KRX, NX:NXT, UN:통합')")

    if fid_input_iscd == "" or fid_input_iscd is None:
        raise ValueError("fid_input_iscd is required (e.g. '123456')")

    if fid_input_hour_1 == "" or fid_input_hour_1 is None:
        raise ValueError("fid_input_hour_1 is required (e.g. '입력시간')")

    if fid_pw_data_incu_yn == "" or fid_pw_data_incu_yn is None:
        raise ValueError("fid_pw_data_incu_yn is required")

    # tr_id 설정 (실전/모의 동일)
    if env_dv == "real" or env_dv == "demo":
        tr_id = "FHKST03010200"
    else:
        raise ValueError("env_dv can only be real or demo")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_HOUR_1": fid_input_hour_1,
        "FID_PW_DATA_INCU_YN": fid_pw_data_incu_yn,
        "FID_ETC_CLS_CODE": fid_etc_cls_code
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        # output1 (object) -> DataFrame (1행)
        output1_data = pd.DataFrame(res.getBody().output1, index=[0])

        # output2 (array) -> DataFrame (여러행)
        output2_data = pd.DataFrame(res.getBody().output2)

        return output1_data, output2_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 주식현재가 당일시간대별체결[v1_국내주식-023]
##############################################################################################

def inquire_time_itemconclusion(
        env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
        fid_input_iscd: str,  # [필수] 입력 종목코드
        fid_input_hour_1: str  # [필수] 입력 시간1
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    주식현재가 당일시간대별체결 API입니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (real:실전, demo:모의)
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (J:KRX, NX:NXT, UN:통합)
        fid_input_iscd (str): [필수] 입력 종목코드
        fid_input_hour_1 (str): [필수] 입력 시간1

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> df1, df2 = inquire_time_itemconclusion("real", "U", "0001", "115959")
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-time-itemconclusion"

    # 필수 파라미터 검증
    if env_dv == "" or env_dv is None:
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")

    if fid_cond_mrkt_div_code == "" or fid_cond_mrkt_div_code is None:
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:KRX, NX:NXT, UN:통합')")

    if fid_input_iscd == "" or fid_input_iscd is None:
        raise ValueError("fid_input_iscd is required (e.g. '입력 종목코드')")

    if fid_input_hour_1 == "" or fid_input_hour_1 is None:
        raise ValueError("fid_input_hour_1 is required (e.g. '입력 시간1')")

    # tr_id 설정
    if env_dv == "real":
        tr_id = "FHPST01060000"
    elif env_dv == "demo":
        tr_id = "FHPST01060000"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_HOUR_1": fid_input_hour_1
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        # output1 처리 (object -> DataFrame)
        output1_data = pd.DataFrame([res.getBody().output1])

        # output2 처리 (object -> DataFrame)  
        output2_data = pd.DataFrame(res.getBody().output2)

        return output1_data, output2_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 주식현재가 시간외시간별체결[v1_국내주식-025]
##############################################################################################

def inquire_time_overtimeconclusion(
        env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code: str,  # [필수] 조건시장분류코드 (ex. J:주식/ETF/ETN)
        fid_input_iscd: str,  # [필수] 입력종목코드 (ex. 123456(ETN의 경우 Q로 시작 Q500001))
        fid_hour_cls_code: str  # [필수] 적립금구분코드 (ex. 1: 시간외)
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    주식현재가 시간외시간별체결 API입니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        fid_cond_mrkt_div_code (str): [필수] 조건시장분류코드 (ex. J:주식/ETF/ETN)
        fid_input_iscd (str): [필수] 입력종목코드 (ex. 123456(ETN의 경우 Q로 시작 Q500001))
        fid_hour_cls_code (str): [필수] 적립금구분코드 (ex. 1: 시간외)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> output1, output2 = inquire_time_overtimeconclusion("real", "J", "005930", "1")
        >>> print(output1)
        >>> print(output2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-time-overtimeconclusion"

    # 필수 파라미터 검증
    if env_dv == "" or env_dv is None:
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")

    if fid_cond_mrkt_div_code == "" or fid_cond_mrkt_div_code is None:
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:주식/ETF/ETN')")

    if fid_input_iscd == "" or fid_input_iscd is None:
        raise ValueError("fid_input_iscd is required (e.g. '123456(ETN의 경우 Q로 시작 Q500001)')")

    if fid_hour_cls_code == "" or fid_hour_cls_code is None:
        raise ValueError("fid_hour_cls_code is required (e.g. '1: 시간외')")

    # TR_ID 설정
    if env_dv == "real":
        tr_id = "FHPST02310000"
    elif env_dv == "demo":
        tr_id = "FHPST02310000"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_HOUR_CLS_CODE": fid_hour_cls_code
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        # output1 (object) -> DataFrame
        output1_data = pd.DataFrame(res.getBody().output1, index=[0])

        # output2 (array) -> DataFrame  
        output2_data = pd.DataFrame(res.getBody().output2)

        return output1_data, output2_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 변동성완화장치(VI) 현황[v1_국내주식-055]
##############################################################################################

def inquire_vi_status(
        fid_div_cls_code: str,  # FID 분류 구분 코드
        fid_cond_scr_div_code: str,  # FID 조건 화면 분류 코드
        fid_mrkt_cls_code: str,  # FID 시장 구분 코드
        fid_input_iscd: str,  # FID 입력 종목코드
        fid_rank_sort_cls_code: str,  # FID 순위 정렬 구분 코드
        fid_input_date_1: str,  # FID 입력 날짜1
        fid_trgt_cls_code: str,  # FID 대상 구분 코드
        fid_trgt_exls_cls_code: str,  # FID 대상 제외 구분 코드
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 업종/기타 
    변동성완화장치(VI) 현황[v1_국내주식-055]
    변동성완화장치(VI) 현황 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_div_cls_code (str): 0:전체 1:상승 2:하락
        fid_cond_scr_div_code (str): 20139
        fid_mrkt_cls_code (str): 0:전체 K:거래소 Q:코스닥
        fid_input_iscd (str): 종목코드
        fid_rank_sort_cls_code (str): 0:전체 1:정적 2:동적 3:정적&동적
        fid_input_date_1 (str): 영업일
        fid_trgt_cls_code (str): 대상 구분 코드
        fid_trgt_exls_cls_code (str): 대상 제외 구분 코드
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 변동성완화장치(VI) 현황 데이터
        
    Example:
        >>> df = inquire_vi_status(
        ...     fid_div_cls_code="0",
        ...     fid_cond_scr_div_code="20139",
        ...     fid_mrkt_cls_code="0",
        ...     fid_input_iscd="005930",
        ...     fid_rank_sort_cls_code="0",
        ...     fid_input_date_1="20240126",
        ...     fid_trgt_cls_code="",
        ...     fid_trgt_exls_cls_code=""
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/inquire-vi-status"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증 (첨부된 사진 기준, 비어있으면 빼고 체크)
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20139')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20139')")

    if not fid_mrkt_cls_code:
        logger.error("fid_mrkt_cls_code is required. (e.g. '0')")
        raise ValueError("fid_mrkt_cls_code is required. (e.g. '0')")

    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '0')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '0')")

    if not fid_input_date_1:
        logger.error("fid_input_date_1 is required. (e.g. '20200420')")
        raise ValueError("fid_input_date_1 is required. (e.g. '20200420')")

    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHPST01390000"

    params = {
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_MRKT_CLS_CODE": fid_mrkt_cls_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_TRGT_CLS_CODE": fid_trgt_cls_code,
        "FID_TRGT_EXLS_CLS_CODE": fid_trgt_exls_cls_code,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_vi_status(
                fid_div_cls_code,
                fid_cond_scr_div_code,
                fid_mrkt_cls_code,
                fid_input_iscd,
                fid_rank_sort_cls_code,
                fid_input_date_1,
                fid_trgt_cls_code,
                fid_trgt_exls_cls_code,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 주식통합증거금 현황 [국내주식-191]
##############################################################################################

def intgr_margin(
        cano: str,  # [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 01)
        cma_evlu_amt_icld_yn: str,  # [필수] CMA평가금액포함여부 (ex. Y: 포함, N: 미포함)
        wcrc_frcr_dvsn_cd: str,  # [필수] 원화외화구분코드 (ex. 01: 외화기준, 02: 원화기준)
        fwex_ctrt_frcr_dvsn_cd: str  # [필수] 선도환계약외화구분코드 (ex. 01: 외화기준, 02: 원화기준)
) -> pd.DataFrame:
    """
    주식통합증거금 현황 API입니다.
    한국투자 HTS(eFriend Plus) > [0867] 통합증거금조회 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

    ※ 해당 화면은 일반계좌와 통합증거금 신청계좌에 대해서 국내 및 해외 주문가능금액을 간단하게 조회하는 화면입니다.
    ※ 해외 국가별 상세한 증거금현황을 원하시면 [해외주식] 주문/계좌 > 해외증거금 통화별조회 API를 이용하여 주시기 바랍니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 01)
        cma_evlu_amt_icld_yn (str): [필수] CMA평가금액포함여부 (ex. Y: 포함, N: 미포함)
        wcrc_frcr_dvsn_cd (str): [필수] 원화외화구분코드 (ex. 01: 외화기준, 02: 원화기준)
        fwex_ctrt_frcr_dvsn_cd (str): [필수] 선도환계약외화구분코드 (ex. 01: 외화기준, 02: 원화기준)

    Returns:
        pd.DataFrame: 주식통합증거금 현황 데이터
        
    Example:
        >>> df = intgr_margin(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, cma_evlu_amt_icld_yn="N", wcrc_frcr_dvsn_cd="01", fwex_ctrt_frcr_dvsn_cd="01")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/trading/intgr-margin"

    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '01')")

    if cma_evlu_amt_icld_yn == "":
        raise ValueError("cma_evlu_amt_icld_yn is required (e.g. 'Y' or 'N')")

    if wcrc_frcr_dvsn_cd == "":
        raise ValueError("wcrc_frcr_dvsn_cd is required (e.g. '01' or '02')")

    if fwex_ctrt_frcr_dvsn_cd == "":
        raise ValueError("fwex_ctrt_frcr_dvsn_cd is required (e.g. '01' or '02')")

    tr_id = "TTTC0869R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "CMA_EVLU_AMT_ICLD_YN": cma_evlu_amt_icld_yn,
        "WCRC_FRCR_DVSN_CD": wcrc_frcr_dvsn_cd,
        "FWEX_CTRT_FRCR_DVSN_CD": fwex_ctrt_frcr_dvsn_cd
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame([res.getBody().output])
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 관심종목 그룹조회 [국내주식-204]
##############################################################################################

def intstock_grouplist(
        type: str,  # [필수] 관심종목구분코드 (ex. 1)
        fid_etc_cls_code: str,  # [필수] FID 기타 구분 코드 (ex. 00)
        user_id: str  # [필수] 사용자 ID
) -> pd.DataFrame:
    """
    관심종목 그룹조회 API입니다.
    ① 관심종목 그룹조회 → ② 관심종목 그룹별 종목조회 → ③ 관심종목(멀티종목) 시세조회 순서대로 호출하셔서 관심종목 시세 조회 가능합니다.

    ※ 한 번의 호출에 최대 30종목의 시세 확인 가능합니다.

    한국투자증권 Github 에서 관심종목 복수시세조회 파이썬 샘플코드를 참고하실 수 있습니다.
    https://github.com/koreainvestment/open-trading-api/blob/main/rest/interest_stocks_price.py
    
    Args:
        type (str): [필수] 관심종목구분코드 (ex. 1)
        fid_etc_cls_code (str): [필수] FID 기타 구분 코드 (ex. 00)
        user_id (str): [필수] 사용자 ID

    Returns:
        pd.DataFrame: 관심종목 그룹 정보를 담은 DataFrame
        
    Example:
        >>> df = intstock_grouplist(type="1", fid_etc_cls_code="00", user_id=trenv.my_htsid)
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/intstock-grouplist"

    if type == "":
        raise ValueError("type is required (e.g. '1')")

    if fid_etc_cls_code == "":
        raise ValueError("fid_etc_cls_code is required (e.g. '00')")

    if user_id == "":
        raise ValueError("user_id is required")

    tr_id = "HHKCM113004C7"  # 관심종목 그룹조회

    params = {
        "TYPE": type,  # 관심종목구분코드
        "FID_ETC_CLS_CODE": fid_etc_cls_code,  # FID 기타 구분 코드
        "USER_ID": user_id  # 사용자 ID
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output2)
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 관심종목(멀티종목) 시세조회 [국내주식-205]
##############################################################################################

def intstock_multprice(
        fid_cond_mrkt_div_code_1: str,  # [필수] 조건 시장 분류 코드1 (ex. J)
        fid_input_iscd_1: str,  # [필수] 입력 종목코드1 (ex. 123456)
        fid_cond_mrkt_div_code_2: Optional[str] = None,  # 조건 시장 분류 코드2
        fid_input_iscd_2: Optional[str] = None,  # 입력 종목코드2
        fid_cond_mrkt_div_code_3: Optional[str] = None,  # 조건 시장 분류 코드3
        fid_input_iscd_3: Optional[str] = None,  # 입력 종목코드3
        fid_cond_mrkt_div_code_4: Optional[str] = None,  # 조건 시장 분류 코드4
        fid_input_iscd_4: Optional[str] = None,  # 입력 종목코드4
        fid_cond_mrkt_div_code_5: Optional[str] = None,  # 조건 시장 분류 코드5
        fid_input_iscd_5: Optional[str] = None,  # 입력 종목코드5
        fid_cond_mrkt_div_code_6: Optional[str] = None,  # 조건 시장 분류 코드6
        fid_input_iscd_6: Optional[str] = None,  # 입력 종목코드6
        fid_cond_mrkt_div_code_7: Optional[str] = None,  # 조건 시장 분류 코드7
        fid_input_iscd_7: Optional[str] = None,  # 입력 종목코드7
        fid_cond_mrkt_div_code_8: Optional[str] = None,  # 조건 시장 분류 코드8
        fid_input_iscd_8: Optional[str] = None,  # 입력 종목코드8
        fid_cond_mrkt_div_code_9: Optional[str] = None,  # 조건 시장 분류 코드9
        fid_input_iscd_9: Optional[str] = None,  # 입력 종목코드9
        fid_cond_mrkt_div_code_10: Optional[str] = None,  # 조건 시장 분류 코드10
        fid_input_iscd_10: Optional[str] = None,  # 입력 종목코드10
        fid_cond_mrkt_div_code_11: Optional[str] = None,  # 조건 시장 분류 코드11
        fid_input_iscd_11: Optional[str] = None,  # 입력 종목코드11
        fid_cond_mrkt_div_code_12: Optional[str] = None,  # 조건 시장 분류 코드12
        fid_input_iscd_12: Optional[str] = None,  # 입력 종목코드12
        fid_cond_mrkt_div_code_13: Optional[str] = None,  # 조건 시장 분류 코드13
        fid_input_iscd_13: Optional[str] = None,  # 입력 종목코드13
        fid_cond_mrkt_div_code_14: Optional[str] = None,  # 조건 시장 분류 코드14
        fid_input_iscd_14: Optional[str] = None,  # 입력 종목코드14
        fid_cond_mrkt_div_code_15: Optional[str] = None,  # 조건 시장 분류 코드15
        fid_input_iscd_15: Optional[str] = None,  # 입력 종목코드15
        fid_cond_mrkt_div_code_16: Optional[str] = None,  # 조건 시장 분류 코드16
        fid_input_iscd_16: Optional[str] = None,  # 입력 종목코드16
        fid_cond_mrkt_div_code_17: Optional[str] = None,  # 조건 시장 분류 코드17
        fid_input_iscd_17: Optional[str] = None,  # 입력 종목코드17
        fid_cond_mrkt_div_code_18: Optional[str] = None,  # 조건 시장 분류 코드18
        fid_input_iscd_18: Optional[str] = None,  # 입력 종목코드18
        fid_cond_mrkt_div_code_19: Optional[str] = None,  # 조건 시장 분류 코드19
        fid_input_iscd_19: Optional[str] = None,  # 입력 종목코드19
        fid_cond_mrkt_div_code_20: Optional[str] = None,  # 조건 시장 분류 코드20
        fid_input_iscd_20: Optional[str] = None,  # 입력 종목코드20
        fid_cond_mrkt_div_code_21: Optional[str] = None,  # 조건 시장 분류 코드21
        fid_input_iscd_21: Optional[str] = None,  # 입력 종목코드21
        fid_cond_mrkt_div_code_22: Optional[str] = None,  # 조건 시장 분류 코드22
        fid_input_iscd_22: Optional[str] = None,  # 입력 종목코드22
        fid_cond_mrkt_div_code_23: Optional[str] = None,  # 조건 시장 분류 코드23
        fid_input_iscd_23: Optional[str] = None,  # 입력 종목코드23
        fid_cond_mrkt_div_code_24: Optional[str] = None,  # 조건 시장 분류 코드24
        fid_input_iscd_24: Optional[str] = None,  # 입력 종목코드24
        fid_cond_mrkt_div_code_25: Optional[str] = None,  # 조건 시장 분류 코드25
        fid_input_iscd_25: Optional[str] = None,  # 입력 종목코드25
        fid_cond_mrkt_div_code_26: Optional[str] = None,  # 조건 시장 분류 코드26
        fid_input_iscd_26: Optional[str] = None,  # 입력 종목코드26
        fid_cond_mrkt_div_code_27: Optional[str] = None,  # 조건 시장 분류 코드27
        fid_input_iscd_27: Optional[str] = None,  # 입력 종목코드27
        fid_cond_mrkt_div_code_28: Optional[str] = None,  # 조건 시장 분류 코드28
        fid_input_iscd_28: Optional[str] = None,  # 입력 종목코드28
        fid_cond_mrkt_div_code_29: Optional[str] = None,  # 조건 시장 분류 코드29
        fid_input_iscd_29: Optional[str] = None,  # 입력 종목코드29
        fid_cond_mrkt_div_code_30: Optional[str] = None,  # 조건 시장 분류 코드30
        fid_input_iscd_30: Optional[str] = None  # 입력 종목코드30
) -> pd.DataFrame:
    """
    관심종목(멀티종목) 시세조회 API입니다.
    ① 관심종목 그룹조회 → ② 관심종목 그룹별 종목조회 → ③ 관심종목(멀티종목) 시세조회 순서대로 호출하셔서 관심종목 시세 조회 가능합니다.

    ※ 한 번의 호출에 최대 30종목의 시세 확인 가능합니다.
    그룹별종목조회 결과를 아래와 같이 입력하셔서 총 30종목까지 복수종목 조회 가능합니다.(아래 Example 참고)
    . fid_mrkt_cls_code(시장구분) → FID_COND_MRKT_DIV_CODE_1
    . jong_code(종목코드) 1 → FID_INPUT_ISCD_1
    ...

    한국투자증권 Github 에서 관심종목 복수시세조회 파이썬 샘플코드를 참고하실 수 있습니다.
    https://github.com/koreainvestment/open-trading-api/blob/main/rest/interest_stocks_price.py
    
    Args:
        fid_cond_mrkt_div_code_1 (str): [필수] 조건 시장 분류 코드1 (ex. J:KRX, NX:NXT)
        fid_input_iscd_1 (str): [필수] 입력 종목코드1 (ex. 123456)
        fid_cond_mrkt_div_code_2 (Optional[str]): 조건 시장 분류 코드2
        fid_input_iscd_2 (Optional[str]): 입력 종목코드2
        fid_cond_mrkt_div_code_3 (Optional[str]): 조건 시장 분류 코드3
        fid_input_iscd_3 (Optional[str]): 입력 종목코드3
        fid_cond_mrkt_div_code_4 (Optional[str]): 조건 시장 분류 코드4
        fid_input_iscd_4 (Optional[str]): 입력 종목코드4
        fid_cond_mrkt_div_code_5 (Optional[str]): 조건 시장 분류 코드5
        fid_input_iscd_5 (Optional[str]): 입력 종목코드5
        fid_cond_mrkt_div_code_6 (Optional[str]): 조건 시장 분류 코드6
        fid_input_iscd_6 (Optional[str]): 입력 종목코드6
        fid_cond_mrkt_div_code_7 (Optional[str]): 조건 시장 분류 코드7
        fid_input_iscd_7 (Optional[str]): 입력 종목코드7
        fid_cond_mrkt_div_code_8 (Optional[str]): 조건 시장 분류 코드8
        fid_input_iscd_8 (Optional[str]): 입력 종목코드8
        fid_cond_mrkt_div_code_9 (Optional[str]): 조건 시장 분류 코드9
        fid_input_iscd_9 (Optional[str]): 입력 종목코드9
        fid_cond_mrkt_div_code_10 (Optional[str]): 조건 시장 분류 코드10
        fid_input_iscd_10 (Optional[str]): 입력 종목코드10
        fid_cond_mrkt_div_code_11 (Optional[str]): 조건 시장 분류 코드11
        fid_input_iscd_11 (Optional[str]): 입력 종목코드11
        fid_cond_mrkt_div_code_12 (Optional[str]): 조건 시장 분류 코드12
        fid_input_iscd_12 (Optional[str]): 입력 종목코드12
        fid_cond_mrkt_div_code_13 (Optional[str]): 조건 시장 분류 코드13
        fid_input_iscd_13 (Optional[str]): 입력 종목코드13
        fid_cond_mrkt_div_code_14 (Optional[str]): 조건 시장 분류 코드14
        fid_input_iscd_14 (Optional[str]): 입력 종목코드14
        fid_cond_mrkt_div_code_15 (Optional[str]): 조건 시장 분류 코드15
        fid_input_iscd_15 (Optional[str]): 입력 종목코드15
        fid_cond_mrkt_div_code_16 (Optional[str]): 조건 시장 분류 코드16
        fid_input_iscd_16 (Optional[str]): 입력 종목코드16
        fid_cond_mrkt_div_code_17 (Optional[str]): 조건 시장 분류 코드17
        fid_input_iscd_17 (Optional[str]): 입력 종목코드17
        fid_cond_mrkt_div_code_18 (Optional[str]): 조건 시장 분류 코드18
        fid_input_iscd_18 (Optional[str]): 입력 종목코드18
        fid_cond_mrkt_div_code_19 (Optional[str]): 조건 시장 분류 코드19
        fid_input_iscd_19 (Optional[str]): 입력 종목코드19
        fid_cond_mrkt_div_code_20 (Optional[str]): 조건 시장 분류 코드20
        fid_input_iscd_20 (Optional[str]): 입력 종목코드20
        fid_cond_mrkt_div_code_21 (Optional[str]): 조건 시장 분류 코드21
        fid_input_iscd_21 (Optional[str]): 입력 종목코드21
        fid_cond_mrkt_div_code_22 (Optional[str]): 조건 시장 분류 코드22
        fid_input_iscd_22 (Optional[str]): 입력 종목코드22
        fid_cond_mrkt_div_code_23 (Optional[str]): 조건 시장 분류 코드23
        fid_input_iscd_23 (Optional[str]): 입력 종목코드23
        fid_cond_mrkt_div_code_24 (Optional[str]): 조건 시장 분류 코드24
        fid_input_iscd_24 (Optional[str]): 입력 종목코드24
        fid_cond_mrkt_div_code_25 (Optional[str]): 조건 시장 분류 코드25
        fid_input_iscd_25 (Optional[str]): 입력 종목코드25
        fid_cond_mrkt_div_code_26 (Optional[str]): 조건 시장 분류 코드26
        fid_input_iscd_26 (Optional[str]): 입력 종목코드26
        fid_cond_mrkt_div_code_27 (Optional[str]): 조건 시장 분류 코드27
        fid_input_iscd_27 (Optional[str]): 입력 종목코드27
        fid_cond_mrkt_div_code_28 (Optional[str]): 조건 시장 분류 코드28
        fid_input_iscd_28 (Optional[str]): 입력 종목코드28
        fid_cond_mrkt_div_code_29 (Optional[str]): 조건 시장 분류 코드29
        fid_input_iscd_29 (Optional[str]): 입력 종목코드29
        fid_cond_mrkt_div_code_30 (Optional[str]): 조건 시장 분류 코드30
        fid_input_iscd_30 (Optional[str]): 입력 종목코드30

    Returns:
        pd.DataFrame: 관심종목(멀티종목) 시세 데이터
        
    Example:
        >>> df = intstock_multprice(fid_cond_mrkt_div_code_1="J", fid_input_iscd_1="419530")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/intstock-multprice"

    if fid_cond_mrkt_div_code_1 == "":
        raise ValueError("fid_cond_mrkt_div_code_1 is required (e.g. 'J')")

    if fid_input_iscd_1 == "":
        raise ValueError("fid_input_iscd_1 is required (e.g. '123456')")

    tr_id = "FHKST11300006"  # 관심종목(멀티종목) 시세조회

    params = {
        "FID_COND_MRKT_DIV_CODE_1": fid_cond_mrkt_div_code_1,
        "FID_INPUT_ISCD_1": fid_input_iscd_1
    }

    # 옵션 파라미터 처리
    if fid_cond_mrkt_div_code_2 is not None:
        params["FID_COND_MRKT_DIV_CODE_2"] = fid_cond_mrkt_div_code_2
    if fid_input_iscd_2 is not None:
        params["FID_INPUT_ISCD_2"] = fid_input_iscd_2
    if fid_cond_mrkt_div_code_3 is not None:
        params["FID_COND_MRKT_DIV_CODE_3"] = fid_cond_mrkt_div_code_3
    if fid_input_iscd_3 is not None:
        params["FID_INPUT_ISCD_3"] = fid_input_iscd_3
    if fid_cond_mrkt_div_code_4 is not None:
        params["FID_COND_MRKT_DIV_CODE_4"] = fid_cond_mrkt_div_code_4
    if fid_input_iscd_4 is not None:
        params["FID_INPUT_ISCD_4"] = fid_input_iscd_4
    if fid_cond_mrkt_div_code_5 is not None:
        params["FID_COND_MRKT_DIV_CODE_5"] = fid_cond_mrkt_div_code_5
    if fid_input_iscd_5 is not None:
        params["FID_INPUT_ISCD_5"] = fid_input_iscd_5
    if fid_cond_mrkt_div_code_6 is not None:
        params["FID_COND_MRKT_DIV_CODE_6"] = fid_cond_mrkt_div_code_6
    if fid_input_iscd_6 is not None:
        params["FID_INPUT_ISCD_6"] = fid_input_iscd_6
    if fid_cond_mrkt_div_code_7 is not None:
        params["FID_COND_MRKT_DIV_CODE_7"] = fid_cond_mrkt_div_code_7
    if fid_input_iscd_7 is not None:
        params["FID_INPUT_ISCD_7"] = fid_input_iscd_7
    if fid_cond_mrkt_div_code_8 is not None:
        params["FID_COND_MRKT_DIV_CODE_8"] = fid_cond_mrkt_div_code_8
    if fid_input_iscd_8 is not None:
        params["FID_INPUT_ISCD_8"] = fid_input_iscd_8
    if fid_cond_mrkt_div_code_9 is not None:
        params["FID_COND_MRKT_DIV_CODE_9"] = fid_cond_mrkt_div_code_9
    if fid_input_iscd_9 is not None:
        params["FID_INPUT_ISCD_9"] = fid_input_iscd_9
    if fid_cond_mrkt_div_code_10 is not None:
        params["FID_COND_MRKT_DIV_CODE_10"] = fid_cond_mrkt_div_code_10
    if fid_input_iscd_10 is not None:
        params["FID_INPUT_ISCD_10"] = fid_input_iscd_10
    if fid_cond_mrkt_div_code_11 is not None:
        params["FID_COND_MRKT_DIV_CODE_11"] = fid_cond_mrkt_div_code_11
    if fid_input_iscd_11 is not None:
        params["FID_INPUT_ISCD_11"] = fid_input_iscd_11
    if fid_cond_mrkt_div_code_12 is not None:
        params["FID_COND_MRKT_DIV_CODE_12"] = fid_cond_mrkt_div_code_12
    if fid_input_iscd_12 is not None:
        params["FID_INPUT_ISCD_12"] = fid_input_iscd_12
    if fid_cond_mrkt_div_code_13 is not None:
        params["FID_COND_MRKT_DIV_CODE_13"] = fid_cond_mrkt_div_code_13
    if fid_input_iscd_13 is not None:
        params["FID_INPUT_ISCD_13"] = fid_input_iscd_13
    if fid_cond_mrkt_div_code_14 is not None:
        params["FID_COND_MRKT_DIV_CODE_14"] = fid_cond_mrkt_div_code_14
    if fid_input_iscd_14 is not None:
        params["FID_INPUT_ISCD_14"] = fid_input_iscd_14
    if fid_cond_mrkt_div_code_15 is not None:
        params["FID_COND_MRKT_DIV_CODE_15"] = fid_cond_mrkt_div_code_15
    if fid_input_iscd_15 is not None:
        params["FID_INPUT_ISCD_15"] = fid_input_iscd_15
    if fid_cond_mrkt_div_code_16 is not None:
        params["FID_COND_MRKT_DIV_CODE_16"] = fid_cond_mrkt_div_code_16
    if fid_input_iscd_16 is not None:
        params["FID_INPUT_ISCD_16"] = fid_input_iscd_16
    if fid_cond_mrkt_div_code_17 is not None:
        params["FID_COND_MRKT_DIV_CODE_17"] = fid_cond_mrkt_div_code_17
    if fid_input_iscd_17 is not None:
        params["FID_INPUT_ISCD_17"] = fid_input_iscd_17
    if fid_cond_mrkt_div_code_18 is not None:
        params["FID_COND_MRKT_DIV_CODE_18"] = fid_cond_mrkt_div_code_18
    if fid_input_iscd_18 is not None:
        params["FID_INPUT_ISCD_18"] = fid_input_iscd_18
    if fid_cond_mrkt_div_code_19 is not None:
        params["FID_COND_MRKT_DIV_CODE_19"] = fid_cond_mrkt_div_code_19
    if fid_input_iscd_19 is not None:
        params["FID_INPUT_ISCD_19"] = fid_input_iscd_19
    if fid_cond_mrkt_div_code_20 is not None:
        params["FID_COND_MRKT_DIV_CODE_20"] = fid_cond_mrkt_div_code_20
    if fid_input_iscd_20 is not None:
        params["FID_INPUT_ISCD_20"] = fid_input_iscd_20
    if fid_cond_mrkt_div_code_21 is not None:
        params["FID_COND_MRKT_DIV_CODE_21"] = fid_cond_mrkt_div_code_21
    if fid_input_iscd_21 is not None:
        params["FID_INPUT_ISCD_21"] = fid_input_iscd_21
    if fid_cond_mrkt_div_code_22 is not None:
        params["FID_COND_MRKT_DIV_CODE_22"] = fid_cond_mrkt_div_code_22
    if fid_input_iscd_22 is not None:
        params["FID_INPUT_ISCD_22"] = fid_input_iscd_22
    if fid_cond_mrkt_div_code_23 is not None:
        params["FID_COND_MRKT_DIV_CODE_23"] = fid_cond_mrkt_div_code_23
    if fid_input_iscd_23 is not None:
        params["FID_INPUT_ISCD_23"] = fid_input_iscd_23
    if fid_cond_mrkt_div_code_24 is not None:
        params["FID_COND_MRKT_DIV_CODE_24"] = fid_cond_mrkt_div_code_24
    if fid_input_iscd_24 is not None:
        params["FID_INPUT_ISCD_24"] = fid_input_iscd_24
    if fid_cond_mrkt_div_code_25 is not None:
        params["FID_COND_MRKT_DIV_CODE_25"] = fid_cond_mrkt_div_code_25
    if fid_input_iscd_25 is not None:
        params["FID_INPUT_ISCD_25"] = fid_input_iscd_25
    if fid_cond_mrkt_div_code_26 is not None:
        params["FID_COND_MRKT_DIV_CODE_26"] = fid_cond_mrkt_div_code_26
    if fid_input_iscd_26 is not None:
        params["FID_INPUT_ISCD_26"] = fid_input_iscd_26
    if fid_cond_mrkt_div_code_27 is not None:
        params["FID_COND_MRKT_DIV_CODE_27"] = fid_cond_mrkt_div_code_27
    if fid_input_iscd_27 is not None:
        params["FID_INPUT_ISCD_27"] = fid_input_iscd_27
    if fid_cond_mrkt_div_code_28 is not None:
        params["FID_COND_MRKT_DIV_CODE_28"] = fid_cond_mrkt_div_code_28
    if fid_input_iscd_28 is not None:
        params["FID_INPUT_ISCD_28"] = fid_input_iscd_28
    if fid_cond_mrkt_div_code_29 is not None:
        params["FID_COND_MRKT_DIV_CODE_29"] = fid_cond_mrkt_div_code_29
    if fid_input_iscd_29 is not None:
        params["FID_INPUT_ISCD_29"] = fid_input_iscd_29
    if fid_cond_mrkt_div_code_30 is not None:
        params["FID_COND_MRKT_DIV_CODE_30"] = fid_cond_mrkt_div_code_30
    if fid_input_iscd_30 is not None:
        params["FID_INPUT_ISCD_30"] = fid_input_iscd_30

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 관심종목 그룹별 종목조회 [국내주식-203]
##############################################################################################

def intstock_stocklist_by_group(
        type: str,  # 관심종목구분코드 (ex. 1)
        user_id: str,  # 사용자 ID
        inter_grp_code: str,  # 관심 그룹 코드 (ex. 001)
        fid_etc_cls_code: str,  # 기타 구분 코드 (ex. 4)
        data_rank: str = "",  # 데이터 순위
        inter_grp_name: str = "",  # 관심 그룹 명
        hts_kor_isnm: str = "",  # HTS 한글 종목명
        cntg_cls_code: str = ""  # 체결 구분 코드
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    관심종목 그룹별 종목조회 API입니다.
    ① 관심종목 그룹조회 → ② 관심종목 그룹별 종목조회 → ③ 관심종목(멀티종목) 시세조회 순서대로 호출하셔서 관심종목 시세 조회 가능합니다.

    ※ 한 번의 호출에 최대 30종목의 시세 확인 가능합니다.

    한국투자증권 Github 에서 관심종목 복수시세조회 파이썬 샘플코드를 참고하실 수 있습니다.
    https://github.com/koreainvestment/open-trading-api/blob/main/rest/interest_stocks_price.py
    
    Args:
        type (str): [필수] 관심종목구분코드 (ex. 1)
        user_id (str): [필수] 사용자 ID
        inter_grp_code (str): [필수] 관심 그룹 코드 (ex. 001)
        fid_etc_cls_code (str): [필수] 기타 구분 코드 (ex. 4)
        data_rank (str): 데이터 순위
        inter_grp_name (str): 관심 그룹 명
        hts_kor_isnm (str): HTS 한글 종목명
        cntg_cls_code (str): 체결 구분 코드

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터프레임, output2 데이터프레임)
        
    Example:
        >>> df1, df2 = intstock_stocklist_by_group(
        ...     type="1", user_id=trenv.my_htsid, inter_grp_code="001", fid_etc_cls_code="4"
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/intstock-stocklist-by-group"

    if type == "":
        raise ValueError("type is required (e.g. '1')")

    if user_id == "":
        raise ValueError("user_id is required")

    if inter_grp_code == "":
        raise ValueError("inter_grp_code is required (e.g. '001')")

    if fid_etc_cls_code == "":
        raise ValueError("fid_etc_cls_code is required (e.g. '4')")

    tr_id = "HHKCM113004C6"  # 관심종목 그룹별 종목조회

    params = {
        "TYPE": type,  # 관심종목구분코드
        "USER_ID": user_id,  # 사용자 ID
        "INTER_GRP_CODE": inter_grp_code,  # 관심 그룹 코드
        "FID_ETC_CLS_CODE": fid_etc_cls_code,  # 기타 구분 코드
        "DATA_RANK": data_rank,  # 데이터 순위
        "INTER_GRP_NAME": inter_grp_name,  # 관심 그룹 명
        "HTS_KOR_ISNM": hts_kor_isnm,  # HTS 한글 종목명
        "CNTG_CLS_CODE": cntg_cls_code  # 체결 구분 코드
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        # output1 데이터프레임 생성
        output1_data = pd.DataFrame([res.getBody().output1])

        # output2 데이터프레임 생성
        output2_data = pd.DataFrame(res.getBody().output2)

        logging.info("Data fetch complete.")
        return output1_data, output2_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 국내주식 증권사별 투자의견[국내주식-189]
##############################################################################################

def invest_opbysec(
        fid_cond_mrkt_div_code: str,  # 조건시장분류코드
        fid_cond_scr_div_code: str,  # 조건화면분류코드
        fid_input_iscd: str,  # 입력종목코드
        fid_div_cls_code: str,  # 분류구분코드
        fid_input_date_1: str,  # 입력날짜1
        fid_input_date_2: str,  # 입력날짜2
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    국내주식 증권사별 투자의견[국내주식-189]
    국내주식 증권사별 투자의견 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): J(시장 구분 코드)
        fid_cond_scr_div_code (str): 16634(Primary key)
        fid_input_iscd (str): 회원사코드 (kis developers 포탈 사이트 포럼-> FAQ -> 종목정보 다운로드(국내) 참조)
        fid_div_cls_code (str): 전체(0) 매수(1) 중립(2) 매도(3)
        fid_input_date_1 (str): 이후 ~
        fid_input_date_2 (str): ~ 이전
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 증권사별 투자의견 데이터
        
    Example:
        >>> df = invest_opbysec(
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_cond_scr_div_code="16634",
        ...     fid_input_iscd="005930",
        ...     fid_div_cls_code="0",
        ...     fid_input_date_1="20230101",
        ...     fid_input_date_2="20231231"
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/invest-opbysec"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '16634')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '16634')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '005930')")
        raise ValueError("fid_input_iscd is required. (e.g. '005930')")

    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")

    if not fid_input_date_1:
        logger.error("fid_input_date_1 is required. (e.g. '20230101')")
        raise ValueError("fid_input_date_1 is required. (e.g. '20230101')")

    if not fid_input_date_2:
        logger.error("fid_input_date_2 is required. (e.g. '20231231')")
        raise ValueError("fid_input_date_2 is required. (e.g. '20231231')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # API 호출 URL 및 거래 ID 설정

    tr_id = "FHKST663400C0"

    # API 요청 파라미터 설정
    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_DATE_2": fid_input_date_2,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    # API 응답 처리
    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return invest_opbysec(
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_div_cls_code,
                fid_input_date_1,
                fid_input_date_2,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 국내주식 종목투자의견[국내주식-188]
##############################################################################################

def invest_opinion(
        fid_cond_mrkt_div_code: str,  # 조건시장분류코드
        fid_cond_scr_div_code: str,  # 조건화면분류코드
        fid_input_iscd: str,  # 입력종목코드
        fid_input_date_1: str,  # 입력날짜1
        fid_input_date_2: str,  # 입력날짜2
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    국내주식 종목투자의견[국내주식-188]
    국내주식 종목투자의견 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): J(시장 구분 코드)
        fid_cond_scr_div_code (str): 16633(Primary key)
        fid_input_iscd (str): 종목코드(ex) 005930(삼성전자))
        fid_input_date_1 (str): 이후 ~(ex) 0020231113)
        fid_input_date_2 (str): ~ 이전(ex) 0020240513)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 종목투자의견 데이터
        
    Example:
        >>> df = invest_opinion(
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_cond_scr_div_code="16633",
        ...     fid_input_iscd="005930",
        ...     fid_input_date_1="20231113",
        ...     fid_input_date_2="20240513"
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/invest-opinion"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '16633')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '16633')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '005930')")
        raise ValueError("fid_input_iscd is required. (e.g. '005930')")

    if not fid_input_date_1:
        logger.error("fid_input_date_1 is required. (e.g. '20231113')")
        raise ValueError("fid_input_date_1 is required. (e.g. '20231113')")

    if not fid_input_date_2:
        logger.error("fid_input_date_2 is required. (e.g. '20240513')")
        raise ValueError("fid_input_date_2 is required. (e.g. '20240513')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # API 호출 URL 및 거래 ID 설정

    tr_id = "FHKST663300C0"

    # 요청 파라미터 설정
    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_DATE_2": fid_input_date_2,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    # API 응답 처리
    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return invest_opinion(
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_input_date_1,
                fid_input_date_2,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 프로그램매매 투자자매매동향(당일) [국내주식-116]
##############################################################################################

def investor_program_trade_today(
        mrkt_div_cls_code: str  # [필수] 시장 구분 코드 (ex. 1:코스피, 4:코스닥)
) -> pd.DataFrame:
    """
    프로그램매매 투자자매매동향(당일) API입니다.
    한국투자 HTS(eFriend Plus) > [0466] 프로그램매매 투자자별 동향 화면 의 "당일동향" 표의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        mrkt_div_cls_code (str): [필수] 시장 구분 코드 (ex. 1:코스피, 4:코스닥)
        
    Returns:
        pd.DataFrame: 프로그램매매 투자자매매동향 데이터
        
    Example:
        >>> df = investor_program_trade_today(mrkt_div_cls_code="1")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/investor-program-trade-today"

    if mrkt_div_cls_code == "":
        raise ValueError("mrkt_div_cls_code is required (e.g. '1' or '4')")

    tr_id = "HHPPG046600C1"

    params = {
        "MRKT_DIV_CLS_CODE": mrkt_div_cls_code
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output1)
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


########################################################################################
# [국내주식] 시세분석  > 종목별 투자자매매동향(일별)[종목별 투자자매매동향(일별)]
########################################################################################

def investor_trade_by_stock_daily(
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_input_date_1: str,  # 입력 날짜1
        fid_org_adj_prc: str,  # 수정주가 원주가 가격
        fid_etc_cls_code: str,  # 기타 구분 코드
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        tr_cont: str = "",
        depth: int = 0,
        max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 시세분석 
    종목별 투자자매매동향(일별)[종목별 투자자매매동향(일별)]
    종목별 투자자매매동향(일별) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): J:KRX, NX:NXT, UN:통합
        fid_input_iscd (str): 종목번호 (6자리)
        fid_input_date_1 (str): 입력 날짜(20250812)
        fid_org_adj_prc (str): 공란 입력
        fid_etc_cls_code (str): 공란 입력
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 종목별 투자자매매동향(일별) 데이터
        
    Example:
        >>> df1, df2 = investor_trade_by_stock_daily(
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_input_iscd="005930",
        ...     fid_input_date_1="20250812",
        ...     fid_org_adj_prc="",
        ...     fid_etc_cls_code=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/investor-trade-by-stock-daily"
    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '005930')")
        raise ValueError("fid_input_iscd is required. (e.g. '005930')")
    if not fid_input_date_1:
        logger.error("fid_input_date_1 is required. (e.g. '20250812')")
        raise ValueError("fid_input_date_1 is required. (e.g. '20250812')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()

    tr_id = "FHPTJ04160001"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_ORG_ADJ_PRC": fid_org_adj_prc,
        "FID_ETC_CLS_CODE": fid_etc_cls_code,
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                if isinstance(output_data, list):
                    current_data1 = pd.DataFrame(output_data)
                else:
                    current_data1 = pd.DataFrame([output_data])

                if dataframe1 is not None:
                    dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
                else:
                    dataframe1 = current_data1
            else:
                if dataframe1 is None:
                    dataframe1 = pd.DataFrame()
        else:
            if dataframe1 is None:
                dataframe1 = pd.DataFrame()

        # output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                if isinstance(output_data, list):
                    current_data2 = pd.DataFrame(output_data)
                else:
                    current_data2 = pd.DataFrame([output_data])

                if dataframe2 is not None:
                    dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
                else:
                    dataframe2 = current_data2
            else:
                if dataframe2 is None:
                    dataframe2 = pd.DataFrame()
        else:
            if dataframe2 is None:
                dataframe2 = pd.DataFrame()

        tr_cont = res.getHeader().tr_cont

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return investor_trade_by_stock_daily(
                fid_cond_mrkt_div_code,
                fid_input_iscd,
                fid_input_date_1,
                fid_org_adj_prc,
                fid_etc_cls_code,
                "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 종목별 외인기관 추정가집계[v1_국내주식-046]
##############################################################################################

def investor_trend_estimate(
        mksc_shrn_iscd: str  # [필수] 종목코드 (ex. 123456)
) -> pd.DataFrame:
    """
    국내주식 종목별 외국인, 기관 추정가집계 API입니다.

    한국투자 MTS > 국내 현재가 > 투자자 > 투자자동향 탭 > 왼쪽구분을 '추정(주)'로 선택 시 확인 가능한 데이터를 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

    증권사 직원이 장중에 집계/입력한 자료를 단순 누계한 수치로서,
    입력시간은 외국인 09:30, 11:20, 13:20, 14:30 / 기관종합 10:00, 11:20, 13:20, 14:30 이며, 사정에 따라 변동될 수 있습니다.
    
    Args:
        mksc_shrn_iscd (str): [필수] 종목코드 (ex. 123456)

    Returns:
        pd.DataFrame: 종목별 외인기관 추정가집계 데이터
        
    Example:
        >>> df = investor_trend_estimate(mksc_shrn_iscd="005930")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/investor-trend-estimate"

    if mksc_shrn_iscd == "":
        raise ValueError("mksc_shrn_iscd is required (ex. '123456')")

    tr_id = "HHPTJ04160200"

    params = {
        "MKSC_SHRN_ISCD": mksc_shrn_iscd
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output2)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 예탁원정보(무상증자일정)[국내주식-144]
##############################################################################################

def ksdinfo_bonus_issue(
        cts: str,  # CTS
        f_dt: str,  # 조회일자From
        t_dt: str,  # 조회일자To
        sht_cd: str,  # 종목코드
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    예탁원정보(무상증자일정)[국내주식-144]
    예탁원정보(무상증자일정) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cts (str): 공백
        f_dt (str): 일자 ~
        t_dt (str): ~ 일자
        sht_cd (str): 공백: 전체, 특정종목 조회시 : 종목코드
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 예탁원정보(무상증자일정) 데이터
        
    Example:
        >>> df = ksdinfo_bonus_issue(" ", "20230101", "20231231", "005930")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ksdinfo/bonus-issue"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not f_dt:
        logger.error("f_dt is required. (e.g. '20230101')")
        raise ValueError("f_dt is required. (e.g. '20230101')")

    if not t_dt:
        logger.error("t_dt is required. (e.g. '20231231')")
        raise ValueError("t_dt is required. (e.g. '20231231')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "HHKDB669101C0"

    params = {
        "CTS": cts,
        "F_DT": f_dt,
        "T_DT": t_dt,
        "SHT_CD": sht_cd,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return ksdinfo_bonus_issue(
                cts,
                f_dt,
                t_dt,
                sht_cd,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 예탁원정보(자본감소일정) [국내주식-149]
##############################################################################################

def ksdinfo_cap_dcrs(
        cts: str,  # CTS
        f_dt: str,  # 조회일자From
        t_dt: str,  # 조회일자To
        sht_cd: str,  # 종목코드
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    예탁원정보(자본감소일정)[국내주식-149]
    예탁원정보(자본감소일정) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cts (str): 공백
        f_dt (str): 일자 ~
        t_dt (str): ~ 일자
        sht_cd (str): 공백: 전체,  특정종목 조회시 : 종목코드
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 예탁원정보(자본감소일정) 데이터
        
    Example:
        >>> df = ksdinfo_cap_dcrs(" ", "20230101", "20231231", "005930")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ksdinfo/cap-dcrs"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not f_dt:
        logger.error("f_dt is required. (e.g. '20230101')")
        raise ValueError("f_dt is required. (e.g. '20230101')")

    if not t_dt:
        logger.error("t_dt is required. (e.g. '20231231')")
        raise ValueError("t_dt is required. (e.g. '20231231')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "HHKDB669106C0"

    params = {
        "CTS": cts,
        "F_DT": f_dt,
        "T_DT": t_dt,
        "SHT_CD": sht_cd,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return ksdinfo_cap_dcrs(
                cts,
                f_dt,
                t_dt,
                sht_cd,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 예탁원정보(배당일정)[국내주식-145]
##############################################################################################

def ksdinfo_dividend(
        cts: str,  # CTS
        gb1: str,  # 조회구분
        f_dt: str,  # 조회일자From
        t_dt: str,  # 조회일자To
        sht_cd: str,  # 종목코드
        high_gb: str,  # 고배당여부
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    예탁원정보(배당일정)[국내주식-145]
    예탁원정보(배당일정) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cts (str): 공백
        gb1 (str): 0:배당전체, 1:결산배당, 2:중간배당
        f_dt (str): 일자 ~
        t_dt (str): ~ 일자
        sht_cd (str): 공백: 전체,  특정종목 조회시 : 종목코드
        high_gb (str): 공백
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 예탁원정보(배당일정) 데이터
        
    Example:
        >>> df = ksdinfo_dividend(" ", "0", "20230101", "20231231", " ", " ")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ksdinfo/dividend"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not gb1:
        logger.error("gb1 is required. (e.g. '0')")
        raise ValueError("gb1 is required. (e.g. '0')")

    if not f_dt:
        logger.error("f_dt is required. (e.g. '20230101')")
        raise ValueError("f_dt is required. (e.g. '20230101')")

    if not t_dt:
        logger.error("t_dt is required. (e.g. '20231231')")
        raise ValueError("t_dt is required. (e.g. '20231231')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "HHKDB669102C0"

    params = {
        "CTS": cts,
        "GB1": gb1,
        "F_DT": f_dt,
        "T_DT": t_dt,
        "SHT_CD": sht_cd,
        "HIGH_GB": high_gb,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return ksdinfo_dividend(
                cts,
                gb1,
                f_dt,
                t_dt,
                sht_cd,
                high_gb,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 예탁원정보(실권주일정)[국내주식-152]
##############################################################################################

def ksdinfo_forfeit(
        sht_cd: str,  # 종목코드
        t_dt: str,  # 조회일자To
        f_dt: str,  # 조회일자From
        cts: str,  # CTS
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    예탁원정보(실권주일정)[국내주식-152]
    예탁원정보(실권주일정) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        sht_cd (str): 공백: 전체, 특정종목 조회시 : 종목코드
        t_dt (str): ~ 일자
        f_dt (str): 일자 ~
        cts (str): 공백
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 예탁원정보(실권주일정) 데이터
        
    Example:
        >>> df = ksdinfo_forfeit("001440", "20240315", "20240314", " ")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ksdinfo/forfeit"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not t_dt:
        logger.error("t_dt is required. (e.g. '20240315')")
        raise ValueError("t_dt is required. (e.g. '20240315')")

    if not f_dt:
        logger.error("f_dt is required. (e.g. '20240314')")
        raise ValueError("f_dt is required. (e.g. '20240314')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "HHKDB669109C0"

    params = {
        "SHT_CD": sht_cd,
        "T_DT": t_dt,
        "F_DT": f_dt,
        "CTS": cts,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return ksdinfo_forfeit(
                sht_cd,
                t_dt,
                f_dt,
                cts,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 예탁원정보(상장정보일정)[국내주식-150]
##############################################################################################

def ksdinfo_list_info(
        sht_cd: str,  # 종목코드
        t_dt: str,  # 조회일자To
        f_dt: str,  # 조회일자From
        cts: str,  # CTS
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    예탁원정보(상장정보일정)[국내주식-150]
    예탁원정보(상장정보일정) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        sht_cd (str): 공백: 전체, 특정종목 조회시 : 종목코드
        t_dt (str): ~ 일자
        f_dt (str): 일자 ~
        cts (str): 공백
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 예탁원정보(상장정보일정) 데이터
        
    Example:
        >>> df = ksdinfo_list_info("000660", "20231010", "20231001", "")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ksdinfo/list-info"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not t_dt:
        logger.error("t_dt is required. (e.g. '20231010')")
        raise ValueError("t_dt is required. (e.g. '20231010')")
    if not f_dt:
        logger.error("f_dt is required. (e.g. '20231001')")
        raise ValueError("f_dt is required. (e.g. '20231001')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # API 호출 URL 및 ID 설정

    tr_id = "HHKDB669107C0"

    # 요청 파라미터 설정
    params = {
        "SHT_CD": sht_cd,
        "T_DT": t_dt,
        "F_DT": f_dt,
        "CTS": cts,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    # API 응답 처리
    if res.isOK():
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return ksdinfo_list_info(
                sht_cd,
                t_dt,
                f_dt,
                cts,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 예탁원정보(의무예치일정) [국내주식-153]
##############################################################################################

def ksdinfo_mand_deposit(
        t_dt: str,  # 조회일자To
        sht_cd: str,  # 종목코드
        f_dt: str,  # 조회일자From
        cts: str,  # CTS
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    예탁원정보(의무예치일정)[국내주식-153]
    예탁원정보(의무예치일정) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        t_dt (str): 조회 종료 일자 (예: '20230301')
        sht_cd (str): 종목코드 (공백: 전체, 특정종목 조회시 : 종목코드)
        f_dt (str): 조회 시작 일자 (예: '20230101')
        cts (str): CTS (공백)
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 예탁원정보(의무예치일정) 데이터
        
    Example:
        >>> df = ksdinfo_mand_deposit('20230301', '005930', '20230101', '')
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ksdinfo/mand-deposit"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not t_dt:
        logger.error("t_dt is required. (e.g. '20230301')")
        raise ValueError("t_dt is required. (e.g. '20230301')")

    if not f_dt:
        logger.error("f_dt is required. (e.g. '20230101')")
        raise ValueError("f_dt is required. (e.g. '20230101')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # API 호출 URL 및 거래 ID 설정

    tr_id = "HHKDB669110C0"

    # 요청 파라미터 설정
    params = {
        "T_DT": t_dt,
        "SHT_CD": sht_cd,
        "F_DT": f_dt,
        "CTS": cts,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    # API 호출 성공 시 데이터 처리
    if res.isOK():
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        # 기존 데이터프레임과 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        # 다음 페이지 호출
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return ksdinfo_mand_deposit(
                t_dt,
                sht_cd,
                f_dt,
                cts,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 호출 실패 시 에러 로그 출력
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 예탁원정보(합병_분할일정)[국내주식-147]
##############################################################################################

def ksdinfo_merger_split(
        cts: str,  # CTS
        f_dt: str,  # 조회일자From
        t_dt: str,  # 조회일자To
        sht_cd: str,  # 종목코드
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    예탁원정보(합병_분할일정)[국내주식-147]
    예탁원정보(합병_분할일정) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cts (str): 공백
        f_dt (str): 일자 ~
        t_dt (str): ~ 일자
        sht_cd (str): 공백: 전체, 특정종목 조회시 : 종목코드
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 예탁원정보(합병_분할일정) 데이터
        
    Example:
        >>> df = ksdinfo_merger_split(" ", "20230101", "20231231", "005930")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ksdinfo/merger-split"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not f_dt:
        logger.error("f_dt is required. (e.g. '20230101')")
        raise ValueError("f_dt is required. (e.g. '20230101')")

    if not t_dt:
        logger.error("t_dt is required. (e.g. '20231231')")
        raise ValueError("t_dt is required. (e.g. '20231231')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "HHKDB669104C0"

    params = {
        "CTS": cts,
        "F_DT": f_dt,
        "T_DT": t_dt,
        "SHT_CD": sht_cd,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
        if hasattr(res.getBody(), 'output1'):
            current_data = pd.DataFrame(res.getBody().output1)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return ksdinfo_merger_split(
                cts,
                f_dt,
                t_dt,
                sht_cd,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 호출 실패 시 에러 로그
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 예탁원정보(유상증자일정)[국내주식-143]
##############################################################################################

def ksdinfo_paidin_capin(
        cts: str,  # CTS
        gb1: str,  # 조회구분
        f_dt: str,  # 조회일자From
        t_dt: str,  # 조회일자To
        sht_cd: str,  # 종목코드
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    예탁원정보(유상증자일정)[국내주식-143]
    예탁원정보(유상증자일정) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cts (str): 공백
        gb1 (str): 1(청약일별), 2(기준일별)
        f_dt (str): 일자 ~
        t_dt (str): ~ 일자
        sht_cd (str): 공백(전체),  특정종목 조회시(종목코드)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 예탁원정보(유상증자일정) 데이터
        
    Example:
        >>> df = ksdinfo_paidin_capin(" ", "1", "20230101", "20231231", " ")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ksdinfo/paidin-capin"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not gb1:
        logger.error("gb1 is required. (e.g. '1')")
        raise ValueError("gb1 is required. (e.g. '1')")

    if not f_dt:
        logger.error("f_dt is required. (e.g. '20230101')")
        raise ValueError("f_dt is required. (e.g. '20230101')")

    if not t_dt:
        logger.error("t_dt is required. (e.g. '20231231')")
        raise ValueError("t_dt is required. (e.g. '20231231')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "HHKDB669100C0"

    params = {
        "CTS": cts,
        "GB1": gb1,
        "F_DT": f_dt,
        "T_DT": t_dt,
        "SHT_CD": sht_cd,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output1'):
            current_data = pd.DataFrame(res.getBody().output1)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return ksdinfo_paidin_capin(
                cts,
                gb1,
                f_dt,
                t_dt,
                sht_cd,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 예탁원정보(공모주청약일정)[국내주식-151]
##############################################################################################

def ksdinfo_pub_offer(
        sht_cd: str,  # 종목코드
        cts: str,  # CTS
        f_dt: str,  # 조회일자From
        t_dt: str,  # 조회일자To
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    예탁원정보(공모주청약일정)[국내주식-151]
    예탁원정보(공모주청약일정) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        sht_cd (str): 공백: 전체, 특정종목 조회시 : 종목코드
        cts (str): 공백
        f_dt (str): 일자 ~
        t_dt (str): ~ 일자
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 예탁원정보(공모주청약일정) 데이터
        
    Example:
        >>> df = ksdinfo_pub_offer("000000", "", "20230101", "20231231")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ksdinfo/pub-offer"
    # 필수 파라미터 검증
    if not f_dt:
        logger.error("f_dt is required. (e.g. '20230101')")
        raise ValueError("f_dt is required. (e.g. '20230101')")

    if not t_dt:
        logger.error("t_dt is required. (e.g. '20231231')")
        raise ValueError("t_dt is required. (e.g. '20231231')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "HHKDB669108C0"

    params = {
        "SHT_CD": sht_cd,
        "CTS": cts,
        "F_DT": f_dt,
        "T_DT": t_dt,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return ksdinfo_pub_offer(
                sht_cd,
                cts,
                f_dt,
                t_dt,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 예탁원정보(주식매수청구일정)[국내주식-146]
##############################################################################################

def ksdinfo_purreq(
        sht_cd: str,  # 종목코드
        t_dt: str,  # 조회일자To
        f_dt: str,  # 조회일자From
        cts: str,  # CTS
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    예탁원정보(주식매수청구일정)[국내주식-146]
    예탁원정보(주식매수청구일정) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        sht_cd (str): 공백: 전체, 특정종목 조회시 : 종목코드
        t_dt (str): ~ 일자
        f_dt (str): 일자 ~
        cts (str): 공백
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 예탁원정보(주식매수청구일정) 데이터
        
    Example:
        >>> df = ksdinfo_purreq("005930", "20231010", "20231001", "")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ksdinfo/purreq"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not t_dt:
        logger.error("t_dt is required. (e.g. '20231010')")
        raise ValueError("t_dt is required. (e.g. '20231010')")
    if not f_dt:
        logger.error("f_dt is required. (e.g. '20231001')")
        raise ValueError("f_dt is required. (e.g. '20231001')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "HHKDB669103C0"

    params = {
        "SHT_CD": sht_cd,
        "T_DT": t_dt,
        "F_DT": f_dt,
        "CTS": cts,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return ksdinfo_purreq(
                sht_cd,
                t_dt,
                f_dt,
                cts,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 에러 처리
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 예탁원정보(액면교체일정)[국내주식-148]
##############################################################################################

def ksdinfo_rev_split(
        sht_cd: str,  # 종목코드
        cts: str,  # CTS
        f_dt: str,  # 조회일자From
        t_dt: str,  # 조회일자To
        market_gb: str,  # 시장구분
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    예탁원정보(액면교체일정)[국내주식-148]
    예탁원정보(액면교체일정) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        sht_cd (str): 공백: 전체, 특정종목 조회시 : 종목코드
        cts (str): 공백
        f_dt (str): 일자 ~
        t_dt (str): ~ 일자
        market_gb (str): 0:전체, 1:코스피, 2:코스닥
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 예탁원정보(액면교체일정) 데이터
        
    Example:
        >>> df = ksdinfo_rev_split("001390", "", "20230101", "20231231", "0")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ksdinfo/rev-split"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not f_dt:
        logger.error("f_dt is required. (e.g. '20230101')")
        raise ValueError("f_dt is required. (e.g. '20230101')")

    if not t_dt:
        logger.error("t_dt is required. (e.g. '20231231')")
        raise ValueError("t_dt is required. (e.g. '20231231')")

    if market_gb not in ["0", "1", "2"]:
        logger.error("market_gb must be one of ['0', '1', '2'].")
        raise ValueError("market_gb must be one of ['0', '1', '2'].")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "HHKDB669105C0"

    params = {
        "SHT_CD": sht_cd,
        "CTS": cts,
        "F_DT": f_dt,
        "T_DT": t_dt,
        "MARKET_GB": market_gb,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return ksdinfo_rev_split(
                sht_cd,
                cts,
                f_dt,
                t_dt,
                market_gb,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 예탁원정보(주주총회일정)[국내주식-154]
##############################################################################################

def ksdinfo_sharehld_meet(
        cts: str,  # CTS
        f_dt: str,  # 조회일자From
        t_dt: str,  # 조회일자To
        sht_cd: str,  # 종목코드
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    예탁원정보(주주총회일정)[국내주식-154]
    예탁원정보(주주총회일정) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cts (str): 공백
        f_dt (str): 일자 ~
        t_dt (str): ~ 일자
        sht_cd (str): 공백: 전체,  특정종목 조회시 : 종목코드
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 예탁원정보(주주총회일정) 데이터
        
    Example:
        >>> df = ksdinfo_sharehld_meet(" ", "20230101", "20231231", " ")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ksdinfo/sharehld-meet"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not f_dt:
        logger.error("f_dt is required. (e.g. '20230101')")
        raise ValueError("f_dt is required. (e.g. '20230101')")

    if not t_dt:
        logger.error("t_dt is required. (e.g. '20231231')")
        raise ValueError("t_dt is required. (e.g. '20231231')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "HHKDB669111C0"

    params = {
        "CTS": cts,
        "F_DT": f_dt,
        "T_DT": t_dt,
        "SHT_CD": sht_cd,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output1'):
            current_data = pd.DataFrame(res.getBody().output1)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return ksdinfo_sharehld_meet(
                cts,
                f_dt,
                t_dt,
                sht_cd,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 당사 대주가능 종목 [국내주식-195]
##############################################################################################

def lendable_by_company(
        excg_dvsn_cd: str,  # 거래소구분코드
        pdno: str,  # 상품번호
        thco_stln_psbl_yn: str,  # 당사대주가능여부
        inqr_dvsn_1: str,  # 조회구분1
        ctx_area_fk200: str,  # 연속조회검색조건200
        ctx_area_nk100: str,  # 연속조회키100
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        tr_cont: str = "",
        depth: int = 0,
        max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 종목정보 
    당사 대주가능 종목[국내주식-195]
    당사 대주가능 종목 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        excg_dvsn_cd (str): 00(전체), 02(거래소), 03(코스닥)
        pdno (str): 공백 : 전체조회, 종목코드 입력 시 해당종목만 조회
        thco_stln_psbl_yn (str): Y
        inqr_dvsn_1 (str): 0 : 전체조회, 1: 종목코드순 정렬
        ctx_area_fk200 (str): 미입력 (다음조회 불가)
        ctx_area_nk100 (str): 미입력 (다음조회 불가)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 당사 대주가능 종목 데이터
        
    Example:
        >>> df1, df2 = lendable_by_company('00', '', 'Y', '0', '', '')
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/lendable-by-company"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not excg_dvsn_cd:
        logger.error("excg_dvsn_cd is required. (e.g. '00')")
        raise ValueError("excg_dvsn_cd is required. (e.g. '00')")

    if not thco_stln_psbl_yn:
        logger.error("thco_stln_psbl_yn is required. (e.g. 'Y')")
        raise ValueError("thco_stln_psbl_yn is required. (e.g. 'Y')")

    if not inqr_dvsn_1:
        logger.error("inqr_dvsn_1 is required. (e.g. '0')")
        raise ValueError("inqr_dvsn_1 is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()

    tr_id = "CTSC2702R"

    params = {
        "EXCG_DVSN_CD": excg_dvsn_cd,
        "PDNO": pdno,
        "THCO_STLN_PSBL_YN": thco_stln_psbl_yn,
        "INQR_DVSN_1": inqr_dvsn_1,
        "CTX_AREA_FK200": ctx_area_fk200,
        "CTX_AREA_NK100": ctx_area_nk100,
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                # output1은 단일 객체, output2는 배열일 수 있음
                if isinstance(output_data, list):
                    current_data1 = pd.DataFrame(output_data)
                else:
                    # 단일 객체인 경우 리스트로 감싸서 DataFrame 생성
                    current_data1 = pd.DataFrame([output_data])

                if dataframe1 is not None:
                    dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
                else:
                    dataframe1 = current_data1
            else:
                if dataframe1 is None:
                    dataframe1 = pd.DataFrame()
        else:
            if dataframe1 is None:
                dataframe1 = pd.DataFrame()
        # output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                # output1은 단일 객체, output2는 배열일 수 있음
                if isinstance(output_data, list):
                    current_data2 = pd.DataFrame(output_data)
                else:
                    # 단일 객체인 경우 리스트로 감싸서 DataFrame 생성
                    current_data2 = pd.DataFrame([output_data])

                if dataframe2 is not None:
                    dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
                else:
                    dataframe2 = current_data2
            else:
                if dataframe2 is None:
                    dataframe2 = pd.DataFrame()
        else:
            if dataframe2 is None:
                dataframe2 = pd.DataFrame()
        tr_cont = res.getHeader().tr_cont

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return lendable_by_company(
                excg_dvsn_cd,
                pdno,
                thco_stln_psbl_yn,
                inqr_dvsn_1,
                ctx_area_fk200,
                ctx_area_nk100,
                dataframe1, dataframe2, "N", depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 순위분석 > 국내주식 시가총액 상위 [v1_국내주식-091]
##############################################################################################

def market_cap(
        fid_input_price_2: str,  # 입력 가격2
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_trgt_cls_code: str,  # 대상 구분 코드
        fid_trgt_exls_cls_code: str,  # 대상 제외 구분 코드
        fid_input_price_1: str,  # 입력 가격1
        fid_vol_cnt: str,  # 거래량 수
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None  # 누적 데이터프레임
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 시가총액 상위[v1_국내주식-091]
    국내주식 시가총액 상위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_input_price_2 (str): 입력값 없을때 전체 (~ 가격)
        fid_cond_mrkt_div_code (str): 시장구분코드 (J:KRX, NX:NXT)
        fid_cond_scr_div_code (str): Unique key( 20174 )
        fid_div_cls_code (str): 0: 전체,  1:보통주,  2:우선주
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200
        fid_trgt_cls_code (str): 0 : 전체
        fid_trgt_exls_cls_code (str): 0 : 전체
        fid_input_price_1 (str): 입력값 없을때 전체 (가격 ~)
        fid_vol_cnt (str): 입력값 없을때 전체 (거래량 ~)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 시가총액 상위 데이터
        
    Example:
        >>> df = market_cap(
        ...     fid_input_price_2="",
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_cond_scr_div_code="20174",
        ...     fid_div_cls_code="0",
        ...     fid_input_iscd="0000",
        ...     fid_trgt_cls_code="0",
        ...     fid_trgt_exls_cls_code="0",
        ...     fid_input_price_1="",
        ...     fid_vol_cnt=""
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/market-cap"
    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code != "J":
        raise ValueError("조건 시장 분류 코드 확인요망!!!")
    if fid_cond_scr_div_code != "20174":
        raise ValueError("조건 화면 분류 코드 확인요망!!!")
    if fid_div_cls_code not in ["0", "1", "2"]:
        raise ValueError("분류 구분 코드 확인요망!!!")
    if fid_input_iscd not in ["0000", "0001", "1001", "2001"]:
        raise ValueError("입력 종목코드 확인요망!!!")
    if fid_trgt_cls_code != "0":
        raise ValueError("대상 구분 코드 확인요망!!!")
    if fid_trgt_exls_cls_code != "0":
        raise ValueError("대상 제외 구분 코드 확인요망!!!")

    tr_id = "FHPST01740000"

    params = {
        "fid_input_price_2": fid_input_price_2,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_input_iscd": fid_input_iscd,
        "fid_trgt_cls_code": fid_trgt_cls_code,
        "fid_trgt_exls_cls_code": fid_trgt_exls_cls_code,
        "fid_input_price_1": fid_input_price_1,
        "fid_vol_cnt": fid_vol_cnt,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
        current_data = pd.DataFrame(res.getBody().output) if hasattr(res.getBody(), 'output') else pd.DataFrame()

        # 기존 데이터프레임과 병합
        dataframe = pd.concat([dataframe, current_data], ignore_index=True) if dataframe is not None else current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont
        if tr_cont == "M":
            print("Call Next")
            ka.smart_sleep()
            return market_cap(
                fid_input_price_2,
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_div_cls_code,
                fid_input_iscd,
                fid_trgt_cls_code,
                fid_trgt_exls_cls_code,
                fid_input_price_1,
                fid_vol_cnt,
                "N", dataframe
            )
        else:
            print("The End")
            return dataframe
    else:
        # 오류 출력
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 업종/기타 > 국내선물 영업일조회 [국내주식-160]
##############################################################################################

def market_time() -> pd.DataFrame:
    """
    국내선물 영업일조회 API입니다.
    API호출 시 body 혹은 params로 입력하는 사항이 없습니다.
    
    Returns:
        pd.DataFrame: 국내선물 영업일조회 데이터
        
    Example:
        >>> df = market_time()
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/market-time"

    tr_id = "HHMCM000002C0"  # 국내선물 영업일조회

    params = {}

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        result = pd.DataFrame([res.getBody().output1])
        return result
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 순위분석 > 국내주식 시장가치 순위[v1_국내주식-096]
##############################################################################################

def market_value(
        fid_trgt_cls_code: str,  # 대상 구분 코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_input_price_1: str,  # 입력 가격1
        fid_input_price_2: str,  # 입력 가격2
        fid_vol_cnt: str,  # 거래량 수
        fid_input_option_1: str,  # 입력 옵션1
        fid_input_option_2: str,  # 입력 옵션2
        fid_rank_sort_cls_code: str,  # 순위 정렬 구분 코드
        fid_blng_cls_code: str,  # 소속 구분 코드
        fid_trgt_exls_cls_code: str,  # 대상 제외 구분 코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None  # 누적 데이터프레임
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 시장가치 순위[v1_국내주식-096]
    국내주식 시장가치 순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_trgt_cls_code (str): 0 : 전체
        fid_cond_mrkt_div_code (str): 시장구분코드 (J:KRX, NX:NXT)
        fid_cond_scr_div_code (str): Unique key( 20179 )
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200
        fid_div_cls_code (str): 0: 전체, 1:관리종목, 2:투자주의, 3:투자경고, 4:투자위험예고, 5:투자위험, 6:보통주, 7:우선주
        fid_input_price_1 (str): 입력값 없을때 전체 (가격 ~)
        fid_input_price_2 (str): 입력값 없을때 전체 (~ 가격)
        fid_vol_cnt (str): 입력값 없을때 전체 (거래량 ~)
        fid_input_option_1 (str): 회계연도 입력 (ex 2023)
        fid_input_option_2 (str): 0: 1/4분기 , 1: 반기, 2: 3/4분기, 3: 결산
        fid_rank_sort_cls_code (str): '가치분석(23:PER, 24:PBR, 25:PCR, 26:PSR, 27: EPS, 28:EVA, 29: EBITDA, 30: EV/EBITDA, 31:EBITDA/금융비율'
        fid_blng_cls_code (str): 0 : 전체
        fid_trgt_exls_cls_code (str): 0 : 전체
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 시장가치 순위 데이터
        
    Example:
        >>> df = market_value(
        ...     fid_trgt_cls_code="0",
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_cond_scr_div_code="20179",
        ...     fid_input_iscd="0000",
        ...     fid_div_cls_code="0",
        ...     fid_input_price_1="",
        ...     fid_input_price_2="",
        ...     fid_vol_cnt="",
        ...     fid_input_option_1="2023",
        ...     fid_input_option_2="3",
        ...     fid_rank_sort_cls_code="23",
        ...     fid_blng_cls_code="0",
        ...     fid_trgt_exls_cls_code="0"
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/market-value"
    # 필수 파라미터 검증
    if fid_trgt_cls_code not in ["0"]:
        raise ValueError("대상 구분 코드 확인요망!!!")
    if fid_cond_mrkt_div_code not in ["J"]:
        raise ValueError("조건 시장 분류 코드 확인요망!!!")
    if fid_cond_scr_div_code != "20179":
        raise ValueError("조건 화면 분류 코드 확인요망!!!")
    if fid_input_iscd not in ["0000", "0001", "1001", "2001"]:
        raise ValueError("입력 종목코드 확인요망!!!")
    if fid_div_cls_code not in ["0", "1", "2", "3", "4", "5", "6", "7"]:
        raise ValueError("분류 구분 코드 확인요망!!!")
    if fid_input_option_2 not in ["0", "1", "2", "3"]:
        raise ValueError("입력 옵션2 확인요망!!!")
    if fid_rank_sort_cls_code not in ["23", "24", "25", "26", "27", "28", "29", "30", "31"]:
        raise ValueError("순위 정렬 구분 코드 확인요망!!!")
    if fid_blng_cls_code not in ["0"]:
        raise ValueError("소속 구분 코드 확인요망!!!")
    if fid_trgt_exls_cls_code not in ["0"]:
        raise ValueError("대상 제외 구분 코드 확인요망!!!")

    tr_id = "FHPST01790000"

    params = {
        "fid_trgt_cls_code": fid_trgt_cls_code,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_input_iscd": fid_input_iscd,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_input_price_1": fid_input_price_1,
        "fid_input_price_2": fid_input_price_2,
        "fid_vol_cnt": fid_vol_cnt,
        "fid_input_option_1": fid_input_option_1,
        "fid_input_option_2": fid_input_option_2,
        "fid_rank_sort_cls_code": fid_rank_sort_cls_code,
        "fid_blng_cls_code": fid_blng_cls_code,
        "fid_trgt_exls_cls_code": fid_trgt_exls_cls_code,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            print("Call Next")
            ka.smart_sleep()
            return market_value(
                fid_trgt_cls_code,
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_div_cls_code,
                fid_input_price_1,
                fid_input_price_2,
                fid_vol_cnt,
                fid_input_option_1,
                fid_input_option_2,
                fid_rank_sort_cls_code,
                fid_blng_cls_code,
                fid_trgt_exls_cls_code,
                "N", dataframe
            )
        else:
            print("The End")
            return dataframe
    else:
        # 오류 처리
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 국내 증시자금 종합 [국내주식-193]
##############################################################################################

def mktfunds(
        fid_input_date_1: str = ""
) -> pd.DataFrame:
    """
    국내 증시자금 종합 API입니다. 
    한국투자 HTS(eFriend Plus) > [0470] 증시자금 종합 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다. (단위: 억원)

    ※ 해당자료는 금융투자협회의 자료를 제공하고 있으며, 오류와 지연이 발생할 수 있습니다.
    ※ 위 정보에 의한 투자판단의 최종책임은 정보이용자에게 있으며, 당사와 한국금융투자협회는 어떠한 법적인 책임도 지지 않사오니 투자에 참고로만 이용하시기 바랍니다.
    
    Args:
        fid_input_date_1 (str): [입력날짜]
        
    Returns:
        pd.DataFrame: 국내 증시자금 종합 데이터
        
    Example:
        >>> df = mktfunds()
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/mktfunds"

    tr_id = "FHKST649100C0"

    params = {
        "FID_INPUT_DATE_1": fid_input_date_1
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 순위분석 > 국내주식 신고_신저근접종목 상위[v1_국내주식-105]
##############################################################################################

def near_new_highlow(
        fid_aply_rang_vol: str,  # 적용 범위 거래량
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_input_cnt_1: str,  # 입력 수1
        fid_input_cnt_2: str,  # 입력 수2
        fid_prc_cls_code: str,  # 가격 구분 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_trgt_cls_code: str,  # 대상 구분 코드
        fid_trgt_exls_cls_code: str,  # 대상 제외 구분 코드
        fid_aply_rang_prc_1: str,  # 적용 범위 가격1
        fid_aply_rang_prc_2: str,  # 적용 범위 가격2
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None  # 누적 데이터프레임
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 신고_신저근접종목 상위[v1_국내주식-105]
    국내주식 신고_신저근접종목 상위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_aply_rang_vol (str): 0: 전체, 100: 100주 이상
        fid_cond_mrkt_div_code (str): 시장구분코드 (주식 J)
        fid_cond_scr_div_code (str): Unique key(20187)
        fid_div_cls_code (str): 0:전체, 1:관리종목, 2:투자주의, 3:투자경고
        fid_input_cnt_1 (str): 괴리율 최소
        fid_input_cnt_2 (str): 괴리율 최대
        fid_prc_cls_code (str): 0:신고근접, 1:신저근접
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100
        fid_trgt_cls_code (str): 0: 전체
        fid_trgt_exls_cls_code (str): 0:전체, 1:관리종목, 2:투자주의, 3:투자경고, 4:투자위험예고, 5:투자위험, 6:보통주, 7:우선주
        fid_aply_rang_prc_1 (str): 가격 ~
        fid_aply_rang_prc_2 (str): ~ 가격
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 신고_신저근접종목 상위 데이터
        
    Example:
        >>> df = near_new_highlow(
        ...     fid_aply_rang_vol="0",
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_cond_scr_div_code="20187",
        ...     fid_div_cls_code="0",
        ...     fid_input_cnt_1="0",
        ...     fid_input_cnt_2="100",
        ...     fid_prc_cls_code="0",
        ...     fid_input_iscd="0000",
        ...     fid_trgt_cls_code="0",
        ...     fid_trgt_exls_cls_code="0",
        ...     fid_aply_rang_prc_1="0",
        ...     fid_aply_rang_prc_2="1000000"
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/near-new-highlow"
    # 필수 파라미터 검증
    if fid_aply_rang_vol not in ["0", "100"]:
        raise ValueError("적용 범위 거래량 확인요망!!!")
    if fid_cond_mrkt_div_code != "J":
        raise ValueError("조건 시장 분류 코드 확인요망!!!")
    if fid_cond_scr_div_code != "20187":
        raise ValueError("조건 화면 분류 코드 확인요망!!!")
    if fid_div_cls_code not in ["0", "1", "2", "3"]:
        raise ValueError("분류 구분 코드 확인요망!!!")
    if fid_prc_cls_code not in ["0", "1"]:
        raise ValueError("가격 구분 코드 확인요망!!!")
    if fid_input_iscd not in ["0000", "0001", "1001", "2001", "4001"]:
        raise ValueError("입력 종목코드 확인요망!!!")
    if fid_trgt_cls_code != "0":
        raise ValueError("대상 구분 코드 확인요망!!!")
    if fid_trgt_exls_cls_code not in ["0", "1", "2", "3", "4", "5", "6", "7"]:
        raise ValueError("대상 제외 구분 코드 확인요망!!!")

    tr_id = "FHPST01870000"

    params = {
        "fid_aply_rang_vol": fid_aply_rang_vol,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_input_cnt_1": fid_input_cnt_1,
        "fid_input_cnt_2": fid_input_cnt_2,
        "fid_prc_cls_code": fid_prc_cls_code,
        "fid_input_iscd": fid_input_iscd,
        "fid_trgt_cls_code": fid_trgt_cls_code,
        "fid_trgt_exls_cls_code": fid_trgt_exls_cls_code,
        "fid_aply_rang_prc_1": fid_aply_rang_prc_1,
        "fid_aply_rang_prc_2": fid_aply_rang_prc_2,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        # 기존 데이터프레임과 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            print("Call Next")
            ka.smart_sleep()
            return near_new_highlow(
                fid_aply_rang_vol,
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_div_cls_code,
                fid_input_cnt_1,
                fid_input_cnt_2,
                fid_prc_cls_code,
                fid_input_iscd,
                fid_trgt_cls_code,
                fid_trgt_exls_cls_code,
                fid_aply_rang_prc_1,
                fid_aply_rang_prc_2,
                "N", dataframe
            )
        else:
            print("The End")
            return dataframe
    else:
        # 오류 발생 시 처리
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 종합 시황/공시(제목) [국내주식-141]
##############################################################################################

def news_title(
        fid_news_ofer_entp_code: str,  # 뉴스 제공 업체 코드
        fid_cond_mrkt_cls_code: str,  # 조건 시장 구분 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_titl_cntt: str,  # 제목 내용
        fid_input_date_1: str,  # 입력 날짜
        fid_input_hour_1: str,  # 입력 시간
        fid_rank_sort_cls_code: str,  # 순위 정렬 구분 코드
        fid_input_srno: str,  # 입력 일련번호
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 업종/기타 
    종합 시황_공시(제목)[국내주식-141]
    종합 시황_공시(제목) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_news_ofer_entp_code (str): 뉴스 제공 업체 코드
        fid_cond_mrkt_cls_code (str): 조건 시장 구분 코드
        fid_input_iscd (str): 입력 종목코드
        fid_titl_cntt (str): 제목 내용
        fid_input_date_1 (str): 입력 날짜
        fid_input_hour_1 (str): 입력 시간
        fid_rank_sort_cls_code (str): 순위 정렬 구분 코드
        fid_input_srno (str): 입력 일련번호
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 종합 시황_공시(제목) 데이터
        
    Example:
        >>> df = news_title(
        ...     fid_news_ofer_entp_code='2',
        ...     fid_cond_mrkt_cls_code='00',
        ...     fid_input_iscd='005930',
        ...     fid_titl_cntt='',
        ...     fid_input_date_1='20231010',
        ...     fid_input_hour_1='090000',
        ...     fid_rank_sort_cls_code='01',
        ...     fid_input_srno='1'
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/news-title"
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # API URL 및 거래 ID 설정
    tr_id = "FHKST01011800"

    # 요청 파라미터 설정
    params = {
        "FID_NEWS_OFER_ENTP_CODE": fid_news_ofer_entp_code,
        "FID_COND_MRKT_CLS_CODE": fid_cond_mrkt_cls_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_TITL_CNTT": fid_titl_cntt,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_HOUR_1": fid_input_hour_1,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_INPUT_SRNO": fid_input_srno,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    # API 응답 처리
    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return news_title(
                fid_news_ofer_entp_code,
                fid_cond_mrkt_cls_code,
                fid_input_iscd,
                fid_titl_cntt,
                fid_input_date_1,
                fid_input_hour_1,
                fid_rank_sort_cls_code,
                fid_input_srno,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 주식주문(현금)[v1_국내주식-001]
##############################################################################################

def order_cash(
        env_dv: str,  # 실전모의구분 (real:실전, demo:모의)
        ord_dv: str,  # 매도매수구분 (buy:매수, sell:매도)
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        pdno: str,  # 상품번호 (종목코드)
        ord_dvsn: str,  # 주문구분
        ord_qty: str,  # 주문수량
        ord_unpr: str,  # 주문단가
        excg_id_dvsn_cd: str,  # 거래소ID구분코드
        sll_type: str = "",  # 매도유형 (매도주문 시)
        cndt_pric: str = ""  # 조건가격
) -> pd.DataFrame:
    """
    국내주식주문(현금) API 입니다.

    ※ TTC0802U(현금매수) 사용하셔서 미수매수 가능합니다. 단, 거래하시는 계좌가 증거금40%계좌로 신청이 되어있어야 가능합니다. 
    ※ 신용매수는 별도의 API가 준비되어 있습니다.

    ※ ORD_QTY(주문수량), ORD_UNPR(주문단가) 등을 String으로 전달해야 함에 유의 부탁드립니다.

    ※ ORD_UNPR(주문단가)가 없는 주문은 상한가로 주문금액을 선정하고 이후 체결이되면 체결금액로 정산됩니다.

    ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)

    ※ 종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
    
    Args:
        env_dv (str): [필수] 실전모의구분 (real:실전, demo:모의)
        ord_dv (str): [필수] 매도매수구분 (buy:매수, sell:매도)
        cano (str): [필수] 종합계좌번호 (종합계좌번호)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (상품유형코드)
        pdno (str): [필수] 상품번호 (종목코드(6자리) , ETN의 경우 7자리 입력)
        ord_dvsn (str): [필수] 주문구분
        ord_qty (str): [필수] 주문수량
        ord_unpr (str): [필수] 주문단가
        excg_id_dvsn_cd (str): [필수] 거래소ID구분코드 (KRX)
        sll_type (str): 매도유형 (매도주문 시) (01:일반매도,02:임의매매,05:대차매도)
        cndt_pric (str): 조건가격 (스탑지정가호가 주문 시 사용)

    Returns:
        pd.DataFrame: 주식주문 결과 데이터
        
    Example:
        >>> df = order_cash(env_dv="demo", ord_dv="buy", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, pdno="005930", ord_dvsn="00", ord_qty="1", ord_unpr="70000", excg_id_dvsn_cd="KRX")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/trading/order-cash"

    # 필수 파라미터 검증
    if env_dv == "" or env_dv is None:
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")

    if ord_dv == "" or ord_dv is None:
        raise ValueError("ord_dv is required (e.g. 'buy:매수, sell:매도')")

    if cano == "" or cano is None:
        raise ValueError("cano is required (e.g. '종합계좌번호')")

    if acnt_prdt_cd == "" or acnt_prdt_cd is None:
        raise ValueError("acnt_prdt_cd is required (e.g. '상품유형코드')")

    if pdno == "" or pdno is None:
        raise ValueError("pdno is required (e.g. '종목코드(6자리) , ETN의 경우 7자리 입력')")

    if ord_dvsn == "" or ord_dvsn is None:
        raise ValueError("ord_dvsn is required (e.g. '')")

    if ord_qty == "" or ord_qty is None:
        raise ValueError("ord_qty is required (e.g. '')")

    if ord_unpr == "" or ord_unpr is None:
        raise ValueError("ord_unpr is required (e.g. '')")

    if excg_id_dvsn_cd == "" or excg_id_dvsn_cd is None:
        raise ValueError("excg_id_dvsn_cd is required (e.g. 'KRX')")

    # tr_id 설정
    if env_dv == "real":
        if ord_dv == "sell":
            tr_id = "TTTC0011U"
        elif ord_dv == "buy":
            tr_id = "TTTC0012U"
        else:
            raise ValueError("ord_dv can only be sell or buy")
    elif env_dv == "demo":
        if ord_dv == "sell":
            tr_id = "VTTC0011U"
        elif ord_dv == "buy":
            tr_id = "VTTC0012U"
        else:
            raise ValueError("ord_dv can only be sell or buy")
    else:
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")

    params = {
        "CANO": cano,  # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "PDNO": pdno,  # 상품번호
        "ORD_DVSN": ord_dvsn,  # 주문구분
        "ORD_QTY": ord_qty,  # 주문수량
        "ORD_UNPR": ord_unpr,  # 주문단가
        "EXCG_ID_DVSN_CD": excg_id_dvsn_cd,  # 거래소ID구분코드
        "SLL_TYPE": sll_type,  # 매도유형
        "CNDT_PRIC": cndt_pric  # 조건가격
    }

    res = ka._url_fetch(api_url, tr_id, "", params, postFlag=True)

    if res.isOK():
        current_data = pd.DataFrame([res.getBody().output])
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 주식주문(신용)[v1_국내주식-002]
##############################################################################################

def order_credit(
        ord_dv: str,  # 매수매도구분 (buy:매수, sell:매도)
        cano: str,  # 종합계좌번호 (12345678)
        acnt_prdt_cd: str,  # 계좌상품코드 (01)
        pdno: str,  # 상품번호 (123456)
        crdt_type: str,  # 신용유형
        loan_dt: str,  # 대출일자
        ord_dvsn: str,  # 주문구분
        ord_qty: str,  # 주문수량
        ord_unpr: str,  # 주문단가
        excg_id_dvsn_cd: str = "",  # 거래소ID구분코드 (KRX:한국거래소, NXT:넥스트레이드, SOR:SOR)
        sll_type: str = "",  # 매도유형
        rsvn_ord_yn: str = "",  # 예약주문여부 (Y: 예약주문, N: 신용주문)
        emgc_ord_yn: str = "",  # 비상주문여부
        pgtr_dvsn: str = "",  # 프로그램매매구분
        mgco_aptm_odno: str = "",  # 운용사지정주문번호
        lqty_tr_ngtn_dtl_no: str = "",  # 대량거래협상상세번호
        lqty_tr_agmt_no: str = "",  # 대량거래협정번호
        lqty_tr_ngtn_id: str = "",  # 대량거래협상자Id
        lp_ord_yn: str = "",  # LP주문여부
        mdia_odno: str = "",  # 매체주문번호
        ord_svr_dvsn_cd: str = "",  # 주문서버구분코드
        pgm_nmpr_stmt_dvsn_cd: str = "",  # 프로그램호가신고구분코드
        cvrg_slct_rson_cd: str = "",  # 반대매매선정사유코드
        cvrg_seq: str = "",  # 반대매매순번
        cndt_pric: str = ""  # 조건가격
) -> pd.DataFrame:
    """
    국내주식주문(신용) API입니다. 
    ※ 모의투자는 사용 불가합니다.

    ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)
    
    Args:
        ord_dv (str): [필수] 매수매도구분 (ex. buy:매수, sell:매도)
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 01)
        pdno (str): [필수] 상품번호 (ex. 123456)
        crdt_type (str): [필수] 신용유형 (ex. [매도] 22:유통대주신규, 24:자기대주신규, 25:자기융자상환, 27:유통융자상환 / [매수] 21:자기융자신규, 23:유통융자신규 , 26:유통대주상환, 28:자기대주상환)
        loan_dt (str): [필수] 대출일자 (ex. [신용매수] 오늘날짜(yyyyMMdd), [신용매도] 매도할 종목의 대출일자(yyyyMMdd))
        ord_dvsn (str): [필수] 주문구분 
        ord_qty (str): [필수] 주문수량
        ord_unpr (str): [필수] 주문단가
        excg_id_dvsn_cd (str): 거래소ID구분코드 (ex. KRX:한국거래소, NXT:넥스트레이드, SOR:SOR)
        sll_type (str): 매도유형
        rsvn_ord_yn (str): 예약주문여부 (ex. Y: 예약주문, N: 신용주문)
        emgc_ord_yn (str): 비상주문여부
        pgtr_dvsn (str): 프로그램매매구분
        mgco_aptm_odno (str): 운용사지정주문번호
        lqty_tr_ngtn_dtl_no (str): 대량거래협상상세번호
        lqty_tr_agmt_no (str): 대량거래협정번호
        lqty_tr_ngtn_id (str): 대량거래협상자Id
        lp_ord_yn (str): LP주문여부
        mdia_odno (str): 매체주문번호
        ord_svr_dvsn_cd (str): 주문서버구분코드
        pgm_nmpr_stmt_dvsn_cd (str): 프로그램호가신고구분코드
        cvrg_slct_rson_cd (str): 반대매매선정사유코드
        cvrg_seq (str): 반대매매순번
        cndt_pric (str): 조건가격

    Returns:
        pd.DataFrame: 주식주문(신용) 결과 데이터
        
    Example:
        >>> df = order_credit(ord_dv="buy", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, pdno="005930", crdt_type="21", loan_dt="20220810", ord_dvsn="00", ord_qty="1", ord_unpr="55000")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/trading/order-credit"

    # 필수 파라미터 검증
    if ord_dv == "" or ord_dv is None:
        raise ValueError("ord_dv is required (e.g. 'buy:매수, sell:매도')")

    if cano == "" or cano is None:
        raise ValueError("cano is required (e.g. '12345678')")

    if acnt_prdt_cd == "" or acnt_prdt_cd is None:
        raise ValueError("acnt_prdt_cd is required (e.g. '01')")

    if pdno == "" or pdno is None:
        raise ValueError("pdno is required (e.g. '123456')")

    if crdt_type == "" or crdt_type is None:
        raise ValueError(
            "crdt_type is required (e.g. '[매도] 22:유통대주신규, 24:자기대주신규, 25:자기융자상환, 27:유통융자상환 / [매수] 21:자기융자신규, 23:유통융자신규 , 26:유통대주상환, 28:자기대주상환')")

    if loan_dt == "" or loan_dt is None:
        raise ValueError("loan_dt is required (e.g. '[신용매수] 오늘날짜(yyyyMMdd), [신용매도] 매도할 종목의 대출일자(yyyyMMdd)')")

    if ord_dvsn == "" or ord_dvsn is None:
        raise ValueError("ord_dvsn is required")

    if ord_qty == "" or ord_qty is None:
        raise ValueError("ord_qty is required")

    if ord_unpr == "" or ord_unpr is None:
        raise ValueError("ord_unpr is required")

    # tr_id 설정
    if ord_dv == "buy":
        tr_id = "TTTC0052U"
    elif ord_dv == "sell":
        tr_id = "TTTC0051U"
    else:
        raise ValueError("ord_dv can only be buy or sell")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "CRDT_TYPE": crdt_type,
        "LOAN_DT": loan_dt,
        "ORD_DVSN": ord_dvsn,
        "ORD_QTY": ord_qty,
        "ORD_UNPR": ord_unpr
    }

    # 옵션 파라미터 추가
    if excg_id_dvsn_cd:
        params["EXCG_ID_DVSN_CD"] = excg_id_dvsn_cd
    if sll_type:
        params["SLL_TYPE"] = sll_type
    if rsvn_ord_yn:
        params["RSVN_ORD_YN"] = rsvn_ord_yn
    if emgc_ord_yn:
        params["EMGC_ORD_YN"] = emgc_ord_yn
    if pgtr_dvsn:
        params["PGTR_DVSN"] = pgtr_dvsn
    if mgco_aptm_odno:
        params["MGCO_APTM_ODNO"] = mgco_aptm_odno
    if lqty_tr_ngtn_dtl_no:
        params["LQTY_TR_NGTN_DTL_NO"] = lqty_tr_ngtn_dtl_no
    if lqty_tr_agmt_no:
        params["LQTY_TR_AGMT_NO"] = lqty_tr_agmt_no
    if lqty_tr_ngtn_id:
        params["LQTY_TR_NGTN_ID"] = lqty_tr_ngtn_id
    if lp_ord_yn:
        params["LP_ORD_YN"] = lp_ord_yn
    if mdia_odno:
        params["MDIA_ODNO"] = mdia_odno
    if ord_svr_dvsn_cd:
        params["ORD_SVR_DVSN_CD"] = ord_svr_dvsn_cd
    if pgm_nmpr_stmt_dvsn_cd:
        params["PGM_NMPR_STMT_DVSN_CD"] = pgm_nmpr_stmt_dvsn_cd
    if cvrg_slct_rson_cd:
        params["CVRG_SLCT_RSON_CD"] = cvrg_slct_rson_cd
    if cvrg_seq:
        params["CVRG_SEQ"] = cvrg_seq
    if cndt_pric:
        params["CNDT_PRIC"] = cndt_pric

    res = ka._url_fetch(api_url, tr_id, "", params, postFlag=True)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output, index=[0])
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 주식예약주문[v1_국내주식-017]
##############################################################################################

def order_resv(
        cano: str,
        acnt_prdt_cd: str,
        pdno: str,
        ord_qty: str,
        ord_unpr: str,
        sll_buy_dvsn_cd: str,
        ord_dvsn_cd: str,
        ord_objt_cblc_dvsn_cd: str,
        loan_dt: Optional[str] = "",
        rsvn_ord_end_dt: Optional[str] = "",
        ldng_dt: Optional[str] = ""
) -> pd.DataFrame:
    """
    국내주식 예약주문 매수/매도 API 입니다.

    ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)

    ※ 유의사항
    1. 예약주문 가능시간 : 15시 40분 ~ 다음 영업일 7시 30분 
        (단, 서버 초기화 작업 시 예약주문 불가 : 23시 40분 ~ 00시 10분)
        ※ 예약주문 처리내역은 통보되지 않으므로 주문처리일 장 시작전에 반드시 주문처리 결과를 확인하시기 바랍니다.

    2. 예약주문 안내
    - 예약종료일 미입력 시 일반예약주문으로 최초 도래하는 영업일에 주문 전송됩니다.
    - 예약종료일 입력 시 기간예약주문으로 최초 예약주문수량 중 미체결 된 수량에 대해 예약종료일까지 매 영업일 주문이
        실행됩니다. (예약종료일은 익영업일부터 달력일 기준으로 공휴일 포함하여 최대 30일이 되는 일자까지 입력가능)
    - 예약주문 접수 처리순서는 일반/기간예약주문 중 신청일자가 빠른 주문이 우선합니다.
        단, 기간예약주문 자동배치시간(약 15시35분 ~ 15시55분)사이 접수되는 주문의 경우 당일에 한해 순서와 상관없이
        처리될 수 있습니다.
    - 기간예약주문 자동배치시간(약 15시35분 ~ 15시55분)에는 예약주문 조회가 제한 될 수 있습니다.
    - 기간예약주문은 계좌 당 주문건수 최대 1,000건으로 제한됩니다.

    3. 예약주문 접수내역 중 아래의 사유 등으로 인해 주문이 거부될 수 있사오니, 주문처리일 장 시작전에 반드시
        주문처리 결과를 확인하시기 바랍니다.
        * 주문처리일 기준 : 매수가능금액 부족, 매도가능수량 부족, 주문수량/호가단위 오류, 대주 호가제한, 
                                신용/대주가능종목 변경, 상/하한폭 변경, 시가형성 종목(신규상장 등)의 시장가, 거래서비스 미신청 등

    4. 익일 예상 상/하한가는 조회시점의 현재가로 계산되며 익일의 유/무상증자, 배당, 감자, 합병, 액면변경 등에 의해
        변동될 수 있으며 이로 인해 상/하한가를 벗어나 주문이 거부되는 경우가 발생할 수 있사오니, 주문처리일 장 시작전에
        반드시 주문처리결과를 확인하시기 바랍니다.

    5. 정리매매종목, ELW, 신주인수권증권, 신주인수권증서 등은 가격제한폭(상/하한가) 적용 제외됩니다.

    6. 영업일 장 시작 후 [기간예약주문] 내역 취소는 해당시점 이후의 예약주문이 취소되는 것으로, 
        일반주문으로 이미 전환된 주문에는 영향을 미치지 않습니다. 반드시 장 시작전 주문처리결과를 확인하시기 바랍니다. 
    
    Args:
        cano (str): [필수] 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        pdno (str): [필수] 종목코드(6자리)
        ord_qty (str): [필수] 주문수량 (주0문주식수)
        ord_unpr (str): [필수] 주문단가 (1주당 가격, 시장가/장전 시간외는 0 입력)
        sll_buy_dvsn_cd (str): [필수] 매도매수구분코드 (01 : 매도, 02 : 매수)
        ord_dvsn_cd (str): [필수] 주문구분코드 (00 : 지정가, 01 : 시장가, 02 : 조건부지정가, 05 : 장전 시간외)
        ord_objt_cblc_dvsn_cd (str): [필수] 주문대상잔고구분코드 (10: 현금, 12~28: 각종 대출/상환코드)
        loan_dt (Optional[str]): 대출일자
        rsvn_ord_end_dt (Optional[str]): 예약주문종료일자 (YYYYMMDD, 익영업일부터 최대 30일 이내)
        ldng_dt (Optional[str]): 대여일자

    Returns:
        pd.DataFrame: 예약주문 결과 데이터
        
    Example:
        >>> df = order_resv(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, pdno="005930", ord_qty="1", ord_unpr="55000", sll_buy_dvsn_cd="02", ord_dvsn_cd="00", ord_objt_cblc_dvsn_cd="10")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/trading/order-resv"

    if cano == "" or cano is None:
        raise ValueError("cano is required (e.g. '계좌번호 체계(8-2)의 앞 8자리')")

    if acnt_prdt_cd == "" or acnt_prdt_cd is None:
        raise ValueError("acnt_prdt_cd is required (e.g. '계좌번호 체계(8-2)의 뒤 2자리')")

    if pdno == "" or pdno is None:
        raise ValueError("pdno is required (e.g. '종목코드(6자리)')")

    if ord_qty == "" or ord_qty is None:
        raise ValueError("ord_qty is required (e.g. '주0문주식수')")

    if ord_unpr == "" or ord_unpr is None:
        raise ValueError("ord_unpr is required (e.g. '1주당 가격, 시장가/장전 시간외는 0 입력')")

    if sll_buy_dvsn_cd == "" or sll_buy_dvsn_cd is None:
        raise ValueError("sll_buy_dvsn_cd is required (e.g. '01 : 매도, 02 : 매수')")

    if ord_dvsn_cd == "" or ord_dvsn_cd is None:
        raise ValueError("ord_dvsn_cd is required (e.g. '00 : 지정가, 01 : 시장가, 02 : 조건부지정가, 05 : 장전 시간외')")

    if ord_objt_cblc_dvsn_cd == "" or ord_objt_cblc_dvsn_cd is None:
        raise ValueError("ord_objt_cblc_dvsn_cd is required (e.g. '10: 현금, 12~28: 각종 대출/상환코드')")

    tr_id = "CTSC0008U"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "ORD_QTY": ord_qty,
        "ORD_UNPR": ord_unpr,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "ORD_DVSN_CD": ord_dvsn_cd,
        "ORD_OBJT_CBLC_DVSN_CD": ord_objt_cblc_dvsn_cd
    }

    if loan_dt:
        params["LOAN_DT"] = loan_dt
    if rsvn_ord_end_dt:
        params["RSVN_ORD_END_DT"] = rsvn_ord_end_dt
    if ldng_dt:
        params["LDNG_DT"] = ldng_dt

    res = ka._url_fetch(api_url, tr_id, "", params, postFlag=True)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output, index=[0])
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 주식예약주문조회[v1_국내주식-020]
##############################################################################################

def order_resv_ccnl(
        rsvn_ord_ord_dt: str,  # [필수] 예약주문시작일자
        rsvn_ord_end_dt: str,  # [필수] 예약주문종료일자
        tmnl_mdia_kind_cd: str,  # [필수] 단말매체종류코드 (ex. 00)
        cano: str,  # [필수] 종합계좌번호
        acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 01)
        prcs_dvsn_cd: str,  # [필수] 처리구분코드 (ex. 0)
        cncl_yn: str,  # [필수] 취소여부 (ex. Y)
        rsvn_ord_seq: str = "",  # 예약주문순번
        pdno: str = "",  # 상품번호 (ex. 005930)
        sll_buy_dvsn_cd: str = "",  # 매도매수구분코드 (ex. 01)
        FK200: str = "",  # 연속조회검색조건200
        NK200: str = "",  # 연속조회키200
        tr_cont: str = "",  # 연속거래여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 내부 재귀깊이 (자동관리)
        max_depth: int = 10  # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    국내예약주문 처리내역 조회 API 입니다.
    실전계좌/모의계좌의 경우, 한 번의 호출에 최대 20건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.
    
    Args:
        rsvn_ord_ord_dt (str): [필수] 예약주문시작일자
        rsvn_ord_end_dt (str): [필수] 예약주문종료일자 
        tmnl_mdia_kind_cd (str): [필수] 단말매체종류코드 (ex. 00)
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 01)
        prcs_dvsn_cd (str): [필수] 처리구분코드 (ex. 0)
        cncl_yn (str): [필수] 취소여부 (ex. Y)
        rsvn_ord_seq (str): 예약주문순번
        pdno (str): 상품번호 (ex. 005930)
        sll_buy_dvsn_cd (str): 매도매수구분코드 (ex. 01)
        FK200 (str): 연속조회검색조건200
        NK200 (str): 연속조회키200
        tr_cont (str): 연속거래여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        pd.DataFrame: 주식예약주문조회 데이터
        
    Example:
        >>> df = order_resv_ccnl(
        ...     rsvn_ord_ord_dt="20220729",
        ...     rsvn_ord_end_dt="20220810", 
        ...     tmnl_mdia_kind_cd="00",
        ...     cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod,
        ...     prcs_dvsn_cd="0",
        ...     cncl_yn="Y"
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/trading/order-resv-ccnl"

    # 필수 파라미터 검증
    if rsvn_ord_ord_dt == "":
        raise ValueError("rsvn_ord_ord_dt is required")

    if rsvn_ord_end_dt == "":
        raise ValueError("rsvn_ord_end_dt is required")

    if tmnl_mdia_kind_cd == "":
        raise ValueError("tmnl_mdia_kind_cd is required (e.g. '00')")

    if cano == "":
        raise ValueError("cano is required")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '01')")

    if prcs_dvsn_cd == "":
        raise ValueError("prcs_dvsn_cd is required (e.g. '0')")

    if cncl_yn == "":
        raise ValueError("cncl_yn is required (e.g. 'Y')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    tr_id = "CTSC0004R"  # 주식예약주문조회

    params = {
        "RSVN_ORD_ORD_DT": rsvn_ord_ord_dt,  # 예약주문시작일자
        "RSVN_ORD_END_DT": rsvn_ord_end_dt,  # 예약주문종료일자
        "TMNL_MDIA_KIND_CD": tmnl_mdia_kind_cd,  # 단말매체종류코드
        "CANO": cano,  # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "PRCS_DVSN_CD": prcs_dvsn_cd,  # 처리구분코드
        "CNCL_YN": cncl_yn,  # 취소여부
        "RSVN_ORD_SEQ": rsvn_ord_seq,  # 예약주문순번
        "PDNO": pdno,  # 상품번호
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,  # 매도매수구분코드
        "CTX_AREA_FK200": FK200,  # 연속조회검색조건200
        "CTX_AREA_NK200": NK200  # 연속조회키200
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont
        FK200 = res.getBody().ctx_area_fk200
        NK200 = res.getBody().ctx_area_nk200

        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return order_resv_ccnl(
                rsvn_ord_ord_dt, rsvn_ord_end_dt, tmnl_mdia_kind_cd, cano, acnt_prdt_cd,
                prcs_dvsn_cd, cncl_yn, rsvn_ord_seq, pdno, sll_buy_dvsn_cd,
                FK200, NK200, "N", dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 주식예약주문정정취소[v1_국내주식-018,019]
##############################################################################################

def order_resv_rvsecncl(
        cano: str,  # [필수] 종합계좌번호
        acnt_prdt_cd: str,  # [필수] 계좌상품코드
        rsvn_ord_seq: str,  # [필수] 예약주문순번
        rsvn_ord_orgno: str,  # [필수] 예약주문조직번호
        rsvn_ord_ord_dt: str,  # [필수] 예약주문주문일자
        ord_type: str,  # [필수] 주문구분 (ex. cancel:취소, modify:정정)
        pdno: Optional[str] = "",  # 종목코드
        ord_qty: Optional[str] = "",  # 주문수량
        ord_unpr: Optional[str] = "",  # 주문단가
        sll_buy_dvsn_cd: Optional[str] = "",  # 매도매수구분코드 (ex. 01:매도, 02:매수)
        ord_dvsn_cd: Optional[str] = "",  # 주문구분코드 (ex. 00:지정가, 01:시장가, 02:조건부지정가, 05:장전 시간외)
        ord_objt_cblc_dvsn_cd: Optional[str] = "",  # 주문대상잔고구분코드 (ex. 10 : 현금, 12 : 주식담보대출, ... 28 : 자기대주상환)
        loan_dt: Optional[str] = "",  # 대출일자
        rsvn_ord_end_dt: Optional[str] = "",  # 예약주문종료일자
        ctal_tlno: Optional[str] = ""  # 연락전화번호
) -> pd.DataFrame:
    """
    국내주식 예약주문 정정/취소 API 입니다.
    *  정정주문은 취소주문에 비해 필수 입력값이 추가 됩니다. 
    하단의 입력값을 참조하시기 바랍니다.

    ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)
    
    Args:
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드
        rsvn_ord_seq (str): [필수] 예약주문순번
        rsvn_ord_orgno (str): [필수] 예약주문조직번호
        rsvn_ord_ord_dt (str): [필수] 예약주문주문일자
        ord_type (str): [필수] 주문구분 (ex. cancel:취소, modify:정정)
        pdno (Optional[str]): 종목코드
        ord_qty (Optional[str]): 주문수량
        ord_unpr (Optional[str]): 주문단가
        sll_buy_dvsn_cd (Optional[str]): 매도매수구분코드 (ex. 01:매도, 02:매수)
        ord_dvsn_cd (Optional[str]): 주문구분코드 (ex. 00:지정가, 01:시장가, 02:조건부지정가, 05:장전 시간외)
        ord_objt_cblc_dvsn_cd (Optional[str]): 주문대상잔고구분코드 (ex. 10 : 현금, 12 : 주식담보대출, ... 28 : 자기대주상환)
        loan_dt (Optional[str]): 대출일자
        rsvn_ord_end_dt (Optional[str]): 예약주문종료일자
        ctal_tlno (Optional[str]): 연락전화번호

    Returns:
        pd.DataFrame: 주식예약주문정정취소 결과 데이터
        
    Example:
        >>> df = order_resv_rvsecncl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, rsvn_ord_seq="88793", rsvn_ord_orgno="123", rsvn_ord_ord_dt="20250113", ord_type="cancel")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/trading/order-resv-rvsecncl"

    # 필수 파라미터 검증
    if cano == "" or cano is None:
        raise ValueError("cano is required")

    if acnt_prdt_cd == "" or acnt_prdt_cd is None:
        raise ValueError("acnt_prdt_cd is required")

    if rsvn_ord_seq == "" or rsvn_ord_seq is None:
        raise ValueError("rsvn_ord_seq is required")

    if rsvn_ord_orgno == "" or rsvn_ord_orgno is None:
        raise ValueError("rsvn_ord_orgno is required")

    if rsvn_ord_ord_dt == "" or rsvn_ord_ord_dt is None:
        raise ValueError("rsvn_ord_ord_dt is required")

    if ord_type == "" or ord_type is None:
        raise ValueError("ord_type is required")

    # tr_id 설정
    if ord_type == "cancel":
        tr_id = "CTSC0009U"
    elif ord_type == "modify":
        tr_id = "CTSC0013U"
    else:
        raise ValueError("ord_type can only be cancel or modify")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "RSVN_ORD_SEQ": rsvn_ord_seq,
        "RSVN_ORD_ORGNO": rsvn_ord_orgno,
        "RSVN_ORD_ORD_DT": rsvn_ord_ord_dt
    }

    # 옵션 파라미터 추가
    if pdno:
        params["PDNO"] = pdno
    if ord_qty:
        params["ORD_QTY"] = ord_qty
    if ord_unpr:
        params["ORD_UNPR"] = ord_unpr
    if sll_buy_dvsn_cd:
        params["SLL_BUY_DVSN_CD"] = sll_buy_dvsn_cd
    if ord_dvsn_cd:
        params["ORD_DVSN_CD"] = ord_dvsn_cd
    if ord_objt_cblc_dvsn_cd:
        params["ORD_OBJT_CBLC_DVSN_CD"] = ord_objt_cblc_dvsn_cd
    if loan_dt:
        params["LOAN_DT"] = loan_dt
    if rsvn_ord_end_dt:
        params["RSVN_ORD_END_DT"] = rsvn_ord_end_dt
    if ctal_tlno:
        params["CTAL_TLNO"] = ctal_tlno

    res = ka._url_fetch(api_url, tr_id, "", params, postFlag=True)

    if res.isOK():
        current_data = pd.DataFrame([res.getBody().output])
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 주식주문(정정취소)[v1_국내주식-003]
##############################################################################################

def order_rvsecncl(
        env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
        cano: str,  # [필수] 종합계좌번호
        acnt_prdt_cd: str,  # [필수] 계좌상품코드
        krx_fwdg_ord_orgno: str,  # [필수] 한국거래소전송주문조직번호
        orgn_odno: str,  # [필수] 원주문번호
        ord_dvsn: str,  # [필수] 주문구분
        rvse_cncl_dvsn_cd: str,  # [필수] 정정취소구분코드 (ex. 01:정정,02:취소)
        ord_qty: str,  # [필수] 주문수량
        ord_unpr: str,  # [필수] 주문단가
        qty_all_ord_yn: str,  # [필수] 잔량전부주문여부 (ex. Y:전량, N:일부)
        excg_id_dvsn_cd: str,  # [필수] 거래소ID구분코드 (ex. KRX: 한국거래소, NXT:대체거래소,SOR:SOR)
        cndt_pric: Optional[str] = ""  # 조건가격
) -> pd.DataFrame:
    """
    주문 건에 대하여 정정 및 취소하는 API입니다. 단, 이미 체결된 건은 정정 및 취소가 불가합니다.

    ※ 정정은 원주문에 대한 주문단가 혹은 주문구분을 변경하는 사항으로, 정정이 가능한 수량은 원주문수량을 초과 할 수 없습니다.

    ※ 주식주문(정정취소) 호출 전에 반드시 주식정정취소가능주문조회 호출을 통해 정정취소가능수량(output > psbl_qty)을 확인하신 후 정정취소주문 내시기 바랍니다.

    ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드
        krx_fwdg_ord_orgno (str): [필수] 한국거래소전송주문조직번호
        orgn_odno (str): [필수] 원주문번호
        ord_dvsn (str): [필수] 주문구분
        rvse_cncl_dvsn_cd (str): [필수] 정정취소구분코드 (ex. 01:정정,02:취소)
        ord_qty (str): [필수] 주문수량
        ord_unpr (str): [필수] 주문단가
        qty_all_ord_yn (str): [필수] 잔량전부주문여부 (ex. Y:전량, N:일부)
        excg_id_dvsn_cd (str): [필수] 거래소ID구분코드 (ex. KRX: 한국거래소, NXT:대체거래소,SOR:SOR)
        cndt_pric (Optional[str]): 조건가격

    Returns:
        pd.DataFrame: 주식주문(정정취소) 결과 데이터
        
    Example:
        >>> df = order_rvsecncl(env_dv="real", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, ...)
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/trading/order-rvsecncl"

    # 필수 파라미터 검증
    if env_dv == "" or env_dv is None:
        raise ValueError("env_dv is required (e.g. 'real', 'demo')")

    if cano == "" or cano is None:
        raise ValueError("cano is required")

    if acnt_prdt_cd == "" or acnt_prdt_cd is None:
        raise ValueError("acnt_prdt_cd is required")

    if krx_fwdg_ord_orgno == "" or krx_fwdg_ord_orgno is None:
        raise ValueError("krx_fwdg_ord_orgno is required")

    if orgn_odno == "" or orgn_odno is None:
        raise ValueError("orgn_odno is required")

    if ord_dvsn == "" or ord_dvsn is None:
        raise ValueError("ord_dvsn is required")

    if rvse_cncl_dvsn_cd == "" or rvse_cncl_dvsn_cd is None:
        raise ValueError("rvse_cncl_dvsn_cd is required (e.g. '01', '02')")

    if ord_qty == "" or ord_qty is None:
        raise ValueError("ord_qty is required")

    if ord_unpr == "" or ord_unpr is None:
        raise ValueError("ord_unpr is required")

    if qty_all_ord_yn == "" or qty_all_ord_yn is None:
        raise ValueError("qty_all_ord_yn is required (e.g. 'Y', 'N')")

    if excg_id_dvsn_cd == "" or excg_id_dvsn_cd is None:
        raise ValueError("excg_id_dvsn_cd is required (e.g. 'KRX', 'NXT', 'SOR')")

    # tr_id 설정
    if env_dv == "real":
        tr_id = "TTTC0013U"
    elif env_dv == "demo":
        tr_id = "VTTC0013U"
    else:
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "KRX_FWDG_ORD_ORGNO": krx_fwdg_ord_orgno,
        "ORGN_ODNO": orgn_odno,
        "ORD_DVSN": ord_dvsn,
        "RVSE_CNCL_DVSN_CD": rvse_cncl_dvsn_cd,
        "ORD_QTY": ord_qty,
        "ORD_UNPR": ord_unpr,
        "QTY_ALL_ORD_YN": qty_all_ord_yn,
        "EXCG_ID_DVSN_CD": excg_id_dvsn_cd
    }

    # 옵션 파라미터 추가
    if cndt_pric:
        params["CNDT_PRIC"] = cndt_pric

    res = ka._url_fetch(api_url, tr_id, "", params, postFlag=True)

    if res.isOK():
        return pd.DataFrame([res.getBody().output])
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 국내주식 시간외예상체결등락률 [국내주식-140]
##############################################################################################

def overtime_exp_trans_fluct(
        fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J:주식)
        fid_cond_scr_div_code: str,  # [필수] 조건 화면 분류 코드 (ex. 11186)
        fid_input_iscd: str,  # [필수] 입력 종목코드 (ex. 0000:전체, 0001:코스피, 1001:코스닥)
        fid_rank_sort_cls_code: str,  # [필수] 순위 정렬 구분 코드 (ex. 0:상승률, 1:상승폭, 2:보합, 3:하락률, 4:하락폭)
        fid_div_cls_code: str,  # [필수] 분류 구분 코드 (ex. 0:전체, 1:관리종목, 2:투자주의, 3:투자경고, 4:투자위험예고, 5:투자위험, 6:보통주, 7:우선주)
        fid_input_price_1: str = "",  # 입력 가격1
        fid_input_price_2: str = "",  # 입력 가격2
        fid_input_vol_1: str = ""  # 입력 거래량
) -> pd.DataFrame:
    """
    국내주식 시간외예상체결등락률 API입니다. 
    한국투자 HTS(eFriend Plus) > [0236] 시간외 예상체결등락률 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:주식)
        fid_cond_scr_div_code (str): [필수] 조건 화면 분류 코드 (ex. 11186)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 0000:전체, 0001:코스피, 1001:코스닥)
        fid_rank_sort_cls_code (str): [필수] 순위 정렬 구분 코드 (ex. 0:상승률, 1:상승폭, 2:보합, 3:하락률, 4:하락폭)
        fid_div_cls_code (str): [필수] 분류 구분 코드 (ex. 0:전체, 1:관리종목, 2:투자주의, 3:투자경고, 4:투자위험예고, 5:투자위험, 6:보통주, 7:우선주)
        fid_input_price_1 (str): 입력 가격1
        fid_input_price_2 (str): 입력 가격2
        fid_input_vol_1 (str): 입력 거래량

    Returns:
        pd.DataFrame: 국내주식 시간외예상체결등락률 데이터
        
    Example:
        >>> df = overtime_exp_trans_fluct("J", "11186", "0000", "0", "0")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/overtime-exp-trans-fluct"

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")

    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '11186')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '0000')")

    if fid_rank_sort_cls_code == "":
        raise ValueError("fid_rank_sort_cls_code is required (e.g. '0')")

    if fid_div_cls_code == "":
        raise ValueError("fid_div_cls_code is required (e.g. '0')")

    tr_id = "FHKST11860000"  # 국내주식 시간외예상체결등락률

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_INPUT_PRICE_1": fid_input_price_1,
        "FID_INPUT_PRICE_2": fid_input_price_2,
        "FID_INPUT_VOL_1": fid_input_vol_1
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 순위분석 > 국내주식 시간외등락율순위[국내주식-138]
##############################################################################################

def overtime_fluctuation(
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_mrkt_cls_code: str,  # 시장 구분 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_input_price_1: str,  # 입력 가격1
        fid_input_price_2: str,  # 입력 가격2
        fid_vol_cnt: str,  # 거래량 수
        fid_trgt_cls_code: str,  # 대상 구분 코드
        fid_trgt_exls_cls_code: str,  # 대상 제외 구분 코드
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        tr_cont: str = "",
        depth: int = 0,
        max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 시간외등락율순위[국내주식-138]
    국내주식 시간외등락율순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 시장구분코드 (J: 주식)
        fid_mrkt_cls_code (str): 공백 입력
        fid_cond_scr_div_code (str): Unique key(20234)
        fid_input_iscd (str): 0000(전체), 0001(코스피), 1001(코스닥)
        fid_div_cls_code (str): 1(상한가), 2(상승률), 3(보합),4(하한가),5(하락률)
        fid_input_price_1 (str): 입력값 없을때 전체 (가격 ~)
        fid_input_price_2 (str): 입력값 없을때 전체 (~ 가격)
        fid_vol_cnt (str): 입력값 없을때 전체 (거래량 ~)
        fid_trgt_cls_code (str): 공백 입력
        fid_trgt_exls_cls_code (str): 공백 입력
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 국내주식 시간외등락율순위 데이터
        
    Example:
        >>> df1, df2 = overtime_fluctuation(
        ...     fid_cond_mrkt_div_code='J',
        ...     fid_mrkt_cls_code='',
        ...     fid_cond_scr_div_code='20234',
        ...     fid_input_iscd='0000',
        ...     fid_div_cls_code='1',
        ...     fid_input_price_1='',
        ...     fid_input_price_2='',
        ...     fid_vol_cnt='',
        ...     fid_trgt_cls_code='',
        ...     fid_trgt_exls_cls_code=''
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/overtime-fluctuation"
    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20234')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20234')")
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0000')")
        raise ValueError("fid_input_iscd is required. (e.g. '0000')")
    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '1')")
        raise ValueError("fid_div_cls_code is required. (e.g. '1')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()

    tr_id = "FHPST02340000"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_MRKT_CLS_CODE": fid_mrkt_cls_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_INPUT_PRICE_1": fid_input_price_1,
        "FID_INPUT_PRICE_2": fid_input_price_2,
        "FID_VOL_CNT": fid_vol_cnt,
        "FID_TRGT_CLS_CODE": fid_trgt_cls_code,
        "FID_TRGT_EXLS_CLS_CODE": fid_trgt_exls_cls_code,
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                current_data1 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe1 = pd.concat([dataframe1, current_data1],
                                       ignore_index=True) if dataframe1 is not None else current_data1
            else:
                dataframe1 = dataframe1 if dataframe1 is not None else pd.DataFrame()
        else:
            dataframe1 = dataframe1 if dataframe1 is not None else pd.DataFrame()

        # output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                current_data2 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe2 = pd.concat([dataframe2, current_data2],
                                       ignore_index=True) if dataframe2 is not None else current_data2
            else:
                dataframe2 = dataframe2 if dataframe2 is not None else pd.DataFrame()
        else:
            dataframe2 = dataframe2 if dataframe2 is not None else pd.DataFrame()

        tr_cont = res.getHeader().tr_cont

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return overtime_fluctuation(
                fid_cond_mrkt_div_code,
                fid_mrkt_cls_code,
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_div_cls_code,
                fid_input_price_1,
                fid_input_price_2,
                fid_vol_cnt,
                fid_trgt_cls_code,
                fid_trgt_exls_cls_code,
                "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 국내주식 > 국내주식 시간외거래량순위[국내주식-139]
##############################################################################################

def overtime_volume(
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_rank_sort_cls_code: str,  # 순위 정렬 구분 코드
        fid_input_price_1: str,  # 입력 가격1
        fid_input_price_2: str,  # 입력 가격2
        fid_vol_cnt: str,  # 거래량 수
        fid_trgt_cls_code: str,  # 대상 구분 코드
        fid_trgt_exls_cls_code: str,  # 대상 제외 구분 코드
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        tr_cont: str = "",
        depth: int = 0,
        max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 시간외거래량순위[국내주식-139]
    국내주식 시간외거래량순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 시장구분코드 (J: 주식)
        fid_cond_scr_div_code (str): Unique key(20235)
        fid_input_iscd (str): 0000(전체), 0001(코스피), 1001(코스닥)
        fid_rank_sort_cls_code (str): 0(매수잔량),  1(매도잔량), 2(거래량)
        fid_input_price_1 (str): 가격 ~
        fid_input_price_2 (str): ~ 가격
        fid_vol_cnt (str): 거래량 ~
        fid_trgt_cls_code (str): 공백
        fid_trgt_exls_cls_code (str): 공백
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 국내주식 시간외거래량순위 데이터
        
    Example:
        >>> df1, df2 = overtime_volume(
                fid_cond_mrkt_div_code='J',
                fid_cond_scr_div_code='20235',
                fid_input_iscd='0000',
                fid_rank_sort_cls_code='2',
                fid_input_price_1='',
                fid_input_price_2='',
                fid_vol_cnt='',
                fid_trgt_cls_code='',
                fid_trgt_exls_cls_code=''
            )
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/overtime-volume"
    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")

    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20235')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20235')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0000')")
        raise ValueError("fid_input_iscd is required. (e.g. '0000')")

    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '2')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '2')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()

    tr_id = "FHPST02350000"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_INPUT_PRICE_1": fid_input_price_1,
        "FID_INPUT_PRICE_2": fid_input_price_2,
        "FID_VOL_CNT": fid_vol_cnt,
        "FID_TRGT_CLS_CODE": fid_trgt_cls_code,
        "FID_TRGT_EXLS_CLS_CODE": fid_trgt_exls_cls_code,
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                current_data1 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe1 = pd.concat([dataframe1, current_data1],
                                       ignore_index=True) if dataframe1 is not None else current_data1
            else:
                dataframe1 = dataframe1 if dataframe1 is not None else pd.DataFrame()
        else:
            dataframe1 = dataframe1 if dataframe1 is not None else pd.DataFrame()

        # output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                current_data2 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe2 = pd.concat([dataframe2, current_data2],
                                       ignore_index=True) if dataframe2 is not None else current_data2
            else:
                dataframe2 = dataframe2 if dataframe2 is not None else pd.DataFrame()
        else:
            dataframe2 = dataframe2 if dataframe2 is not None else pd.DataFrame()

        tr_cont = res.getHeader().tr_cont

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return overtime_volume(
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_rank_sort_cls_code,
                fid_input_price_1,
                fid_input_price_2,
                fid_vol_cnt,
                fid_trgt_cls_code,
                fid_trgt_exls_cls_code,
                "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 국내주식 매물대/거래비중 [국내주식-196]
##############################################################################################

def pbar_tratio(
        fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J)
        fid_input_iscd: str,  # [필수] 입력 종목코드 (ex. 123456)
        fid_cond_scr_div_code: str,  # [필수] 조건화면분류코드 (ex. 20113)
        fid_input_hour_1: str = "",  # 입력시간 (기본값: "")
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    국내주식 매물대/거래비중 API입니다.
    한국투자 HTS(eFriend Plus) > [0113] 당일가격대별 매물대 화면의 데이터 중 일부를 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 123456)
        fid_cond_scr_div_code (str): [필수] 조건화면분류코드 (ex. 20113)
        fid_input_hour_1 (str): 입력시간 (기본값: "")

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> df1, df2 = pbar_tratio("J", "005930", "20113")
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/pbar-tratio"

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '123456')")

    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '20113')")

    tr_id = "FHPST01130000"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_INPUT_HOUR_1": fid_input_hour_1
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        # output1 (object) - 단일 객체를 DataFrame으로 변환
        output1_data = pd.DataFrame([res.getBody().output1])

        # output2 (array) - 배열을 DataFrame으로 변환
        output2_data = pd.DataFrame(res.getBody().output2)

        return output1_data, output2_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 퇴직연금 잔고조회[v1_국내주식-036]
##############################################################################################

def pension_inquire_balance(
        cano: str,  # [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 29)
        acca_dvsn_cd: str,  # [필수] 적립금구분코드 (ex. 00)
        inqr_dvsn: str,  # [필수] 조회구분 (ex. 00)
        FK100: str = "",  # 연속조회검색조건100
        NK100: str = "",  # 연속조회키100
        tr_cont: str = "",  # 연속 거래 여부
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
        depth: int = 0,  # 내부 재귀깊이 (자동관리)
        max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    주식, ETF, ETN만 조회 가능하며 펀드는 조회 불가합니다.

    ​※ 55번 계좌(DC가입자계좌)의 경우 해당 API 이용이 불가합니다.
    KIS Developers API의 경우 HTS ID에 반드시 연결되어있어야만 API 신청 및 앱정보 발급이 가능한 서비스로 개발되어서 실물계좌가 아닌 55번 계좌는 API 이용이 불가능한 점 양해 부탁드립니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 29)
        acca_dvsn_cd (str): [필수] 적립금구분코드 (ex. 00)
        inqr_dvsn (str): [필수] 조회구분 (ex. 00)
        FK100 (str): 연속조회검색조건100
        NK100 (str): 연속조회키100
        tr_cont (str): 연속 거래 여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 퇴직연금 잔고 데이터
        
    Example:
        >>> df1, df2 = pension_inquire_balance(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, acca_dvsn_cd="00", inqr_dvsn="00")
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/trading/pension/inquire-balance"

    if cano == "" or cano is None:
        raise ValueError("cano is required (e.g. '12345678')")

    if acnt_prdt_cd == "" or acnt_prdt_cd is None:
        raise ValueError("acnt_prdt_cd is required (e.g. '29')")

    if acca_dvsn_cd == "" or acca_dvsn_cd is None:
        raise ValueError("acca_dvsn_cd is required (e.g. '00')")

    if inqr_dvsn == "" or inqr_dvsn is None:
        raise ValueError("inqr_dvsn is required (e.g. '00')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "TTTC2208R"  # 퇴직연금 잔고조회

    params = {
        "CANO": cano,  # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "ACCA_DVSN_CD": acca_dvsn_cd,  # 적립금구분코드
        "INQR_DVSN": inqr_dvsn,  # 조회구분
        "CTX_AREA_FK100": FK100,  # 연속조회검색조건100
        "CTX_AREA_NK100": NK100  # 연속조회키100
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리 (array)
        current_data1 = pd.DataFrame(res.getBody().output1)
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1

        # output2 처리 (object)
        current_data2 = pd.DataFrame(res.getBody().output2, index=[0])
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2

        tr_cont = res.getHeader().tr_cont
        FK100 = res.getBody().ctx_area_fk100
        NK100 = res.getBody().ctx_area_nk100

        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return pension_inquire_balance(
                cano, acnt_prdt_cd, acca_dvsn_cd, inqr_dvsn, FK100, NK100, "N", dataframe1, dataframe2, depth + 1,
                max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 퇴직연금 미체결내역[v1_국내주식-033]
##############################################################################################

def pension_inquire_daily_ccld(
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        user_dvsn_cd: str,  # 사용자구분코드
        sll_buy_dvsn_cd: str,  # 매도매수구분코드
        ccld_nccs_dvsn: str,  # 체결미체결구분
        inqr_dvsn_3: str,  # 조회구분3
        FK100: str = "",  # 연속조회검색조건100
        NK100: str = "",  # 연속조회키100
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 내부 재귀 깊이 (자동 관리)
        max_depth: int = 10  # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    [국내주식] 주문/계좌 > 퇴직연금 미체결내역[v1_국내주식-033]
    ※ 55번 계좌(DC가입자계좌)의 경우 해당 API 이용이 불가합니다.
    KIS Developers API의 경우 HTS ID에 반드시 연결되어있어야만 API 신청 및 앱정보 발급이 가능한 서비스로 개발되어서 실물계좌가 아닌 55번 계좌는 API 이용이 불가능한 점 양해 부탁드립니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 29)
        user_dvsn_cd (str): [필수] 사용자구분코드 (ex. %%)
        sll_buy_dvsn_cd (str): [필수] 매도매수구분코드 (ex. 00: 전체, 01: 매도, 02: 매수)
        ccld_nccs_dvsn (str): [필수] 체결미체결구분 (ex. %%: 전체, 01: 체결, 02: 미체결)
        inqr_dvsn_3 (str): [필수] 조회구분3 (ex. 00: 전체)
        FK100 (str): 연속조회검색조건100
        NK100 (str): 연속조회키100
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        pd.DataFrame: 퇴직연금 미체결내역 데이터
        
    Example:
        >>> df = pension_inquire_daily_ccld(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, user_dvsn_cd="%%", sll_buy_dvsn_cd="00", ccld_nccs_dvsn="%%", inqr_dvsn_3="00")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/trading/pension/inquire-daily-ccld"

    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '29')")

    if user_dvsn_cd == "":
        raise ValueError("user_dvsn_cd is required (e.g. '%%')")

    if sll_buy_dvsn_cd == "":
        raise ValueError("sll_buy_dvsn_cd is required (e.g. '00: 전체, 01: 매도, 02: 매수')")

    if ccld_nccs_dvsn == "":
        raise ValueError("ccld_nccs_dvsn is required (e.g. '%%: 전체, 01: 체결, 02: 미체결')")

    if inqr_dvsn_3 == "":
        raise ValueError("inqr_dvsn_3 is required (e.g. '00: 전체')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    tr_id = "TTTC2201R"  # 퇴직연금 미체결내역

    params = {
        "CANO": cano,  # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "USER_DVSN_CD": user_dvsn_cd,  # 사용자구분코드
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,  # 매도매수구분코드
        "CCLD_NCCS_DVSN": ccld_nccs_dvsn,  # 체결미체결구분
        "INQR_DVSN_3": inqr_dvsn_3,  # 조회구분3
        "CTX_AREA_FK100": FK100,
        "CTX_AREA_NK100": NK100
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont
        FK100 = res.getBody().ctx_area_fk100
        NK100 = res.getBody().ctx_area_nk100

        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return pension_inquire_daily_ccld(
                cano, acnt_prdt_cd, user_dvsn_cd, sll_buy_dvsn_cd, ccld_nccs_dvsn, inqr_dvsn_3, FK100, NK100, "N",
                dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 퇴직연금 예수금조회[v1_국내주식-035]
##############################################################################################

def pension_inquire_deposit(
        cano: str,  # 종합계좌번호 (12345678)
        acnt_prdt_cd: str,  # 계좌상품코드 (29)
        acca_dvsn_cd: str  # 적립금구분코드 (00)
) -> pd.DataFrame:
    """
    ​※ 55번 계좌(DC가입자계좌)의 경우 해당 API 이용이 불가합니다.
    KIS Developers API의 경우 HTS ID에 반드시 연결되어있어야만 API 신청 및 앱정보 발급이 가능한 서비스로 개발되어서 실물계좌가 아닌 55번 계좌는 API 이용이 불가능한 점 양해 부탁드립니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 29)
        acca_dvsn_cd (str): [필수] 적립금구분코드 (ex. 00)

    Returns:
        pd.DataFrame: 퇴직연금 예수금 데이터
        
    Example:
        >>> df = pension_inquire_deposit(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, acca_dvsn_cd="00")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/trading/pension/inquire-deposit"

    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '29')")

    if acca_dvsn_cd == "":
        raise ValueError("acca_dvsn_cd is required (e.g. '00')")

    tr_id = "TTTC0506R"  # 퇴직연금 예수금조회

    params = {
        "CANO": cano,  # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "ACCA_DVSN_CD": acca_dvsn_cd  # 적립금구분코드
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame([res.getBody().output])
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 퇴직연금 체결기준잔고[v1_국내주식-032]
##############################################################################################

def pension_inquire_present_balance(
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        user_dvsn_cd: str,  # 상품번호
        FK100: str = "",  # 연속조회검색조건100
        NK100: str = ""  # 연속조회키100
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [국내주식] 주문/계좌 > 퇴직연금 체결기준잔고[v1_국내주식-032]
    
    ※ 55번 계좌(DC가입자계좌)의 경우 해당 API 이용이 불가합니다.
    KIS Developers API의 경우 HTS ID에 반드시 연결되어있어야만 API 신청 및 앱정보 발급이 가능한 서비스로 개발되어서 실물계좌가 아닌 55번 계좌는 API 이용이 불가능한 점 양해 부탁드립니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. '12345678')
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. '29')
        user_dvsn_cd (str): [필수] 상품번호 (ex. '00')
        FK100 (str): 연속조회검색조건100
        NK100 (str): 연속조회키100

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 데이터프레임 튜플
        
    Example:
        >>> df1, df2 = pension_inquire_present_balance(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, user_dvsn_cd="00")
        >>> print(df1)
        >>> print(df2)
    """
    api_url = "/uapi/domestic-stock/v1/trading/pension/inquire-present-balance"

    # 필수 파라미터 검증
    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '29')")

    if user_dvsn_cd == "":
        raise ValueError("user_dvsn_cd is required (e.g. '00')")

    tr_id = "TTTC2202R"  # 퇴직연금 체결기준잔고

    params = {
        "CANO": cano,  # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "USER_DVSN_CD": user_dvsn_cd,  # 상품번호
        "CTX_AREA_FK100": FK100,  # 연속조회검색조건100
        "CTX_AREA_NK100": NK100  # 연속조회키100
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        # output1 (array) - 보유종목 정보
        output1_data = pd.DataFrame(res.getBody().output1)

        # output2 (array) - 계좌 요약 정보
        output2_data = pd.DataFrame(res.getBody().output2)

        return output1_data, output2_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 퇴직연금 매수가능조회[v1_국내주식-034]
##############################################################################################

def pension_inquire_psbl_order(
        cano: str,  # [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 29)
        pdno: str,  # [필수] 상품번호 (ex. 123456)
        acca_dvsn_cd: str,  # [필수] 적립금구분코드 (ex. 00)
        cma_evlu_amt_icld_yn: str,  # [필수] CMA평가금액포함여부 (ex. Y:포함, N:미포함)
        ord_unpr: str,  # [필수] 주문단가
        ord_dvsn: str  # [필수] 주문구분 (ex. 00: 지정가, 01: 시장가)
) -> pd.DataFrame:
    """
    [국내주식] 주문/계좌 > 퇴직연금 매수가능조회[v1_국내주식-034]
    
    ※ 55번 계좌(DC가입자계좌)의 경우 해당 API 이용이 불가합니다.
    KIS Developers API의 경우 HTS ID에 반드시 연결되어있어야만 API 신청 및 앱정보 발급이 가능한 서비스로 개발되어서 실물계좌가 아닌 55번 계좌는 API 이용이 불가능한 점 양해 부탁드립니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 29)
        pdno (str): [필수] 상품번호 (ex. 123456)
        acca_dvsn_cd (str): [필수] 적립금구분코드 (ex. 00)
        cma_evlu_amt_icld_yn (str): [필수] CMA평가금액포함여부 (ex. Y:포함, N:미포함)
        ord_unpr (str): [필수] 주문단가
        ord_dvsn (str): [필수] 주문구분 (ex. 00: 지정가, 01: 시장가)

    Returns:
        pd.DataFrame: 퇴직연금 매수가능조회 데이터
        
    Example:
        >>> df = pension_inquire_psbl_order(
        ...     cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod,
        ...     pdno="069500",
        ...     acca_dvsn_cd="00",
        ...     cma_evlu_amt_icld_yn="Y",
        ...     ord_unpr="30800",
        ...     ord_dvsn="00"
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/trading/pension/inquire-psbl-order"

    # 필수 파라미터 검증
    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '29')")

    if pdno == "":
        raise ValueError("pdno is required (e.g. '123456')")

    if acca_dvsn_cd == "":
        raise ValueError("acca_dvsn_cd is required (e.g. '00')")

    if cma_evlu_amt_icld_yn == "":
        raise ValueError("cma_evlu_amt_icld_yn is required (e.g. 'Y:포함, N:미포함')")

    if ord_unpr == "":
        raise ValueError("ord_unpr is required")

    if ord_dvsn == "":
        raise ValueError("ord_dvsn is required (e.g. '00: 지정가, 01: 시장가')")

    tr_id = "TTTC0503R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "ACCA_DVSN_CD": acca_dvsn_cd,
        "CMA_EVLU_AMT_ICLD_YN": cma_evlu_amt_icld_yn,
        "ORD_UNPR": ord_unpr,
        "ORD_DVSN": ord_dvsn
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output, index=[0])
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 주문/계좌 > 기간별계좌권리현황조회 [국내주식-211]
##############################################################################################

def period_rights(
        inqr_dvsn: str,  # [필수] 조회구분 (ex. 03)
        cano: str,  # [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 01 or 22)
        inqr_strt_dt: str,  # [필수] 조회시작일자 (ex. 20250101)
        inqr_end_dt: str,  # [필수] 조회종료일자 (ex. 20250103)
        cust_rncno25: str = "",  # 고객실명확인번호25
        hmid: str = "",  # 홈넷ID
        rght_type_cd: str = "",  # 권리유형코드
        pdno: str = "",  # 상품번호
        prdt_type_cd: str = "",  # 상품유형코드
        NK100: str = "",  # 연속조회키100
        FK100: str = "",  # 연속조회검색조건100
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 내부 재귀깊이 (자동관리)
        max_depth: int = 10  # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    기간별계좌권리현황조회 API입니다.
    한국투자 HTS(eFriend Plus) > [7344] 권리유형별 현황조회 화면을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        inqr_dvsn (str): [필수] 조회구분 (ex. 03)
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 01 or 22)
        inqr_strt_dt (str): [필수] 조회시작일자 (ex. 20250101)
        inqr_end_dt (str): [필수] 조회종료일자 (ex. 20250103)
        cust_rncno25 (str): 고객실명확인번호25
        hmid (str): 홈넷ID
        rght_type_cd (str): 권리유형코드
        pdno (str): 상품번호
        prdt_type_cd (str): 상품유형코드
        NK100 (str): 연속조회키100
        FK100 (str): 연속조회검색조건100
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        pd.DataFrame: 기간별계좌권리현황 데이터
        
    Example:
        >>> df = period_rights(inqr_dvsn="03", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, inqr_strt_dt="20250101", inqr_end_dt="20250103")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/trading/period-rights"

    if inqr_dvsn == "":
        raise ValueError("inqr_dvsn is required (e.g. '03')")

    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '01' or '22')")

    if inqr_strt_dt == "":
        raise ValueError("inqr_strt_dt is required (e.g. '20250101')")

    if inqr_end_dt == "":
        raise ValueError("inqr_end_dt is required (e.g. '20250103')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    tr_id = "CTRGA011R"  # 기간별계좌권리현황조회

    params = {
        "INQR_DVSN": inqr_dvsn,
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "INQR_STRT_DT": inqr_strt_dt,
        "INQR_END_DT": inqr_end_dt,
        "CUST_RNCNO25": cust_rncno25,
        "HMID": hmid,
        "RGHT_TYPE_CD": rght_type_cd,
        "PDNO": pdno,
        "PRDT_TYPE_CD": prdt_type_cd,
        "CTX_AREA_NK100": NK100,
        "CTX_AREA_FK100": FK100
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont
        FK100 = res.getBody().ctx_area_fk100
        NK100 = res.getBody().ctx_area_nk100

        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return period_rights(
                inqr_dvsn, cano, acnt_prdt_cd, inqr_strt_dt, inqr_end_dt,
                cust_rncno25, hmid, rght_type_cd, pdno, prdt_type_cd,
                NK100, FK100, "N", dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 순위분석 > 국내주식 우선주_괴리율 상위[v1_국내주식-094]
##############################################################################################

def prefer_disparate_ratio(
        fid_vol_cnt: str,  # 거래량 수
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_trgt_cls_code: str,  # 대상 구분 코드
        fid_trgt_exls_cls_code: str,  # 대상 제외 구분 코드
        fid_input_price_1: str,  # 입력 가격1
        fid_input_price_2: str,  # 입력 가격2
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 우선주_괴리율 상위[v1_국내주식-094]
    국내주식 우선주_괴리율 상위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_vol_cnt (str): 입력값 없을때 전체 (거래량 ~)
        fid_cond_mrkt_div_code (str): 시장구분코드 (J:KRX, NX:NXT)
        fid_cond_scr_div_code (str): Unique key( 20177 )
        fid_div_cls_code (str): 0: 전체
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200
        fid_trgt_cls_code (str): 0 : 전체
        fid_trgt_exls_cls_code (str): 0 : 전체
        fid_input_price_1 (str): 입력값 없을때 전체 (가격 ~)
        fid_input_price_2 (str): 입력값 없을때 전체 (~ 가격)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 우선주_괴리율 상위 데이터
        
    Example:
        >>> df = prefer_disparate_ratio(
        ...     fid_vol_cnt="",
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_cond_scr_div_code="20177",
        ...     fid_div_cls_code="0",
        ...     fid_input_iscd="0000",
        ...     fid_trgt_cls_code="0",
        ...     fid_trgt_exls_cls_code="0",
        ...     fid_input_price_1="",
        ...     fid_input_price_2=""
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/prefer-disparate-ratio"
    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20177')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20177')")
    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0000')")
        raise ValueError("fid_input_iscd is required. (e.g. '0000')")
    if not fid_trgt_cls_code:
        logger.error("fid_trgt_cls_code is required. (e.g. '0')")
        raise ValueError("fid_trgt_cls_code is required. (e.g. '0')")
    if not fid_trgt_exls_cls_code:
        logger.error("fid_trgt_exls_cls_code is required. (e.g. '0')")
        raise ValueError("fid_trgt_exls_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHPST01770000"

    params = {
        "fid_vol_cnt": fid_vol_cnt,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_input_iscd": fid_input_iscd,
        "fid_trgt_cls_code": fid_trgt_cls_code,
        "fid_trgt_exls_cls_code": fid_trgt_exls_cls_code,
        "fid_input_price_1": fid_input_price_1,
        "fid_input_price_2": fid_input_price_2,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return prefer_disparate_ratio(
                fid_vol_cnt,
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_div_cls_code,
                fid_input_iscd,
                fid_trgt_cls_code,
                fid_trgt_exls_cls_code,
                fid_input_price_1,
                fid_input_price_2,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 에러 처리
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 순위분석 > 국내주식 수익자산지표 순위[v1_국내주식-090]
##############################################################################################

def profit_asset_index(
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_trgt_cls_code: str,  # 대상 구분 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_input_price_1: str,  # 입력 가격1
        fid_input_price_2: str,  # 입력 가격2
        fid_vol_cnt: str,  # 거래량 수
        fid_input_option_1: str,  # 입력 옵션1
        fid_input_option_2: str,  # 입력 옵션2
        fid_rank_sort_cls_code: str,  # 순위 정렬 구분 코드
        fid_blng_cls_code: str,  # 소속 구분 코드
        fid_trgt_exls_cls_code: str,  # 대상 제외 구분 코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None  # 누적 데이터프레임
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 수익자산지표 순위[v1_국내주식-090]
    국내주식 수익자산지표 순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (필수) (J:KRX, NX:NXT)
        fid_trgt_cls_code (str): 대상 구분 코드 (필수)
        fid_cond_scr_div_code (str): 조건 화면 분류 코드 (필수)
        fid_input_iscd (str): 입력 종목코드 (필수)
        fid_div_cls_code (str): 분류 구분 코드 (필수)
        fid_input_price_1 (str): 입력 가격1 (필수)
        fid_input_price_2 (str): 입력 가격2 (필수)
        fid_vol_cnt (str): 거래량 수 (필수)
        fid_input_option_1 (str): 입력 옵션1 (필수)
        fid_input_option_2 (str): 입력 옵션2 (필수)
        fid_rank_sort_cls_code (str): 순위 정렬 구분 코드 (필수)
        fid_blng_cls_code (str): 소속 구분 코드 (필수)
        fid_trgt_exls_cls_code (str): 대상 제외 구분 코드 (필수)
        tr_cont (str): 연속 거래 여부 (옵션)
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (옵션)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 수익자산지표 순위 데이터
        
    Example:
        >>> df = profit_asset_index(
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_trgt_cls_code="0",
        ...     fid_cond_scr_div_code="20173",
        ...     fid_input_iscd="0000",
        ...     fid_div_cls_code="0",
        ...     fid_input_price_1="",
        ...     fid_input_price_2="",
        ...     fid_vol_cnt="",
        ...     fid_input_option_1="2023",
        ...     fid_input_option_2="0",
        ...     fid_rank_sort_cls_code="0",
        ...     fid_blng_cls_code="0",
        ...     fid_trgt_exls_cls_code="0"
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/profit-asset-index"
    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code != "J":
        raise ValueError("조건 시장 분류 코드 확인요망!!!")
    if fid_trgt_cls_code != "0":
        raise ValueError("대상 구분 코드 확인요망!!!")
    if fid_cond_scr_div_code != "20173":
        raise ValueError("조건 화면 분류 코드 확인요망!!!")
    if fid_input_iscd not in ["0000", "0001", "1001", "2001"]:
        raise ValueError("입력 종목코드 확인요망!!!")
    if fid_div_cls_code != "0":
        raise ValueError("분류 구분 코드 확인요망!!!")
    if fid_input_option_1 != "2023":
        raise ValueError("입력 옵션1 확인요망!!!")
    if fid_input_option_2 not in ["0", "1", "2", "3"]:
        raise ValueError("입력 옵션2 확인요망!!!")
    if fid_rank_sort_cls_code not in ["0", "1", "2", "3", "4", "5", "6"]:
        raise ValueError("순위 정렬 구분 코드 확인요망!!!")
    if fid_blng_cls_code != "0":
        raise ValueError("소속 구분 코드 확인요망!!!")
    if fid_trgt_exls_cls_code != "0":
        raise ValueError("대상 제외 구분 코드 확인요망!!!")

    tr_id = "FHPST01730000"

    params = {
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_trgt_cls_code": fid_trgt_cls_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_input_iscd": fid_input_iscd,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_input_price_1": fid_input_price_1,
        "fid_input_price_2": fid_input_price_2,
        "fid_vol_cnt": fid_vol_cnt,
        "fid_input_option_1": fid_input_option_1,
        "fid_input_option_2": fid_input_option_2,
        "fid_rank_sort_cls_code": fid_rank_sort_cls_code,
        "fid_blng_cls_code": fid_blng_cls_code,
        "fid_trgt_exls_cls_code": fid_trgt_exls_cls_code,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            print("Call Next")
            ka.smart_sleep()
            return profit_asset_index(
                fid_cond_mrkt_div_code,
                fid_trgt_cls_code,
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_div_cls_code,
                fid_input_price_1,
                fid_input_price_2,
                fid_vol_cnt,
                fid_input_option_1,
                fid_input_option_2,
                fid_rank_sort_cls_code,
                fid_blng_cls_code,
                fid_trgt_exls_cls_code,
                "N", dataframe
            )
        else:
            print("The End")
            return dataframe
    else:
        # 오류 처리
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 종목별 프로그램매매추이(체결)[v1_국내주식-044]
##############################################################################################

def program_trade_by_stock(
        fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J:KRX,NX:NXT,UN:통합)
        fid_input_iscd: str  # [필수] 종목코드 (ex. 123456)
) -> pd.DataFrame:
    """
    국내주식 종목별 프로그램매매추이(체결) API입니다.

    한국투자 HTS(eFriend Plus) > [0465] 종목별 프로그램 매매추이 화면(혹은 한국투자 MTS > 국내 현재가 > 기타수급 > 프로그램) 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX,NX:NXT,UN:통합)
        fid_input_iscd (str): [필수] 종목코드 (ex. 123456)

    Returns:
        pd.DataFrame: 종목별 프로그램매매추이 데이터
        
    Example:
        >>> df = program_trade_by_stock(fid_cond_mrkt_div_code="J", fid_input_iscd="005930")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/program-trade-by-stock"

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (ex. J:KRX,NX:NXT,UN:통합)")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (ex. 123456)")

    tr_id = "FHPPG04650101"  # 종목별 프로그램매매추이(체결)

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,  # 조건 시장 분류 코드
        "FID_INPUT_ISCD": fid_input_iscd  # 종목코드
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 종목별 프로그램매매추이(일별) [국내주식-113]
##############################################################################################

def program_trade_by_stock_daily(
        fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J:KRX,NX:NXT,UN:통합)
        fid_input_iscd: str,  # [필수] 입력 종목코드 (ex. 123456)
        fid_input_date_1: str = ""  # [필수] 입력날짜 (초기값: "")
) -> pd.DataFrame:
    """
    국내주식 종목별 프로그램매매추이(일별) API입니다.
    한국투자 HTS(eFriend Plus) > [0465] 종목별 프로그램 매매추이 화면(혹은 한국투자 MTS > 국내 현재가 > 기타수급 > 프로그램) 의 "일자별" 클릭 시 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX,NX:NXT,UN:통합)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 123456)
        fid_input_date_1 (str): [필수] 입력날짜 (초기값: "")

    Returns:
        pd.DataFrame: 종목별 프로그램매매추이(일별) 데이터
        
    Example:
        >>> df = program_trade_by_stock_daily("J", "005930")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/program-trade-by-stock-daily"

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (ex. J:KRX,NX:NXT,UN:통합)")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (ex. 123456)")

    tr_id = "FHPPG04650201"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_DATE_1": fid_input_date_1
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 종목조건검색조회 [국내주식-039]
##############################################################################################

def psearch_result(
        user_id: str,  # 사용자 HTS ID
        seq: str  # 사용자조건 키값
) -> pd.DataFrame:
    """
    HTS(efriend Plus) [0110] 조건검색에서 등록 및 서버저장한 나의 조건 목록을 확인할 수 있는 API입니다.
    종목조건검색 목록조회 API(/uapi/domestic-stock/v1/quotations/psearch-title)의 output인 'seq'을 종목조건검색조회 API(/uapi/domestic-stock/v1/quotations/psearch-result)의 input으로 사용하시면 됩니다.

    ※ 시스템 안정성을 위해 API로 제공되는 조건검색 결과의 경우 조건당 100건으로 제한을 둔 점 양해 부탁드립니다.

    ※ [0110] 화면의 '대상변경' 설정사항은 HTS [0110] 사용자 조건검색 화면에만 적용됨에 유의 부탁드립니다.

    ※ '조회가 계속 됩니다. (다음을 누르십시오.)' 오류 발생 시 해결방법
    → HTS(efriend Plus) [0110] 조건검색 화면에서 조건을 등록하신 후, 왼쪽 하단의 "사용자조건 서버저장" 클릭하셔서 등록한 조건들을 서버로 보낸 후 다시 API 호출 시도 부탁드립니다.

    ※ {"rt_cd":"1","msg_cd":"MCA05918","msg1":"종목코드 오류입니다."} 메시지 발생 이유
    → 조건검색 결과 검색된 종목이 0개인 경우 위 응답값을 수신하게 됩니다.
    
    Args:
        user_id (str): [필수] 사용자 HTS ID
        seq (str): [필수] 사용자조건 키값 (종목조건검색 목록조회 API의 output인 'seq'을 이용)

    Returns:
        pd.DataFrame: 종목조건검색조회 데이터
        
    Example:
        >>> df = psearch_result(user_id=trenv.my_htsid, seq="0")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/psearch-result"

    if user_id == "":
        raise ValueError("user_id is required")

    if seq == "":
        raise ValueError("seq is required (e.g. '종목조건검색 목록조회 API의 output인 'seq'을 이용')")

    tr_id = "HHKST03900400"  # 종목조건검색조회

    params = {
        "user_id": user_id,  # 사용자 HTS ID
        "seq": seq  # 사용자조건 키값
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output2)
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 종목조건검색 목록조회[국내주식-038]
##############################################################################################

def psearch_title(
        user_id: str  # [필수] 사용자 HTS ID (ex. U:업종)
) -> pd.DataFrame:
    """
    [국내주식] 시세분석 > 종목조건검색 목록조회[국내주식-038]
    HTS(efriend Plus) [0110] 조건검색에서 등록 및 서버저장한 나의 조건 목록을 확인할 수 있는 API입니다.
    종목조건검색 목록조회 API(/uapi/domestic-stock/v1/quotations/psearch-title)의 output인 'seq'을 종목조건검색조회 API(/uapi/domestic-stock/v1/quotations/psearch-result)의 input으로 사용하시면 됩니다.

    ※ 시스템 안정성을 위해 API로 제공되는 조건검색 결과의 경우 조건당 100건으로 제한을 둔 점 양해 부탁드립니다.

    ※ [0110] 화면의 '대상변경' 설정사항은 HTS [0110] 사용자 조건검색 화면에만 적용됨에 유의 부탁드립니다.

    ※ '조회가 계속 됩니다. (다음을 누르십시오.)' 오류 발생 시 해결방법
    → HTS(efriend Plus) [0110] 조건검색 화면에서 조건을 등록하신 후, 왼쪽 하단의 "사용자조건 서버저장" 클릭하셔서 등록한 조건들을 서버로 보낸 후 다시 API 호출 시도 부탁드립니다.
    
    Args:
        user_id (str): [필수] 사용자 HTS ID (ex. U:업종)

    Returns:
        pd.DataFrame: 종목조건검색 목록 데이터
        
    Example:
        >>> df = psearch_title(user_id=trenv.my_htsid)
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/psearch-title"

    if user_id == "":
        raise ValueError("user_id is required (e.g. 'U:업종')")

    tr_id = "HHKST03900300"  # 종목조건검색 목록조회

    params = {
        "user_id": user_id  # 사용자 HTS ID
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output2)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 기본시세 > 국내주식 호가잔량 순위[국내주식-089]
##############################################################################################

def quote_balance(
        fid_vol_cnt: str,  # 거래량 수
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_rank_sort_cls_code: str,  # 순위 정렬 구분 코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_trgt_cls_code: str,  # 대상 구분 코드
        fid_trgt_exls_cls_code: str,  # 대상 제외 구분 코드
        fid_input_price_1: str,  # 입력 가격1
        fid_input_price_2: str,  # 입력 가격2
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None  # 누적 데이터프레임
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 호가잔량 순위[국내주식-089]
    국내주식 호가잔량 순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_vol_cnt (str): 입력값 없을때 전체 (거래량 ~)
        fid_cond_mrkt_div_code (str): 시장구분코드 (J:KRX, NX:NXT)
        fid_cond_scr_div_code (str): Unique key( 20172 )
        fid_input_iscd (str): 0000(전체) 코스피(0001), 코스닥(1001), 코스피200(2001)
        fid_rank_sort_cls_code (str): 0: 순매수잔량순, 1:순매도잔량순, 2:매수비율순, 3:매도비율순
        fid_div_cls_code (str): 0:전체
        fid_trgt_cls_code (str): 0:전체
        fid_trgt_exls_cls_code (str): 0:전체
        fid_input_price_1 (str): 입력값 없을때 전체 (가격 ~)
        fid_input_price_2 (str): 입력값 없을때 전체 (~ 가격)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 호가잔량 순위 데이터
        
    Example:
        >>> df = quote_balance(
        ...     fid_vol_cnt="",
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_cond_scr_div_code="20172",
        ...     fid_input_iscd="0000",
        ...     fid_rank_sort_cls_code="0",
        ...     fid_div_cls_code="0",
        ...     fid_trgt_cls_code="0",
        ...     fid_trgt_exls_cls_code="0",
        ...     fid_input_price_1="",
        ...     fid_input_price_2=""
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/quote-balance"
    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code != "J":
        raise ValueError("조건 시장 분류 코드 확인요망!!!")
    if fid_cond_scr_div_code != "20172":
        raise ValueError("조건 화면 분류 코드 확인요망!!!")
    if fid_input_iscd not in ["0000", "0001", "1001", "2001"]:
        raise ValueError("입력 종목코드 확인요망!!!")
    if fid_rank_sort_cls_code not in ["0", "1", "2", "3"]:
        raise ValueError("순위 정렬 구분 코드 확인요망!!!")
    if fid_div_cls_code != "0":
        raise ValueError("분류 구분 코드 확인요망!!!")
    if fid_trgt_cls_code != "0":
        raise ValueError("대상 구분 코드 확인요망!!!")
    if fid_trgt_exls_cls_code != "0":
        raise ValueError("대상 제외 구분 코드 확인요망!!!")

    tr_id = "FHPST01720000"

    params = {
        "fid_vol_cnt": fid_vol_cnt,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_input_iscd": fid_input_iscd,
        "fid_rank_sort_cls_code": fid_rank_sort_cls_code,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_trgt_cls_code": fid_trgt_cls_code,
        "fid_trgt_exls_cls_code": fid_trgt_exls_cls_code,
        "fid_input_price_1": fid_input_price_1,
        "fid_input_price_2": fid_input_price_2,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            print("Call Next")
            ka.smart_sleep()
            return quote_balance(
                fid_vol_cnt,
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_rank_sort_cls_code,
                fid_div_cls_code,
                fid_trgt_cls_code,
                fid_trgt_exls_cls_code,
                fid_input_price_1,
                fid_input_price_2,
                "N", dataframe
            )
        else:
            print("The End")
            return dataframe
    else:
        # 오류 출력
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 상품기본조회[v1_국내주식-029]
##############################################################################################

def search_info(
        pdno: str,  # 상품번호
        prdt_type_cd: str,  # 상품유형코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    상품기본조회[v1_국내주식-029]
    상품기본조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        pdno (str): 상품번호 (예: '000660', 'KR4101SC0009', 'AAPL')
        prdt_type_cd (str): 상품유형코드 (예: '300', '301', '512')
        tr_cont (str): 연속 거래 여부 (기본값: 공백)
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 상품기본조회 데이터
        
    Example:
        >>> df = search_info('AAPL', '512')
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/search-info"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not pdno:
        logger.error("pdno is required. (e.g. '000660')")
        raise ValueError("pdno is required. (e.g. '000660')")

    if not prdt_type_cd:
        logger.error("prdt_type_cd is required. (e.g. '300')")
        raise ValueError("prdt_type_cd is required. (e.g. '300')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # API 호출 URL 및 거래 ID 설정

    tr_id = "CTPF1604R"

    # 요청 파라미터 설정
    params = {
        "PDNO": pdno,
        "PRDT_TYPE_CD": prdt_type_cd,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    # API 응답 처리
    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return search_info(
                pdno,
                prdt_type_cd,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 종목정보 > 주식기본조회[v1_국내주식-067]
##############################################################################################

def search_stock_info(
        prdt_type_cd: str,  # 상품유형코드
        pdno: str,  # 상품번호
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 종목정보 
    주식기본조회[v1_국내주식-067]
    주식기본조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        prdt_type_cd (str): 300: 주식, ETF, ETN, ELW  301 : 선물옵션  302 : 채권  306 : ELS'
        pdno (str): 종목번호 (6자리) ETN의 경우, Q로 시작 (EX. Q500001)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 주식기본조회 데이터
        
    Example:
        >>> df = search_stock_info("300", "000660")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/search-stock-info"
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not prdt_type_cd:
        logger.error("prdt_type_cd is required. (e.g. '300')")
        raise ValueError("prdt_type_cd is required. (e.g. '300')")

    if not pdno:
        logger.error("pdno is required. (e.g. '000660')")
        raise ValueError("pdno is required. (e.g. '000660')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "CTPF1002R"

    params = {
        "PRDT_TYPE_CD": prdt_type_cd,
        "PDNO": pdno,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
        else:
            current_data = pd.DataFrame()

        # 데이터프레임 병합
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        # 연속 거래 여부 확인
        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return search_stock_info(
                prdt_type_cd,
                pdno,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 순위분석 > 국내주식 공매도 상위종목[국내주식-133]
##############################################################################################

def short_sale(
        fid_aply_rang_vol: str,  # FID 적용 범위 거래량
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_period_div_code: str,  # 조회구분 (일/월)
        fid_input_cnt_1: str,  # 조회가간(일수)
        fid_trgt_exls_cls_code: str,  # 대상 제외 구분 코드
        fid_trgt_cls_code: str,  # FID 대상 구분 코드
        fid_aply_rang_prc_1: str,  # FID 적용 범위 가격1
        fid_aply_rang_prc_2: str,  # FID 적용 범위 가격2
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 공매도 상위종목[국내주식-133]
    국내주식 공매도 상위종목 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_aply_rang_vol (str): FID 적용 범위 거래량
        fid_cond_mrkt_div_code (str): 시장구분코드 (주식 J)
        fid_cond_scr_div_code (str): Unique key(20482)
        fid_input_iscd (str): 0000:전체, 0001:코스피, 1001:코스닥, 2001:코스피200, 4001: KRX100, 3003: 코스닥150
        fid_period_div_code (str): 조회구분 (일/월) D: 일, M:월
        fid_input_cnt_1 (str): 조회가간(일수): 조회구분(D) 0:1일, 1:2일, 2:3일, 3:4일, 4:1주일, 9:2주일, 14:3주일, 조회구분(M) 1:1개월, 2:2개월, 3:3개월
        fid_trgt_exls_cls_code (str): 대상 제외 구분 코드
        fid_trgt_cls_code (str): FID 대상 구분 코드
        fid_aply_rang_prc_1 (str): FID 적용 범위 가격1
        fid_aply_rang_prc_2 (str): FID 적용 범위 가격2
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 공매도 상위종목 데이터
        
    Example:
        >>> df = short_sale(
        ...     fid_aply_rang_vol="1000",
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_cond_scr_div_code="20482",
        ...     fid_input_iscd="0000",
        ...     fid_period_div_code="D",
        ...     fid_input_cnt_1="0",
        ...     fid_trgt_exls_cls_code="",
        ...     fid_trgt_cls_code="",
        ...     fid_aply_rang_prc_1="1000",
        ...     fid_aply_rang_prc_2="5000"
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/short-sale"
    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        return None
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20482')")
        return None
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '0000')")
        return None
    if not fid_period_div_code:
        logger.error("fid_period_div_code is required. (e.g. 'D')")
        return None
    if not fid_input_cnt_1:
        logger.error("fid_input_cnt_1 is required. (e.g. '0')")
        return None

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHPST04820000"

    params = {
        "FID_APLY_RANG_VOL": fid_aply_rang_vol,
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_PERIOD_DIV_CODE": fid_period_div_code,
        "FID_INPUT_CNT_1": fid_input_cnt_1,
        "FID_TRGT_EXLS_CLS_CODE": fid_trgt_exls_cls_code,
        "FID_TRGT_CLS_CODE": fid_trgt_cls_code,
        "FID_APLY_RANG_PRC_1": fid_aply_rang_prc_1,
        "FID_APLY_RANG_PRC_2": fid_aply_rang_prc_2,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return short_sale(
                fid_aply_rang_vol,
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_period_div_code,
                fid_input_cnt_1,
                fid_trgt_exls_cls_code,
                fid_trgt_cls_code,
                fid_aply_rang_prc_1,
                fid_aply_rang_prc_2,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 순위분석 > 국내주식 관심종목등록 상위[v1_국내주식-102]
##############################################################################################

def top_interest_stock(
        fid_input_iscd_2: str,  # 입력 종목코드2
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_trgt_cls_code: str,  # 대상 구분 코드
        fid_trgt_exls_cls_code: str,  # 대상 제외 구분 코드
        fid_input_price_1: str,  # 입력 가격1
        fid_input_price_2: str,  # 입력 가격2
        fid_vol_cnt: str,  # 거래량 수
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_input_cnt_1: str,  # 입력 수1
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 관심종목등록 상위[v1_국내주식-102]
    국내주식 관심종목등록 상위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_input_iscd_2 (str): 000000 : 필수입력값
        fid_cond_mrkt_div_code (str): 시장구분코드 (J:KRX, NX:NXT)
        fid_cond_scr_div_code (str): Unique key(20180)
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200
        fid_trgt_cls_code (str): 0 : 전체
        fid_trgt_exls_cls_code (str): 0 : 전체
        fid_input_price_1 (str): 입력값 없을때 전체 (가격 ~)
        fid_input_price_2 (str): 입력값 없을때 전체 (~ 가격)
        fid_vol_cnt (str): 입력값 없을때 전체 (거래량 ~)
        fid_div_cls_code (str): 0: 전체 1: 관리종목 2: 투자주의 3: 투자경고 4: 투자위험예고 5: 투자위험 6: 보통주 7: 우선주
        fid_input_cnt_1 (str): 순위검색 입력값(1: 1위부터, 10:10위부터)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 관심종목등록 상위 데이터
        
    Example:
        >>> df = top_interest_stock(
        ...     fid_input_iscd_2="000000",
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_cond_scr_div_code="20180",
        ...     fid_input_iscd="0000",
        ...     fid_trgt_cls_code="0",
        ...     fid_trgt_exls_cls_code="0",
        ...     fid_input_price_1="",
        ...     fid_input_price_2="",
        ...     fid_vol_cnt="",
        ...     fid_div_cls_code="0",
        ...     fid_input_cnt_1="1"
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/top-interest-stock"
    # 필수 파라미터 검증
    if not fid_input_iscd_2:
        logger.error("fid_input_iscd_2 is required. (e.g. '000000')")
        raise ValueError("fid_input_iscd_2 is required. (e.g. '000000')")
    if fid_cond_mrkt_div_code not in ['J']:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'J')")
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20180')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20180')")
    if fid_input_iscd not in ['0000', '0001', '1001', '2001']:
        logger.error("fid_input_iscd is required. (e.g. '0000', '0001', '1001', '2001')")
        raise ValueError("fid_input_iscd is required. (e.g. '0000', '0001', '1001', '2001')")
    if fid_div_cls_code not in ['0', '1', '2', '3', '4', '5', '6', '7']:
        logger.error("fid_div_cls_code is required. (e.g. '0', '1', '2', '3', '4', '5', '6', '7')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0', '1', '2', '3', '4', '5', '6', '7')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHPST01800000"

    params = {
        "fid_input_iscd_2": fid_input_iscd_2,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_input_iscd": fid_input_iscd,
        "fid_trgt_cls_code": fid_trgt_cls_code,
        "fid_trgt_exls_cls_code": fid_trgt_exls_cls_code,
        "fid_input_price_1": fid_input_price_1,
        "fid_input_price_2": fid_input_price_2,
        "fid_vol_cnt": fid_vol_cnt,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_input_cnt_1": fid_input_cnt_1,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return top_interest_stock(
                fid_input_iscd_2,
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_trgt_cls_code,
                fid_trgt_exls_cls_code,
                fid_input_price_1,
                fid_input_price_2,
                fid_vol_cnt,
                fid_div_cls_code,
                fid_input_cnt_1,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 순위분석 > 국내주식 당사매매종목 상위[v1_국내주식-104]
##############################################################################################

def traded_by_company(
        fid_trgt_exls_cls_code: str,  # 대상 제외 구분 코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_rank_sort_cls_code: str,  # 순위 정렬 구분 코드
        fid_input_date_1: str,  # 입력 날짜1
        fid_input_date_2: str,  # 입력 날짜2
        fid_input_iscd: str,  # 입력 종목코드
        fid_trgt_cls_code: str,  # 대상 구분 코드
        fid_aply_rang_vol: str,  # 적용 범위 거래량
        fid_aply_rang_prc_2: str,  # 적용 범위 가격2
        fid_aply_rang_prc_1: str,  # 적용 범위 가격1
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 당사매매종목 상위[v1_국내주식-104]
    국내주식 당사매매종목 상위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_trgt_exls_cls_code (str): 0: 전체
        fid_cond_mrkt_div_code (str): 시장구분코드 (J:KRX, NX:NXT)
        fid_cond_scr_div_code (str): Unique key(20186)
        fid_div_cls_code (str): 0:전체, 1:관리종목, 2:투자주의, 3:투자경고, 4:투자위험예고, 5:투자위험, 6:보통주, 7:우선주
        fid_rank_sort_cls_code (str): 0:매도상위,1:매수상위
        fid_input_date_1 (str): 기간~
        fid_input_date_2 (str): ~기간
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100
        fid_trgt_cls_code (str): 0: 전체
        fid_aply_rang_vol (str): 0: 전체, 100: 100주 이상
        fid_aply_rang_prc_2 (str): ~ 가격
        fid_aply_rang_prc_1 (str): 가격 ~
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 당사매매종목 상위 데이터
        
    Example:
        >>> df = traded_by_company(
        ...     fid_trgt_exls_cls_code="0",
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_cond_scr_div_code="20186",
        ...     fid_div_cls_code="0",
        ...     fid_rank_sort_cls_code="0",
        ...     fid_input_date_1="20240314",
        ...     fid_input_date_2="20240315",
        ...     fid_input_iscd="0000",
        ...     fid_trgt_cls_code="0",
        ...     fid_aply_rang_vol="0",
        ...     fid_aply_rang_prc_2="",
        ...     fid_aply_rang_prc_1=""
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/traded-by-company"
    # 필수 파라미터 검증
    if not fid_trgt_exls_cls_code:
        logger.error("fid_trgt_exls_cls_code is required. (e.g. '0')")
        return None
    if fid_cond_mrkt_div_code != "J":
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'J')")
        return None
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20186')")
        return None
    if fid_div_cls_code not in ["0", "1", "2", "3", "4", "5", "6", "7"]:
        logger.error("fid_div_cls_code is required. (e.g. '0', '1', '2', '3', '4', '5', '6', '7')")
        return None
    if fid_rank_sort_cls_code not in ["0", "1"]:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '0', '1')")
        return None
    if not fid_input_date_1:
        logger.error("fid_input_date_1 is required.")
        return None
    if not fid_input_date_2:
        logger.error("fid_input_date_2 is required.")
        return None
    if fid_input_iscd not in ["0000", "0001", "1001", "2001", "4001"]:
        logger.error("fid_input_iscd is required. (e.g. '0000', '0001', '1001', '2001', '4001')")
        return None
    if not fid_trgt_cls_code:
        logger.error("fid_trgt_cls_code is required. (e.g. '0')")
        return None
    if fid_aply_rang_vol not in ["0", "100"]:
        logger.error("fid_aply_rang_vol is required. (e.g. '0', '100')")
        return None

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHPST01860000"

    params = {
        "fid_trgt_exls_cls_code": fid_trgt_exls_cls_code,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_rank_sort_cls_code": fid_rank_sort_cls_code,
        "fid_input_date_1": fid_input_date_1,
        "fid_input_date_2": fid_input_date_2,
        "fid_input_iscd": fid_input_iscd,
        "fid_trgt_cls_code": fid_trgt_cls_code,
        "fid_aply_rang_vol": fid_aply_rang_vol,
        "fid_aply_rang_prc_2": fid_aply_rang_prc_2,
        "fid_aply_rang_prc_1": fid_aply_rang_prc_1,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return traded_by_company(
                fid_trgt_exls_cls_code,
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_div_cls_code,
                fid_rank_sort_cls_code,
                fid_input_date_1,
                fid_input_date_2,
                fid_input_iscd,
                fid_trgt_cls_code,
                fid_aply_rang_vol,
                fid_aply_rang_prc_2,
                fid_aply_rang_prc_1,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 에러 처리
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 시세분석 > 국내주식 체결금액별 매매비중 [국내주식-192]
##############################################################################################

def tradprt_byamt(
        fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J)
        fid_cond_scr_div_code: str,  # [필수] 조건화면분류코드 (ex. 11119)
        fid_input_iscd: str  # [필수] 입력 종목코드 (ex. 123456)
) -> pd.DataFrame:
    """
    국내주식 체결금액별 매매비중 API입니다.
    한국투자 HTS(eFriend Plus) > [0135] 체결금액별 매매비중 화면의 "상단 표" 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT)
        fid_cond_scr_div_code (str): [필수] 조건화면분류코드 (ex. 11119)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 123456)

    Returns:
        pd.DataFrame: 국내주식 체결금액별 매매비중 데이터
        
    Example:
        >>> df = tradprt_byamt("J", "11119", "005930")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/tradprt-byamt"

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")

    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '11119')")

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '123456')")

    tr_id = "FHKST111900C0"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_INPUT_ISCD": fid_input_iscd
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 순위분석 > 국내주식 체결강도 상위[v1_국내주식-101]
##############################################################################################

def volume_power(
        fid_trgt_exls_cls_code: str,  # 대상 제외 구분 코드
        fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 조건 화면 분류 코드
        fid_input_iscd: str,  # 입력 종목코드
        fid_div_cls_code: str,  # 분류 구분 코드
        fid_input_price_1: str,  # 입력 가격1
        fid_input_price_2: str,  # 입력 가격2
        fid_vol_cnt: str,  # 거래량 수
        fid_trgt_cls_code: str,  # 대상 구분 코드
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석 
    국내주식 체결강도 상위[v1_국내주식-101]
    국내주식 체결강도 상위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_trgt_exls_cls_code (str): 0 : 전체
        fid_cond_mrkt_div_code (str): 시장구분코드 (J:KRX, NX:NXT)
        fid_cond_scr_div_code (str): Unique key( 20168 )
        fid_input_iscd (str): 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200
        fid_div_cls_code (str): 0: 전체,  1: 보통주 2: 우선주
        fid_input_price_1 (str): 입력값 없을때 전체 (가격 ~)
        fid_input_price_2 (str): 입력값 없을때 전체 (~ 가격)
        fid_vol_cnt (str): 입력값 없을때 전체 (거래량 ~)
        fid_trgt_cls_code (str): 0 : 전체
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 국내주식 체결강도 상위 데이터
        
    Example:
        >>> df = volume_power(
        ...     fid_trgt_exls_cls_code="0",
        ...     fid_cond_mrkt_div_code="J",
        ...     fid_cond_scr_div_code="20168",
        ...     fid_input_iscd="0000",
        ...     fid_div_cls_code="0",
        ...     fid_input_price_1="",
        ...     fid_input_price_2="",
        ...     fid_vol_cnt="",
        ...     fid_trgt_cls_code="0"
        ... )
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/ranking/volume-power"
    # 필수 파라미터 검증
    if not fid_trgt_exls_cls_code:
        logger.error("fid_trgt_exls_cls_code is required. (e.g. '0')")
        raise ValueError("fid_trgt_exls_cls_code is required. (e.g. '0')")
    if fid_cond_mrkt_div_code != "J":
        logger.error("fid_cond_mrkt_div_code must be 'J'.")
        raise ValueError("fid_cond_mrkt_div_code must be 'J'.")
    if fid_cond_scr_div_code != "20168":
        logger.error("fid_cond_scr_div_code must be '20168'.")
        raise ValueError("fid_cond_scr_div_code must be '20168'.")
    if fid_input_iscd not in ["0000", "0001", "1001", "2001"]:
        logger.error("fid_input_iscd must be one of ['0000', '0001', '1001', '2001'].")
        raise ValueError("fid_input_iscd must be one of ['0000', '0001', '1001', '2001'].")
    if fid_div_cls_code not in ["0", "1", "2"]:
        logger.error("fid_div_cls_code must be one of ['0', '1', '2'].")
        raise ValueError("fid_div_cls_code must be one of ['0', '1', '2'].")
    if not fid_trgt_cls_code:
        logger.error("fid_trgt_cls_code is required. (e.g. '0')")
        raise ValueError("fid_trgt_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHPST01680000"

    params = {
        "fid_trgt_exls_cls_code": fid_trgt_exls_cls_code,
        "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
        "fid_cond_scr_div_code": fid_cond_scr_div_code,
        "fid_input_iscd": fid_input_iscd,
        "fid_div_cls_code": fid_div_cls_code,
        "fid_input_price_1": fid_input_price_1,
        "fid_input_price_2": fid_input_price_2,
        "fid_vol_cnt": fid_vol_cnt,
        "fid_trgt_cls_code": fid_trgt_cls_code,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # 응답 데이터 처리
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return volume_power(
                fid_trgt_exls_cls_code,
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_input_iscd,
                fid_div_cls_code,
                fid_input_price_1,
                fid_input_price_2,
                fid_vol_cnt,
                fid_trgt_cls_code,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        # API 에러 처리
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()


##############################################################################################
# [국내주식] 순위분석 > 거래량순위[v1_국내주식-047]
##############################################################################################

def volume_rank(
        fid_cond_mrkt_div_code: str,  # 필수, 조건 시장 분류 코드
        fid_cond_scr_div_code: str,  # 필수, 조건 화면 분류 코드
        fid_input_iscd: str,  # 필수, 입력 종목코드
        fid_div_cls_code: str,  # 필수, 분류 구분 코드
        fid_blng_cls_code: str,  # 필수, 소속 구분 코드
        fid_trgt_cls_code: str,  # 필수, 대상 구분 코드
        fid_trgt_exls_cls_code: str,  # 필수, 대상 제외 구분 코드
        fid_input_price_1: str,  # 필수, 입력 가격1
        fid_input_price_2: str,  # 필수, 입력 가격2
        fid_vol_cnt: str,  # 필수, 거래량 수
        fid_input_date_1: str,  # 필수, 입력 날짜1
        tr_cont: str = "",  # 선택, 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None  # 선택, 누적 데이터프레임
) -> Optional[pd.DataFrame]:
    """
    [국내주식] 순위분석
    순위분석[v1_국내주식-047]
    순위분석 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 ("J": KRX, "NX": NXT, "UN": 통합, "W": ELW)
        fid_cond_scr_div_code (str): 조건 화면 분류 코드 ("20171")
        fid_input_iscd (str): 입력 종목코드 ("0000": 전체, 기타: 업종코드)
        fid_div_cls_code (str): 분류 구분 코드 ("0": 전체, "1": 보통주, "2": 우선주)
        fid_blng_cls_code (str): 소속 구분 코드 ("0": 평균거래량, "1": 거래증가율, "2": 평균거래회전율, "3": 거래금액순, "4": 평균거래금액회전율)
        fid_trgt_cls_code (str): 대상 구분 코드 (9자리, "1" or "0", 차례대로 증거금 30% 40% 50% 60% 100% 신용보증금 30% 40% 50% 60%)
        fid_trgt_exls_cls_code (str): 대상 제외 구분 코드 (10자리, "1" or "0", 차례대로 투자위험/경고/주의 관리종목 정리매매 불성실공시 우선주 거래정지 ETF ETN 신용주문불가 SPAC)
        fid_input_price_1 (str): 입력 가격1 (가격 ~, 전체 가격 대상 조회 시 공란)
        fid_input_price_2 (str): 입력 가격2 (~ 가격, 전체 가격 대상 조회 시 공란)
        fid_vol_cnt (str): 거래량 수 (거래량 ~, 전체 거래량 대상 조회 시 공란)
        fid_input_date_1 (str): 입력 날짜1 (공란)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        
    Returns:
        pd.DataFrame: 순위분석 데이터
        
    Example:
        >>> df = volume_rank(fid_cond_mrkt_div_code="J", fid_cond_scr_div_code="20171", fid_input_iscd="0000", fid_div_cls_code="0", fid_blng_cls_code="0", fid_trgt_cls_code="111111111", fid_trgt_exls_cls_code="0000000000", fid_input_price_1="0", fid_input_price_2="1000000", fid_vol_cnt="100000", fid_input_date_1="")
        >>> print(df)
    """
    api_url = "/uapi/domestic-stock/v1/quotations/volume-rank"
    if fid_cond_mrkt_div_code not in ["J", "NX", "UN", "W"]:
        raise ValueError("조건 시장 분류 코드 확인요망!!!")

    if fid_cond_scr_div_code != "20171":
        raise ValueError("조건 화면 분류 코드 확인요망!!!")

    if fid_input_iscd == "":  # "0000"은 전체를 의미하므로 유효한 값
        raise ValueError("입력 종목코드 확인요망!!!")

    if fid_div_cls_code not in ["0", "1", "2"]:
        raise ValueError("분류 구분 코드 확인요망!!!")

    if fid_blng_cls_code not in ["0", "1", "2", "3", "4"]:
        raise ValueError("소속 구분 코드 확인요망!!!")

    # To fix: description에 나와있는 자릿수와 다름(0 6개 입력해야 나옴)
    # if len(fid_trgt_cls_code) != 9 or not (all(c == '0' for c in fid_trgt_cls_code) or all(c == '1' for c in fid_trgt_cls_code)):
    #     raise ValueError("대상 구분 코드 확인요망!!!")

    # if len(fid_trgt_exls_cls_code) != 10 or not (all(c == '0' for c in fid_trgt_exls_cls_code) or all(c == '1' for c in fid_trgt_exls_cls_code)):
    #     raise ValueError("대상 제외 구분 코드 확인요망!!!")

    tr_id = "FHPST01710000"  # 거래량순위

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_BLNG_CLS_CODE": fid_blng_cls_code,
        "FID_TRGT_CLS_CODE": fid_trgt_cls_code,
        "FID_TRGT_EXLS_CLS_CODE": fid_trgt_exls_cls_code,
        "FID_INPUT_PRICE_1": fid_input_price_1,
        "FID_INPUT_PRICE_2": fid_input_price_2,
        "FID_VOL_CNT": fid_vol_cnt,
        "FID_INPUT_DATE_1": fid_input_date_1
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            current_data = pd.DataFrame(res.getBody().output)
        else:
            current_data = pd.DataFrame()

        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data

        tr_cont = res.getHeader().tr_cont

        if tr_cont == "M":  # 다음 페이지 존재
            print("Call Next")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return volume_rank(
                fid_cond_mrkt_div_code, fid_cond_scr_div_code, fid_input_iscd,
                fid_div_cls_code, fid_blng_cls_code, fid_trgt_cls_code,
                fid_trgt_exls_cls_code, fid_input_price_1, fid_input_price_2,
                fid_vol_cnt, fid_input_date_1, "N", dataframe
            )
        else:
            print("The End")
            return dataframe
    else:
        res.printError(api_url)
        return pd.DataFrame()
