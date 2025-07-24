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
# [해외선물옵션] 기본시세 > 해외선물 체결추이(일간) [해외선물-018]
##############################################################################################

def daily_ccnl(
    srs_cd: str,  # 종목코드
    exch_cd: str,  # 거래소코드
    start_date_time: str,  # 조회시작일시
    close_date_time: str,  # 조회종료일시
    qry_tp: str,  # 조회구분
    qry_cnt: str,  # 요청개수
    qry_gap: str,  # 묶음개수
    index_key: str,  # 이전조회KEY
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외선물옵션] 기본시세 
    해외선물 체결추이(일간)[해외선물-018]
    해외선물 체결추이(일간) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        srs_cd (str): 종목코드 (예: 6AM24)
        exch_cd (str): 거래소코드 (예: CME)
        start_date_time (str): 조회시작일시 (공백)
        close_date_time (str): 조회종료일시 (예: 20240402)
        qry_tp (str): 조회구분 (Q: 최초조회시, P: 다음키(INDEX_KEY) 입력하여 조회시)
        qry_cnt (str): 요청개수 (예: 30, 최대 40)
        qry_gap (str): 묶음개수 (공백, 분만 사용)
        index_key (str): 이전조회KEY (공백)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외선물 체결추이(일간) 데이터
        
    Example:
        >>> df1, df2 = daily_ccnl(
        ...     srs_cd="6AM24",
        ...     exch_cd="CME",
        ...     start_date_time="",
        ...     close_date_time="20240402",
        ...     qry_tp="Q",
        ...     qry_cnt="30",
        ...     qry_gap="",
        ...     index_key=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not srs_cd:
        logger.error("srs_cd is required. (e.g. '6AM24')")
        raise ValueError("srs_cd is required. (e.g. '6AM24')")
    if not exch_cd:
        logger.error("exch_cd is required. (e.g. 'CME')")
        raise ValueError("exch_cd is required. (e.g. 'CME')")
    if not close_date_time:
        logger.error("close_date_time is required. (e.g. '20240402')")
        raise ValueError("close_date_time is required. (e.g. '20240402')")
    if not qry_tp:
        logger.error("qry_tp is required. (e.g. 'Q')")
        raise ValueError("qry_tp is required. (e.g. 'Q')")
    if not qry_cnt:
        logger.error("qry_cnt is required. (e.g. '30')")
        raise ValueError("qry_cnt is required. (e.g. '30')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    tr_id = "HHDFC55020100"


    api_url = "/uapi/overseas-futureoption/v1/quotations/daily-ccnl"



    params = {
        "SRS_CD": srs_cd,
        "EXCH_CD": exch_cd,
        "START_DATE_TIME": start_date_time,
        "CLOSE_DATE_TIME": close_date_time,
        "QRY_TP": qry_tp,
        "QRY_CNT": qry_cnt,
        "QRY_GAP": qry_gap,
        "INDEX_KEY": index_key,
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
            return daily_ccnl(
                srs_cd,
                exch_cd,
                start_date_time,
                close_date_time,
                qry_tp,
                qry_cnt,
                qry_gap,
                index_key,
                dataframe1,
                dataframe2,
                "N",
                depth + 1,
                max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물 호가 [해외선물-031]
##############################################################################################

def inquire_asking_price(
    srs_cd: str,  # 종목명
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외선물옵션] 기본시세 
    해외선물 호가[해외선물-031]
    해외선물 호가 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        srs_cd (str): 종목코드
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외선물 호가 데이터
        
    Example:
        >>> df1, df2 = inquire_asking_price(srs_cd="EXAMPLE_SRS_CD")
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not srs_cd:
        logger.error("srs_cd is required. (e.g. 'EXAMPLE_SRS_CD')")
        raise ValueError("srs_cd is required. (e.g. 'EXAMPLE_SRS_CD')")
    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    tr_id = "HHDFC86000000"


    api_url = "/uapi/overseas-futureoption/v1/quotations/inquire-asking-price"



    params = {
        "SRS_CD": srs_cd,
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
            return inquire_asking_price(
                srs_cd,
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
# [해외선물옵션] 주문/계좌 > 해외선물옵션 당일주문내역조회 [v1_해외선물-004]
##############################################################################################

def inquire_ccld(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ccld_nccs_dvsn: str,  # 체결미체결구분
    sll_buy_dvsn_cd: str,  # 매도매수구분코드
    fuop_dvsn: str,  # 선물옵션구분
    ctx_area_fk200: str,  # 연속조회검색조건200
    ctx_area_nk200: str,  # 연속조회키200
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 주문/계좌 
    해외선물옵션 당일주문내역조회[v1_해외선물-004]
    해외선물옵션 당일주문내역조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ccld_nccs_dvsn (str): 01:전체 / 02:체결 / 03:미체결
        sll_buy_dvsn_cd (str): %%:전체 / 01:매도 / 02:매수
        fuop_dvsn (str): 00:전체 / 01:선물 / 02:옵션
        ctx_area_fk200 (str): 연속조회검색조건200
        ctx_area_nk200 (str): 연속조회키200
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외선물옵션 당일주문내역조회 데이터
        
    Example:
        >>> df = inquire_ccld(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ccld_nccs_dvsn="01",
        ...     sll_buy_dvsn_cd="01",
        ...     fuop_dvsn="00",
        ...     ctx_area_fk200="",
        ...     ctx_area_nk200=""
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '80012345')")
        raise ValueError("cano is required. (e.g. '80012345')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '08')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '08')")
    if not ccld_nccs_dvsn:
        logger.error("ccld_nccs_dvsn is required. (e.g. '01')")
        raise ValueError("ccld_nccs_dvsn is required. (e.g. '01')")
    if not sll_buy_dvsn_cd:
        logger.error("sll_buy_dvsn_cd is required. (e.g. '01')")
        raise ValueError("sll_buy_dvsn_cd is required. (e.g. '01')")
    if not fuop_dvsn:
        logger.error("fuop_dvsn is required. (e.g. '00')")
        raise ValueError("fuop_dvsn is required. (e.g. '00')")
    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    tr_id = "OTFM3116R"


    api_url = "/uapi/overseas-futureoption/v1/trading/inquire-ccld"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "CCLD_NCCS_DVSN": ccld_nccs_dvsn,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "FUOP_DVSN": fuop_dvsn,
        "CTX_AREA_FK200": ctx_area_fk200,
        "CTX_AREA_NK200": ctx_area_nk200,
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
        
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_ccld(
                cano,
                acnt_prdt_cd,
                ccld_nccs_dvsn,
                sll_buy_dvsn_cd,
                fuop_dvsn,
                ctx_area_fk200,
                ctx_area_nk200,
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
# [해외선물옵션] 주문/계좌 > 해외선물옵션 일별체결내역[해외선물-011]
##############################################################################################

def inquire_daily_ccld(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    strt_dt: str,  # 시작일자
    end_dt: str,  # 종료일자
    fuop_dvsn_cd: str,  # 선물옵션구분코드
    fm_pdgr_cd: str,  # FM상품군코드
    crcy_cd: str,  # 통화코드
    fm_item_ftng_yn: str,  # FM종목합산여부
    sll_buy_dvsn_cd: str,  # 매도매수구분코드
    ctx_area_fk200: str,  # 연속조회검색조건200
    ctx_area_nk200: str,  # 연속조회키200
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외선물옵션] 주문/계좌 
    해외선물옵션 일별 체결내역[해외선물-011]
    해외선물옵션 일별 체결내역 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        strt_dt (str): 시작일자(YYYYMMDD)
        end_dt (str): 종료일자(YYYYMMDD)
        fuop_dvsn_cd (str): 00:전체 / 01:선물 / 02:옵션
        fm_pdgr_cd (str): 공란(Default)
        crcy_cd (str): %%% : 전체 TUS: TOT_USD  / TKR: TOT_KRW KRW: 한국  / USD: 미국 EUR: EUR   / HKD: 홍콩 CNY: 중국  / JPY: 일본 VND: 베트남
        fm_item_ftng_yn (str): "N"(Default)
        sll_buy_dvsn_cd (str): %%: 전체 / 01 : 매도 / 02 : 매수
        ctx_area_fk200 (str): 연속조회검색조건200
        ctx_area_nk200 (str): 연속조회키200
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외선물옵션 일별 체결내역 데이터
        
    Example:
        >>> df1, df2 = inquire_daily_ccld(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     strt_dt="20221010",
        ...     end_dt="20221216",
        ...     fuop_dvsn_cd="00",
        ...     fm_pdgr_cd="",
        ...     crcy_cd="%%%",
        ...     fm_item_ftng_yn="N",
        ...     sll_buy_dvsn_cd="%%",
        ...     ctx_area_fk200="",
        ...     ctx_area_nk200=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '80012345')")
        raise ValueError("cano is required. (e.g. '80012345')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '08')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '08')")
    if not strt_dt:
        logger.error("strt_dt is required. (e.g. '20221010')")
        raise ValueError("strt_dt is required. (e.g. '20221010')")
    if not end_dt:
        logger.error("end_dt is required. (e.g. '20221216')")
        raise ValueError("end_dt is required. (e.g. '20221216')")
    if fuop_dvsn_cd not in ['00', '01', '02']:
        logger.error("fuop_dvsn_cd is required. (e.g. '00', '01', '02')")
        raise ValueError("fuop_dvsn_cd is required. (e.g. '00', '01', '02')")
    if not crcy_cd:
        logger.error("crcy_cd is required. (e.g. '%%%',KRW, USD, EUR..)")
        raise ValueError("crcy_cd is required. (e.g. '%%%',KRW, USD, EUR..)")
    if not fm_item_ftng_yn:
        logger.error("fm_item_ftng_yn is required. (e.g. 'N')")
        raise ValueError("fm_item_ftng_yn is required. (e.g. 'N')")
    if not sll_buy_dvsn_cd:
        logger.error("sll_buy_dvsn_cd is required. (e.g. '%%')")
        raise ValueError("sll_buy_dvsn_cd is required. (e.g. '%%')")
    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    tr_id = "OTFM3122R"


    api_url = "/uapi/overseas-futureoption/v1/trading/inquire-daily-ccld"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "STRT_DT": strt_dt,
        "END_DT": end_dt,
        "FUOP_DVSN_CD": fuop_dvsn_cd,
        "FM_PDGR_CD": fm_pdgr_cd,
        "CRCY_CD": crcy_cd,
        "FM_ITEM_FTNG_YN": fm_item_ftng_yn,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "CTX_AREA_FK200": ctx_area_fk200,
        "CTX_AREA_NK200": ctx_area_nk200,
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # output 처리
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
        # output1 처리
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
        tr_cont, ctx_area_fk200, ctx_area_nk200 = res.getHeader().tr_cont, res.getBody().ctx_area_fk200, res.getBody().ctx_area_fk200
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_daily_ccld(
                cano,
                acnt_prdt_cd,
                strt_dt,
                end_dt,
                fuop_dvsn_cd,
                fm_pdgr_cd,
                crcy_cd,
                fm_item_ftng_yn,
                sll_buy_dvsn_cd,
                ctx_area_fk200,
                ctx_area_nk200,
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
# [해외선물옵션] 주문/계좌 > 해외선물옵션 일별 주문내역 [해외선물-013]
##############################################################################################

def inquire_daily_order(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    strt_dt: str,  # 시작일자
    end_dt: str,  # 종료일자
    fm_pdgr_cd: str,  # FM상품군코드
    ccld_nccs_dvsn: str,  # 체결미체결구분
    sll_buy_dvsn_cd: str,  # 매도매수구분코드
    fuop_dvsn: str,  # 선물옵션구분
    ctx_area_fk200: str,  # 연속조회검색조건200
    ctx_area_nk200: str,  # 연속조회키200
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 주문/계좌 
    해외선물옵션 일별 주문내역[해외선물-013]
    해외선물옵션 일별 주문내역 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        strt_dt (str): 시작일자 (YYYYMMDD)
        end_dt (str): 종료일자 (YYYYMMDD)
        fm_pdgr_cd (str): FM상품군코드
        ccld_nccs_dvsn (str): 체결미체결구분 (01:전체 / 02:체결 / 03:미체결)
        sll_buy_dvsn_cd (str): 매도매수구분코드 (%%전체 / 01:매도 / 02:매수)
        fuop_dvsn (str): 선물옵션구분 (00:전체 / 01:선물 / 02:옵션)
        ctx_area_fk200 (str): 연속조회검색조건200
        ctx_area_nk200 (str): 연속조회키200
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외선물옵션 일별 주문내역 데이터
        
    Example:
        >>> df = inquire_daily_order(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     strt_dt="20220101",
        ...     end_dt="20221214",
        ...     fm_pdgr_cd="",
        ...     ccld_nccs_dvsn="01",
        ...     sll_buy_dvsn_cd="%%",
        ...     fuop_dvsn="00",
        ...     ctx_area_fk200="",
        ...     ctx_area_nk200=""
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '12345678')")
        raise ValueError("cano is required. (e.g. '12345678')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '08')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '08')")
    if not strt_dt:
        logger.error("strt_dt is required. (e.g. '20220101')")
        raise ValueError("strt_dt is required. (e.g. '20220101')")
    if not end_dt:
        logger.error("end_dt is required. (e.g. '20221214')")
        raise ValueError("end_dt is required. (e.g. '20221214')")
    if not ccld_nccs_dvsn:
        logger.error("ccld_nccs_dvsn is required. (e.g. '01')")
        raise ValueError("ccld_nccs_dvsn is required. (e.g. '01')")
    if not sll_buy_dvsn_cd:
        logger.error("sll_buy_dvsn_cd is required. (e.g. '%%')")
        raise ValueError("sll_buy_dvsn_cd is required. (e.g. '%%')")
    if not fuop_dvsn:
        logger.error("fuop_dvsn is required. (e.g. '00')")
        raise ValueError("fuop_dvsn is required. (e.g. '00')")
    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    tr_id = "OTFM3120R"


    api_url = "/uapi/overseas-futureoption/v1/trading/inquire-daily-order"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "STRT_DT": strt_dt,
        "END_DT": end_dt,
        "FM_PDGR_CD": fm_pdgr_cd,
        "CCLD_NCCS_DVSN": ccld_nccs_dvsn,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "FUOP_DVSN": fuop_dvsn,
        "CTX_AREA_FK200": ctx_area_fk200,
        "CTX_AREA_NK200": ctx_area_nk200,
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
        
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_daily_order(
                cano,
                acnt_prdt_cd,
                strt_dt,
                end_dt,
                fm_pdgr_cd,
                ccld_nccs_dvsn,
                sll_buy_dvsn_cd,
                fuop_dvsn,
                ctx_area_fk200,
                ctx_area_nk200,
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
# [해외선물옵션] 주문/계좌 > 해외선물옵션 예수금현황 [해외선물-012]
##############################################################################################

def inquire_deposit(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    crcy_cd: str,  # 통화코드
    inqr_dt: str,  # 조회일자
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 주문/계좌 
    해외선물옵션 예수금현황[해외선물-012]
    해외선물옵션 예수금현황 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        crcy_cd (str): TUS: TOT_USD  / TKR: TOT_KRW KRW: 한국  / USD: 미국 EUR: EUR   / HKD: 홍콩 CNY: 중국  / JPY: 일본 VND: 베트남
        inqr_dt (str): 조회일자 (YYYYMMDD 형식)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외선물옵션 예수금현황 데이터
        
    Example:
        >>> df = inquire_deposit(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     crcy_cd="KRW",
        ...     inqr_dt="20221214"
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '80012345')")
        raise ValueError("cano is required. (e.g. '80012345')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '08')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '08')")
    if not crcy_cd:
        logger.error("crcy_cd is required. (e.g. 'KRW')")
        raise ValueError("crcy_cd is required. (e.g. 'KRW')")
    if not inqr_dt:
        logger.error("inqr_dt is required. (e.g. '20221214')")
        raise ValueError("inqr_dt is required. (e.g. '20221214')")
    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    tr_id = "OTFM1411R"


    api_url = "/uapi/overseas-futureoption/v1/trading/inquire-deposit"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "CRCY_CD": crcy_cd,
        "INQR_DT": inqr_dt,
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
        
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_deposit(
                cano,
                acnt_prdt_cd,
                crcy_cd,
                inqr_dt,
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
# [해외선물옵션] 주문/계좌 > 해외선물옵션 기간계좌손익 일별 [해외선물-010]
##############################################################################################

def inquire_period_ccld(
    inqr_term_from_dt: str,  # 조회기간FROM일자
    inqr_term_to_dt: str,  # 조회기간TO일자
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    crcy_cd: str,  # 통화코드
    whol_trsl_yn: str,  # 전체환산여부
    fuop_dvsn: str,  # 선물옵션구분
    ctx_area_fk200: str,  # 연속조회검색조건200
    ctx_area_nk200: str,  # 연속조회키200
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외선물옵션] 주문/계좌 
    해외선물옵션 기간계좌손익 일별[해외선물-010]
    해외선물옵션 기간계좌손익 일별 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        inqr_term_from_dt (str): 조회기간FROM일자
        inqr_term_to_dt (str): 조회기간TO일자
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        crcy_cd (str): '%%% : 전체 TUS: TOT_USD  / TKR: TOT_KRW KRW: 한국  / USD: 미국 EUR: EUR   / HKD: 홍콩 CNY: 중국  / JPY: 일본'
        whol_trsl_yn (str): 전체환산여부
        fuop_dvsn (str): 00:전체 / 01:선물 / 02:옵션
        ctx_area_fk200 (str): 연속조회검색조건200
        ctx_area_nk200 (str): 연속조회키200
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외선물옵션 기간계좌손익 일별 데이터
        
    Example:
        >>> df1, df2 = inquire_period_ccld(
        ...     inqr_term_from_dt="20250601",
        ...     inqr_term_to_dt="20250630",
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     crcy_cd="%%%",
        ...     whol_trsl_yn="N",
        ...     fuop_dvsn="00",
        ...     ctx_area_fk200="",
        ...     ctx_area_nk200=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not inqr_term_from_dt:
        logger.error("inqr_term_from_dt is required. (e.g. '20250601')")
        raise ValueError("inqr_term_from_dt is required. (e.g. '20250601')")
    if not inqr_term_to_dt:
        logger.error("inqr_term_to_dt is required. (e.g. '20250630')")
        raise ValueError("inqr_term_to_dt is required. (e.g. '20250630')")
    if not cano:
        logger.error("cano is required. (e.g. '80012345')")
        raise ValueError("cano is required. (e.g. '80012345')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '08')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '08')")
    if not crcy_cd:
        logger.error("crcy_cd is required. (e.g. '%%%')")
        raise ValueError("crcy_cd is required. (e.g. '%%%')")
    if not whol_trsl_yn:
        logger.error("whol_trsl_yn is required. (e.g. 'N')")
        raise ValueError("whol_trsl_yn is required. (e.g. 'N')")
    if not fuop_dvsn:
        logger.error("fuop_dvsn is required. (e.g. '00')")
        raise ValueError("fuop_dvsn is required. (e.g. '00')")
    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    tr_id = "OTFM3118R"


    api_url = "/uapi/overseas-futureoption/v1/trading/inquire-period-ccld"



    params = {
        "INQR_TERM_FROM_DT": inqr_term_from_dt,
        "INQR_TERM_TO_DT": inqr_term_to_dt,
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "CRCY_CD": crcy_cd,
        "WHOL_TRSL_YN": whol_trsl_yn,
        "FUOP_DVSN": fuop_dvsn,
        "CTX_AREA_FK200": ctx_area_fk200,
        "CTX_AREA_NK200": ctx_area_nk200,
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
            return inquire_period_ccld(
                inqr_term_from_dt,
                inqr_term_to_dt,
                cano,
                acnt_prdt_cd,
                crcy_cd,
                whol_trsl_yn,
                fuop_dvsn,
                ctx_area_fk200,
                ctx_area_nk200,
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
# [해외선물옵션] 주문/계좌 > 해외선물옵션 기간계좌거래내역 [해외선물-014]
##############################################################################################

def inquire_period_trans(
    inqr_term_from_dt: str,  # 조회기간FROM일자
    inqr_term_to_dt: str,  # 조회기간TO일자
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    acnt_tr_type_cd: str,  # 계좌거래유형코드
    crcy_cd: str,  # 통화코드
    ctx_area_fk100: str,  # 연속조회검색조건100
    ctx_area_nk100: str,  # 연속조회키100
    pwd_chk_yn: str,  # 비밀번호체크여부
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 주문/계좌 
    해외선물옵션 기간계좌거래내역[해외선물-014]
    해외선물옵션 기간계좌거래내역 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        inqr_term_from_dt (str): 조회기간FROM일자 (예: '20220101')
        inqr_term_to_dt (str): 조회기간TO일자 (예: '20221214')
        cano (str): 계좌번호 체계(8-2)의 앞 8자리 (예: '80012345')
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리 (예: '08')
        acnt_tr_type_cd (str): 계좌거래유형코드 (1: 전체, 2:입출금 , 3: 결제)
        crcy_cd (str): 통화코드 ('%%%': 전체, 'TUS': TOT_USD, 'TKR': TOT_KRW, 'KRW': 한국, 'USD': 미국, 'EUR': EUR, 'HKD': 홍콩, 'CNY': 중국, 'JPY': 일본, 'VND': 베트남)
        ctx_area_fk100 (str): 연속조회검색조건100
        ctx_area_nk100 (str): 연속조회키100
        pwd_chk_yn (str): 비밀번호체크여부
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외선물옵션 기간계좌거래내역 데이터
        
    Example:
        >>> df = inquire_period_trans(
        ...     inqr_term_from_dt="20220101",
        ...     inqr_term_to_dt="20221214",
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     acnt_tr_type_cd="%%",
        ...     crcy_cd="%%%",
        ...     ctx_area_fk100="",
        ...     ctx_area_nk100="",
        ...     pwd_chk_yn=""
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not inqr_term_from_dt:
        logger.error("inqr_term_from_dt is required. (e.g. '20220101')")
        raise ValueError("inqr_term_from_dt is required. (e.g. '20220101')")
    if not inqr_term_to_dt:
        logger.error("inqr_term_to_dt is required. (e.g. '20221214')")
        raise ValueError("inqr_term_to_dt is required. (e.g. '20221214')")
    if not cano:
        logger.error("cano is required. (e.g. '80012345')")
        raise ValueError("cano is required. (e.g. '80012345')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '08')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '08')")
    if not acnt_tr_type_cd:
        logger.error("acnt_tr_type_cd is required. (e.g. '%%')")
        raise ValueError("acnt_tr_type_cd is required. (e.g. '%%')")
    if not crcy_cd:
        logger.error("crcy_cd is required. (e.g. '%%%')")
        raise ValueError("crcy_cd is required. (e.g. '%%%')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    tr_id = "OTFM3114R"


    api_url = "/uapi/overseas-futureoption/v1/trading/inquire-period-trans"



    params = {
        "INQR_TERM_FROM_DT": inqr_term_from_dt,
        "INQR_TERM_TO_DT": inqr_term_to_dt,
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "ACNT_TR_TYPE_CD": acnt_tr_type_cd,
        "CRCY_CD": crcy_cd,
        "CTX_AREA_FK100": ctx_area_fk100,
        "CTX_AREA_NK100": ctx_area_nk100,
        "PWD_CHK_YN": pwd_chk_yn,
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
        
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_period_trans(
                inqr_term_from_dt,
                inqr_term_to_dt,
                cano,
                acnt_prdt_cd,
                acnt_tr_type_cd,
                crcy_cd,
                ctx_area_fk100,
                ctx_area_nk100,
                pwd_chk_yn,
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
# [해외선물옵션] 기본시세 > 해외선물종목현재가 [v1_해외선물-009]
##############################################################################################

def inquire_price(
    srs_cd: str,  # 종목코드
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 기본시세 
    해외선물종목현재가[v1_해외선물-009]
    해외선물종목현재가 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        srs_cd (str): 종목코드 (예: CNHU24)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외선물종목현재가 데이터
        
    Example:
        >>> df = inquire_price(srs_cd="CNHU24")
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not srs_cd:
        logger.error("srs_cd is required. (e.g. 'CNHU24')")
        raise ValueError("srs_cd is required. (e.g. 'CNHU24')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    tr_id = "HHDFC55010000"


    api_url = "/uapi/overseas-futureoption/v1/quotations/inquire-price"



    params = {
        "SRS_CD": srs_cd,
    }

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
            return inquire_price(
                srs_cd,
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
# [해외선물옵션] 주문/계좌 > 해외선물옵션 주문가능조회 [v1_해외선물-006]
##############################################################################################

def inquire_psamount(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ovrs_futr_fx_pdno: str,  # 해외선물FX상품번호
    sll_buy_dvsn_cd: str,  # 매도매수구분코드
    fm_ord_pric: str,  # FM주문가격
    ecis_rsvn_ord_yn: str,  # 행사예약주문여부
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 주문/계좌 
    해외선물옵션 주문가능조회[v1_해외선물-006]
    해외선물옵션 주문가능조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ovrs_futr_fx_pdno (str): 해외선물FX상품번호
        sll_buy_dvsn_cd (str): 01 : 매도 / 02 : 매수
        fm_ord_pric (str): FM주문가격
        ecis_rsvn_ord_yn (str): 행사예약주문여부
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외선물옵션 주문가능조회 데이터
        
    Example:
        >>> df = inquire_psamount(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ovrs_futr_fx_pdno="6AU22",
        ...     sll_buy_dvsn_cd="02",
        ...     fm_ord_pric="",
        ...     ecis_rsvn_ord_yn=""
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '80012345')")
        raise ValueError("cano is required. (e.g. '80012345')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '08')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '08')")
    if not ovrs_futr_fx_pdno:
        logger.error("ovrs_futr_fx_pdno is required. (e.g. '6AU22')")
        raise ValueError("ovrs_futr_fx_pdno is required. (e.g. '6AU22')")
    if sll_buy_dvsn_cd not in ["01", "02"]:
        logger.error("sll_buy_dvsn_cd is required. (e.g. '01' or '02')")
        raise ValueError("sll_buy_dvsn_cd is required. (e.g. '01' or '02')")

    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "OTFM3304R"


    api_url = "/uapi/overseas-futureoption/v1/trading/inquire-psamount"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "OVRS_FUTR_FX_PDNO": ovrs_futr_fx_pdno,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "FM_ORD_PRIC": fm_ord_pric,
        "ECIS_RSVN_ORD_YN": ecis_rsvn_ord_yn,
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
        
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_psamount(
                cano,
                acnt_prdt_cd,
                ovrs_futr_fx_pdno,
                sll_buy_dvsn_cd,
                fm_ord_pric,
                ecis_rsvn_ord_yn,
                dataframe, "N", depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()

##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물 분봉조회[해외선물-016]
##############################################################################################

def inquire_time_futurechartprice(
    srs_cd: str,  # 종목코드
    exch_cd: str,  # 거래소코드
    start_date_time: str,  # 조회시작일시
    close_date_time: str,  # 조회종료일시
    qry_tp: str,  # 조회구분
    qry_cnt: str,  # 요청개수
    qry_gap: str,  # 묶음개수
    index_key: str,  # 이전조회KEY
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외선물옵션] 기본시세 
    해외선물 분봉조회[해외선물-016]
    해외선물 분봉조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        srs_cd (str): ex) CNHU24 ※ 종목코드 "포럼 > FAQ > 종목정보 다운로드(해외) - 해외지수선물" 참고
        exch_cd (str): CME
        start_date_time (str): 공백
        close_date_time (str): ex) 20230823
        qry_tp (str): Q : 최초조회시 , P : 다음키(INDEX_KEY) 입력하여 조회시
        qry_cnt (str): 120 (조회갯수)
        qry_gap (str): 5 (분간격)
        index_key (str): 다음조회(QRY_TP를 P로 입력) 시, 이전 호출의 "output1 > index_key" 기입하여 조회
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외선물 분봉조회 데이터
        
    Example:
        >>> df1, df2 = inquire_time_futurechartprice(
        ...     srs_cd="BONU25",
        ...     exch_cd="EUREX",
        ...     start_date_time="20250101",
        ...     close_date_time="20250702",
        ...     qry_tp="Q",
        ...     qry_cnt="120",
        ...     qry_gap="1",
        ...     index_key=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not srs_cd:
        logger.error("srs_cd is required. (e.g. 'BONU25')")
        raise ValueError("srs_cd is required. (e.g. 'BONU25')")
    if not exch_cd:
        logger.error("exch_cd is required. (e.g. 'EUREX')")
        raise ValueError("exch_cd is required. (e.g. 'EUREX')")
    if not close_date_time:
        logger.error("close_date_time is required. (e.g. '20250702')")
        raise ValueError("close_date_time is required. (e.g. '20250702')")
    if not qry_cnt:
        logger.error("qry_cnt is required. (e.g. '120')")
        raise ValueError("qry_cnt is required. (e.g. '120')")
    if not qry_gap:
        logger.error("qry_gap is required. (e.g. '1', '5', '10', '15', '30', '60')")
        raise ValueError("qry_gap is required. (e.g. '1', '5', '10', '15', '30', '60')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    tr_id = "HHDFC55020400"


    api_url = "/uapi/overseas-futureoption/v1/quotations/inquire-time-futurechartprice"



    params = {
        "SRS_CD": srs_cd,
        "EXCH_CD": exch_cd,
        "START_DATE_TIME": start_date_time,
        "CLOSE_DATE_TIME": close_date_time,
        "QRY_TP": qry_tp,
        "QRY_CNT": qry_cnt,
        "QRY_GAP": qry_gap,
        "INDEX_KEY": index_key,
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
        index_key = res.getBody().output2["index_key"]
        qry_tp = "P"

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_time_futurechartprice(
                srs_cd,
                exch_cd,
                start_date_time,
                close_date_time,
                qry_tp,
                qry_cnt,
                qry_gap,
                index_key,
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
# [해외선물옵션] 기본시세 > 해외옵션 분봉조회 [해외선물-040]
##############################################################################################

def inquire_time_optchartprice(
    srs_cd: str,  # 종목코드
    exch_cd: str,  # 거래소코드
    qry_cnt: str,  # 요청개수
    start_date_time: str = "",  # 조회시작일시
    close_date_time: str = "",  # 조회종료일시
    qry_gap: str = "",  # 묶음개수
    qry_tp: str = "",  # 조회구분
    index_key: str = "",  # 이전조회KEY
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    해외옵션 분봉조회 API입니다. 
    한 번의 호출에 120건까지 확인 가능하며, QRY_TP, INDEX_KEY 를 이용하여 다음조회 가능합니다.

    ※ 다음조회 방법
    (처음조회) "QRY_TP":"Q", "QRY_CNT":"120", "INDEX_KEY":""
    (다음조회) "QRY_TP":"P", "QRY_CNT":"120", "INDEX_KEY":"20240902         5"  ◀ 이전 호출의 "output1 > index_key" 기입

    (중요) 해외옵션시세 출력값을 해석하실 때 focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)에 있는 sCalcDesz(계산 소수점) 값을 활용하셔야 정확한 값을 받아오실 수 있습니다.

    - focode.mst(해외지수옵션 종목마스터파일), (해외주식옵션 종목마스터파일) 다운로드 방법
    1) focode.mst(해외지수옵션 종목마스터파일)
        : 포럼 > FAQ > 종목정보 다운로드(해외) - 해외지수옵션 클릭하여 다운로드 후
        Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외옵션정보.h)를 참고하여 해석
    2) fostkcode.mst(해외주식옵션 종목마스터파일)
        : 포럼 > FAQ > 종목정보 다운로드(해외) - 해외주식옵션 클릭하여 다운로드 후
        Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외주식옵션정보.h)를 참고하여 해석

    - 소수점 계산 시, focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)의 sCalcDesz(계산 소수점) 값 참고
    EX) focode.mst 파일의 sCalcDesz(계산 소수점) 값
        품목코드 OES 계산소수점 -2 → 시세 7525 수신 시 75.25 로 해석
        품목코드 O6E 계산소수점 -4 → 시세 54.0 수신 시 0.0054 로 해석
    
    Args:
        srs_cd (str): [필수] 종목코드 (ex. OESU24 C5500)
        exch_cd (str): [필수] 거래소코드 (ex. CME)
        qry_cnt (str): [필수] 요청개수 (ex. 20)
        start_date_time (str): 조회시작일시
        close_date_time (str): 조회종료일시
        qry_gap (str): 묶음개수
        qry_tp (str): 조회구분
        index_key (str): 이전조회KEY
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 DataFrame, output2 DataFrame)
        
    Example:
        >>> df1, df2 = inquire_time_optchartprice("OESU24 C5500", "CME", "20")
        >>> print(df1)
        >>> print(df2)
    """

    if srs_cd == "":
        raise ValueError("srs_cd is required (e.g. 'OESU24 C5500')")
    
    if exch_cd == "":
        raise ValueError("exch_cd is required (e.g. 'CME')")
    
    if qry_cnt == "":
        raise ValueError("qry_cnt is required (e.g. '20')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None and dataframe2 is None:
            return pd.DataFrame(), pd.DataFrame()
        else:
            return (dataframe1 if dataframe1 is not None else pd.DataFrame(), 
                   dataframe2 if dataframe2 is not None else pd.DataFrame())

    tr_id = "HHDFO55020100"  # 해외옵션 분봉조회


    api_url = "/uapi/overseas-futureoption/v1/quotations/inquire-time-optchartprice"



    params = {
        "SRS_CD": srs_cd,  # 종목코드
        "EXCH_CD": exch_cd,  # 거래소코드
        "QRY_CNT": qry_cnt,  # 요청개수
        "START_DATE_TIME": start_date_time,  # 조회시작일시
        "CLOSE_DATE_TIME": close_date_time,  # 조회종료일시
        "QRY_GAP": qry_gap,  # 묶음개수
        "QRY_TP": qry_tp,  # 조회구분
        "INDEX_KEY": index_key  # 이전조회KEY
    }
    
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 처리 (object)
        current_data1 = pd.DataFrame([res.getBody().output1])
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1
            
        # output2 처리 (array)
        current_data2 = pd.DataFrame(res.getBody().output2)  
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2
            
        tr_cont = res.getHeader().tr_cont
        index_key = res.getBody().output1["index_key"]
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_time_optchartprice(
                srs_cd, exch_cd, qry_cnt, start_date_time, close_date_time, 
                qry_gap, qry_tp, index_key, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 미결제내역조회(잔고) [v1_해외선물-005]
##############################################################################################

def inquire_unpd(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    fuop_dvsn: str,  # 선물옵션구분
    ctx_area_fk100: str,  # 연속조회검색조건100
    ctx_area_nk100: str,  # 연속조회키100
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 주문/계좌 
    해외선물옵션 미결제내역조회(잔고)[v1_해외선물-005]
    해외선물옵션 미결제내역조회(잔고) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        fuop_dvsn (str): 00: 전체 / 01:선물 / 02: 옵션
        ctx_area_fk100 (str): 연속조회검색조건100
        ctx_area_nk100 (str): 연속조회키100
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외선물옵션 미결제내역조회(잔고) 데이터
        
    Example:
        >>> df = inquire_unpd(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     fuop_dvsn="00",
        ...     ctx_area_fk100="",
        ...     ctx_area_nk100=""
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '80012345')")
        raise ValueError("cano is required. (e.g. '80012345')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '08')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '08')")
    if fuop_dvsn not in ['00', '01', '02']:
        logger.error("fuop_dvsn is required. (e.g. '00')")
        raise ValueError("fuop_dvsn is required. (e.g. '00')")
    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    tr_id = "OTFM1412R"


    api_url = "/uapi/overseas-futureoption/v1/trading/inquire-unpd"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "FUOP_DVSN": fuop_dvsn,
        "CTX_AREA_FK100": ctx_area_fk100,
        "CTX_AREA_NK100": ctx_area_nk100,
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
        
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_unpd(
                cano,
                acnt_prdt_cd,
                fuop_dvsn,
                ctx_area_fk100,
                ctx_area_nk100,
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
# [해외선물옵션] 기본시세 > 해외선물 미결제추이 [해외선물-029]
##############################################################################################

def investor_unpd_trend(
    prod_iscd: str,  # 상품
    bsop_date: str,  # 일자
    upmu_gubun: str,  # 구분
    cts_key: str,  # CTS_KEY
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외선물옵션] 기본시세 
    해외선물 미결제추이[해외선물-029]
    해외선물 미결제추이 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        prod_iscd (str): 금리 (GE, ZB, ZF,ZN,ZT), 금속(GC, PA, PL,SI, HG), 농산물(CC, CT,KC, OJ, SB, ZC,ZL, ZM, ZO, ZR, ZS, ZW), 에너지(CL, HO, NG, WBS), 지수(ES, NQ, TF, YM, VX), 축산물(GF, HE, LE), 통화(6A, 6B, 6C, 6E, 6J, 6N, 6S, DX)
        bsop_date (str): 기준일(ex)20240513)
        upmu_gubun (str): 0(수량), 1(증감)
        cts_key (str): 공백
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외선물 미결제추이 데이터
        
    Example:
        >>> df1, df2 = investor_unpd_trend(
        ...     prod_iscd="ES",
        ...     bsop_date="20240624",
        ...     upmu_gubun="0",
        ...     cts_key=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not prod_iscd:
        logger.error("prod_iscd is required. (e.g. 'ES')")
        raise ValueError("prod_iscd is required. (e.g. 'ES')")
    if not bsop_date:
        logger.error("bsop_date is required. (e.g. '20240624')")
        raise ValueError("bsop_date is required. (e.g. '20240624')")
    if not upmu_gubun:
        logger.error("upmu_gubun is required. (e.g. '0')")
        raise ValueError("upmu_gubun is required. (e.g. '0')")
    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    tr_id = "HHDDB95030000"


    api_url = "/uapi/overseas-futureoption/v1/quotations/investor-unpd-trend"



    params = {
        "PROD_ISCD": prod_iscd,
        "BSOP_DATE": bsop_date,
        "UPMU_GUBUN": upmu_gubun,
        "CTS_KEY": cts_key,
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
            return investor_unpd_trend(
                prod_iscd,
                bsop_date,
                upmu_gubun,
                cts_key,
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
# [해외선물옵션] 주문/계좌 > 해외선물옵션 증거금상세 [해외선물-032]
##############################################################################################

def margin_detail(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    crcy_cd: str,  # 통화코드
    inqr_dt: str,  # 조회일자
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 주문/계좌 
    해외선물옵션 증거금상세[해외선물-032]
    해외선물옵션 증거금상세 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 종합계좌번호 (8자리)
        acnt_prdt_cd (str): 계좌상품코드 (2자리)
        crcy_cd (str): 통화코드 ('TKR', 'TUS', 'USD', 'HKD', 'CNY', 'JPY', 'VND')
        inqr_dt (str): 조회일자 (8자리, YYYYMMDD 형식)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외선물옵션 증거금상세 데이터
        
    Example:
        >>> df = margin_detail(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     crcy_cd="USD",
        ...     inqr_dt="20230701"
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '12345678')")
        raise ValueError("cano is required. (e.g. '12345678')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")
    if not crcy_cd:
        logger.error("crcy_cd is required. (e.g. 'USD')")
        raise ValueError("crcy_cd is required. (e.g. 'USD')")
    if not inqr_dt:
        logger.error("inqr_dt is required. (e.g. '20230701')")
        raise ValueError("inqr_dt is required. (e.g. '20230701')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    tr_id = "OTFM3115R"


    api_url = "/uapi/overseas-futureoption/v1/trading/margin-detail"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "CRCY_CD": crcy_cd,
        "INQR_DT": inqr_dt,
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
        
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return margin_detail(
                cano,
                acnt_prdt_cd,
                crcy_cd,
                inqr_dt,
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
# [해외선물옵션] 기본시세 > 해외선물옵션 장운영시간 [해외선물-030]
##############################################################################################

def market_time(
    fm_pdgr_cd: str,  # FM상품군코드
    fm_clas_cd: str,  # FM클래스코드
    fm_excg_cd: str,  # FM거래소코드
    opt_yn: str,  # 옵션여부
    ctx_area_nk200: str,  # 연속조회키200
    ctx_area_fk200: str,  # 연속조회검색조건200
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 기본시세 
    해외선물옵션 장운영시간[해외선물-030]
    해외선물옵션 장운영시간 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fm_pdgr_cd (str): FM상품군코드
        fm_clas_cd (str): FM클래스코드
        fm_excg_cd (str): FM거래소코드
        opt_yn (str): 옵션여부
        ctx_area_nk200 (str): 연속조회키200
        ctx_area_fk200 (str): 연속조회검색조건200
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외선물옵션 장운영시간 데이터
        
    Example:
        >>> df = market_time(
        ...     fm_pdgr_cd="001",
        ...     fm_clas_cd="003",
        ...     fm_excg_cd="CME",
        ...     opt_yn="N",
        ...     ctx_area_nk200="",
        ...     ctx_area_fk200=""
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not fm_excg_cd:
        logger.error("fm_excg_cd is required. (e.g. 'CME')")
        raise ValueError("fm_excg_cd is required. (e.g. 'CME')")
    if not opt_yn:
        logger.error("opt_yn is required. (e.g. 'N')")
        raise ValueError("opt_yn is required. (e.g. 'N')")
    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    tr_id = "OTFM2229R"


    api_url = "/uapi/overseas-futureoption/v1/quotations/market-time"



    params = {
        "FM_PDGR_CD": fm_pdgr_cd,
        "FM_CLAS_CD": fm_clas_cd,
        "FM_EXCG_CD": fm_excg_cd,
        "OPT_YN": opt_yn,
        "CTX_AREA_NK200": ctx_area_nk200,
        "CTX_AREA_FK200": ctx_area_fk200,
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
            
        tr_cont, ctx_area_nk200, ctx_area_fk200 = res.getHeader().tr_cont, res.getBody().ctx_area_nk200, res.getBody().ctx_area_fk200
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return market_time(
                fm_pdgr_cd,
                fm_clas_cd,
                fm_excg_cd,
                opt_yn,
                ctx_area_nk200,
                ctx_area_fk200,
                "N",
                dataframe,
                depth + 1,
                max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()

##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물 체결추이(월간)[해외선물-020]
##############################################################################################

def monthly_ccnl(
    srs_cd: str,  # 종목코드
    exch_cd: str,  # 거래소코드
    start_date_time: str,  # 조회시작일시
    close_date_time: str,  # 조회종료일시
    qry_tp: str,  # 조회구분
    qry_cnt: str,  # 요청개수
    qry_gap: str,  # 묶음개수
    index_key: str,  # 이전조회KEY
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외선물옵션] 기본시세 
    해외선물 체결추이(월간)[해외선물-020]
    해외선물 체결추이(월간) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        srs_cd (str): 종목코드 (예: '6AM24')
        exch_cd (str): 거래소코드 (예: 'CME')
        start_date_time (str): 조회시작일시 (공백 허용)
        close_date_time (str): 조회종료일시 (예: '20240402')
        qry_tp (str): 조회구분 ('Q': 최초조회, 'P': 다음키 입력하여 조회)
        qry_cnt (str): 요청개수 (예: '30', 최대 '40')
        qry_gap (str): 묶음개수 (공백 허용)
        index_key (str): 이전조회KEY (공백 허용)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외선물 체결추이(월간) 데이터
        
    Example:
        >>> df1, df2 = monthly_ccnl(
        ...     srs_cd="6AM24",
        ...     exch_cd="CME",
        ...     start_date_time="",
        ...     close_date_time="20240402",
        ...     qry_tp="Q",
        ...     qry_cnt="30",
        ...     qry_gap="",
        ...     index_key=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not srs_cd:
        logger.error("srs_cd is required. (e.g. '6AM24')")
        raise ValueError("srs_cd is required. (e.g. '6AM24')")
    if not exch_cd:
        logger.error("exch_cd is required. (e.g. 'CME')")
        raise ValueError("exch_cd is required. (e.g. 'CME')")
    if not close_date_time:
        logger.error("close_date_time is required. (e.g. '20240402')")
        raise ValueError("close_date_time is required. (e.g. '20240402')")
    if not qry_tp:
        logger.error("qry_tp is required. ('Q' or 'P')")
        raise ValueError("qry_tp is required. ('Q' or 'P')")
    if not qry_cnt:
        logger.error("qry_cnt is required. (e.g. '30')")
        raise ValueError("qry_cnt is required. (e.g. '30')")
    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    tr_id = "HHDFC55020300"


    api_url = "/uapi/overseas-futureoption/v1/quotations/monthly-ccnl"



    params = {
        "SRS_CD": srs_cd,
        "EXCH_CD": exch_cd,
        "START_DATE_TIME": start_date_time,
        "CLOSE_DATE_TIME": close_date_time,
        "QRY_TP": qry_tp,
        "QRY_CNT": qry_cnt,
        "QRY_GAP": qry_gap,
        "INDEX_KEY": index_key,
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
            return monthly_ccnl(
                srs_cd,
                exch_cd,
                start_date_time,
                close_date_time,
                qry_tp,
                qry_cnt,
                qry_gap,
                index_key,
                dataframe1,
                dataframe2,
                "N",
                depth + 1,
                max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외선물옵션] 기본시세 > 해외옵션 호가 [해외선물-033]
##############################################################################################

def opt_asking_price(
    srs_cd: str,  # 종목명
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외선물옵션] 기본시세 
    해외옵션 호가[해외선물-033]
    해외옵션 호가 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        srs_cd (str): 종목명 (예: 'OTXM24 C22000')
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외옵션 호가 데이터
        
    Example:
        >>> df1, df2 = opt_asking_price(srs_cd="OTXM24 C22000")
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not srs_cd:
        logger.error("srs_cd is required. (e.g. 'OTXM24 C22000')")
        raise ValueError("srs_cd is required. (e.g. 'OTXM24 C22000')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    tr_id = "HHDFO86000000"


    api_url = "/uapi/overseas-futureoption/v1/quotations/opt-asking-price"



    params = {
        "SRS_CD": srs_cd,
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
            return opt_asking_price(
                srs_cd,
                dataframe1, dataframe2, tr_cont, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외선물옵션] 기본시세 > 해외옵션 체결추이(일간) [해외선물-037]
##############################################################################################

def opt_daily_ccnl(
    srs_cd: str,                              # [필수] 종목코드 (ex. OESU24 C5500)  
    exch_cd: str,                             # [필수] 거래소코드 (ex. CME)
    qry_cnt: str,                             # [필수] 요청개수 (ex. 20)
    start_date_time: str = "",                # 조회시작일시
    close_date_time: str = "",                # 조회종료일시
    qry_gap: str = "",                        # 묶음개수
    qry_tp: str = "",                         # 조회구분
    index_key: str = "",                      # 이전조회KEY
    tr_cont: str = "",                        # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None, # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None, # 누적 데이터프레임 (output2)
    depth: int = 0,                           # 내부 재귀깊이 (자동관리)
    max_depth: int = 10                       # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    해외옵션 체결추이(일간) API입니다.
    최근 120건까지 데이터 확인이 가능합니다. ("QRY_CNT: 119 입력", START_DATE_TIME, CLOSE_DATE_TIME은 공란)

    ※ 호출 시 유의사항
    : START_DATE_TIME, CLOSE_DATE_TIME은 공란 입력, QRY_CNT는 확인 데이터 개수의 -1 개 입력
    ex) "START_DATE_TIME":"","CLOSE_DATE_TIME":"","QRY_CNT":"119" → 최근 120건 데이터 조회

    (중요) 해외옵션시세 출력값을 해석하실 때 focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)에 있는 sCalcDesz(계산 소수점) 값을 활용하셔야 정확한 값을 받아오실 수 있습니다.

    Args:
        srs_cd (str): [필수] 종목코드 (ex. OESU24 C5500)
        exch_cd (str): [필수] 거래소코드 (ex. CME)
        qry_cnt (str): [필수] 요청개수 (ex. 20)
        start_date_time (str): 조회시작일시
        close_date_time (str): 조회종료일시
        qry_gap (str): 묶음개수
        qry_tp (str): 조회구분
        index_key (str): 이전조회KEY
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> result1, result2 = opt_daily_ccnl("OESU24 C5500", "CME", "20")
        >>> print(result1)
        >>> print(result2)
    """

    # 필수 파라미터 검증
    if srs_cd == "" or srs_cd is None:
        raise ValueError("srs_cd is required (e.g. 'OESU24 C5500')")
    
    if exch_cd == "" or exch_cd is None:
        raise ValueError("exch_cd is required (e.g. 'CME')")
    
    if qry_cnt == "" or qry_cnt is None:
        raise ValueError("qry_cnt is required (e.g. '20')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "HHDFO55020100"


    api_url = "/uapi/overseas-futureoption/v1/quotations/opt-daily-ccnl"



    params = {
        "SRS_CD": srs_cd,
        "EXCH_CD": exch_cd,
        "QRY_CNT": qry_cnt,
        "START_DATE_TIME": start_date_time,
        "CLOSE_DATE_TIME": close_date_time,
        "QRY_GAP": qry_gap,
        "QRY_TP": qry_tp,
        "INDEX_KEY": index_key
    }
    
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 처리 (object)
        current_data1 = pd.DataFrame([res.getBody().output1])
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1
            
        # output2 처리 (array)
        current_data2 = pd.DataFrame(res.getBody().output2)
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2
            
        tr_cont = res.getHeader().tr_cont
        index_key = res.getBody().output1["index_key"]
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return opt_daily_ccnl(
                srs_cd, exch_cd, qry_cnt, start_date_time, close_date_time, 
                qry_gap, qry_tp, index_key, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외선물옵션] 기본시세 > 해외옵션종목상세 [해외선물-034]
##############################################################################################

def opt_detail(
    srs_cd: str  # [필수] 종목명
) -> pd.DataFrame:
    """
    해외옵션종목상세 API입니다.

    (주의) sstl_price 자리에 정산가 X 전일종가 O 가 수신되는 점 유의 부탁드립니다.

    (중요) 해외옵션시세 출력값을 해석하실 때 focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)에 있는 sCalcDesz(계산 소수점) 값을 활용하셔야 정확한 값을 받아오실 수 있습니다.

    - focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일) 다운로드 방법
    1) focode.mst(해외지수옵션 종목마스터파일)
        : 포럼 > FAQ > 종목정보 다운로드(해외) - 해외지수옵션 클릭하여 다운로드 후
        Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외옵션정보.h)를 참고하여 해석
    2) fostkcode.mst(해외주식옵션 종목마스터파일)
        : 포럼 > FAQ > 종목정보 다운로드(해외) - 해외주식옵션 클릭하여 다운로드 후
        Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외주식옵션정보.h)를 참고하여 해석

    - 소수점 계산 시, focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)의 sCalcDesz(계산 소수점) 값 참고
    EX) focode.mst 파일의 sCalcDesz(계산 소수점) 값
        품목코드 OES 계산소수점 -2 → 시세 7525 수신 시 75.25 로 해석
        품목코드 O6E 계산소수점 -4 → 시세 54.0 수신 시 0.0054 로 해석
    
    Args:
        srs_cd (str): [필수] 종목명
        
    Returns:
        pd.DataFrame: 해외옵션종목상세 데이터
        
    Raises:
        ValueError: 필수 파라미터 누락 시
        
    Examples:
        >>> df = opt_detail("C5500")
        >>> print(df)
    """

    if srs_cd == "":
        raise ValueError("srs_cd is required (e.g. 'C5500')")

    tr_id = "HHDFO55010100"


    api_url = "/uapi/overseas-futureoption/v1/quotations/opt-detail"



    params = {
        "SRS_CD": srs_cd
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output1, index=[0])
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

##############################################################################################
# [해외선물옵션] 기본시세 > 해외옵션 체결추이(월간) [해외선물-039]
##############################################################################################

def opt_monthly_ccnl(
    srs_cd: str,  # 종목코드
    exch_cd: str,  # 거래소코드
    qry_cnt: str,  # 요청개수
    start_date_time: str = "",  # 조회시작일시
    close_date_time: str = "",  # 조회종료일시
    qry_gap: str = "",  # 묶음개수
    qry_tp: str = "",  # 조회구분
    index_key: str = "",  # 이전조회KEY
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    해외옵션 체결추이(월간) API입니다. 
    최근 120건까지 데이터 확인이 가능합니다. (START_DATE_TIME, CLOSE_DATE_TIME은 공란 입력)

    (중요) 해외옵션시세 출력값을 해석하실 때 focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)에 있는 sCalcDesz(계산 소수점) 값을 활용하셔야 정확한 값을 받아오실 수 있습니다.

    - focode.mst(해외지수옵션 종목마스터파일), (해외주식옵션 종목마스터파일) 다운로드 방법
    1) focode.mst(해외지수옵션 종목마스터파일)
        : 포럼 > FAQ > 종목정보 다운로드(해외) - 해외지수옵션 클릭하여 다운로드 후
        Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외옵션정보.h)를 참고하여 해석
    2) fostkcode.mst(해외주식옵션 종목마스터파일)
        : 포럼 > FAQ > 종목정보 다운로드(해외) - 해외주식옵션 클릭하여 다운로드 후
        Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외주식옵션정보.h)를 참고하여 해석

    - 소수점 계산 시, focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)의 sCalcDesz(계산 소수점) 값 참고
    EX) focode.mst 파일의 sCalcDesz(계산 소수점) 값
        품목코드 OES 계산소수점 -2 → 시세 7525 수신 시 75.25 로 해석
        품목코드 O6E 계산소수점 -4 → 시세 54.0 수신 시 0.0054 로 해석
    
    Args:
        srs_cd (str): [필수] 종목코드 (ex. OESU24 C5500)
        exch_cd (str): [필수] 거래소코드 (ex. CME)
        qry_cnt (str): [필수] 요청개수 (ex. 20)
        start_date_time (str): 조회시작일시 (ex. "")
        close_date_time (str): 조회종료일시 (ex. "")
        qry_gap (str): 묶음개수 (ex. "")
        qry_tp (str): 조회구분 (ex. "")
        index_key (str): 이전조회KEY (ex. "")
        tr_cont (str): 연속거래여부 (ex. "")
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외옵션 체결추이(월간) 정보 (output1, output2)
        
    Example:
        >>> result1, result2 = opt_monthly_ccnl("OESU24 C5500", "CME", "20")
        >>> print(result1)
        >>> print(result2)
    """

    if srs_cd == "":
        raise ValueError("srs_cd is required (e.g. 'OESU24 C5500')")
    
    if exch_cd == "":
        raise ValueError("exch_cd is required (e.g. 'CME')")
    
    if qry_cnt == "":
        raise ValueError("qry_cnt is required (e.g. '20')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "HHDFO55020300"  # 해외옵션 체결추이(월간)


    api_url = "/uapi/overseas-futureoption/v1/quotations/opt-monthly-ccnl"



    params = {
        "SRS_CD": srs_cd,
        "EXCH_CD": exch_cd,
        "QRY_CNT": qry_cnt,
        "START_DATE_TIME": start_date_time,
        "CLOSE_DATE_TIME": close_date_time,
        "QRY_GAP": qry_gap,
        "QRY_TP": qry_tp,
        "INDEX_KEY": index_key
    }
    
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)
    
    if res.isOK():
        current_data1 = pd.DataFrame([res.getBody().output1])
        current_data2 = pd.DataFrame(res.getBody().output2)
            
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1
            
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2
            
        tr_cont = res.getHeader().tr_cont
        index_key = res.getBody().output1["index_key"]
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return opt_monthly_ccnl(
                srs_cd, exch_cd, qry_cnt, start_date_time, close_date_time, 
                qry_gap, qry_tp, index_key, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외선물옵션] 기본시세 > 해외옵션종목현재가 [해외선물-035]
##############################################################################################

def opt_price(
    srs_cd: str  # 종목코드
) -> pd.DataFrame:
    """
    해외옵션종목현재가 API입니다.

    (중요) 해외옵션시세 출력값을 해석하실 때 focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)에 있는 sCalcDesz(계산 소수점) 값을 활용하셔야 정확한 값을 받아오실 수 있습니다.

    - focode.mst(해외지수옵션 종목마스터파일), (해외주식옵션 종목마스터파일) 다운로드 방법
    1) focode.mst(해외지수옵션 종목마스터파일)
        : 포럼 > FAQ > 종목정보 다운로드(해외) - 해외지수옵션 클릭하여 다운로드 후
        Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외옵션정보.h)를 참고하여 해석
    2) fostkcode.mst(해외주식옵션 종목마스터파일)
        : 포럼 > FAQ > 종목정보 다운로드(해외) - 해외주식옵션 클릭하여 다운로드 후
        Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외주식옵션정보.h)를 참고하여 해석

    - 소수점 계산 시, focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)의 sCalcDesz(계산 소수점) 값 참고
    EX) focode.mst 파일의 sCalcDesz(계산 소수점) 값
        품목코드 OES 계산소수점 -2 → 시세 7525 수신 시 75.25 로 해석
        품목코드 O6E 계산소수점 -4 → 시세 54.0 수신 시 0.0054 로 해석
    
    Args:
        srs_cd (str): [필수] 종목코드
        
    Returns:
        pd.DataFrame: 해외옵션종목현재가 데이터
        
    Example:
        >>> df = opt_price(srs_cd="DXM24")
        >>> print(df)
    """

    if srs_cd == "":
        raise ValueError("srs_cd is required")
    
    tr_id = "HHDFO55010000"  # 해외옵션종목현재가


    api_url = "/uapi/overseas-futureoption/v1/quotations/opt-price"



    params = {
        "SRS_CD": srs_cd  # 종목코드
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output1, index=[0])
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

##############################################################################################
# [해외선물옵션] 기본시세 > 해외옵션 체결추이(틱) [해외선물-038]
##############################################################################################

def opt_tick_ccnl(
    srs_cd: str,                                    # [필수] 종목코드
    exch_cd: str,                                   # [필수] 거래소코드  
    qry_cnt: str,                                   # [필수] 요청개수
    start_date_time: str = "",                      # 조회시작일시
    close_date_time: str = "",                      # 조회종료일시
    qry_gap: str = "",                              # 묶음개수
    qry_tp: str = "",                               # 조회구분
    index_key: str = "",                            # 이전조회KEY
    tr_cont: str = "",                              # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,      # 누적 데이터프레임1 (output1)
    dataframe2: Optional[pd.DataFrame] = None,      # 누적 데이터프레임2 (output2)
    depth: int = 0,                                 # 내부 재귀깊이 (자동관리)
    max_depth: int = 10                             # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    해외옵션 체결추이(틱) API입니다. 
    한 번의 호출에 40건까지 확인 가능하며, QRY_TP, INDEX_KEY 를 이용하여 다음조회 가능합니다.

    ※ 다음조회 방법
    (처음조회) "QRY_TP":"Q", "QRY_CNT":"40", "INDEX_KEY":""
    (다음조회) "QRY_TP":"P", "QRY_CNT":"40", "INDEX_KEY":"20240906       221"  ◀ 이전 호출의 "output1 > index_key" 기입

    (중요) 해외옵션시세 출력값을 해석하실 때 focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)에 있는 sCalcDesz(계산 소수점) 값을 활용하셔야 정확한 값을 받아오실 수 있습니다.

    - focode.mst(해외지수옵션 종목마스터파일), (해외주식옵션 종목마스터파일) 다운로드 방법
    1) focode.mst(해외지수옵션 종목마스터파일)
        : 포럼 > FAQ > 종목정보 다운로드(해외) - 해외지수옵션 클릭하여 다운로드 후
        Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외옵션정보.h)를 참고하여 해석
    2) fostkcode.mst(해외주식옵션 종목마스터파일)
        : 포럼 > FAQ > 종목정보 다운로드(해외) - 해외주식옵션 클릭하여 다운로드 후
        Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외주식옵션정보.h)를 참고하여 해석

    - 소수점 계산 시, focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)의 sCalcDesz(계산 소수점) 값 참고
    EX) focode.mst 파일의 sCalcDesz(계산 소수점) 값
        품목코드 OES 계산소수점 -2 → 시세 7525 수신 시 75.25 로 해석
        품목코드 O6E 계산소수점 -4 → 시세 54.0 수신 시 0.0054 로 해석
    
    Args:
        srs_cd (str): [필수] 종목코드 (ex. OESU24 C5500)
        exch_cd (str): [필수] 거래소코드 (ex. CME)
        qry_cnt (str): [필수] 요청개수 (ex. 20)
        start_date_time (str): 조회시작일시
        close_date_time (str): 조회종료일시
        qry_gap (str): 묶음개수
        qry_tp (str): 조회구분
        index_key (str): 이전조회KEY
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2 (output2)
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Raises:
        ValueError: 필수 파라미터가 누락된 경우
        
    Example:
        >>> df1, df2 = opt_tick_ccnl("OESU24 C5500", "CME", "20")
        >>> print(df1)  # output1 데이터
        >>> print(df2)  # output2 데이터
    """

    # 필수 파라미터 검증
    if srs_cd == "":
        raise ValueError("srs_cd is required (e.g. 'OESU24 C5500')")
    
    if exch_cd == "":
        raise ValueError("exch_cd is required (e.g. 'CME')")
    
    if qry_cnt == "":
        raise ValueError("qry_cnt is required (e.g. '20')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "HHDFO55020200"


    api_url = "/uapi/overseas-futureoption/v1/quotations/opt-tick-ccnl"



    params = {
        "SRS_CD": srs_cd,
        "EXCH_CD": exch_cd,
        "QRY_CNT": qry_cnt,
        "START_DATE_TIME": start_date_time,
        "CLOSE_DATE_TIME": close_date_time,
        "QRY_GAP": qry_gap,
        "QRY_TP": qry_tp,
        "INDEX_KEY": index_key
    }
    
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 처리 (object 타입)
        current_data1 = pd.DataFrame([res.getBody().output1])
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1
            
        # output2 처리 (array 타입)
        current_data2 = pd.DataFrame(res.getBody().output2)
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2
            
        tr_cont = res.getHeader().tr_cont
        index_key = res.getBody().output1["index_key"]
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return opt_tick_ccnl(
                srs_cd, exch_cd, qry_cnt, start_date_time, close_date_time,
                qry_gap, qry_tp, index_key, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외선물옵션] 기본시세 > 해외옵션 체결추이(주간) [해외선물-036]
##############################################################################################

def opt_weekly_ccnl(
    srs_cd: str,  # 종목코드
    exch_cd: str,  # 거래소코드
    qry_cnt: str,  # 요청개수
    start_date_time: str = "",  # 조회시작일시
    close_date_time: str = "",  # 조회종료일시
    qry_gap: str = "",  # 묶음개수
    qry_tp: str = "",  # 조회구분
    index_key: str = "",  # 이전조회KEY
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # output1 누적 데이터프레임
    dataframe2: Optional[pd.DataFrame] = None,  # output2 누적 데이터프레임
    depth: int = 0,  # 내부 재귀 깊이 (자동 관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    해외옵션 체결추이(주간) API입니다.
    최근 120건까지 데이터 확인이 가능합니다. (START_DATE_TIME, CLOSE_DATE_TIME은 공란 입력)

    (중요) 해외옵션시세 출력값을 해석하실 때 focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)에 있는 sCalcDesz(계산 소수점) 값을 활용하셔야 정확한 값을 받아오실 수 있습니다.

    - focode.mst(해외지수옵션 종목마스터파일), (해외주식옵션 종목마스터파일) 다운로드 방법
    1) focode.mst(해외지수옵션 종목마스터파일)
        : 포럼 > FAQ > 종목정보 다운로드(해외) - 해외지수옵션 클릭하여 다운로드 후
        Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외옵션정보.h)를 참고하여 해석
    2) fostkcode.mst(해외주식옵션 종목마스터파일)
        : 포럼 > FAQ > 종목정보 다운로드(해외) - 해외주식옵션 클릭하여 다운로드 후
        Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외주식옵션정보.h)를 참고하여 해석

    - 소수점 계산 시, focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)의 sCalcDesz(계산 소수점) 값 참고
    EX) focode.mst 파일의 sCalcDesz(계산 소수점) 값
        품목코드 OES 계산소수점 -2 → 시세 7525 수신 시 75.25 로 해석
        품목코드 O6E 계산소수점 -4 → 시세 54.0 수신 시 0.0054 로 해석
    
    Args:
        srs_cd (str): [필수] 종목코드 (ex. OESU24 C5500)
        exch_cd (str): [필수] 거래소코드 (ex. CME)
        qry_cnt (str): [필수] 요청개수 (ex. 20)
        start_date_time (str): 조회시작일시
        close_date_time (str): 조회종료일시
        qry_gap (str): 묶음개수
        qry_tp (str): 조회구분
        index_key (str): 이전조회KEY
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): output1 누적 데이터프레임
        dataframe2 (Optional[pd.DataFrame]): output2 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: output1과 output2 데이터프레임 튜플
        
    Example:
        >>> df1, df2 = opt_weekly_ccnl(srs_cd="OESU24 C5500", exch_cd="CME", qry_cnt="20")
        >>> print(df1)
        >>> print(df2)
    """

    # 필수 파라미터 검증
    if srs_cd == "":
        raise ValueError("srs_cd is required (e.g. 'OESU24 C5500')")
    
    if exch_cd == "":
        raise ValueError("exch_cd is required (e.g. 'CME')")
    
    if qry_cnt == "":
        raise ValueError("qry_cnt is required (e.g. '20')")

    # 재귀 깊이 제한 확인
    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    tr_id = "HHDFO55020000"  # 해외옵션 체결추이(주간)


    api_url = "/uapi/overseas-futureoption/v1/quotations/opt-weekly-ccnl"



    params = {
        "SRS_CD": srs_cd,  # 종목코드
        "EXCH_CD": exch_cd,  # 거래소코드
        "QRY_CNT": qry_cnt,  # 요청개수
        "START_DATE_TIME": start_date_time,  # 조회시작일시
        "CLOSE_DATE_TIME": close_date_time,  # 조회종료일시
        "QRY_GAP": qry_gap,  # 묶음개수
        "QRY_TP": qry_tp,  # 조회구분
        "INDEX_KEY": index_key  # 이전조회KEY
    }
    
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 처리 (object 타입)
        current_data1 = pd.DataFrame([res.getBody().output1])
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1
            
        # output2 처리 (array 타입)
        current_data2 = pd.DataFrame(res.getBody().output2)
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2
            
        # 다음 페이지 정보 확인
        tr_cont = res.getHeader().tr_cont
        index_key = res.getBody().output1["index_key"]
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return opt_weekly_ccnl(
                srs_cd, exch_cd, qry_cnt, start_date_time, close_date_time, 
                qry_gap, qry_tp, index_key, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 주문[v1_해외선물-001]
##############################################################################################

def order(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ovrs_futr_fx_pdno: str,  # 해외선물FX상품번호
    sll_buy_dvsn_cd: str,  # 매도매수구분코드
    fm_lqd_ustl_ccld_dt: str,  # FM청산미결제체결일자
    fm_lqd_ustl_ccno: str,  # FM청산미결제체결번호
    pric_dvsn_cd: str,  # 가격구분코드
    fm_limit_ord_pric: str,  # FMLIMIT주문가격
    fm_stop_ord_pric: str,  # FMSTOP주문가격
    fm_ord_qty: str,  # FM주문수량
    fm_lqd_lmt_ord_pric: str,  # FM청산LIMIT주문가격
    fm_lqd_stop_ord_pric: str,  # FM청산STOP주문가격
    ccld_cndt_cd: str,  # 체결조건코드
    cplx_ord_dvsn_cd: str,  # 복합주문구분코드
    ecis_rsvn_ord_yn: str,  # 행사예약주문여부
    fm_hdge_ord_scrn_yn: str,  # FM_HEDGE주문화면여부

) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 주문/계좌 
    해외선물옵션 주문[v1_해외선물-001]
    해외선물옵션 주문 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ovrs_futr_fx_pdno (str): 해외선물FX상품번호
        sll_buy_dvsn_cd (str): 01 : 매도 02 : 매수
        fm_lqd_ustl_ccld_dt (str): 빈칸 (hedge청산만 이용)
        fm_lqd_ustl_ccno (str): 빈칸 (hedge청산만 이용)
        pric_dvsn_cd (str): 1.지정, 2. 시장, 3. STOP, 4 S/L
        fm_limit_ord_pric (str): 지정가인 경우 가격 입력 * 시장가, STOP주문인 경우, 빈칸("") 입력
        fm_stop_ord_pric (str): STOP 주문 가격 입력 * 시장가, 지정가인 경우, 빈칸("") 입력
        fm_ord_qty (str): FM주문수량
        fm_lqd_lmt_ord_pric (str): 빈칸 (hedge청산만 이용)
        fm_lqd_stop_ord_pric (str): 빈칸 (hedge청산만 이용)
        ccld_cndt_cd (str): 일반적으로 6 (EOD, 지정가)  GTD인 경우 5, 시장가인 경우만 2
        cplx_ord_dvsn_cd (str): 0 (hedge청산만 이용)
        ecis_rsvn_ord_yn (str): N
        fm_hdge_ord_scrn_yn (str): N
        
    Returns:
        Optional[pd.DataFrame]: 해외선물옵션 주문 데이터
        
    Example:
        >>> df = order(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ovrs_futr_fx_pdno="6BZ22",
        ...     sll_buy_dvsn_cd="02",
        ...     fm_lqd_ustl_ccld_dt="",
        ...     fm_lqd_ustl_ccno="",
        ...     pric_dvsn_cd="1",
        ...     fm_limit_ord_pric="1.17",
        ...     fm_stop_ord_pric="",
        ...     fm_ord_qty="1",
        ...     fm_lqd_lmt_ord_pric="",
        ...     fm_lqd_stop_ord_pric="",
        ...     ccld_cndt_cd="6",
        ...     cplx_ord_dvsn_cd="0",
        ...     ecis_rsvn_ord_yn="N",
        ...     fm_hdge_ord_scrn_yn="N"
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '81012345')")
        raise ValueError("cano is required. (e.g. '81012345')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '08')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '08')")
    if not ovrs_futr_fx_pdno:
        logger.error("ovrs_futr_fx_pdno is required. (e.g. '1AALN25 C10.0')")
        raise ValueError("ovrs_futr_fx_pdno is required. (e.g. '1AALN25 C10.0')")
    if not sll_buy_dvsn_cd:
        logger.error("sll_buy_dvsn_cd is required. (e.g. '02')")
        raise ValueError("sll_buy_dvsn_cd is required. (e.g. '02')")
    if not pric_dvsn_cd:
        logger.error("pric_dvsn_cd is required. (e.g. '1')")
        raise ValueError("pric_dvsn_cd is required. (e.g. '1')")
    if not fm_ord_qty:
        logger.error("fm_ord_qty is required. (e.g. '1')")
        raise ValueError("fm_ord_qty is required. (e.g. '1')")
    if not ccld_cndt_cd:
        logger.error("ccld_cndt_cd is required. (e.g. '6')")
        raise ValueError("ccld_cndt_cd is required. (e.g. '6')")

    tr_id = "OTFM3001U"


    api_url = "/uapi/overseas-futureoption/v1/trading/order"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "OVRS_FUTR_FX_PDNO": ovrs_futr_fx_pdno,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "FM_LQD_USTL_CCLD_DT": fm_lqd_ustl_ccld_dt,
        "FM_LQD_USTL_CCNO": fm_lqd_ustl_ccno,
        "PRIC_DVSN_CD": pric_dvsn_cd,
        "FM_LIMIT_ORD_PRIC": fm_limit_ord_pric,
        "FM_STOP_ORD_PRIC": fm_stop_ord_pric,
        "FM_ORD_QTY": fm_ord_qty,
        "FM_LQD_LMT_ORD_PRIC": fm_lqd_lmt_ord_pric,
        "FM_LQD_STOP_ORD_PRIC": fm_lqd_stop_ord_pric,
        "CCLD_CNDT_CD": ccld_cndt_cd,
        "CPLX_ORD_DVSN_CD": cplx_ord_dvsn_cd,
        "ECIS_RSVN_ORD_YN": ecis_rsvn_ord_yn,
        "FM_HDGE_ORD_SCRN_YN": fm_hdge_ord_scrn_yn,
    }

    res = ka._url_fetch(api_url=api_url,
                        ptr_id=tr_id,
                        tr_cont="",
                        params=params,
                        postFlag=True
            )

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            dataframe = pd.DataFrame(output_data)
        else:
            dataframe = pd.DataFrame()
                    
        logger.info("Data fetch complete.")
        return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()

##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 정정취소주문[v1_해외선물-002, 003]
##############################################################################################

def order_rvsecncl(
    cano: str,  # 종합계좌번호
    ord_dv: str, # 주문구분
    acnt_prdt_cd: str,  # 계좌상품코드
    orgn_ord_dt: str,  # 원주문일자
    orgn_odno: str,  # 원주문번호
    fm_limit_ord_pric: str,  # FMLIMIT주문가격
    fm_stop_ord_pric: str,  # FMSTOP주문가격
    fm_lqd_lmt_ord_pric: str,  # FM청산LIMIT주문가격
    fm_lqd_stop_ord_pric: str,  # FM청산STOP주문가격
    fm_hdge_ord_scrn_yn: str,  # FM_HEDGE주문화면여부
    fm_mkpr_cvsn_yn: str,  # FM시장가전환여부

) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 주문/계좌 
    해외선물옵션 정정취소주문[v1_해외선물-002, 003]
    해외선물옵션 정정취소주문 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        ord_dv (str): 주문구분 (0:정정, 1:취소)
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        orgn_ord_dt (str): 원 주문 시 출력되는 ORD_DT 값을 입력 (현지거래일)
        orgn_odno (str): 정정/취소시 주문번호(ODNO) 8자리를 문자열처럼 "0"을 포함해서 전송 (원 주문 시 출력된 ODNO 값 활용) (ex. ORGN_ODNO : 00360686)
        fm_limit_ord_pric (str): OTFM3002U(해외선물옵션주문정정)만 사용
        fm_stop_ord_pric (str): OTFM3002U(해외선물옵션주문정정)만 사용
        fm_lqd_lmt_ord_pric (str): OTFM3002U(해외선물옵션주문정정)만 사용
        fm_lqd_stop_ord_pric (str): OTFM3002U(해외선물옵션주문정정)만 사용
        fm_hdge_ord_scrn_yn (str): N
        fm_mkpr_cvsn_yn (str): OTFM3003U(해외선물옵션주문취소)만 사용  ※ FM_MKPR_CVSN_YN 항목에 'Y'로 설정하여 취소주문을 접수할 경우, 주문 취소확인이 들어오면 원장에서 시장가주문을 하나 또 내줌
        
    Returns:
        Optional[pd.DataFrame]: 해외선물옵션 정정취소주문 데이터
        
    Example:
        >>> df = order_rvsecncl(
        ...     cano=trenv.my_acct,
        ...     ord_dv="0",
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     orgn_ord_dt="20250630",
        ...     orgn_odno="00360686",
        ...     fm_limit_ord_pric="",
        ...     fm_stop_ord_pric="",
        ...     fm_lqd_lmt_ord_pric="",
        ...     fm_lqd_stop_ord_pric="",
        ...     fm_hdge_ord_scrn_yn="N",
        ...     fm_mkpr_cvsn_yn="N"
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '81012345')")
        raise ValueError("cano is required. (e.g. '81012345')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '08')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '08')")
    if not orgn_ord_dt:
        logger.error("orgn_ord_dt is required. (e.g. '20250630')")
        raise ValueError("orgn_ord_dt is required. (e.g. '20250630')")
    if not orgn_odno:
        logger.error("orgn_odno is required. (e.g. '00360686')")
        raise ValueError("orgn_odno is required. (e.g. '00360686')")

    if ord_dv == "0":
        tr_id = "OTFM3002U"
    elif ord_dv == "1":
        tr_id = "OTFM3003U"
    else:
        logger.error("ord_dv is required. (e.g. '0' or '1')")
        raise ValueError("ord_dv is required. (e.g. '0' or '1')")


    api_url = "/uapi/overseas-futureoption/v1/trading/order-rvsecncl"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "ORGN_ORD_DT": orgn_ord_dt,
        "ORGN_ODNO": orgn_odno,
        "FM_LIMIT_ORD_PRIC": fm_limit_ord_pric,
        "FM_STOP_ORD_PRIC": fm_stop_ord_pric,
        "FM_LQD_LMT_ORD_PRIC": fm_lqd_lmt_ord_pric,
        "FM_LQD_STOP_ORD_PRIC": fm_lqd_stop_ord_pric,
        "FM_HDGE_ORD_SCRN_YN": fm_hdge_ord_scrn_yn,
        "FM_MKPR_CVSN_YN": fm_mkpr_cvsn_yn,
    }

    logger.info("Calling API with parameters: %s", params)

    res = ka._url_fetch(api_url=api_url,
                         ptr_id=tr_id,
                         tr_cont="",
                         params=params,
                         postFlag=True)

    if res.isOK():
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            if not isinstance(output_data, list):
                output_data = [output_data]
            dataframe = pd.DataFrame(output_data)
        else:
            dataframe = pd.DataFrame()
                    
        logger.info("Data fetch complete.")
        return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()

##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물 상품기본정보[해외선물-023]
##############################################################################################

def search_contract_detail(
    qry_cnt: str,  # 요청개수
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10,
    **kwargs  # srs_cd_01, srs_cd_02, ... srs_cd_32 등을 받음
) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 기본시세 
    해외선물 상품기본정보[해외선물-023]
    해외선물 상품기본정보 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        qry_cnt (str): 입력한 코드 개수
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        **kwargs: srs_cd_01, srs_cd_02, ... srs_cd_32 품목종류 코드들
        
    Returns:
        Optional[pd.DataFrame]: 해외선물 상품기본정보 데이터
        
    Example:
        >>> df = search_contract_detail(
        ...     qry_cnt="3",
        ...     srs_cd_01="SRS001",
        ...     srs_cd_02="SRS002",
        ...     srs_cd_03="SRS003"
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not 1 <= int(qry_cnt) <= 32:
        logger.error("qry_cnt is required. (e.g. '1' ~ '32')")
        raise ValueError("qry_cnt is required. (e.g. '1' ~ '32')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    tr_id = "HHDFC55200000"

    # 기본 파라미터

    api_url = "/uapi/overseas-futureoption/v1/quotations/search-contract-detail"


    params = {
        "QRY_CNT": qry_cnt,
    }
    
    # SRS_CD_01 ~ SRS_CD_32 파라미터 동적 생성
    for i in range(1, 33):
        srs_key = f"srs_cd_{i:02d}"
        api_key = f"SRS_CD_{i:02d}"
        params[api_key] = kwargs.get(srs_key, "")

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
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
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return search_contract_detail(
                qry_cnt, "N", dataframe, depth + 1, max_depth, **kwargs
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()

##############################################################################################
# [해외선물옵션] 기본시세 > 해외옵션 상품기본정보 [해외선물-041]
##############################################################################################

def search_opt_detail(
    qry_cnt: str,  # [필수] 요청개수 (SRS_CD_N 개수)
    srs_cd_01: str,  # [필수] 종목코드1
    srs_cd_02: Optional[str] = "",  # 종목코드2
    srs_cd_03: Optional[str] = "",  # 종목코드3
    srs_cd_04: Optional[str] = "",  # 종목코드4
    srs_cd_05: Optional[str] = "",  # 종목코드5
    srs_cd_06: Optional[str] = "",  # 종목코드6
    srs_cd_07: Optional[str] = "",  # 종목코드7
    srs_cd_08: Optional[str] = "",  # 종목코드8
    srs_cd_09: Optional[str] = "",  # 종목코드9
    srs_cd_10: Optional[str] = "",  # 종목코드10
    srs_cd_11: Optional[str] = "",  # 종목코드11
    srs_cd_12: Optional[str] = "",  # 종목코드12
    srs_cd_13: Optional[str] = "",  # 종목코드13
    srs_cd_14: Optional[str] = "",  # 종목코드14
    srs_cd_15: Optional[str] = "",  # 종목코드15
    srs_cd_16: Optional[str] = "",  # 종목코드16
    srs_cd_17: Optional[str] = "",  # 종목코드17
    srs_cd_18: Optional[str] = "",  # 종목코드18
    srs_cd_19: Optional[str] = "",  # 종목코드19
    srs_cd_20: Optional[str] = "",  # 종목코드20
    srs_cd_21: Optional[str] = "",  # 종목코드21
    srs_cd_22: Optional[str] = "",  # 종목코드22
    srs_cd_23: Optional[str] = "",  # 종목코드23
    srs_cd_24: Optional[str] = "",  # 종목코드24
    srs_cd_25: Optional[str] = "",  # 종목코드25
    srs_cd_26: Optional[str] = "",  # 종목코드26
    srs_cd_27: Optional[str] = "",  # 종목코드27
    srs_cd_28: Optional[str] = "",  # 종목코드28
    srs_cd_29: Optional[str] = "",  # 종목코드29
    srs_cd_30: Optional[str] = ""   # 종목코드30
) -> pd.DataFrame:
    """
    해외옵션 상품기본정보 API입니다.

    (중요) 해외옵션시세 출력값을 해석하실 때 focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)에 있는 sCalcDesz(계산 소수점) 값을 활용하셔야 정확한 값을 받아오실 수 있습니다.

    - focode.mst(해외지수옵션 종목마스터파일), (해외주식옵션 종목마스터파일) 다운로드 방법
    1) focode.mst(해외지수옵션 종목마스터파일)
        : 포럼 > FAQ > 종목정보 다운로드(해외) - 해외지수옵션 클릭하여 다운로드 후
        Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외옵션정보.h)를 참고하여 해석
    2) fostkcode.mst(해외주식옵션 종목마스터파일)
        : 포럼 > FAQ > 종목정보 다운로드(해외) - 해외주식옵션 클릭하여 다운로드 후
        Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외주식옵션정보.h)를 참고하여 해석

    - 소수점 계산 시, focode.mst(해외지수옵션 종목마스터파일), fostkcode.mst(해외주식옵션 종목마스터파일)의 sCalcDesz(계산 소수점) 값 참고
    EX) focode.mst 파일의 sCalcDesz(계산 소수점) 값
        품목코드 OES 계산소수점 -2 → 시세 7525 수신 시 75.25 로 해석
        품목코드 O6E 계산소수점 -4 → 시세 54.0 수신 시 0.0054 로 해석
    
    Args:
        qry_cnt (str): [필수] 요청개수 (ex. SRS_CD_N 개수)
        srs_cd_01 (str): [필수] 종목코드1
        srs_cd_02 (Optional[str]): 종목코드2
        srs_cd_03 (Optional[str]): 종목코드3
        srs_cd_04 (Optional[str]): 종목코드4
        srs_cd_05 (Optional[str]): 종목코드5
        srs_cd_06 (Optional[str]): 종목코드6
        srs_cd_07 (Optional[str]): 종목코드7
        srs_cd_08 (Optional[str]): 종목코드8
        srs_cd_09 (Optional[str]): 종목코드9
        srs_cd_10 (Optional[str]): 종목코드10
        srs_cd_11 (Optional[str]): 종목코드11
        srs_cd_12 (Optional[str]): 종목코드12
        srs_cd_13 (Optional[str]): 종목코드13
        srs_cd_14 (Optional[str]): 종목코드14
        srs_cd_15 (Optional[str]): 종목코드15
        srs_cd_16 (Optional[str]): 종목코드16
        srs_cd_17 (Optional[str]): 종목코드17
        srs_cd_18 (Optional[str]): 종목코드18
        srs_cd_19 (Optional[str]): 종목코드19
        srs_cd_20 (Optional[str]): 종목코드20
        srs_cd_21 (Optional[str]): 종목코드21
        srs_cd_22 (Optional[str]): 종목코드22
        srs_cd_23 (Optional[str]): 종목코드23
        srs_cd_24 (Optional[str]): 종목코드24
        srs_cd_25 (Optional[str]): 종목코드25
        srs_cd_26 (Optional[str]): 종목코드26
        srs_cd_27 (Optional[str]): 종목코드27
        srs_cd_28 (Optional[str]): 종목코드28
        srs_cd_29 (Optional[str]): 종목코드29
        srs_cd_30 (Optional[str]): 종목코드30

    Returns:
        pd.DataFrame: 해외옵션 상품기본정보 데이터
        
    Example:
        >>> df = search_opt_detail(qry_cnt="1", srs_cd_01="6AM24")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if qry_cnt == "":
        raise ValueError("qry_cnt is required (e.g. 'SRS_CD_N 개수')")
    
    if srs_cd_01 == "":
        raise ValueError("srs_cd_01 is required")

    tr_id = "HHDFO55200000"  # 해외옵션 상품기본정보


    api_url = "/uapi/overseas-futureoption/v1/quotations/search-opt-detail"



    params = {
        "QRY_CNT": qry_cnt,
        "SRS_CD_01": srs_cd_01
    }
    
    # 옵션 파라미터 추가
    if srs_cd_02:
        params["SRS_CD_02"] = srs_cd_02
    if srs_cd_03:
        params["SRS_CD_03"] = srs_cd_03
    if srs_cd_04:
        params["SRS_CD_04"] = srs_cd_04
    if srs_cd_05:
        params["SRS_CD_05"] = srs_cd_05
    if srs_cd_06:
        params["SRS_CD_06"] = srs_cd_06
    if srs_cd_07:
        params["SRS_CD_07"] = srs_cd_07
    if srs_cd_08:
        params["SRS_CD_08"] = srs_cd_08
    if srs_cd_09:
        params["SRS_CD_09"] = srs_cd_09
    if srs_cd_10:
        params["SRS_CD_10"] = srs_cd_10
    if srs_cd_11:
        params["SRS_CD_11"] = srs_cd_11
    if srs_cd_12:
        params["SRS_CD_12"] = srs_cd_12
    if srs_cd_13:
        params["SRS_CD_13"] = srs_cd_13
    if srs_cd_14:
        params["SRS_CD_14"] = srs_cd_14
    if srs_cd_15:
        params["SRS_CD_15"] = srs_cd_15
    if srs_cd_16:
        params["SRS_CD_16"] = srs_cd_16
    if srs_cd_17:
        params["SRS_CD_17"] = srs_cd_17
    if srs_cd_18:
        params["SRS_CD_18"] = srs_cd_18
    if srs_cd_19:
        params["SRS_CD_19"] = srs_cd_19
    if srs_cd_20:
        params["SRS_CD_20"] = srs_cd_20
    if srs_cd_21:
        params["SRS_CD_21"] = srs_cd_21
    if srs_cd_22:
        params["SRS_CD_22"] = srs_cd_22
    if srs_cd_23:
        params["SRS_CD_23"] = srs_cd_23
    if srs_cd_24:
        params["SRS_CD_24"] = srs_cd_24
    if srs_cd_25:
        params["SRS_CD_25"] = srs_cd_25
    if srs_cd_26:
        params["SRS_CD_26"] = srs_cd_26
    if srs_cd_27:
        params["SRS_CD_27"] = srs_cd_27
    if srs_cd_28:
        params["SRS_CD_28"] = srs_cd_28
    if srs_cd_29:
        params["SRS_CD_29"] = srs_cd_29
    if srs_cd_30:
        params["SRS_CD_30"] = srs_cd_30
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        # 메타데이터에 따라 output2 (array)를 pd.DataFrame으로 반환
        return pd.DataFrame(res.getBody().output2)
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물종목상세[v1_해외선물-008]
##############################################################################################

