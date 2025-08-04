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
# [국내선물옵션] 기본시세 > 국내옵션전광판_콜풋[국내선물-022]
##############################################################################################

def display_board_callput(
    fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. O: 옵션)
    fid_cond_scr_div_code: str,   # [필수] 조건 화면 분류 코드 (ex. 20503)
    fid_mrkt_cls_code: str,       # [필수] 시장 구분 코드 (ex. CO: 콜옵션)
    fid_mtrt_cnt: str,            # [필수] 만기 수 (ex. 202508)
    fid_mrkt_cls_code1: str,      # [필수] 시장 구분 코드 (ex. PO: 풋옵션)
    fid_cond_mrkt_cls_code: str = ""  # 조건 시장 구분 코드
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    국내옵션전광판_콜풋 API입니다.
    한국투자 HTS(eFriend Plus) > [0503] 선물옵션 종합시세(Ⅰ) 화면의 "중앙" 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

    ※ output1, output2 각각 100건까지만 확인이 가능합니다. (FY25년도 서비스 개선 예정)
    ※ 조회시간이 긴 API인 점 참고 부탁드리며, 잦은 호출을 삼가해주시기 바랍니다. (1초당 최대 1건 권장)
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. O: 옵션)
        fid_cond_scr_div_code (str): [필수] 조건 화면 분류 코드 (ex. 20503)
        fid_mrkt_cls_code (str): [필수] 시장 구분 코드 (ex. CO: 콜옵션)
        fid_mtrt_cnt (str): [필수] 만기 수 (ex. 202508)
        fid_mrkt_cls_code1 (str): [필수] 시장 구분 코드 (ex. PO: 풋옵션)
        fid_cond_mrkt_cls_code (str): 조건 시장 구분 코드

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 DataFrame, output2 DataFrame)
        
    Example:
        >>> df1, df2 = display_board_callput("O", "20503", "CO", "202508", "PO")
        >>> print(df1)
        >>> print(df2)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'O')")
        
    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '20503')")
        
    if fid_mrkt_cls_code == "":
        raise ValueError("fid_mrkt_cls_code is required (e.g. 'CO')")
        
    if fid_mtrt_cnt == "":
        raise ValueError("fid_mtrt_cnt is required (e.g. '202508')")
        
    if fid_mrkt_cls_code1 == "":
        raise ValueError("fid_mrkt_cls_code1 is required (e.g. 'PO')")

    tr_id = "FHPIF05030100"


    api_url = "/uapi/domestic-futureoption/v1/quotations/display-board-callput"



    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_MRKT_CLS_CODE": fid_mrkt_cls_code,
        "FID_MTRT_CNT": fid_mtrt_cnt,
        "FID_MRKT_CLS_CODE1": fid_mrkt_cls_code1,
        "FID_COND_MRKT_CLS_CODE": fid_cond_mrkt_cls_code
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        output1_df = pd.DataFrame(res.getBody().output1)
        output2_df = pd.DataFrame(res.getBody().output2)
        return output1_df, output2_df
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [국내선물옵션] 기본시세 > 국내옵션전광판_선물[국내선물-023]
##############################################################################################

def display_board_futures(
    fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
    fid_cond_scr_div_code: str,   # 조건 화면 분류 코드
    fid_cond_mrkt_cls_code: str   # 조건 시장 구분 코드
) -> pd.DataFrame:
    """
    국내옵션전광판_선물 API입니다.
    한국투자 HTS(eFriend Plus) > [0503] 선물옵션 종합시세(Ⅰ) 화면의 "하단" 기능을 API로 개발한 사항입니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. F)
        fid_cond_scr_div_code (str): [필수] 조건 화면 분류 코드 (ex. 20503)
        fid_cond_mrkt_cls_code (str): [필수] 조건 시장 구분 코드 (ex. MKI)

    Returns:
        pd.DataFrame: 국내선물옵션 선물전광판 데이터
        
    Example:
        >>> df = display_board_futures("F", "20503", "MKI")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'F')")
    
    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '20503')")
    
    if fid_cond_mrkt_cls_code == "":
        raise ValueError("fid_cond_mrkt_cls_code is required (e.g. 'MKI')")

    tr_id = "FHPIF05030200"


    api_url = "/uapi/domestic-futureoption/v1/quotations/display-board-futures"



    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_COND_MRKT_CLS_CODE": fid_cond_mrkt_cls_code
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        return pd.DataFrame(res.getBody().output)
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

##############################################################################################
# [국내선물옵션] 기본시세 > 국내옵션전광판_옵션월물리스트[국내선물-020]
##############################################################################################

def display_board_option_list(
    fid_cond_scr_div_code: str,
    fid_cond_mrkt_div_code: str = "",
    fid_cond_mrkt_cls_code: str = ""
) -> pd.DataFrame:
    """
    국내옵션전광판_옵션월물리스트 API입니다.
    한국투자 HTS(eFriend Plus) > [0503] 선물옵션 종합시세(Ⅰ) 화면의 "월물리스트 목록 확인" 기능을 API로 개발한 사항입니다.
    
    Args:
        fid_cond_scr_div_code (str): [필수] 조건 화면 분류 코드 (ex. 509)
        fid_cond_mrkt_div_code (str): 조건 시장 분류 코드
        fid_cond_mrkt_cls_code (str): 조건 시장 구분 코드

    Returns:
        pd.DataFrame: 국내옵션전광판_옵션월물리스트 데이터
        
    Example:
        >>> df = display_board_option_list(fid_cond_scr_div_code="509")
        >>> print(df)
    """

    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '509')")

    tr_id = "FHPIO056104C0"


    api_url = "/uapi/domestic-futureoption/v1/quotations/display-board-option-list"



    params = {
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_MRKT_CLS_CODE": fid_cond_mrkt_cls_code
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

##############################################################################################
# [국내선물옵션] 기본시세 > 국내선물 기초자산 시세[국내선물-021]
##############################################################################################

def display_board_top(
    fid_cond_mrkt_div_code: str,  # [필수] 조건 시장 분류 코드 (ex. F)
    fid_input_iscd: str,          # [필수] 입력 종목코드 (ex. 101V06)
    fid_cond_mrkt_div_code1: str = "",  # 조건 시장 분류 코드
    fid_cond_scr_div_code: str = "",    # 조건 화면 분류 코드
    fid_mtrt_cnt: str = "",             # 만기 수
    fid_cond_mrkt_cls_code: str = ""    # 조건 시장 구분 코드
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    국내선물 기초자산 시세 API입니다.
    한국투자 HTS(eFriend Plus) > [0503] 선물옵션 종합시세(Ⅰ) 화면의 "상단 바" 기능을 API로 개발한 사항입니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. F)
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 101V06)
        fid_cond_mrkt_div_code1 (str): 조건 시장 분류 코드
        fid_cond_scr_div_code (str): 조건 화면 분류 코드
        fid_mtrt_cnt (str): 만기 수
        fid_cond_mrkt_cls_code (str): 조건 시장 구분 코드

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 데이터프레임 튜플
        
    Example:
        >>> output1, output2 = display_board_top(fid_cond_mrkt_div_code="F", fid_input_iscd="101W09")
        >>> print(output1)
        >>> print(output2)
    """

    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'F')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '101V06')")

    tr_id = "FHPIF05030000"


    api_url = "/uapi/domestic-futureoption/v1/quotations/display-board-top"



    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_COND_MRKT_DIV_CODE1": fid_cond_mrkt_div_code1,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_MTRT_CNT": fid_mtrt_cnt,
        "FID_COND_MRKT_CLS_CODE": fid_cond_mrkt_cls_code
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        output1 = pd.DataFrame(res.getBody().output1, index=[0])
        output2 = pd.DataFrame(res.getBody().output2)
        
        return output1, output2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [국내선물옵션] 기본시세 > 선물옵션 일중예상체결추이[국내선물-018]
##############################################################################################

