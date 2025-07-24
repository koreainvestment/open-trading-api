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
# [국내주식] 기본시세 > ETF 구성종목시세[국내주식-073]
##############################################################################################

def inquire_component_stock_price(
    fid_cond_mrkt_div_code: str,
    fid_input_iscd: str,
    fid_cond_scr_div_code: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    ETF 구성종목시세 API입니다. 
    한국투자 HTS(eFriend Plus) > [0245] ETF/ETN 구성종목시세 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건시장분류코드 (ex. J: 주식/ETF/ETN)
        fid_input_iscd (str): [필수] 입력종목코드 (ex. 123456)
        fid_cond_scr_div_code (str): [필수] 조건화면분류코드 (ex. 11216)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터프레임, output2 데이터프레임)
        
    Raises:
        ValueError: 필수 파라미터가 누락된 경우
        
    Examples:
        >>> df1, df2 = inquire_component_stock_price("J", "069500", "11216")
        >>> print(df1)  # ETF 기본 정보
        >>> print(df2)  # ETF 구성종목 상세정보
    """
    
    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J: 주식/ETF/ETN')")
        
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '123456')")
        
    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '11216')")
    
    # API 호출 설정
    tr_id = "FHKST121600C0"
    
    # 파라미터 설정

    api_url = "/uapi/etfetn/v1/quotations/inquire-component-stock-price"


    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code
    }
    
    # API 호출
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        # output1 (object) -> DataFrame 변환
        output1_data = res.getBody().output1
        df1 = pd.DataFrame([output1_data]) if output1_data else pd.DataFrame()
        
        # output2 (array) -> DataFrame 변환
        output2_data = res.getBody().output2
        df2 = pd.DataFrame(output2_data) if output2_data else pd.DataFrame()
        
        return df1, df2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [국내주식] 기본시세 > ETF/ETN 현재가[v1_국내주식-068]
##############################################################################################

def inquire_price(
    fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
    fid_input_iscd: str,          # 입력 종목코드
) -> pd.DataFrame:
    """
    ETF/ETN 현재가 API입니다.
    한국투자 HTS(eFriend Plus) > [0240] ETF/ETN 현재가 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J:KRX, NX:NXT, UN:통합)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 123456)

    Returns:
        pd.DataFrame: ETF/ETN 현재가 데이터
        
    Example:
        >>> df = inquire_price("J", "123456")
        >>> print(df)
    """

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:KRX, NX:NXT, UN:통합')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '123456')")

    tr_id = "FHPST02400000"  # ETF/ETN 현재가


    api_url = "/uapi/etfetn/v1/quotations/inquire-price"



    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,  # 조건 시장 분류 코드
        "FID_INPUT_ISCD": fid_input_iscd,                  # 입력 종목코드
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output, index=[0])
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

##############################################################################################
# [국내주식] 기본시세 > NAV 비교추이(일)[v1_국내주식-071]
##############################################################################################

def nav_comparison_daily_trend(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_input_iscd: str,          # 입력종목코드
    fid_input_date_1: str,        # 조회시작일자
    fid_input_date_2: str         # 조회종료일자
) -> pd.DataFrame:
    """
    NAV 비교추이(일) API입니다.
    한국투자 HTS(eFriend Plus) > [0244] ETF/ETN 비교추이(NAV/IIV) 좌측 화면 "일별" 비교추이 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    실전계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건시장분류코드 (ex. J:주식)
        fid_input_iscd (str): [필수] 입력종목코드 (ex. 123456)
        fid_input_date_1 (str): [필수] 조회시작일자 (ex. 20240101)
        fid_input_date_2 (str): [필수] 조회종료일자 (ex. 20240220)

    Returns:
        pd.DataFrame: NAV 비교추이(일) 데이터
        
    Example:
        >>> df = nav_comparison_daily_trend("J", "069500", "20240101", "20240220")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J:주식')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '123456')")
    
    if fid_input_date_1 == "":
        raise ValueError("fid_input_date_1 is required (e.g. '20240101')")
    
    if fid_input_date_2 == "":
        raise ValueError("fid_input_date_2 is required (e.g. '20240220')")

    tr_id = "FHPST02440200"  # NAV 비교추이(일)


    api_url = "/uapi/etfetn/v1/quotations/nav-comparison-daily-trend"



    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,  # 조건시장분류코드
        "FID_INPUT_ISCD": fid_input_iscd,                  # 입력종목코드
        "FID_INPUT_DATE_1": fid_input_date_1,              # 조회시작일자
        "FID_INPUT_DATE_2": fid_input_date_2               # 조회종료일자
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
# [국내주식] 기본시세 > NAV 비교추이(분)[v1_국내주식-070]
##############################################################################################