def stock_detail(
    srs_cd: str,  # 종목코드
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외선물옵션] 기본시세 
    해외선물종목상세[v1_해외선물-008]
    해외선물종목상세 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        srs_cd (str): ex) CNHU24 ※ 종목코드 "포럼 > FAQ > 종목정보 다운로드(해외) - 해외지수선물" 참고
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외선물종목상세 데이터
        
    Example:
        >>> df = stock_detail(srs_cd="6AU22")
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not srs_cd:
        logger.error("srs_cd is required. (e.g. '6AU22')")
        raise ValueError("srs_cd is required. (e.g. '6AU22')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    tr_id = "HHDFC55010100"


    api_url = "/uapi/overseas-futureoption/v1/quotations/stock-detail"



    params = {
        "SRS_CD": srs_cd,
    }

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
            return stock_detail(
                srs_cd,
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
# [해외선물옵션] 기본시세 > 해외선물 체결추이(틱)[해외선물-019]
##############################################################################################

def tick_ccnl(
    srs_cd: str,  # 종목코드
    exch_cd: str,  # 거래소코드
    start_date_time: str,  # 조회시작일시
    close_date_time: str,  # 조회종료일시
    qry_tp: str,  # 조회구분
    qry_cnt: str,  # 요청개수
    qry_gap: str,  # 묶음개수
    index_key: str,  # 이전조회KEY
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외선물옵션] 기본시세 
    해외선물 체결추이(틱)[해외선물-019]
    해외선물 체결추이(틱) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        srs_cd (str): 종목코드 (예: '6AM24')
        exch_cd (str): 거래소코드 (예: 'CME')
        start_date_time (str): 조회시작일시 (공백 허용)
        close_date_time (str): 조회종료일시 (예: '20240402')
        qry_tp (str): 조회구분 ('Q': 최초조회, 'P': 다음키 입력하여 조회)
        qry_cnt (str): 요청개수 (예: '30', 최대 '40')
        qry_gap (str): 묶음개수 (공백 허용)
        index_key (str): 이전조회KEY (공백 허용)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외선물 체결추이(틱) 데이터
        
    Example:
        >>> df1, df2 = tick_ccnl(
        ...     srs_cd="BONU25",
        ...     exch_cd="EUREX",
        ...     start_date_time="",
        ...     close_date_time="20250630",
        ...     qry_tp="Q",
        ...     qry_cnt="30",
        ...     qry_gap="",
        ...     index_key=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not srs_cd:
        logger.error("srs_cd is required. (e.g. '6AM24')")
        raise ValueError("srs_cd is required. (e.g. '6AM24')")
    if not exch_cd:
        logger.error("exch_cd is required. (e.g. 'CME')")
        raise ValueError("exch_cd is required. (e.g. 'CME')")
    if not close_date_time:
        logger.error("close_date_time is required. (e.g. '20240402')")
        raise ValueError("close_date_time is required. (e.g. '20240402')")
    if not qry_tp:
        logger.error("qry_tp is required. ('Q' or 'P')")
        raise ValueError("qry_tp is required. ('Q' or 'P')")
    if not qry_cnt:
        logger.error("qry_cnt is required. (e.g. '30')")
        raise ValueError("qry_cnt is required. (e.g. '30')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    tr_id = "HHDFC55020200"


    api_url = "/uapi/overseas-futureoption/v1/quotations/tick-ccnl"



    params = {
        "SRS_CD": srs_cd,
        "EXCH_CD": exch_cd,
        "START_DATE_TIME": start_date_time,
        "CLOSE_DATE_TIME": close_date_time,
        "QRY_TP": qry_tp,
        "QRY_CNT": qry_cnt,
        "QRY_GAP": qry_gap,
        "INDEX_KEY": index_key,
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
            return tick_ccnl(
                srs_cd,
                exch_cd,
                start_date_time,
                close_date_time,
                qry_tp,
                qry_cnt,
                qry_gap,
                index_key,
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
# [해외선물옵션] 기본시세 > 해외선물 체결추이(주간)[해외선물-017]
##############################################################################################

def weekly_ccnl(
    srs_cd: str,  # 종목코드
    exch_cd: str,  # 거래소코드
    start_date_time: str,  # 조회시작일시
    close_date_time: str,  # 조회종료일시
    qry_tp: str,  # 조회구분
    qry_cnt: str,  # 요청개수
    qry_gap: str,  # 묶음개수
    index_key: str,  # 이전조회KEY
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외선물옵션] 기본시세 
    해외선물 체결추이(주간)[해외선물-017]
    해외선물 체결추이(주간) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        srs_cd (str): 종목코드, 예) 6AM24
        exch_cd (str): 거래소코드, 예) CME
        start_date_time (str): 조회시작일시, 공백
        close_date_time (str): 조회종료일시, 예) 20240402
        qry_tp (str): 조회구분, Q : 최초조회시 , P : 다음키(INDEX_KEY) 입력하여 조회시
        qry_cnt (str): 요청개수, 예) 30 (최대 40)
        qry_gap (str): 묶음개수, 공백 (분만 사용)
        index_key (str): 이전조회KEY, 공백
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외선물 체결추이(주간) 데이터
        
    Example:
        >>> df1, df2 = weekly_ccnl(
        ...     srs_cd="6AM24",
        ...     exch_cd="CME",
        ...     start_date_time="",
        ...     close_date_time="20240402",
        ...     qry_tp="Q",
        ...     qry_cnt="30",
        ...     qry_gap="",
        ...     index_key=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not srs_cd:
        logger.error("srs_cd is required. (e.g. '6AM24')")
        raise ValueError("srs_cd is required. (e.g. '6AM24')")
    if not exch_cd:
        logger.error("exch_cd is required. (e.g. 'CME')")
        raise ValueError("exch_cd is required. (e.g. 'CME')")
    if not close_date_time:
        logger.error("close_date_time is required. (e.g. '20240402')")
        raise ValueError("close_date_time is required. (e.g. '20240402')")
    if not qry_cnt:
        logger.error("qry_cnt is required. (e.g. '30')")
        raise ValueError("qry_cnt is required. (e.g. '30')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    tr_id = "HHDFC55020000"


    api_url = "/uapi/overseas-futureoption/v1/quotations/weekly-ccnl"



    params = {
        "SRS_CD": srs_cd,
        "EXCH_CD": exch_cd,
        "START_DATE_TIME": start_date_time,
        "CLOSE_DATE_TIME": close_date_time,
        "QRY_TP": qry_tp,
        "QRY_CNT": qry_cnt,
        "QRY_GAP": qry_gap,
        "INDEX_KEY": index_key,
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
            return weekly_ccnl(
                srs_cd,
                exch_cd,
                start_date_time,
                close_date_time,
                qry_tp,
                qry_cnt,
                qry_gap,
                index_key,
                dataframe1,
                dataframe2,
                "N",
                depth + 1,
                max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame(), pd.DataFrame()