def exp_price_trend(
    fid_input_iscd: str,  # [필수] 입력 종목코드 (ex. 101V06)
    fid_cond_mrkt_div_code: str  # [필수] 조건 시장 분류 코드 (ex. F)
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    선물옵션 일중예상체결추이 API입니다.
    한국투자 HTS(eFriend Plus) > [0548] 선물옵션 예상체결추이 화면의 기능을 API로 개발한 사항입니다.
    
    Args:
        fid_input_iscd (str): [필수] 입력 종목코드 (ex. 101V06)
        fid_cond_mrkt_div_code (str): [필수] 조건 시장 분류 코드 (ex. F)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 데이터프레임 튜플
        
    Example:
        >>> df1, df2 = exp_price_trend(fid_input_iscd="101W09", fid_cond_mrkt_div_code="F")
        >>> print(df1)
        >>> print(df2)
    """

    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '101V06')")
    
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'F')")

    tr_id = "FHPIF05110100"  # 선물옵션 일중예상체결추이


    api_url = "/uapi/domestic-futureoption/v1/quotations/exp-price-trend"



    params = {
        "FID_INPUT_ISCD": fid_input_iscd,  # 입력 종목코드
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code  # 조건 시장 분류 코드
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        # output1은 object 타입이므로 단일 행 DataFrame
        output1_data = pd.DataFrame([res.getBody().output1])
        
        # output2는 array 타입이므로 여러 행 DataFrame
        output2_data = pd.DataFrame(res.getBody().output2)
        
        return output1_data, output2_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [국내선물옵션] 기본시세 > 선물옵션 시세호가[v1_국내선물-007]
##############################################################################################

def inquire_asking_price(
    fid_cond_mrkt_div_code: str,  # [필수] FID 조건 시장 분류 코드 (ex. F: 지수선물, JF: 주식선물)
    fid_input_iscd: str,          # [필수] FID 입력 종목코드 (ex. 101W09)
    env_dv: str                   # [필수] 실전모의구분 (ex. real:실전, demo:모의)
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    선물옵션 시세호가 API입니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] FID 조건 시장 분류 코드 (ex. F: 지수선물, JF: 주식선물)
        fid_input_iscd (str): [필수] FID 입력 종목코드 (ex. 101W09)
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> df1, df2 = inquire_asking_price("F", "101W09", "real")
        >>> print(df1)
        >>> print(df2)
    """
    
    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'F', 'JF')")
        
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '101W09')")
        
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real', 'demo')")

    # TR_ID 설정
    if env_dv == "real":
        tr_id = "FHMIF10010000"
    elif env_dv == "demo":
        tr_id = "FHMIF10010000"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")


    api_url = "/uapi/domestic-futureoption/v1/quotations/inquire-asking-price"



    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        # output1 (object) -> DataFrame
        output1_data = pd.DataFrame([res.getBody().output1])
        
        # output2 (object) -> DataFrame
        output2_data = pd.DataFrame([res.getBody().output2])
        
        return output1_data, output2_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 잔고현황[v1_국내선물-004]
##############################################################################################

