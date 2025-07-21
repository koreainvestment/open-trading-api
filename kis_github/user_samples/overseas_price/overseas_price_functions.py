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
# [해외주식] 시세분석 > 해외속보(제목) [해외주식-055]
##############################################################################################

def brknews_title(
    fid_news_ofer_entp_code: str,     # [필수] 뉴스제공업체코드 (ex. 0:전체조회)
    fid_cond_scr_div_code: str,       # [필수] 조건화면분류코드 (ex. 11801)
    fid_cond_mrkt_cls_code: str = "",  # 조건시장구분코드
    fid_input_iscd: str = "",          # 입력종목코드
    fid_titl_cntt: str = "",           # 제목내용
    fid_input_date_1: str = "",        # 입력날짜1
    fid_input_hour_1: str = "",        # 입력시간1
    fid_rank_sort_cls_code: str = "",  # 순위정렬구분코드
    fid_input_srno: str = ""           # 입력일련번호
) -> pd.DataFrame:
    """
    해외속보(제목) API입니다.
    한국투자 HTS(eFriend Plus) > [7704] 해외속보 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

    최대 100건까지 조회 가능합니다.
    
    Args:
        fid_news_ofer_entp_code (str): [필수] 뉴스제공업체코드 (ex. 0:전체조회)
        fid_cond_scr_div_code (str): [필수] 조건화면분류코드 (ex. 11801)
        fid_cond_mrkt_cls_code (str): 조건시장구분코드
        fid_input_iscd (str): 입력종목코드
        fid_titl_cntt (str): 제목내용
        fid_input_date_1 (str): 입력날짜1
        fid_input_hour_1 (str): 입력시간1
        fid_rank_sort_cls_code (str): 순위정렬구분코드
        fid_input_srno (str): 입력일련번호

    Returns:
        pd.DataFrame: 해외속보(제목) 데이터
        
    Example:
        >>> df = brknews_title("0", "11801")
        >>> print(df)
    """

    if fid_news_ofer_entp_code == "":
        raise ValueError("fid_news_ofer_entp_code is required (e.g. '0')")
    
    if fid_cond_scr_div_code == "":
        raise ValueError("fid_cond_scr_div_code is required (e.g. '11801')")

    api_url = "/uapi/overseas-price/v1/quotations/brknews-title"


    tr_id = "FHKST01011801"

    params = {
        "FID_NEWS_OFER_ENTP_CODE": fid_news_ofer_entp_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_COND_MRKT_CLS_CODE": fid_cond_mrkt_cls_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_TITL_CNTT": fid_titl_cntt,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_HOUR_1": fid_input_hour_1,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_INPUT_SRNO": fid_input_srno
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        return pd.DataFrame(res.getBody().output)
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

##############################################################################################
# [해외주식] 시세분석 > 당사 해외주식담보대출 가능 종목 [해외주식-051]
##############################################################################################

def colable_by_company(
    pdno: str,  # 상품번호
    natn_cd: str,  # 국가코드
    inqr_sqn_dvsn: str,  # 조회순서구분
    prdt_type_cd: str = "",  # 상품유형코드
    inqr_strt_dt: str = "",  # 조회시작일자
    inqr_end_dt: str = "",  # 조회종료일자
    inqr_dvsn: str = "",  # 조회구분
    rt_dvsn_cd: str = "",  # 비율구분코드
    rt: str = "",  # 비율
    loan_psbl_yn: str = "",  # 대출가능여부
    FK100: str = "",  # 연속조회검색조건100
    NK100: str = "",  # 연속조회키100
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    당사 해외주식담보대출 가능 종목 API입니다.
    한국투자 HTS(eFriend Plus) > [0497] 당사 해외주식담보대출 가능 종목 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

    한 번의 호출에 20건까지 조회가 가능하며 다음조회가 불가하기에, PDNO에 데이터 확인하고자 하는 종목코드를 입력하여 단건조회용으로 사용하시기 바랍니다.
    
    Args:
        pdno (str): [필수] 상품번호 (ex. AMD)
        natn_cd (str): [필수] 국가코드 (ex. 840:미국,344:홍콩,156:중국)
        inqr_sqn_dvsn (str): [필수] 조회순서구분 (ex. 01:이름순,02:코드순)
        prdt_type_cd (str): 상품유형코드
        inqr_strt_dt (str): 조회시작일자
        inqr_end_dt (str): 조회종료일자
        inqr_dvsn (str): 조회구분
        rt_dvsn_cd (str): 비율구분코드
        rt (str): 비율
        loan_psbl_yn (str): 대출가능여부
        FK100 (str): 연속조회검색조건100
        NK100 (str): 연속조회키100
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> df1, df2 = colable_by_company(pdno="AMD", natn_cd="840", inqr_sqn_dvsn="01")
        >>> print(df1)  # output1 데이터
        >>> print(df2)  # output2 데이터
    """

    # 필수 파라미터 검증
    if pdno == "":
        raise ValueError("pdno is required (e.g. 'AMD')")
    
    if natn_cd == "":
        raise ValueError("natn_cd is required (e.g. '840:미국,344:홍콩,156:중국')")
    
    if inqr_sqn_dvsn == "":
        raise ValueError("inqr_sqn_dvsn is required (e.g. '01:이름순,02:코드순')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    api_url = "/uapi/overseas-price/v1/quotations/colable-by-company"


    tr_id = "CTLN4050R"

    params = {
        "PDNO": pdno,
        "NATN_CD": natn_cd,
        "INQR_SQN_DVSN": inqr_sqn_dvsn,
        "PRDT_TYPE_CD": prdt_type_cd,
        "INQR_STRT_DT": inqr_strt_dt,
        "INQR_END_DT": inqr_end_dt,
        "INQR_DVSN": inqr_dvsn,
        "RT_DVSN_CD": rt_dvsn_cd,
        "RT": rt,
        "LOAN_PSBL_YN": loan_psbl_yn,
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
            return colable_by_company(
                pdno, natn_cd, inqr_sqn_dvsn, prdt_type_cd, inqr_strt_dt, inqr_end_dt,
                inqr_dvsn, rt_dvsn_cd, rt, loan_psbl_yn, FK100, NK100, "N",
                dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

##############################################################################################
# [해외주식] 기본시세 > 해외결제일자조회[해외주식-017]
##############################################################################################

def countries_holiday(
    trad_dt: str,  # 기준일자
    ctx_area_nk: str,  # 연속조회키
    ctx_area_fk: str,  # 연속조회검색조건
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [해외주식] 기본시세 
    해외결제일자조회[해외주식-017]
    해외결제일자조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        trad_dt (str): 기준일자(YYYYMMDD)
        ctx_area_nk (str): 공백으로 입력
        ctx_area_fk (str): 공백으로 입력
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외결제일자조회 데이터
        
    Example:
        >>> df = countries_holiday("20221227", "", "")
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not trad_dt:
        logger.error("trad_dt is required. (e.g. '20221227')")
        raise ValueError("trad_dt is required. (e.g. '20221227')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    api_url = "/uapi/overseas-stock/v1/quotations/countries-holiday"

    
    tr_id = "CTOS5011R"

    params = {
        "TRAD_DT": trad_dt,
        "CTX_AREA_NK": ctx_area_nk,
        "CTX_AREA_FK": ctx_area_fk,
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
            return countries_holiday(
                trad_dt,
                ctx_area_nk,
                ctx_area_fk,
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
# [해외주식] 기본시세 > 해외주식 일별기간손익[v1_해외주식-010]
##############################################################################################

def dailyprice(
    auth: str,  # 사용자권한정보
    excd: str,  # 거래소코드
    symb: str,  # 종목코드
    gubn: str,  # 일/주/월구분
    bymd: str,  # 조회기준일자
    modp: str,  # 수정주가반영여부
    env_dv: str = "real",  # 실전모의구분
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 기본시세 
    해외주식 기간별시세[v1_해외주식-010]
    해외주식 기간별시세 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        auth (str): 사용자권한정보 (예: "")
        excd (str): 거래소코드 (예: "NYS")
        symb (str): 종목코드 (예: "TSLA")
        gubn (str): 일/주/월구분 (예: "0")
        bymd (str): 조회기준일자(YYYYMMDD) (예: "20230101")
        modp (str): 수정주가반영여부 (예: "0")
        env_dv (str): 실전모의구분 (real:실전, demo:모의)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식 기간별시세 데이터
        
    Example:
        >>> df1, df2 = dailyprice("auth_token", "NYS", "TSLA", "0", "20230101", "0", "")
        >>> print(df1)
        >>> print(df2)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not excd:
        logger.error("excd is required. (e.g. 'NYS')")
        raise ValueError("excd is required. (e.g. 'NYS')")
    if not symb:
        logger.error("symb is required. (e.g. 'TSLA')")
        raise ValueError("symb is required. (e.g. 'TSLA')")
    if not gubn:
        logger.error("gubn is required. (e.g. '0')")
        raise ValueError("gubn is required. (e.g. '0')")
    if not modp:
        logger.error("modp is required. (e.g. '0')")
        raise ValueError("modp is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real" or env_dv == "demo":
        api_url = "/uapi/overseas-price/v1/quotations/dailyprice"

        tr_id = "HHDFS76240000"  # 실전/모의투자 공통 TR ID
    else:
        logger.error("env_dv can only be 'real' or 'demo'")
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "AUTH": auth,
        "EXCD": excd,
        "SYMB": symb,
        "GUBN": gubn,
        "BYMD": bymd,
        "MODP": modp,
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
            return dailyprice(
                auth,
                excd,
                symb,
                gubn,
                bymd,
                modp,
                env_dv,
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
# [해외주식] 기본시세 > 해외주식 업종별코드조회[해외주식-049]
##############################################################################################

def industry_price(
    excd: str,  # [필수] 거래소명
    auth: str = "",  # 사용자권한정보
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    해외주식 업종별코드조회 API입니다.
    
    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        auth (str): 사용자권한정보
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 데이터
        
    Example:
        >>> df1, df2 = industry_price(excd="NAS")
        >>> print(df1, df2)
    """

    if excd == "":
        raise ValueError("excd is required (e.g. 'NYS', 'NAS', 'AMS', 'HKS', 'SHS', 'SZS', 'HSX', 'HNX', 'TSE')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    api_url = "/uapi/overseas-price/v1/quotations/industry-price"


    tr_id = "HHDFS76370100"

    params = {
        "EXCD": excd,
        "AUTH": auth
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
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return industry_price(
                excd, auth, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외주식] 기본시세 > 해외주식 업종별시세[해외주식-048]
##############################################################################################

def industry_theme(
    excd: str,                                    # [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
    icod: str,                                    # [필수] 업종코드
    vol_rang: str,                                # [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
    auth: str = "",                               # 사용자권한정보
    keyb: str = "",                               # NEXT KEY BUFF
    tr_cont: str = "",                            # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,    # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,    # 누적 데이터프레임2
    depth: int = 0,                               # 내부 재귀깊이 (자동관리)
    max_depth: int = 10                           # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    해외주식 업종별시세 API입니다.
    
    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        icod (str): [필수] 업종코드
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        auth (str): 사용자권한정보
        keyb (str): NEXT KEY BUFF
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> df1, df2 = industry_theme(excd="NAS", icod="010", vol_rang="0")
        >>> print(df1)
        >>> print(df2)
    """

    if excd == "":
        raise ValueError("excd is required (e.g. 'NAS')")
    
    if icod == "":
        raise ValueError("icod is required")
    
    if vol_rang == "":
        raise ValueError("vol_rang is required (e.g. '0')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    api_url = "/uapi/overseas-price/v1/quotations/industry-theme"


    tr_id = "HHDFS76370000"

    params = {
        "EXCD": excd,
        "ICOD": icod,
        "VOL_RANG": vol_rang,
        "AUTH": auth,
        "KEYB": keyb
    }
    
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 데이터 처리
        current_data1 = pd.DataFrame(res.getBody().output1, index=[0])
        if dataframe1 is not None:
            dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True)
        else:
            dataframe1 = current_data1
            
        # output2 데이터 처리
        current_data2 = pd.DataFrame(res.getBody().output2)
        if dataframe2 is not None:
            dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True)
        else:
            dataframe2 = current_data2
            
        tr_cont = res.getHeader().tr_cont
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return industry_theme(
                excd, icod, vol_rang, auth, keyb, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외주식] 기본시세 > 해외주식 현재가 1호가[해외주식-033]
##############################################################################################

def inquire_asking_price(
    auth: str,  # 사용자권한정보
    excd: str,  # 거래소코드
    symb: str,  # 종목코드
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    dataframe3: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output3)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 기본시세 
    해외주식 현재가 1호가[해외주식-033]
    해외주식 현재가 1호가 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        auth (str): 사용자권한정보
        excd (str): 거래소코드 (예: NYS, NAS, AMS, 등)
        symb (str): 종목코드 (예: TSLA)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        dataframe3 (Optional[pd.DataFrame]): 누적 데이터프레임 (output3)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: 해외주식 현재가 1호가 데이터
        
    Example:
        >>> df1, df2, df3 = inquire_asking_price(auth="your_auth_token", excd="NAS", symb="TSLA")
        >>> print(df1)
        >>> print(df2)
        >>> print(df3)
    """
    # [필수 파라미터 검증]
    if not excd:
        logger.error("excd is required. (e.g. 'NAS')")
        raise ValueError("excd is required. (e.g. 'NAS')")
    if not symb:
        logger.error("symb is required. (e.g. 'TSLA')")
        raise ValueError("symb is required. (e.g. 'TSLA')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame(), dataframe3 if dataframe3 is not None else pd.DataFrame()
    
    api_url = "/uapi/overseas-price/v1/quotations/inquire-asking-price"

    
    tr_id = "HHDFS76200100"

    params = {
        "AUTH": auth,
        "EXCD": excd,
        "SYMB": symb,
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
        
        # output3 처리
        if hasattr(res.getBody(), 'output3'):
            output_data = res.getBody().output3
            if output_data:
                if isinstance(output_data, list):
                    current_data3 = pd.DataFrame(output_data)
                else:
                    current_data3 = pd.DataFrame([output_data])
                
                if dataframe3 is not None:
                    dataframe3 = pd.concat([dataframe3, current_data3], ignore_index=True)
                else:
                    dataframe3 = current_data3
            else:
                if dataframe3 is None:
                    dataframe3 = pd.DataFrame()
        else:
            if dataframe3 is None:
                dataframe3 = pd.DataFrame()
        
        tr_cont = res.getHeader().tr_cont
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_asking_price(
                auth,
                excd,
                symb,
                "N", dataframe1, dataframe2, dataframe3, depth + 1, max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2, dataframe3
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외주식] 기본시세 > 해외주식 체결추이[해외주식-037]
##############################################################################################

def inquire_ccnl(
    excd: str,         # [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
    tday: str,         # [필수] 당일전일구분 (ex. 0:전일, 1:당일)
    symb: str,         # [필수] 종목코드 (ex. 해외종목코드)
    auth: str = "",    # 사용자권한정보
    keyb: str = "",    # NEXT KEY BUFF
    tr_cont: str = "", # 연속거래여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,         # 내부 재귀깊이 (자동관리)
    max_depth: int = 10     # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    해외주식 체결추이 API입니다.
    
    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        tday (str): [필수] 당일전일구분 (ex. 0:전일, 1:당일)
        symb (str): [필수] 종목코드 (ex. 해외종목코드)
        auth (str): 사용자권한정보
        keyb (str): NEXT KEY BUFF
        tr_cont (str): 연속거래여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        pd.DataFrame: 해외주식 체결추이 데이터
        
    Example:
        >>> df = inquire_ccnl(excd="NAS", tday="0", symb="TSLA")
        >>> print(df)
    """

    if excd == "":
        raise ValueError("excd is required (e.g. 'NAS')")
    
    if tday == "":
        raise ValueError("tday is required (e.g. '0' or '1')")
    
    if symb == "":
        raise ValueError("symb is required (e.g. 'TSLA')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    api_url = "/uapi/overseas-price/v1/quotations/inquire-ccnl"


    tr_id = "HHDFS76200300"

    params = {
        "EXCD": excd,
        "TDAY": tday,
        "SYMB": symb,
        "AUTH": auth,
        "KEYB": keyb
    }
    
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output1)
            
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data
            
        tr_cont = res.getHeader().tr_cont
        keyb = res.getBody().keyb if hasattr(res.getBody(), 'keyb') else ""
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_ccnl(
                excd, tday, symb, auth, keyb, "N", dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

##############################################################################################
# [해외주식] 기본시세 > 해외주식 종목_지수_환율기간별시세(일_주_월_년)[v1_해외주식-012]
##############################################################################################

def inquire_daily_chartprice(
    fid_cond_mrkt_div_code: str,  # FID 조건 시장 분류 코드
    fid_input_iscd: str,  # FID 입력 종목코드
    fid_input_date_1: str,  # FID 입력 날짜1
    fid_input_date_2: str,  # FID 입력 날짜2
    fid_period_div_code: str,  # FID 기간 분류 코드
    env_dv: str = "real",  # 실전모의구분
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 기본시세 
    해외주식 종목_지수_환율기간별시세(일_주_월_년)[v1_해외주식-012]
    해외주식 종목_지수_환율기간별시세(일_주_월_년) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): N: 해외지수, X 환율, I: 국채, S:금선물
        fid_input_iscd (str): 종목코드 ※ 해외주식 마스터 코드 참조  (포럼 > FAQ > 종목정보 다운로드(해외) > 해외지수)  ※ 해당 API로 미국주식 조회 시, 다우30, 나스닥100, S&P500 종목만 조회 가능합니다. 더 많은 미국주식 종목 시세를 이용할 시에는, 해외주식기간별시세 API 사용 부탁드립니다.
        fid_input_date_1 (str): 시작일자(YYYYMMDD)
        fid_input_date_2 (str): 종료일자(YYYYMMDD)
        fid_period_div_code (str): D:일, W:주, M:월, Y:년
        env_dv (str): 실전모의구분 (real:실전, demo:모의)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식 종목_지수_환율기간별시세(일_주_월_년) 데이터
        
    Example:
        >>> df1, df2 = inquire_daily_chartprice(
        ...     fid_cond_mrkt_div_code="N",
        ...     fid_input_iscd=".DJI",
        ...     fid_input_date_1="20220401",
        ...     fid_input_date_2="20220613",
        ...     fid_period_div_code="D",
        ...     env_dv="real"
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'N')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'N')")
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '.DJI')")
        raise ValueError("fid_input_iscd is required. (e.g. '.DJI')")
    if not fid_input_date_1:
        logger.error("fid_input_date_1 is required. (e.g. '20220401')")
        raise ValueError("fid_input_date_1 is required. (e.g. '20220401')")
    if not fid_input_date_2:
        logger.error("fid_input_date_2 is required. (e.g. '20220613')")
        raise ValueError("fid_input_date_2 is required. (e.g. '20220613')")
    if not fid_period_div_code:
        logger.error("fid_period_div_code is required. (e.g. 'D')")
        raise ValueError("fid_period_div_code is required. (e.g. 'D')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real" or env_dv == "demo":
        api_url = "/uapi/overseas-price/v1/quotations/inquire-daily-chartprice"

        tr_id = "FHKST03030100"  # 실전투자용 TR ID
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_DATE_2": fid_input_date_2,
        "FID_PERIOD_DIV_CODE": fid_period_div_code,
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
            return inquire_daily_chartprice(
                fid_cond_mrkt_div_code,
                fid_input_iscd,
                fid_input_date_1,
                fid_input_date_2,
                fid_period_div_code,
                env_dv,
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
# [해외주식] 시세분석 > 해외주식조건검색[v1_해외주식-015]
##############################################################################################

def inquire_search(
    auth: str,  # 사용자권한정보
    excd: str,  # 거래소코드
    co_yn_pricecur: str,  # 현재가선택조건
    co_st_pricecur: str,  # 현재가시작범위가
    co_en_pricecur: str,  # 현재가끝범위가
    co_yn_rate: str,  # 등락율선택조건
    co_st_rate: str,  # 등락율시작율
    co_en_rate: str,  # 등락율끝율
    co_yn_valx: str,  # 시가총액선택조건
    co_st_valx: str,  # 시가총액시작액
    co_en_valx: str,  # 시가총액끝액
    co_yn_shar: str,  # 발행주식수선택조건
    co_st_shar: str,  # 발행주식시작수
    co_en_shar: str,  # 발행주식끝수
    co_yn_volume: str,  # 거래량선택조건
    co_st_volume: str,  # 거래량시작량
    co_en_volume: str,  # 거래량끝량
    co_yn_amt: str,  # 거래대금선택조건
    co_st_amt: str,  # 거래대금시작금
    co_en_amt: str,  # 거래대금끝금
    co_yn_eps: str,  # EPS선택조건
    co_st_eps: str,  # EPS시작
    co_en_eps: str,  # EPS끝
    co_yn_per: str,  # PER선택조건
    co_st_per: str,  # PER시작
    co_en_per: str,  # PER끝
    keyb: str,  # NEXT KEY BUFF
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 기본시세 
    해외주식조건검색[v1_해외주식-015]
    해외주식조건검색 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        auth (str): "" (Null 값 설정)
        excd (str): NYS : 뉴욕, NAS : 나스닥,  AMS : 아멕스  HKS : 홍콩, SHS : 상해 , SZS : 심천 HSX : 호치민, HNX : 하노이 TSE : 도쿄
        co_yn_pricecur (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_pricecur (str): 단위: 각국통화(JPY, USD, HKD, CNY, VND)
        co_en_pricecur (str): 단위: 각국통화(JPY, USD, HKD, CNY, VND)
        co_yn_rate (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_rate (str): %
        co_en_rate (str): %
        co_yn_valx (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_valx (str): 단위: 천
        co_en_valx (str): 단위: 천
        co_yn_shar (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_shar (str): 단위: 천
        co_en_shar (str): 단위: 천
        co_yn_volume (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_volume (str): 단위: 주
        co_en_volume (str): 단위: 주
        co_yn_amt (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_amt (str): 단위: 천
        co_en_amt (str): 단위: 천
        co_yn_eps (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_eps (str): 
        co_en_eps (str): 
        co_yn_per (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_per (str): 
        co_en_per (str): 
        keyb (str): "" 공백 입력
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식조건검색 데이터
        
    Example:
        >>> df1, df2 = inquire_search(
        ...     auth="", excd="NAS", co_yn_pricecur="1", co_st_pricecur="160", co_en_pricecur="161",
        ...     co_yn_rate="", co_st_rate="", co_en_rate="", co_yn_valx="", co_st_valx="", co_en_valx="",
        ...     co_yn_shar="", co_st_shar="", co_en_shar="", co_yn_volume="", co_st_volume="", co_en_volume="",
        ...     co_yn_amt="", co_st_amt="", co_en_amt="", co_yn_eps="", co_st_eps="", co_en_eps="",
        ...     co_yn_per="", co_st_per="", co_en_per="", keyb=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not excd:
        logger.error("excd is required. (e.g. 'NAS')")
        raise ValueError("excd is required. (e.g. 'NAS')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    api_url = "/uapi/overseas-price/v1/quotations/inquire-search"

    
    tr_id = "HHDFS76410000"

    params = {
        "AUTH": auth,
        "EXCD": excd,
        "CO_YN_PRICECUR": co_yn_pricecur,
        "CO_ST_PRICECUR": co_st_pricecur,
        "CO_EN_PRICECUR": co_en_pricecur,
        "CO_YN_RATE": co_yn_rate,
        "CO_ST_RATE": co_st_rate,
        "CO_EN_RATE": co_en_rate,
        "CO_YN_VALX": co_yn_valx,
        "CO_ST_VALX": co_st_valx,
        "CO_EN_VALX": co_en_valx,
        "CO_YN_SHAR": co_yn_shar,
        "CO_ST_SHAR": co_st_shar,
        "CO_EN_SHAR": co_en_shar,
        "CO_YN_VOLUME": co_yn_volume,
        "CO_ST_VOLUME": co_st_volume,
        "CO_EN_VOLUME": co_en_volume,
        "CO_YN_AMT": co_yn_amt,
        "CO_ST_AMT": co_st_amt,
        "CO_EN_AMT": co_en_amt,
        "CO_YN_EPS": co_yn_eps,
        "CO_ST_EPS": co_st_eps,
        "CO_EN_EPS": co_en_eps,
        "CO_YN_PER": co_yn_per,
        "CO_ST_PER": co_st_per,
        "CO_EN_PER": co_en_per,
        "KEYB": keyb,
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
            return inquire_search(
                auth,
                excd,
                co_yn_pricecur,
                co_st_pricecur,
                co_en_pricecur,
                co_yn_rate,
                co_st_rate,
                co_en_rate,
                co_yn_valx,
                co_st_valx,
                co_en_valx,
                co_yn_shar,
                co_st_shar,
                co_en_shar,
                co_yn_volume,
                co_st_volume,
                co_en_volume,
                co_yn_amt,
                co_st_amt,
                co_en_amt,
                co_yn_eps,
                co_st_eps,
                co_en_eps,
                co_yn_per,
                co_st_per,
                co_en_per,
                keyb,
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
# [해외주식] 기본시세 > 해외지수분봉조회[v1_해외주식-031]
##############################################################################################

def inquire_time_indexchartprice(
    fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
    fid_input_iscd: str,  # 입력 종목코드
    fid_hour_cls_code: str,  # 시간 구분 코드
    fid_pw_data_incu_yn: str,  # 과거 데이터 포함 여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 기본시세 
    해외지수분봉조회[v1_해외주식-031]
    해외지수분봉조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): N 해외지수 X 환율 KX 원화환율
        fid_input_iscd (str): 종목번호(ex. TSLA)
        fid_hour_cls_code (str): 0: 정규장, 1: 시간외
        fid_pw_data_incu_yn (str): Y/N
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외지수분봉조회 데이터
        
    Example:
        >>> df1, df2 = inquire_time_indexchartprice(
        ...     fid_cond_mrkt_div_code="N",
        ...     fid_input_iscd="SPX",
        ...     fid_hour_cls_code="0",
        ...     fid_pw_data_incu_yn="Y"
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'N')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'N')")
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. 'SPX')")
        raise ValueError("fid_input_iscd is required. (e.g. 'SPX')")
    if not fid_hour_cls_code:
        logger.error("fid_hour_cls_code is required. (e.g. '0')")
        raise ValueError("fid_hour_cls_code is required. (e.g. '0')")
    if not fid_pw_data_incu_yn:
        logger.error("fid_pw_data_incu_yn is required. (e.g. 'Y')")
        raise ValueError("fid_pw_data_incu_yn is required. (e.g. 'Y')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    api_url = "/uapi/overseas-price/v1/quotations/inquire-time-indexchartprice"

    
    tr_id = "FHKST03030200"

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_HOUR_CLS_CODE": fid_hour_cls_code,
        "FID_PW_DATA_INCU_YN": fid_pw_data_incu_yn,
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
            return inquire_time_indexchartprice(
                fid_cond_mrkt_div_code,
                fid_input_iscd,
                fid_hour_cls_code,
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
# [해외주식] 기본시세 > 해외주식분봉조회[v1_해외주식-030]
##############################################################################################

def inquire_time_itemchartprice(
    auth: str,  # 사용자권한정보
    excd: str,  # 거래소코드
    symb: str,  # 종목코드
    nmin: str,  # 분갭
    pinc: str,  # 전일포함여부
    next: str,  # 다음여부
    nrec: str,  # 요청갯수
    fill: str,  # 미체결채움구분
    keyb: str,  # NEXT KEY BUFF
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 기본시세 
    해외주식분봉조회[v1_해외주식-030]
    해외주식분봉조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        auth (str): "" 공백으로 입력
        excd (str): NYS : 뉴욕 NAS : 나스닥 AMS : 아멕스  HKS : 홍콩 SHS : 상해  SZS : 심천 HSX : 호치민 HNX : 하노이 TSE : 도쿄   ※ 주간거래는 최대 1일치 분봉만 조회 가능 BAY : 뉴욕(주간) BAQ : 나스닥(주간) BAA : 아멕스(주간)
        symb (str): 종목코드(ex. TSLA)
        nmin (str): 분단위(1: 1분봉, 2: 2분봉, ...)
        pinc (str): 0:당일 1:전일포함 ※ 다음조회 시 반드시 "1"로 입력
        next (str): 처음조회 시, "" 공백 입력 다음조회 시, "1" 입력
        nrec (str): 레코드요청갯수 (최대 120)
        fill (str): "" 공백으로 입력
        keyb (str): 처음 조회 시, "" 공백 입력 다음 조회 시, 이전 조회 결과의 마지막 분봉 데이터를 이용하여, 1분 전 혹은 n분 전의 시간을 입력  (형식: YYYYMMDDHHMMSS, ex. 20241014140100)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식분봉조회 데이터
        
    Example:
        >>> df1, df2 = inquire_time_itemchartprice(
        ...     auth="", excd="NAS", symb="TSLA", nmin="5", pinc="1", next="1", nrec="120", fill="", keyb=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not excd:
        logger.error("excd is required. (e.g. 'NAS')")
        raise ValueError("excd is required. (e.g. 'NAS')")
    if not symb:
        logger.error("symb is required. (e.g. 'TSLA')")
        raise ValueError("symb is required. (e.g. 'TSLA')")
    if not nmin:
        logger.error("nmin is required. (e.g. '5')")
        raise ValueError("nmin is required. (e.g. '5')")
    if not pinc:
        logger.error("pinc is required. (e.g. '1')")
        raise ValueError("pinc is required. (e.g. '1')")
    if not nrec or int(nrec)>120:
        logger.error("nrec is required. (e.g. '120', 최대120개)")
        raise ValueError("nrec is required. (e.g. '120', 최대120개)")
    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    api_url = "/uapi/overseas-price/v1/quotations/inquire-time-itemchartprice"

    
    tr_id = "HHDFS76950200"

    params = {
        "AUTH": auth,
        "EXCD": excd,
        "SYMB": symb,
        "NMIN": nmin,
        "PINC": pinc,
        "NEXT": next,
        "NREC": nrec,
        "FILL": fill,
        "KEYB": keyb,
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # Output1 처리
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
        
        # Output2 처리
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
            return inquire_time_itemchartprice(
                auth,
                excd,
                symb,
                nmin,
                pinc,
                next,
                nrec,
                fill,
                keyb,
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
# [해외주식] 시세분석 > 해외뉴스종합(제목) [해외주식-053]
##############################################################################################

def news_title(
    info_gb: str = "",          # [필수] 뉴스구분
    class_cd: str = "",         # [필수] 중분류  
    nation_cd: str = "",        # [필수] 국가코드 (ex. 공백:전체, CN:중국, HK:홍콩, US:미국)
    exchange_cd: str = "",      # [필수] 거래소코드
    symb: str = "",             # [필수] 종목코드
    data_dt: str = "",          # [필수] 조회일자
    data_tm: str = "",          # [필수] 조회시간
    cts: str = "",              # [필수] 다음키
    tr_cont: str = "",          # [필수] 연속거래여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,             # 내부 재귀깊이 (자동관리)
    max_depth: int = 10         # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    해외뉴스종합(제목) API입니다.
    한국투자 HTS(eFriend Plus) > [7702] 해외뉴스종합 화면의 "우측 상단 뉴스목록" 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        info_gb (str): [필수] 뉴스구분
        class_cd (str): [필수] 중분류
        nation_cd (str): [필수] 국가코드 (ex. 공백:전체, CN:중국, HK:홍콩, US:미국)
        exchange_cd (str): [필수] 거래소코드
        symb (str): [필수] 종목코드
        data_dt (str): [필수] 조회일자
        data_tm (str): [필수] 조회시간
        cts (str): [필수] 다음키
        tr_cont (str): [필수] 연속거래여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        pd.DataFrame: 해외뉴스종합(제목) 데이터
        
    Example:
        >>> df = news_title()
        >>> print(df)
    """

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    api_url = "/uapi/overseas-price/v1/quotations/news-title"


    tr_id = "HHPSTH60100C1"  # 해외뉴스종합(제목)

    params = {
        "INFO_GB": info_gb,           # 뉴스구분
        "CLASS_CD": class_cd,         # 중분류
        "NATION_CD": nation_cd,       # 국가코드
        "EXCHANGE_CD": exchange_cd,   # 거래소코드
        "SYMB": symb,                 # 종목코드
        "DATA_DT": data_dt,           # 조회일자
        "DATA_TM": data_tm,           # 조회시간
        "CTS": cts                    # 다음키
    }
    
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().outblock1)
            
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data
            
        tr_cont = res.getHeader().tr_cont
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return news_title(
                info_gb, class_cd, nation_cd, exchange_cd, symb, data_dt, data_tm, cts, "N", dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

##############################################################################################
# [해외주식] 시세분석 > 해외주식 기간별권리조회 [해외주식-052]
##############################################################################################

def period_rights(
    rght_type_cd: str,  # 권리유형코드
    inqr_dvsn_cd: str,  # 조회구분코드
    inqr_strt_dt: str,  # 조회시작일자
    inqr_end_dt: str,   # 조회종료일자
    pdno: str = "",     # 상품번호
    prdt_type_cd: str = "",  # 상품유형코드
    NK50: str = "",     # 연속조회키50
    FK50: str = "",     # 연속조회검색조건50
    tr_cont: str = "",  # 연속거래여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,     # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    해외주식 기간별권리조회 API입니다.
    한국투자 HTS(eFriend Plus) > [7520] 기간별해외증권권리조회 화면을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

    ※ 확정여부가 '예정'으로 표시되는 경우는 권리정보가 변경될 수 있으니 참고자료로만 활용하시기 바랍니다.
    
    Args:
        rght_type_cd (str): [필수] 권리유형코드 (%%:전체, 01:유상, 02:무상, 03:배당, 11:합병,14:액면분할, 15:액면병합, 17:감자, 54:WR청구,61:원리금상환, 71:WR소멸, 74:배당옵션, 75:특별배당, 76:ISINCODE변경, 77:실권주청약)
        inqr_dvsn_cd (str): [필수] 조회구분코드 (02:현지기준일, 03:청약시작일, 04:청약종료일)
        inqr_strt_dt (str): [필수] 조회시작일자 (20250101)
        inqr_end_dt (str): [필수] 조회종료일자 (20250131)
        pdno (str): 상품번호
        prdt_type_cd (str): 상품유형코드
        NK50 (str): 연속조회키50
        FK50 (str): 연속조회검색조건50
        tr_cont (str): 연속거래여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        pd.DataFrame: 해외주식 기간별권리조회 데이터
        
    Example:
        >>> df = period_rights("%%", "02", "20240417", "20240417")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if rght_type_cd == "":
        raise ValueError("rght_type_cd is required (e.g. '%%:전체, 01:유상, 02:무상, 03:배당, 11:합병,14:액면분할, 15:액면병합, 17:감자, 54:WR청구,61:원리금상환, 71:WR소멸, 74:배당옵션, 75:특별배당, 76:ISINCODE변경, 77:실권주청약')")
    
    if inqr_dvsn_cd == "":
        raise ValueError("inqr_dvsn_cd is required (e.g. '02:현지기준일, 03:청약시작일, 04:청약종료일')")
    
    if inqr_strt_dt == "":
        raise ValueError("inqr_strt_dt is required (e.g. '20250101')")
    
    if inqr_end_dt == "":
        raise ValueError("inqr_end_dt is required (e.g. '20250131')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    api_url = "/uapi/overseas-price/v1/quotations/period-rights"


    tr_id = "CTRGT011R"  # 해외주식 기간별권리조회

    params = {
        "RGHT_TYPE_CD": rght_type_cd,      # 권리유형코드
        "INQR_DVSN_CD": inqr_dvsn_cd,      # 조회구분코드
        "INQR_STRT_DT": inqr_strt_dt,      # 조회시작일자
        "INQR_END_DT": inqr_end_dt,        # 조회종료일자
        "PDNO": pdno,                      # 상품번호
        "PRDT_TYPE_CD": prdt_type_cd,      # 상품유형코드
        "CTX_AREA_NK50": NK50,             # 연속조회키50
        "CTX_AREA_FK50": FK50              # 연속조회검색조건50
    }
    
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
            
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data
            
        tr_cont = res.getHeader().tr_cont
        NK50 = res.getBody().ctx_area_nk50
        FK50 = res.getBody().ctx_area_fk50
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return period_rights(
                rght_type_cd, inqr_dvsn_cd, inqr_strt_dt, inqr_end_dt, 
                pdno, prdt_type_cd, NK50, FK50, "N", dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

##############################################################################################
# [해외주식] 기본시세 > 해외주식 현재체결가[v1_해외주식-009]
##############################################################################################

def price(
    auth: str,  # 사용자권한정보
    excd: str,  # 거래소코드
    symb: str,  # 종목코드
    env_dv: str = "real",  # 실전모의구분
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외주식] 기본시세 
    해외주식 현재체결가[v1_해외주식-009]
    해외주식 현재체결가 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        auth (str): 사용자권한정보
        excd (str): 거래소코드 (예: "NAS")
        symb (str): 종목코드 (예: "AAPL")
        env_dv (str): 실전모의구분 (real:실전, demo:모의)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외주식 현재체결가 데이터
        
    Example:
        >>> df = price("", "NAS", "AAPL")
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not excd:
        logger.error("excd is required. (e.g. 'NAS')")
        raise ValueError("excd is required. (e.g. 'NAS')")
    
    if not symb:
        logger.error("symb is required. (e.g. 'AAPL')")
        raise ValueError("symb is required. (e.g. 'AAPL')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real" or env_dv == "demo":
        api_url = "/uapi/overseas-price/v1/quotations/price"

        tr_id = "HHDFS00000300"  # 실전투자, 모의투자 공통 TR ID
    else:
        logger.error("Invalid env_dv value: %s. Must be 'real' or 'demo'.", env_dv)
        raise ValueError("env_dv must be 'real' or 'demo'")

    params = {
        "AUTH": auth,
        "EXCD": excd,
        "SYMB": symb,
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
            return price(
                auth,
                excd,
                symb,
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
# [해외주식] 기본시세 > 해외주식 현재가상세[v1_해외주식-029]
##############################################################################################

def price_detail(
    auth: str,  # 사용자권한정보
    excd: str,  # 거래소명
    symb: str,  # 종목코드
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외주식] 기본시세 
    해외주식 현재가상세[v1_해외주식-029]
    해외주식 현재가상세 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        auth (str): 사용자권한정보
        excd (str): 거래소명 (예: HKS, NYS, NAS, AMS, TSE, SHS, SZS, SHI, SZI, HSX, HNX, BAY, BAQ, BAA)
        symb (str): 종목코드
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외주식 현재가상세 데이터
        
    Example:
        >>> df = price_detail(auth="your_auth_token", excd="NAS", symb="TSLA")
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not excd:
        logger.error("excd is required. (e.g. 'NAS')")
        raise ValueError("excd is required. (e.g. 'NAS')")
    if not symb:
        logger.error("symb is required. (e.g. 'TSLA')")
        raise ValueError("symb is required. (e.g. 'TSLA')")
    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    api_url = "/uapi/overseas-price/v1/quotations/price-detail"

    
    tr_id = "HHDFS76200200"

    params = {
        "AUTH": auth,
        "EXCD": excd,
        "SYMB": symb,
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
            return price_detail(
                auth,
                excd,
                symb,
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
# [해외주식] 시세분석 > 해외주식 권리종합 [해외주식-050]
##############################################################################################

def rights_by_ice(
    ncod: str,       # 국가코드 (CN:중국,HK:홍콩,US:미국,JP:일본,VN:베트남)
    symb: str,       # 종목코드
    st_ymd: str = "",   # 일자시작일 (미입력시 3개월전)
    ed_ymd: str = ""    # 일자종료일 (미입력시 3개월후)
) -> pd.DataFrame:
    """
    해외주식 권리종합 API입니다.
    한국투자 HTS(eFriend Plus) > [7833] 해외주식 권리(ICE제공) 화면의 "전체" 탭 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

    ※ 조회기간 기준일 입력시 참고 - 상환: 상환일자, 조기상환: 조기상환일자, 티커변경: 적용일, 그 외: 발표일
    
    Args:
        ncod (str): [필수] 국가코드 (ex. CN:중국,HK:홍콩,US:미국,JP:일본,VN:베트남)
        symb (str): [필수] 종목코드
        st_ymd (str): 일자시작일 (ex. 미입력시 3개월전)
        ed_ymd (str): 일자종료일 (ex. 미입력시 3개월후)

    Returns:
        pd.DataFrame: 해외주식 권리종합 정보
        
    Raises:
        ValueError: 필수 파라미터가 누락되었을 때
        
    Example:
        >>> df = rights_by_ice("US", "NVDL")
        >>> print(df)
    """

    # 필수 파라미터 검증
    if ncod == "":
        raise ValueError("ncod is required (e.g. 'CN:중국,HK:홍콩,US:미국,JP:일본,VN:베트남')")
    
    if symb == "":
        raise ValueError("symb is required")

    api_url = "/uapi/overseas-price/v1/quotations/rights-by-ice"


    tr_id = "HHDFS78330900"

    params = {
        "NCOD": ncod,     # 국가코드
        "SYMB": symb,     # 종목코드
        "ST_YMD": st_ymd, # 일자시작일
        "ED_YMD": ed_ymd  # 일자종료일
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output1)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

##############################################################################################
# [해외주식] 시세분석 > 해외주식 상품기본정보[v1_해외주식-034]
##############################################################################################

def search_info(
        prdt_type_cd: str,  # 상품유형코드
        pdno: str,  # 상품번호
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외주식] 기본시세 
    해외주식 상품기본정보[v1_해외주식-034]
    해외주식 상품기본정보 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        prdt_type_cd (str): 512  미국 나스닥 / 513  미국 뉴욕 / 529  미국 아멕스  515  일본 501  홍콩 / 543  홍콩CNY / 558  홍콩USD 507  베트남 하노이 / 508  베트남 호치민 551  중국 상해A / 552  중국 심천A
        pdno (str): 예) AAPL (애플)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외주식 상품기본정보 데이터
        
    Example:
        >>> df = search_info(prdt_type_cd="512", pdno="AAPL")
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not prdt_type_cd:
        logger.error("prdt_type_cd is required. (e.g. '512')")
        raise ValueError("prdt_type_cd is required. (e.g. '512')")
    if not pdno:
        logger.error("pdno is required. (e.g. 'AAPL')")
        raise ValueError("pdno is required. (e.g. 'AAPL')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    api_url = "/uapi/overseas-price/v1/quotations/search-info"


    tr_id = "CTPF1702R"

    params = {
        "PRDT_TYPE_CD": prdt_type_cd,
        "PDNO": pdno,
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
            return search_info(
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