def nav_comparison_time_trend(
    fid_cond_mrkt_div_code: str,  # [필수] 조건시장분류코드 (ex. E)
    fid_input_iscd: str,          # [필수] 입력종목코드 (ex. 123456)
    fid_hour_cls_code: str        # [필수] 시간구분코드 (ex. 60:1분,180:3분,...,7200:120분)
) -> pd.DataFrame:
    """
    NAV 비교추이(분) API입니다.
    한국투자 HTS(eFriend Plus) > [0244] ETF/ETN 비교추이(NAV/IIV) 좌측 화면 "분별" 비교추이 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    실전계좌의 경우, 한 번의 호출에 최근 30건까지 확인 가능합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건시장분류코드 (ex. E)
        fid_input_iscd (str): [필수] 입력종목코드 (ex. 123456)
        fid_hour_cls_code (str): [필수] 시간구분코드 (ex. 60:1분,180:3분,...,7200:120분)

    Returns:
        pd.DataFrame: NAV 비교추이(분) 데이터
        
    Example:
        >>> df = nav_comparison_time_trend("E", "069500", "60")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "" or fid_cond_mrkt_div_code is None:
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'E')")
    
    if fid_input_iscd == "" or fid_input_iscd is None:
        raise ValueError("fid_input_iscd is required (e.g. '123456')")
    
    if fid_hour_cls_code == "" or fid_hour_cls_code is None:
        raise ValueError("fid_hour_cls_code is required (e.g. '60:1분,180:3분,...,7200:120분')")

    tr_id = "FHPST02440100"


    api_url = "/uapi/etfetn/v1/quotations/nav-comparison-time-trend"



    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_HOUR_CLS_CODE": fid_hour_cls_code
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        # output (array) -> pd.DataFrame
        current_data = pd.DataFrame(res.getBody().output)
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

##############################################################################################
# [국내주식] 기본시세 > NAV 비교추이(종목)[v1_국내주식-069]
##############################################################################################

def nav_comparison_trend(
    fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. J)
    fid_input_iscd: str,          # [필수] 입력 종목코드
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    NAV 비교추이(종목) API입니다.
    한국투자 HTS(eFriend Plus) > [0244] ETF/ETN 비교추이(NAV/IIV) 좌측 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. J)
        fid_input_iscd (str): [필수] 입력 종목코드
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: output1, output2 데이터프레임
        
    Example:
        >>> output1, output2 = nav_comparison_trend("J", "069500")
        >>> print(output1)
        >>> print(output2)
    """
    
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'J')")
        
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required")

    tr_id = "FHPST02440000"  # NAV 비교추이(종목)


    api_url = "/uapi/etfetn/v1/quotations/nav-comparison-trend"



    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,  # 조건 시장 분류 코드
        "FID_INPUT_ISCD": fid_input_iscd,                  # 입력 종목코드
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        output1_data = pd.DataFrame(res.getBody().output1, index=[0])
        output2_data = pd.DataFrame(res.getBody().output2, index=[0])
        
        logging.info("Data fetch complete.")
        return output1_data, output2_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