def inquire_balance(
    env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
    cano: str,    # [필수] 종합계좌번호
    acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 03)
    mgna_dvsn: str,     # [필수] 증거금 구분 (ex. 01:게시,02:유지)
    excc_stat_cd: str,  # [필수] 정산상태코드 (ex. 1:정산,2:본정산)
    FK200: str = "",    # 연속조회검색조건200
    NK200: str = "",    # 연속조회키200
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
    depth: int = 0,         # 내부 재귀 깊이 (자동 관리)
    max_depth: int = 10     # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    선물옵션 잔고현황 API입니다. 한 번의 호출에 최대 20건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 03)
        mgna_dvsn (str): [필수] 증거금 구분 (ex. 01:게시,02:유지)
        excc_stat_cd (str): [필수] 정산상태코드 (ex. 1:정산,2:본정산)
        FK200 (str): 연속조회검색조건200
        NK200 (str): 연속조회키200
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀 깊이 (자동 관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 선물옵션 잔고현황 데이터
        
    Example:
        >>> df1, df2 = inquire_balance(env_dv="real", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, mgna_dvsn="01", excc_stat_cd="1")
        >>> print(df1)
        >>> print(df2)
    """

    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")
    
    if cano == "":
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '03')")
    
    if mgna_dvsn == "":
        raise ValueError("mgna_dvsn is required (e.g. '01' or '02')")
    
    if excc_stat_cd == "":
        raise ValueError("excc_stat_cd is required (e.g. '1' or '2')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    # tr_id 설정
    if env_dv == "real":
        tr_id = "CTFO6118R"
    elif env_dv == "demo":
        tr_id = "VTFO6118R"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")


    api_url = "/uapi/domestic-futureoption/v1/trading/inquire-balance"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "MGNA_DVSN": mgna_dvsn,
        "EXCC_STAT_CD": excc_stat_cd,
        "CTX_AREA_FK200": FK200,
        "CTX_AREA_NK200": NK200
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
        FK200 = res.getBody().ctx_area_fk200
        NK200 = res.getBody().ctx_area_nk200
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_balance(
                env_dv, cano, acnt_prdt_cd, mgna_dvsn, excc_stat_cd,
                FK200, NK200, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 잔고정산손익내역[v1_국내선물-013]
##############################################################################################

def inquire_balance_settlement_pl(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드 (ex. 03)
    inqr_dt: str,  # 조회일자
    FK200: str = "",  # 연속조회검색조건200
    NK200: str = "",  # 연속조회키200
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    선물옵션 잔고정산손익내역 API입니다.
    
    Args:
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 03)
        inqr_dt (str): [필수] 조회일자
        FK200 (str): 연속조회검색조건200
        NK200 (str): 연속조회키200
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> df1, df2 = inquire_balance_settlement_pl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, inqr_dt="20230906")
        >>> print(df1)
        >>> print(df2)
    """

    if cano == "":
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required")
    
    if inqr_dt == "":
        raise ValueError("inqr_dt is required")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "CTFO6117R"


    api_url = "/uapi/domestic-futureoption/v1/trading/inquire-balance-settlement-pl"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "INQR_DT": inqr_dt,
        "CTX_AREA_FK200": FK200,
        "CTX_AREA_NK200": NK200
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
        current_data2 = pd.DataFrame([res.getBody().output2])
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2
            
        tr_cont = res.getHeader().tr_cont
        FK200 = res.getBody().ctx_area_fk200
        NK200 = res.getBody().ctx_area_nk200
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_balance_settlement_pl(
                cano, acnt_prdt_cd, inqr_dt, FK200, NK200, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 잔고평가손익내역[v1_국내선물-015]
##############################################################################################

def inquire_balance_valuation_pl(
        cano: str,  # [필수] 종합계좌번호 (ex. 계좌번호 체계(8-2)의 앞 8자리)
        acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 계좌번호 체계(8-2)의 뒤 2자리)
        mgna_dvsn: str,  # [필수] 증거금구분 (ex. 01:개시, 02:유지)
        excc_stat_cd: str,  # [필수] 정산상태코드 (ex. 1:정산, 2:본정산)
        FK200: str = "",  # 연속조회검색조건200 (ex. 연속조회검색조건200)
        NK200: str = "",  # 연속조회키200 (ex. 연속조회키200)
        tr_cont: str = "",  # 연속거래여부
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        depth: int = 0,  # 내부 재귀깊이 (자동관리)
        max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    시장별 투자자매매동향(일별) API입니다.
    한국투자 HTS(eFriend Plus) > [0404] 시장별 일별동향 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. 계좌번호 체계(8-2)의 앞 8자리)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 계좌번호 체계(8-2)의 뒤 2자리)
        mgna_dvsn (str): [필수] 증거금구분 (ex. 01:개시, 02:유지)
        excc_stat_cd (str): [필수] 정산상태코드 (ex. 1:정산, 2:본정산)
        FK200 (str): 연속조회검색조건200 (ex. 연속조회검색조건200)
        NK200 (str): 연속조회키200 (ex. 연속조회키200)
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터프레임, output2 데이터프레임)
        
    Example:
        >>> df1, df2 = inquire_balance_valuation_pl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, mgna_dvsn="01", excc_stat_cd="1")
        >>> print(df1)
        >>> print(df2)
    """

    if cano == "":
        raise ValueError("cano is required (e.g. '계좌번호 체계(8-2)의 앞 8자리')")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '계좌번호 체계(8-2)의 뒤 2자리')")

    if mgna_dvsn == "":
        raise ValueError("mgna_dvsn is required (e.g. '01:개시, 02:유지')")

    if excc_stat_cd == "":
        raise ValueError("excc_stat_cd is required (e.g. '1:정산, 2:본정산')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "CTFO6159R"  # 선물옵션 잔고평가손익내역


    api_url = "/uapi/domestic-futureoption/v1/trading/inquire-balance-valuation-pl"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "MGNA_DVSN": mgna_dvsn,
        "EXCC_STAT_CD": excc_stat_cd,
        "CTX_AREA_FK200": FK200,
        "CTX_AREA_NK200": NK200
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
        current_data2 = pd.DataFrame([res.getBody().output2])
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2

        tr_cont = res.getHeader().tr_cont
        FK200 = res.getBody().ctx_area_fk200
        NK200 = res.getBody().ctx_area_nk200

        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_balance_valuation_pl(
                cano, acnt_prdt_cd, mgna_dvsn, excc_stat_cd, FK200, NK200, "N", dataframe1, dataframe2, depth + 1,
                max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 주문체결내역조회[v1_국내선물-003]
##############################################################################################

def inquire_ccnl(
    env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
    cano: str,    # [필수] 종합계좌번호
    acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 03)
    strt_ord_dt: str,   # [필수] 시작주문일자 (ex. 주문내역 조회 시작 일자, YYYYMMDD)
    end_ord_dt: str,    # [필수] 종료주문일자 (ex. 주문내역 조회 마지막 일자, YYYYMMDD)
    sll_buy_dvsn_cd: str,  # [필수] 매도매수구분코드 (ex. 00:전체, 01:매도, 02:매수)
    ccld_nccs_dvsn: str,   # [필수] 체결미체결구분 (ex. 00:전체, 01:체결, 02:미체결)
    sort_sqn: str,      # [필수] 정렬순서 (ex. AS:정순, DS:역순)
    pdno: str = "",     # 상품번호
    strt_odno: str = "",  # 시작주문번호
    mket_id_cd: str = "",  # 시장ID코드
    FK200: str = "",    # 연속조회검색조건200
    NK200: str = "",    # 연속조회키200
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
    depth: int = 0,     # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    선물옵션 주문체결내역조회 API입니다. 한 번의 호출에 최대 100건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 03)
        strt_ord_dt (str): [필수] 시작주문일자 (ex. 주문내역 조회 시작 일자, YYYYMMDD)
        end_ord_dt (str): [필수] 종료주문일자 (ex. 주문내역 조회 마지막 일자, YYYYMMDD)
        sll_buy_dvsn_cd (str): [필수] 매도매수구분코드 (ex. 00:전체, 01:매도, 02:매수)
        ccld_nccs_dvsn (str): [필수] 체결미체결구분 (ex. 00:전체, 01:체결, 02:미체결)
        sort_sqn (str): [필수] 정렬순서 (ex. AS:정순, DS:역순)
        pdno (str, optional): 상품번호. Defaults to "".
        strt_odno (str, optional): 시작주문번호. Defaults to "".
        mket_id_cd (str, optional): 시장ID코드. Defaults to "".
        FK200 (str, optional): 연속조회검색조건200. Defaults to "".
        NK200 (str, optional): 연속조회키200. Defaults to "".
        tr_cont (str, optional): 연속거래여부. Defaults to "".
        dataframe1 (Optional[pd.DataFrame], optional): 누적 데이터프레임1. Defaults to None.
        dataframe2 (Optional[pd.DataFrame], optional): 누적 데이터프레임2. Defaults to None.
        depth (int, optional): 내부 재귀깊이 (자동관리). Defaults to 0.
        max_depth (int, optional): 최대 재귀 횟수 제한. Defaults to 10.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 주문체결내역 데이터 (output1, output2)
        
    Example:
        >>> df1, df2 = inquire_ccnl(env_dv="real", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, strt_ord_dt="20220730", end_ord_dt="20220830", sll_buy_dvsn_cd="00", ccld_nccs_dvsn="00", sort_sqn="DS")
        >>> print(df1)
        >>> print(df2)
    """

    # 필수 파라미터 검증
    if not env_dv:
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")
    
    if not cano:
        raise ValueError("cano is required")
    
    if not acnt_prdt_cd:
        raise ValueError("acnt_prdt_cd is required (e.g. '03')")
    
    if not strt_ord_dt:
        raise ValueError("strt_ord_dt is required (e.g. '20220730')")
    
    if not end_ord_dt:
        raise ValueError("end_ord_dt is required (e.g. '20220830')")
    
    if not sll_buy_dvsn_cd:
        raise ValueError("sll_buy_dvsn_cd is required (e.g. '00')")
    
    if not ccld_nccs_dvsn:
        raise ValueError("ccld_nccs_dvsn is required (e.g. '00')")
    
    if not sort_sqn:
        raise ValueError("sort_sqn is required (e.g. 'AS' or 'DS')")

    # 재귀 깊이 제한 확인
    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    # tr_id 설정
    if env_dv == "real":
        tr_id = "TTTO5201R"
    elif env_dv == "demo":
        tr_id = "VTTO5201R"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    # 파라미터 설정

    api_url = "/uapi/domestic-futureoption/v1/trading/inquire-ccnl"


    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "STRT_ORD_DT": strt_ord_dt,
        "END_ORD_DT": end_ord_dt,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "CCLD_NCCS_DVSN": ccld_nccs_dvsn,
        "SORT_SQN": sort_sqn,
        "PDNO": pdno,
        "STRT_ODNO": strt_odno,
        "MKET_ID_CD": mket_id_cd,
        "CTX_AREA_FK200": FK200,
        "CTX_AREA_NK200": NK200
    }
    
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 데이터 처리
        current_data1 = pd.DataFrame(res.getBody().output1)
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1
            
        # output2 데이터 처리 (단일 객체)
        current_data2 = pd.DataFrame(res.getBody().output2, index=[0])
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2
            
        # 연속조회 정보 업데이트
        tr_cont = res.getHeader().tr_cont
        FK200 = res.getBody().ctx_area_fk200
        NK200 = res.getBody().ctx_area_nk200
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_ccnl(
                env_dv, cano, acnt_prdt_cd, strt_ord_dt, end_ord_dt, 
                sll_buy_dvsn_cd, ccld_nccs_dvsn, sort_sqn, pdno, strt_odno, 
                mket_id_cd, FK200, NK200, "N", dataframe1, dataframe2, 
                depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 기준일체결내역[v1_국내선물-016]
##############################################################################################

def inquire_ccnl_bstime(
    cano: str,  # [필수] 종합계좌번호
    acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 03)
    ord_dt: str,  # [필수] 주문일자 (ex. 20250101)
    fuop_tr_strt_tmd: str,  # [필수] 선물옵션거래시작시각 (ex. HHMMSS)
    fuop_tr_end_tmd: str,  # [필수] 선물옵션거래종료시각 (ex. HHMMSS)
    FK200: str = "",  # 연속조회검색조건200
    NK200: str = "",  # 연속조회키200
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    선물옵션 기준일체결내역 API입니다.
    
    Args:
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 03)
        ord_dt (str): [필수] 주문일자 (ex. 20250101)
        fuop_tr_strt_tmd (str): [필수] 선물옵션거래시작시각 (ex. HHMMSS)
        fuop_tr_end_tmd (str): [필수] 선물옵션거래종료시각 (ex. HHMMSS)
        FK200 (str): 연속조회검색조건200
        NK200 (str): 연속조회키200
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 선물옵션 기준일체결내역 데이터 (output1, output2)
        
    Example:
        >>> df1, df2 = inquire_ccnl_bstime(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, ord_dt="20230920", fuop_tr_strt_tmd="000000", fuop_tr_end_tmd="240000")
        >>> print(df1)
        >>> print(df2)
    """

    if cano == "":
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '03')")
    
    if ord_dt == "":
        raise ValueError("ord_dt is required (e.g. '20250101')")
        
    if fuop_tr_strt_tmd == "":
        raise ValueError("fuop_tr_strt_tmd is required (e.g. 'HHMMSS')")
        
    if fuop_tr_end_tmd == "":
        raise ValueError("fuop_tr_end_tmd is required (e.g. 'HHMMSS')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "CTFO5139R"


    api_url = "/uapi/domestic-futureoption/v1/trading/inquire-ccnl-bstime"



    params = {
        "CANO": cano,  # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "ORD_DT": ord_dt,  # 주문일자
        "FUOP_TR_STRT_TMD": fuop_tr_strt_tmd,  # 선물옵션거래시작시각
        "FUOP_TR_END_TMD": fuop_tr_end_tmd,  # 선물옵션거래종료시각
        "CTX_AREA_FK200": FK200,  # 연속조회검색조건200
        "CTX_AREA_NK200": NK200  # 연속조회키200
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
        current_data2 = pd.DataFrame([res.getBody().output2])
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2
            
        tr_cont = res.getHeader().tr_cont
        FK200 = res.getBody().ctx_area_fk200
        NK200 = res.getBody().ctx_area_nk200
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_ccnl_bstime(
                cano, acnt_prdt_cd, ord_dt, fuop_tr_strt_tmd, fuop_tr_end_tmd, 
                FK200, NK200, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션기간약정수수료일별[v1_국내선물-017]
##############################################################################################

def inquire_daily_amount_fee(
    cano: str,                                    # [필수] 종합계좌번호
    acnt_prdt_cd: str,                           # [필수] 계좌상품코드 (ex. 03)
    inqr_strt_day: str,                          # [필수] 조회시작일 (ex. 20240401)
    inqr_end_day: str,                           # [필수] 조회종료일 (ex. 20240625)
    FK200: str = "",                             # 연속조회검색조건200
    NK200: str = "",                             # 연속조회키200
    tr_cont: str = "",                           # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,    # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,    # 누적 데이터프레임2
    depth: int = 0,                              # 내부 재귀깊이 (자동관리)
    max_depth: int = 10                          # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    선물옵션기간약정수수료일별 API입니다.
    
    Args:
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 03)
        inqr_strt_day (str): [필수] 조회시작일 (ex. 20240401)
        inqr_end_day (str): [필수] 조회종료일 (ex. 20240625)
        FK200 (str): 연속조회검색조건200
        NK200 (str): 연속조회키200
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 선물옵션기간약정수수료일별 데이터 (output1, output2)
        
    Example:
        >>> df1, df2 = inquire_daily_amount_fee(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, inqr_strt_day="20240401", inqr_end_day="20240625")
        >>> print(df1)
        >>> print(df2)
    """

    if cano == "":
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required")
    
    if inqr_strt_day == "":
        raise ValueError("inqr_strt_day is required")
    
    if inqr_end_day == "":
        raise ValueError("inqr_end_day is required")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "CTFO6119R"  # 선물옵션기간약정수수료일별


    api_url = "/uapi/domestic-futureoption/v1/trading/inquire-daily-amount-fee"



    params = {
        "CANO": cano,                       # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,      # 계좌상품코드
        "INQR_STRT_DAY": inqr_strt_day,    # 조회시작일
        "INQR_END_DAY": inqr_end_day,      # 조회종료일
        "CTX_AREA_FK200": FK200,           # 연속조회검색조건200
        "CTX_AREA_NK200": NK200            # 연속조회키200
    }
    
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
        FK200 = res.getBody().ctx_area_fk200
        NK200 = res.getBody().ctx_area_nk200
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_daily_amount_fee(
                cano, acnt_prdt_cd, inqr_strt_day, inqr_end_day, FK200, NK200, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [국내선물옵션] 기본시세 > 선물옵션기간별시세(일/주/월/년)[v1_국내선물-008]
##############################################################################################

def inquire_daily_fuopchartprice(
    fid_cond_mrkt_div_code: str,  # FID 조건 시장 분류 코드
    fid_input_iscd: str,          # 종목코드
    fid_input_date_1: str,        # 조회 시작일자
    fid_input_date_2: str,        # 조회 종료일자  
    fid_period_div_code: str,     # 기간분류코드
    env_dv: str                   # 실전모의구분
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    (지수)선물옵션 기간별시세 데이터(일/주/월/년) 조회 (최대 100건 조회)
    실전계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다. 
    모의계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] FID 조건 시장 분류 코드 (ex. F: 지수선물, O: 지수옵션)
        fid_input_iscd (str): [필수] 종목코드 (ex. 101W09)
        fid_input_date_1 (str): [필수] 조회 시작일자 (ex. 20250301)
        fid_input_date_2 (str): [필수] 조회 종료일자 (ex. 20250810)
        fid_period_div_code (str): [필수] 기간분류코드 (ex. D: 일봉, W: 주봉)
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (기본정보, 차트데이터) 튜플
        
    Example:
        >>> output1, output2 = inquire_daily_fuopchartprice(
        ...     fid_cond_mrkt_div_code="F",
        ...     fid_input_iscd="101W09",
        ...     fid_input_date_1="20250301",
        ...     fid_input_date_2="20250810",
        ...     fid_period_div_code="D",
        ...     env_dv="real"
        ... )
        >>> print(output1)
        >>> print(output2)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'F: 지수선물, O: 지수옵션')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '101W09')")
    
    if fid_input_date_1 == "":
        raise ValueError("fid_input_date_1 is required (e.g. '20250301')")
    
    if fid_input_date_2 == "":
        raise ValueError("fid_input_date_2 is required (e.g. '20250810')")
    
    if fid_period_div_code == "":
        raise ValueError("fid_period_div_code is required (e.g. 'D: 일봉, W: 주봉')")
    
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real:실전, demo:모의')")

    # tr_id 설정
    if env_dv == "real":
        tr_id = "FHKIF03020100"
    elif env_dv == "demo":
        tr_id = "FHKIF03020100"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")


    api_url = "/uapi/domestic-futureoption/v1/quotations/inquire-daily-fuopchartprice"



    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_DATE_2": fid_input_date_2,
        "FID_PERIOD_DIV_CODE": fid_period_div_code
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        # output1: object -> DataFrame (1행)
        output1_data = pd.DataFrame([res.getBody().output1])
        
        # output2: array -> DataFrame (여러행)
        output2_data = pd.DataFrame(res.getBody().output2)
        
        return output1_data, output2_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 총자산현황[v1_국내선물-014]
##############################################################################################

def inquire_deposit(
    cano: str,  # [필수] 종합계좌번호
    acnt_prdt_cd: str  # [필수] 계좌상품코드 (ex. 03)
) -> pd.DataFrame:
    """
    선물옵션 총자산현황 API 입니다.
    
    Args:
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 03)

    Returns:
        pd.DataFrame: 선물옵션 총자산현황 데이터
        
    Example:
        >>> df = inquire_deposit(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod)
        >>> print(df)
    """

    if cano == "":
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required")

    tr_id = "CTRP6550R"  # 선물옵션 총자산현황


    api_url = "/uapi/domestic-futureoption/v1/trading/inquire-deposit"



    params = {
        "CANO": cano,  # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd  # 계좌상품코드
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame([res.getBody().output])
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

##############################################################################################
# [국내선물옵션] 주문/계좌 > (야간)선물옵션 잔고현황 [국내선물-010]
##############################################################################################

def inquire_ngt_balance(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    mgna_dvsn: str,  # 증거금구분
    excc_stat_cd: str,  # 정산상태코드
    acnt_pwd: str = "",  # 계좌비밀번호
    FK200: str = "",  # 연속조회검색조건200
    NK200: str = "",  # 연속조회키200
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    (야간)선물옵션 잔고현황 API입니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. 계좌번호 체계(8-2)의 앞 8자리)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 계좌번호 체계(8-2)의 뒤 2자리)
        mgna_dvsn (str): [필수] 증거금구분 (ex. 01:개시, 02:유지)
        excc_stat_cd (str): [필수] 정산상태코드 (ex. 1:정산, 2:본정산)
        acnt_pwd (str): 계좌비밀번호
        FK200 (str): 연속조회검색조건200
        NK200 (str): 연속조회키200
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> df1, df2 = inquire_ngt_balance("12345678", "01", "01", "1")
        >>> print(df1, df2)
    """

    # 필수 파라미터 검증
    if cano == "":
        raise ValueError("cano is required (e.g. '계좌번호 체계(8-2)의 앞 8자리')")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '계좌번호 체계(8-2)의 뒤 2자리')")
    
    if mgna_dvsn == "":
        raise ValueError("mgna_dvsn is required (e.g. '01:개시, 02:유지')")
    
    if excc_stat_cd == "":
        raise ValueError("excc_stat_cd is required (e.g. '1:정산, 2:본정산')")

    # 재귀 깊이 제한 확인
    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        return (
            dataframe1 if dataframe1 is not None else pd.DataFrame(),
            dataframe2 if dataframe2 is not None else pd.DataFrame()
        )

    tr_id = "CTFN6118R"


    api_url = "/uapi/domestic-futureoption/v1/trading/inquire-ngt-balance"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "MGNA_DVSN": mgna_dvsn,
        "EXCC_STAT_CD": excc_stat_cd,
        "ACNT_PWD": acnt_pwd,
        "CTX_AREA_FK200": FK200,
        "CTX_AREA_NK200": NK200
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
        FK200 = res.getBody().ctx_area_fk200
        NK200 = res.getBody().ctx_area_nk200
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_ngt_balance(
                cano, acnt_prdt_cd, mgna_dvsn, excc_stat_cd, acnt_pwd,
                FK200, NK200, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return (dataframe1, dataframe2)
    else:
        res.printError(url=api_url)
        return (pd.DataFrame(), pd.DataFrame())

##############################################################################################
# [국내선물옵션] 주문/계좌 > (야간)선물옵션 주문체결 내역조회 [국내선물-009]
##############################################################################################

def inquire_ngt_ccnl(
    cano: str,                                           # 종합계좌번호
    acnt_prdt_cd: str,                                   # 계좌상품코드
    strt_ord_dt: str,                                    # 시작주문일자
    end_ord_dt: str,                                     # 종료주문일자
    sll_buy_dvsn_cd: str,                               # 매도매수구분코드
    ccld_nccs_dvsn: str,                                # 체결미체결구분
    sort_sqn: str = "",                                 # 정렬순서
    strt_odno: str = "",                                # 시작주문번호
    pdno: str = "",                                     # 상품번호
    mket_id_cd: str = "",                               # 시장ID코드
    fuop_dvsn_cd: str = "",                             # 선물옵션구분코드
    scrn_dvsn: str = "",                                # 화면구분
    FK200: str = "",                                    # 연속조회검색조건200
    NK200: str = "",                                    # 연속조회키200
    tr_cont: str = "",                                  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,          # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,          # 누적 데이터프레임2
    depth: int = 0,                                     # 내부 재귀깊이 (자동관리)
    max_depth: int = 10                                 # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    (야간)선물옵션 주문체결 내역조회 API입니다.
    
    Args:
        cano (str): [필수] 종합계좌번호 (ex. 계좌번호 체계(8-2)의 앞 8자리)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 계좌번호 체계(8-2)의 뒤 2자리)
        strt_ord_dt (str): [필수] 시작주문일자
        end_ord_dt (str): [필수] 종료주문일자 (ex. 조회하려는 마지막 일자 다음일자로 조회 (ex. 20221011 까지의 내역을 조회하고자 할 경우, 20221012로 종료주문일자 설정))
        sll_buy_dvsn_cd (str): [필수] 매도매수구분코드 (ex. 공란:default, 00:전체, 01:매도, 02:매수)
        ccld_nccs_dvsn (str): [필수] 체결미체결구분 (ex. 00:전체, 01:체결, 02:미체결)
        sort_sqn (str): 정렬순서 (ex. 공란:default(DS:정순, 그외:역순))
        strt_odno (str): 시작주문번호 (ex. 공란:default)
        pdno (str): 상품번호 (ex. 공란:default)
        mket_id_cd (str): 시장ID코드 (ex. 공란:default)
        fuop_dvsn_cd (str): 선물옵션구분코드 (ex. 공란:전체, 01:선물, 02:옵션)
        scrn_dvsn (str): 화면구분 (ex. 02(Default))
        FK200 (str): 연속조회검색조건200 (ex. 공란:최초 조회시, 이전 조회 Output CTX_AREA_FK200값:다음페이지 조회시(2번째부터))
        NK200 (str): 연속조회키200 (ex. 공란:최초 조회시, 이전 조회 Output CTX_AREA_NK200값:다음페이지 조회시(2번째부터))
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> df1, df2 = inquire_ngt_ccnl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, strt_ord_dt="20231201", end_ord_dt="20231214", sll_buy_dvsn_cd="00", ccld_nccs_dvsn="00")
        >>> print(df1)
        >>> print(df2)
    """

    # 필수 파라미터 검증
    if cano == "" or cano is None:
        raise ValueError("cano is required (e.g. '계좌번호 체계(8-2)의 앞 8자리')")
    
    if acnt_prdt_cd == "" or acnt_prdt_cd is None:
        raise ValueError("acnt_prdt_cd is required (e.g. '계좌번호 체계(8-2)의 뒤 2자리')")
    
    if strt_ord_dt == "" or strt_ord_dt is None:
        raise ValueError("strt_ord_dt is required")
    
    if end_ord_dt == "" or end_ord_dt is None:
        raise ValueError("end_ord_dt is required (e.g. '조회하려는 마지막 일자 다음일자로 조회 (ex. 20221011 까지의 내역을 조회하고자 할 경우, 20221012로 종료주문일자 설정)')")
    
    if sll_buy_dvsn_cd == "" or sll_buy_dvsn_cd is None:
        raise ValueError("sll_buy_dvsn_cd is required (e.g. '공란:default, 00:전체, 01:매도, 02:매수')")
    
    if ccld_nccs_dvsn == "" or ccld_nccs_dvsn is None:
        raise ValueError("ccld_nccs_dvsn is required (e.g. '00:전체, 01:체결, 02:미체결')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "STTN5201R"


    api_url = "/uapi/domestic-futureoption/v1/trading/inquire-ngt-ccnl"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "STRT_ORD_DT": strt_ord_dt,
        "END_ORD_DT": end_ord_dt,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "CCLD_NCCS_DVSN": ccld_nccs_dvsn,
        "SORT_SQN": sort_sqn,
        "STRT_ODNO": strt_odno,
        "PDNO": pdno,
        "MKET_ID_CD": mket_id_cd,
        "FUOP_DVSN_CD": fuop_dvsn_cd,
        "SCRN_DVSN": scrn_dvsn,
        "CTX_AREA_FK200": FK200,
        "CTX_AREA_NK200": NK200
    }
    
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)
    
    print(res.getBody())

    if res.isOK():
        # output1 (array) 처리
        current_data1 = pd.DataFrame(res.getBody().output1)
        
        # output2 (object) 처리
        current_data2 = pd.DataFrame([res.getBody().output2])
        
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1
            
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2
            
        tr_cont = res.getHeader().tr_cont
        FK200 = res.getBody().ctx_area_fk200
        NK200 = res.getBody().ctx_area_nk200
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_ngt_ccnl(
                cano, acnt_prdt_cd, strt_ord_dt, end_ord_dt, sll_buy_dvsn_cd, ccld_nccs_dvsn,
                sort_sqn, strt_odno, pdno, mket_id_cd, fuop_dvsn_cd, scrn_dvsn,
                FK200, NK200, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [국내선물옵션] 기본시세 > 선물옵션 시세[v1_국내선물-006]
##############################################################################################

def inquire_price(
    fid_cond_mrkt_div_code: str,  # [필수] FID 조건 시장 분류 코드 (ex. F: 지수선물, O: 지수옵션)
    fid_input_iscd: str,          # [필수] FID 입력 종목코드 (ex. 101W09)
    env_dv: str                   # [필수] 실전모의구분 (ex. real:실전, demo:모의)
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    선물옵션 시세 API입니다.

    ※ 종목코드 마스터파일 정제코드는 한국투자증권 Github 참고:  
      https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

    Args:
        fid_cond_mrkt_div_code (str): [필수] FID 조건 시장 분류 코드 (ex. F: 지수선물, O: 지수옵션)
        fid_input_iscd (str): [필수] FID 입력 종목코드 (ex. 101W09)
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: 선물옵션 시세 데이터 (output1, output2, output3)
        
    Example:
        >>> result1, result2, result3 = inquire_price(
        ...     fid_cond_mrkt_div_code="F",
        ...     fid_input_iscd="101W09",
        ...     env_dv="real"
        ... )
        >>> print(result1)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'F', 'O')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '101W09')")
    
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real', 'demo')")

    # tr_id 설정
    if env_dv == "real":
        tr_id = "FHMIF10000000"
    elif env_dv == "demo":
        tr_id = "FHMIF10000000"
    else:
        raise ValueError("env_dv can only be real or demo")


    api_url = "/uapi/domestic-futureoption/v1/quotations/inquire-price"



    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        # output1 처리
        output1 = pd.DataFrame(res.getBody().output1, index=[0])
        
        # output2 처리
        output2 = pd.DataFrame(res.getBody().output2, index=[0])
        
        # output3 처리
        output3 = pd.DataFrame(res.getBody().output3, index=[0])
        
        return output1, output2, output3
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [국내선물옵션] 주문/계좌 > (야간)선물옵션 주문가능 조회 [국내선물-011]
##############################################################################################

def inquire_psbl_ngt_order(
    cano: str,                 # 종합계좌번호
    acnt_prdt_cd: str,         # 계좌상품코드
    pdno: str,                 # 상품번호
    prdt_type_cd: str,         # 상품유형코드
    sll_buy_dvsn_cd: str,      # 매도매수구분코드
    unit_price: str,           # 주문가격1
    ord_dvsn_cd: str           # 주문구분코드
) -> pd.DataFrame:
    """
    (야간)선물옵션 주문가능 조회 API입니다.
    
    Args:
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드
        pdno (str): [필수] 상품번호
        prdt_type_cd (str): [필수] 상품유형코드 (ex. 301:선물옵션)
        sll_buy_dvsn_cd (str): [필수] 매도매수구분코드 (ex. 01:매도, 02:매수)
        unit_price (str): [필수] 주문가격1
        ord_dvsn_cd (str): [필수] 주문구분코드 (ex. 01:지정가, 02:시장가, 03:조건부, 04:최유리, 10:지정가(IOC), 11:지정가(FOK), 12:시장가(IOC), 13:시장가(FOK), 14:최유리(IOC), 15:최유리(FOK))

    Returns:
        pd.DataFrame: (야간)선물옵션 주문가능 데이터
        
    Example:
        >>> df = inquire_psbl_ngt_order(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, pdno="101W09", prdt_type_cd="301", sll_buy_dvsn_cd="02", unit_price="322", ord_dvsn_cd="01")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if cano == "" or cano is None:
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "" or acnt_prdt_cd is None:
        raise ValueError("acnt_prdt_cd is required")
    
    if pdno == "" or pdno is None:
        raise ValueError("pdno is required")
    
    if prdt_type_cd == "" or prdt_type_cd is None:
        raise ValueError("prdt_type_cd is required (e.g. '301')")
    
    if sll_buy_dvsn_cd == "" or sll_buy_dvsn_cd is None:
        raise ValueError("sll_buy_dvsn_cd is required (e.g. '01', '02')")
    
    if unit_price == "" or unit_price is None:
        raise ValueError("unit_price is required")
    
    if ord_dvsn_cd == "" or ord_dvsn_cd is None:
        raise ValueError("ord_dvsn_cd is required (e.g. '01', '02', '03', '04', '10', '11', '12', '13', '14', '15')")

    tr_id = "STTN5105R"


    api_url = "/uapi/domestic-futureoption/v1/trading/inquire-psbl-ngt-order"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "PRDT_TYPE_CD": prdt_type_cd,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "UNIT_PRICE": unit_price,
        "ORD_DVSN_CD": ord_dvsn_cd
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame([res.getBody().output])
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 주문가능[v1_국내선물-005]
##############################################################################################

def inquire_psbl_order(
    env_dv: str,         # [필수] 실전모의구분 (ex. real:실전, demo:모의)
    cano: str,           # [필수] 종합계좌번호
    acnt_prdt_cd: str,   # [필수] 계좌상품코드 (ex. 03)
    pdno: str,           # [필수] 상품번호 (ex. 선물 6자리, 옵션 9자리)
    sll_buy_dvsn_cd: str, # [필수] 매도매수구분코드 (ex. 01:매도,02:매수)
    unit_price: str,     # [필수] 주문가격1
    ord_dvsn_cd: str     # [필수] 주문구분코드
) -> pd.DataFrame:
    """
    선물옵션 주문가능 API입니다. 주문가능 내역과 수량을 확인하실 수 있습니다.
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 03)
        pdno (str): [필수] 상품번호 (ex. 선물 6자리, 옵션 9자리)
        sll_buy_dvsn_cd (str): [필수] 매도매수구분코드 (ex. 01:매도,02:매수)
        unit_price (str): [필수] 주문가격1
        ord_dvsn_cd (str): [필수] 주문구분코드

    Returns:
        pd.DataFrame: 선물옵션 주문가능 데이터
        
    Example:
        >>> df = inquire_psbl_order(env_dv="real", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod,
        ...                                    pdno="101W09", sll_buy_dvsn_cd="02", unit_price="1", ord_dvsn_cd="01")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")
    
    if cano == "":
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '03')")
    
    if pdno == "":
        raise ValueError("pdno is required (e.g. '101W09')")
    
    if sll_buy_dvsn_cd == "":
        raise ValueError("sll_buy_dvsn_cd is required (e.g. '01' or '02')")
    
    if unit_price == "":
        raise ValueError("unit_price is required")
    
    if ord_dvsn_cd == "":
        raise ValueError("ord_dvsn_cd is required")

    # tr_id 설정
    if env_dv == "real":
        tr_id = "TTTO5105R"
    elif env_dv == "demo":
        tr_id = "VTTO5105R"
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")


    api_url = "/uapi/domestic-futureoption/v1/trading/inquire-psbl-order"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "UNIT_PRICE": unit_price,
        "ORD_DVSN_CD": ord_dvsn_cd
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame([res.getBody().output])
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

##############################################################################################
# [국내선물옵션] 기본시세 > 선물옵션 분봉조회[v1_국내선물-012]
##############################################################################################

def inquire_time_fuopchartprice(
    fid_cond_mrkt_div_code: str,     # FID 조건 시장 분류 코드 (F: 지수선물, O: 지수옵션)
    fid_input_iscd: str,             # FID 입력 종목코드 (101T12)
    fid_hour_cls_code: str,          # FID 시간 구분 코드 (30: 30초, 60: 1분)
    fid_pw_data_incu_yn: str,        # FID 과거 데이터 포함 여부 (Y:과거, N: 당일)
    fid_fake_tick_incu_yn: str,      # FID 허봉 포함 여부 (N)
    fid_input_date_1: str,           # FID 입력 날짜1 (20230901)
    fid_input_hour_1: str            # FID 입력 시간1 (100000)
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    선물옵션 분봉조회 API입니다.
    실전계좌의 경우, 한 번의 호출에 최대 102건까지 확인 가능하며,  
    FID_INPUT_DATE_1(입력날짜), FID_INPUT_HOUR_1(입력시간)을 이용하여 다음 조회 가능합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): [필수] FID 조건 시장 분류 코드 (ex. F: 지수선물, O: 지수옵션)
        fid_input_iscd (str): [필수] FID 입력 종목코드 (ex. 101T12)
        fid_hour_cls_code (str): [필수] FID 시간 구분 코드 (ex. 30: 30초, 60: 1분)
        fid_pw_data_incu_yn (str): [필수] FID 과거 데이터 포함 여부 (ex. Y:과거, N: 당일)
        fid_fake_tick_incu_yn (str): [필수] FID 허봉 포함 여부 (ex. N)
        fid_input_date_1 (str): [필수] FID 입력 날짜1 (ex. 20230901)
        fid_input_hour_1 (str): [필수] FID 입력 시간1 (ex. 100000)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 선물옵션 분봉 데이터 (output1, output2)
        
    Example:
        >>> df1, df2 = inquire_time_fuopchartprice("F", "101T12", "60", "Y", "N", "20230901", "100000")
        >>> print(df1)
        >>> print(df2)
    """

    # 필수 파라미터 검증
    if fid_cond_mrkt_div_code == "":
        raise ValueError("fid_cond_mrkt_div_code is required (e.g. 'F: 지수선물, O: 지수옵션')")
    
    if fid_input_iscd == "":
        raise ValueError("fid_input_iscd is required (e.g. '101T12')")
    
    if fid_hour_cls_code == "":
        raise ValueError("fid_hour_cls_code is required (e.g. '30: 30초, 60: 1분')")
    
    if fid_pw_data_incu_yn == "":
        raise ValueError("fid_pw_data_incu_yn is required (e.g. 'Y:과거, N: 당일')")
    
    if fid_fake_tick_incu_yn == "":
        raise ValueError("fid_fake_tick_incu_yn is required (e.g. 'N')")
    
    if fid_input_date_1 == "":
        raise ValueError("fid_input_date_1 is required (e.g. '20230901')")
    
    if fid_input_hour_1 == "":
        raise ValueError("fid_input_hour_1 is required (e.g. '100000')")

    tr_id = "FHKIF03020200"  # 선물옵션 분봉조회


    api_url = "/uapi/domestic-futureoption/v1/quotations/inquire-time-fuopchartprice"



    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_HOUR_CLS_CODE": fid_hour_cls_code,
        "FID_PW_DATA_INCU_YN": fid_pw_data_incu_yn,
        "FID_FAKE_TICK_INCU_YN": fid_fake_tick_incu_yn,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_HOUR_1": fid_input_hour_1
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        # output1: object array -> DataFrame
        output1_data = pd.DataFrame(res.getBody().output1, index=[0])
        
        # output2: array -> DataFrame
        output2_data = pd.DataFrame(res.getBody().output2)
            
        logging.info("Data fetch complete.")
        return output1_data, output2_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [국내선물옵션] 주문/계좌 > (야간)선물옵션 증거금 상세 [국내선물-024]
##############################################################################################

def ngt_margin_detail(
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        mgna_dvsn_cd: str  # 증거금 구분코드
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    (야간)선물옵션 증거금상세 API입니다.
    한국투자 HTS(eFriend Force) > [2537] 야간선물옵션 증거금상세 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 03)
        mgna_dvsn_cd (str): [필수] 증거금 구분코드 (ex. 01:위탁, 02:유지)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: (output1, output2, output3) 데이터프레임
        
    Example:
        >>> df1, df2, df3 = ngt_margin_detail(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, mgna_dvsn_cd="01")
        >>> print(df1)
    """

    if cano == "":
        raise ValueError("cano is required")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '03')")

    if mgna_dvsn_cd == "":
        raise ValueError("mgna_dvsn_cd is required (e.g. '01:위탁, 02:유지')")

    tr_id = "CTFN7107R"  # (야간)선물옵션 증거금 상세


    api_url = "/uapi/domestic-futureoption/v1/trading/ngt-margin-detail"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "MGNA_DVSN_CD": mgna_dvsn_cd
    }

    res = ka._url_fetch(api_url, tr_id, "", params)

    if res.isOK():
        output1_data = pd.DataFrame(res.getBody().output1)
        output2_data = pd.DataFrame(res.getBody().output2)
        output3_data = pd.DataFrame([res.getBody().output3])

        return output1_data, output2_data, output3_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 주문[v1_국내선물-001]
##############################################################################################

def order(
    env_dv: str,  # 실전모의구분
    ord_dv: str,  # 매도매수구분  
    ord_prcs_dvsn_cd: str,  # 주문처리구분코드
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    sll_buy_dvsn_cd: str,  # 매도매수구분코드
    shtn_pdno: str,  # 단축상품번호
    ord_qty: str,  # 주문수량
    unit_price: str,  # 주문가격1
    nmpr_type_cd: str,  # 호가유형코드
    krx_nmpr_cndt_cd: str,  # 한국거래소호가조건코드
    ord_dvsn_cd: str,  # 주문구분코드
    ctac_tlno: str = "",  # 연락전화번호
    fuop_item_dvsn_cd: str = ""  # 선물옵션종목구분코드
) -> pd.DataFrame:
    """
    [국내선물옵션] 주문/계좌 > 선물옵션 주문[v1_국내선물-001]
    선물옵션 주문 API입니다.
    * 선물옵션 운영시간 외 API 호출 시 애러가 발생하오니 운영시간을 확인해주세요.

    ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)

    ※ 종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
    https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        ord_dv (str): [필수] 매도매수구분 (ex. day:주간, night:야간)
        ord_prcs_dvsn_cd (str): [필수] 주문처리구분코드 (ex. 02:주문전송)
        cano (str): [필수] 종합계좌번호 (ex. 계좌번호 체계(8-2)의 앞 8자리)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 계좌번호 체계(8-2)의 뒤 2자리)
        sll_buy_dvsn_cd (str): [필수] 매도매수구분코드 (ex. 01:매도, 02:매수)
        shtn_pdno (str): [필수] 단축상품번호 (ex. 종목번호, 선물 6자리 (예: 101W09), 옵션 9자리 (예: 201S03370))
        ord_qty (str): [필수] 주문수량
        unit_price (str): [필수] 주문가격1 (ex. 시장가나 최유리 지정가인 경우 0으로 입력)
        nmpr_type_cd (str): [필수] 호가유형코드 (ex. 01:지정가, 02:시장가, 03:조건부, 04:최유리)
        krx_nmpr_cndt_cd (str): [필수] 한국거래소호가조건코드 (ex. 0:없음, 3:IOC, 4:FOK)
        ord_dvsn_cd (str): [필수] 주문구분코드 (ex. 01:지정가, 02:시장가, 03:조건부, 04:최유리, 10:지정가(IOC), 11:지정가(FOK), 12:시장가(IOC), 13:시장가(FOK), 14:최유리(IOC), 15:최유리(FOK))
        ctac_tlno (str): 연락전화번호 (ex. 고객의 연락 가능한 전화번호)
        fuop_item_dvsn_cd (str): 선물옵션종목구분코드 (ex. 공란(Default))

    Returns:
        pd.DataFrame: 선물옵션 주문 결과 데이터
        
    Example:
        >>> df = order(env_dv="real", ord_dv="day", ord_prcs_dvsn_cd="02", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, sll_buy_dvsn_cd="02", shtn_pdno="101W09", ord_qty="1", unit_price="0", nmpr_type_cd="02", krx_nmpr_cndt_cd="0", ord_dvsn_cd="02")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real', 'demo')")
    
    if ord_dv == "":
        raise ValueError("ord_dv is required (e.g. 'day', 'night')")
        
    if ord_prcs_dvsn_cd == "":
        raise ValueError("ord_prcs_dvsn_cd is required (e.g. '02')")
        
    if cano == "":
        raise ValueError("cano is required (e.g. '계좌번호 체계(8-2)의 앞 8자리')")
        
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '계좌번호 체계(8-2)의 뒤 2자리')")
        
    if sll_buy_dvsn_cd == "":
        raise ValueError("sll_buy_dvsn_cd is required (e.g. '01', '02')")
        
    if shtn_pdno == "":
        raise ValueError("shtn_pdno is required (e.g. '101W09', '201S03370')")
        
    if ord_qty == "":
        raise ValueError("ord_qty is required")
        
    if unit_price == "":
        raise ValueError("unit_price is required (e.g. '0')")
        
    if nmpr_type_cd == "":
        raise ValueError("nmpr_type_cd is required (e.g. '01', '02', '03', '04')")
        
    if krx_nmpr_cndt_cd == "":
        raise ValueError("krx_nmpr_cndt_cd is required (e.g. '0', '3', '4')")
        
    if ord_dvsn_cd == "":
        raise ValueError("ord_dvsn_cd is required (e.g. '01', '02', '03', '04', '10', '11', '12', '13', '14', '15')")

    # tr_id 설정
    if env_dv == "real":
        if ord_dv == "day":
            tr_id = "TTTO1101U"
        elif ord_dv == "night":
            tr_id = "STTN1101U"
        else:
            raise ValueError("ord_dv can only be 'day' or 'night'")
    elif env_dv == "demo":
        if ord_dv == "day":
            tr_id = "VTTO1101U" 
        else:
            raise ValueError("ord_dv can only be 'day' for demo environment")
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")


    api_url = "/uapi/domestic-futureoption/v1/trading/order"



    params = {
        "ORD_PRCS_DVSN_CD": ord_prcs_dvsn_cd,
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "SHTN_PDNO": shtn_pdno,
        "ORD_QTY": ord_qty,
        "UNIT_PRICE": unit_price,
        "NMPR_TYPE_CD": nmpr_type_cd,
        "KRX_NMPR_CNDT_CD": krx_nmpr_cndt_cd,
        "ORD_DVSN_CD": ord_dvsn_cd,
        "CTAC_TLNO": ctac_tlno,
        "FUOP_ITEM_DVSN_CD": fuop_item_dvsn_cd
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params, postFlag=True)
    
    if res.isOK():
        return pd.DataFrame(res.getBody().output, index=[0])
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

##############################################################################################
# [국내선물옵션] 주문/계좌 > 선물옵션 정정취소주문[v1_국내선물-002]
##############################################################################################

def order_rvsecncl(
    env_dv: str,                    # [필수] 실전모의구분 (ex. real:실전, demo:모의)
    day_dv: str,                    # [필수] 주야간구분 (ex. day:주간, night:야간)
    ord_prcs_dvsn_cd: str,          # [필수] 주문처리구분코드 (ex. 02)
    cano: str,                      # [필수] 종합계좌번호
    acnt_prdt_cd: str,              # [필수] 계좌상품코드
    rvse_cncl_dvsn_cd: str,         # [필수] 정정취소구분코드 (ex. 01:정정, 02:취소)
    orgn_odno: str,                 # [필수] 원주문번호
    ord_qty: str,                   # [필수] 주문수량 (ex. 0:전량, 그 외는 수량)
    unit_price: str,                # [필수] 주문가격1 (ex 0:시장가/최유리, 그 외 가격)
    nmpr_type_cd: str,              # [필수] 호가유형코드 (ex. 01:지정가, 02:시장가, 03:조건부, 04:최유리)
    krx_nmpr_cndt_cd: str,          # [필수] 한국거래소호가조건코드 (ex. 0:취소/없음, 3:IOC, 4:FOK)
    rmn_qty_yn: str,                # [필수] 잔여수량여부 (ex. Y:전량, N:일부)
    ord_dvsn_cd: str,               # [필수] 주문구분코드
    fuop_item_dvsn_cd: str = ""     # 선물옵션종목구분코드
) -> pd.DataFrame:
    """
    선물옵션 주문 건에 대하여 정정 및 취소하는 API입니다. 단, 이미 체결된 건은 정정 및 취소가 불가합니다.

    ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        day_dv (str): [필수] 주야간구분 (ex. day:주간, night:야간)
        ord_prcs_dvsn_cd (str): [필수] 주문처리구분코드 (ex. 02)
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드
        rvse_cncl_dvsn_cd (str): [필수] 정정취소구분코드 (ex. 01:정정, 02:취소)
        orgn_odno (str): [필수] 원주문번호
        ord_qty (str): [필수] 주문수량 (ex. 0:전량, 그 외는 수량)
        unit_price (str): [필수] 주문가격1 (ex 0:시장가/최유리, 그 외 가격)
        nmpr_type_cd (str): [필수] 호가유형코드 (ex. 01:지정가, 02:시장가, 03:조건부, 04:최유리)
        krx_nmpr_cndt_cd (str): [필수] 한국거래소호가조건코드 (ex. 0:취소/없음, 3:IOC, 4:FOK)
        rmn_qty_yn (str): [필수] 잔여수량여부 (ex. Y:전량, N:일부)
        ord_dvsn_cd (str): [필수] 주문구분코드
        fuop_item_dvsn_cd (str): 선물옵션종목구분코드

    Returns:
        pd.DataFrame: 선물옵션 정정취소주문 결과 데이터
        
    Example:
        >>> df = order_rvsecncl(
        ...     env_dv="real", day_dv="day", ord_prcs_dvsn_cd="02",
        ...     cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, rvse_cncl_dvsn_cd="02",
        ...     orgn_odno="0000004018", ord_qty="0", unit_price="0",
        ...     nmpr_type_cd="02", krx_nmpr_cndt_cd="0", rmn_qty_yn="Y",
        ...     ord_dvsn_cd="01"
        ... )
        >>> print(df)
    """
    
    # tr_id 설정
    if env_dv == "real":
        if day_dv == "day":
            tr_id = "TTTO1103U"
        elif day_dv == "night":
            tr_id = "TTTN1103U"
        else:
            raise ValueError("day_dv can only be 'day' or 'night'")
    elif env_dv == "demo":
        if day_dv == "day":
            tr_id = "VTTO1103U"
        else:
            raise ValueError("day_dv can only be 'day' for demo environment")
    else:
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")


    api_url = "/uapi/domestic-futureoption/v1/trading/order-rvsecncl"



    params = {
        "ORD_PRCS_DVSN_CD": ord_prcs_dvsn_cd,
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "RVSE_CNCL_DVSN_CD": rvse_cncl_dvsn_cd,
        "ORGN_ODNO": orgn_odno,
        "ORD_QTY": ord_qty,
        "UNIT_PRICE": unit_price,
        "NMPR_TYPE_CD": nmpr_type_cd,
        "KRX_NMPR_CNDT_CD": krx_nmpr_cndt_cd,
        "RMN_QTY_YN": rmn_qty_yn,
        "ORD_DVSN_CD": ord_dvsn_cd,
        "FUOP_ITEM_DVSN_CD": fuop_item_dvsn_cd
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params, postFlag=True)
    
    if res.isOK():
        return pd.DataFrame(res.getBody().output)
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

