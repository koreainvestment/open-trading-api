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
# [해외주식] 주문/계좌 > 해외주식 지정가주문번호조회 [해외주식-071]
##############################################################################################

def algo_ordno(
    cano: str,                    # [필수] 종합계좌번호
    acnt_prdt_cd: str,           # [필수] 계좌상품코드 (ex. 01)
    trad_dt: str,                # [필수] 거래일자
    FK200: str = "",             # 연속조회검색조건200
    NK200: str = "",             # 연속조회키200
    tr_cont: str = "",           # 연속거래여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,              # 내부 재귀깊이 (자동관리)
    max_depth: int = 10          # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    TWAP, VWAP 주문에 대한 주문번호를 조회하는 API
    
    Args:
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 01)
        trad_dt (str): [필수] 거래일자
        FK200 (str): 연속조회검색조건200
        NK200 (str): 연속조회키200
        tr_cont (str): 연속거래여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        pd.DataFrame: 해외주식 지정가주문번호 데이터
        
    Example:
        >>> df = algo_ordno(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, trad_dt="20250619")
        >>> print(df)
    """

    if cano == "":
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '01')")
    
    if trad_dt == "":
        raise ValueError("trad_dt is required")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    api_url = "/uapi/overseas-stock/v1/trading/algo-ordno"


    tr_id = "TTTS6058R"  # 해외주식 지정가주문번호조회

    params = {
        "CANO": cano,                    # 종합계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,   # 계좌상품코드
        "TRAD_DT": trad_dt,             # 거래일자
        "CTX_AREA_FK200": FK200,        # 연속조회검색조건200
        "CTX_AREA_NK200": NK200         # 연속조회키200
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
            return algo_ordno(
                cano, acnt_prdt_cd, trad_dt, FK200, NK200, "N", dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 미국주간주문 [v1_해외주식-026]
##############################################################################################

def daytime_order(
    order_dv: str, # 주문구분 buy(매수) / sell(매도)
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ovrs_excg_cd: str,  # 해외거래소코드
    pdno: str,  # 상품번호
    ord_qty: str,  # 주문수량
    ovrs_ord_unpr: str,  # 해외주문단가
    ctac_tlno: str,  # 연락전화번호
    mgco_aptm_odno: str,  # 운용사지정주문번호
    ord_svr_dvsn_cd: str,  # 주문서버구분코드
    ord_dvsn: str,  # 주문구분

) -> Optional[pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 미국주간주문[v1_해외주식-026]
    해외주식 미국주간주문 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        order_dv (str): 주문구분 buy(매수) / sell(매도)
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ovrs_excg_cd (str): NASD:나스닥 / NYSE:뉴욕 / AMEX:아멕스
        pdno (str): 종목코드
        ord_qty (str): 해외거래소 별 최소 주문수량 및 주문단위 확인 필요
        ovrs_ord_unpr (str): 소수점 포함, 1주당 가격 * 시장가의 경우 1주당 가격을 공란으로 비우지 않음 "0"으로 입력
        ctac_tlno (str): " "
        mgco_aptm_odno (str): " "
        ord_svr_dvsn_cd (str): "0"
        ord_dvsn (str): [미국 매수/매도 주문]  00 : 지정가  * 주간거래는 지정가만 가능
        
    Returns:
        Optional[pd.DataFrame]: 해외주식 미국주간주문 데이터
        
    Example:
        >>> df = daytime_order(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ovrs_excg_cd="NASD",
        ...     pdno="AAPL",
        ...     ord_qty="10",
        ...     ovrs_ord_unpr="150.00",
        ...     ctac_tlno="01012345678",
        ...     mgco_aptm_odno="",
        ...     ord_svr_dvsn_cd="0",
        ...     ord_dvsn="00"
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
    if not ovrs_excg_cd:
        logger.error("ovrs_excg_cd is required. (e.g. 'NASD')")
        raise ValueError("ovrs_excg_cd is required. (e.g. 'NASD')")
    if not pdno:
        logger.error("pdno is required. (e.g. 'AAPL')")
        raise ValueError("pdno is required. (e.g. 'AAPL')")
    if not ord_qty:
        logger.error("ord_qty is required. (e.g. '10')")
        raise ValueError("ord_qty is required. (e.g. '10')")
    if not ovrs_ord_unpr:
        logger.error("ovrs_ord_unpr is required. (e.g. '150.00')")
        raise ValueError("ovrs_ord_unpr is required. (e.g. '150.00')")
    if not ord_svr_dvsn_cd:
        logger.error("ord_svr_dvsn_cd is required. (e.g. '0')")
        raise ValueError("ord_svr_dvsn_cd is required. (e.g. '0')")
    if not ord_dvsn:
        logger.error("ord_dvsn is required. (e.g. '00')")
        raise ValueError("ord_dvsn is required. (e.g. '00')")

    if order_dv == "buy":
        api_url = "/uapi/overseas-stock/v1/trading/daytime-order"

        tr_id = "TTTS6036U"
    elif order_dv == "sell":
        tr_id = "TTTS6037U"
    else:
        logger.error("Invalid order_dv. (e.g. 'buy' or 'sell')")
        raise ValueError("Invalid order_dv. (e.g. 'buy' or 'sell')")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "PDNO": pdno,
        "ORD_QTY": ord_qty,
        "OVRS_ORD_UNPR": ovrs_ord_unpr,
        "CTAC_TLNO": ctac_tlno,
        "MGCO_APTM_ODNO": mgco_aptm_odno,
        "ORD_SVR_DVSN_CD": ord_svr_dvsn_cd,
        "ORD_DVSN": ord_dvsn,
    }

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
# [해외주식] 주문/계좌 > 해외주식 미국주간정정취소 [v1_해외주식-027]
##############################################################################################

def daytime_order_rvsecncl(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ovrs_excg_cd: str,  # 해외거래소코드
    pdno: str,  # 상품번호
    orgn_odno: str,  # 원주문번호
    rvse_cncl_dvsn_cd: str,  # 정정취소구분코드
    ord_qty: str,  # 주문수량
    ovrs_ord_unpr: str,  # 해외주문단가
    ctac_tlno: str,  # 연락전화번호
    mgco_aptm_odno: str,  # 운용사지정주문번호
    ord_svr_dvsn_cd: str,  # 주문서버구분코드

) -> Optional[pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 미국주간정정취소[v1_해외주식-027]
    해외주식 미국주간정정취소 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ovrs_excg_cd (str): NASD:나스닥 / NYSE:뉴욕 / AMEX:아멕스
        pdno (str): 종목코드
        orgn_odno (str): 정정 또는 취소할 원주문번호
        rvse_cncl_dvsn_cd (str): 01 : 정정, 02 : 취소
        ord_qty (str): 주문수량
        ovrs_ord_unpr (str): 소수점 포함, 1주당 가격
        ctac_tlno (str): 연락전화번호
        mgco_aptm_odno (str): 운용사지정주문번호
        ord_svr_dvsn_cd (str): 주문서버구분코드
        
    Returns:
        Optional[pd.DataFrame]: 해외주식 미국주간정정취소 데이터
        
    Example:
        >>> df = daytime_order_rvsecncl(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ovrs_excg_cd="NASD",
        ...     pdno="AAPL",
        ...     orgn_odno="1234567890",
        ...     rvse_cncl_dvsn_cd="01",
        ...     ord_qty="100",
        ...     ovrs_ord_unpr="150.00",
        ...     ctac_tlno="01012345678",
        ...     mgco_aptm_odno="000000000001",
        ...     ord_svr_dvsn_cd="0"
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
    if not ovrs_excg_cd:
        logger.error("ovrs_excg_cd is required. (e.g. 'NASD')")
        raise ValueError("ovrs_excg_cd is required. (e.g. 'NASD')")
    if not pdno:
        logger.error("pdno is required. (e.g. 'AAPL')")
        raise ValueError("pdno is required. (e.g. 'AAPL')")
    if not orgn_odno:
        logger.error("orgn_odno is required. (e.g. '1234567890')")
        raise ValueError("orgn_odno is required. (e.g. '1234567890')")
    if rvse_cncl_dvsn_cd not in ["01", "02"]:
        logger.error("rvse_cncl_dvsn_cd is required. (e.g. '01' or '02')")
        raise ValueError("rvse_cncl_dvsn_cd is required. (e.g. '01' or '02')")
    if not ord_qty:
        logger.error("ord_qty is required. (e.g. '100')")
        raise ValueError("ord_qty is required. (e.g. '100')")
    if not ovrs_ord_unpr:
        logger.error("ovrs_ord_unpr is required. (e.g. '150.00')")
        raise ValueError("ovrs_ord_unpr is required. (e.g. '150.00')")
    if not ord_svr_dvsn_cd:
        logger.error("ord_svr_dvsn_cd is required. (e.g. '0')")
        raise ValueError("ord_svr_dvsn_cd is required. (e.g. '0')")

    api_url = "/uapi/overseas-stock/v1/trading/daytime-order-rvsecncl"


    tr_id = "TTTS6038U"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "PDNO": pdno,
        "ORGN_ODNO": orgn_odno,
        "RVSE_CNCL_DVSN_CD": rvse_cncl_dvsn_cd,
        "ORD_QTY": ord_qty,
        "OVRS_ORD_UNPR": ovrs_ord_unpr,
        "CTAC_TLNO": ctac_tlno,
        "MGCO_APTM_ODNO": mgco_aptm_odno,
        "ORD_SVR_DVSN_CD": ord_svr_dvsn_cd,
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
# [해외주식] 주문/계좌 - 해외증거금 통화별조회 [해외주식-035]
##############################################################################################

def foreign_margin(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이 (기본값: 10)
) -> Optional[pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외증거금 통화별조회[해외주식-035]
    해외증거금 통화별조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 종합계좌번호 (필수)
        acnt_prdt_cd (str): 계좌상품코드 (필수)
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외증거금 통화별조회 데이터
        
    Example:
        >>> df = foreign_margin("12345678", "01")
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not cano:
        logger.error("cano is required. (e.g. '12345678')")
        raise ValueError("cano is required. (e.g. '12345678')")
    
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    api_url = "/uapi/overseas-stock/v1/trading/foreign-margin"

    
    tr_id = "TTTC2101R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
    }

    # API 호출
    res = ka._url_fetch(api_url=api_url, ptr_id=tr_id, tr_cont=tr_cont, params=params)

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
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return foreign_margin(
                cano,
                acnt_prdt_cd,
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
# [해외주식] 주문/계좌 > 해외주식 지정가체결내역조회 [해외주식-070]
##############################################################################################

def inquire_algo_ccnl(
    cano: str,  # [필수] 계좌번호
    acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 01)
    ord_dt: str = "",  # 주문일자
    ord_gno_brno: str = "",  # 주문채번지점번호
    odno: str = "",  # 주문번호 (ex. 지정가주문번호 TTTC6058R에서 조회된 주문번호 입력)
    ttlz_icld_yn: str = "",  # 집계포함여부
    NK200: str = "",  # 연속조회키200
    FK200: str = "",  # 연속조회조건200
    tr_cont: str = "",  # 연속거래여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    dataframe3: Optional[pd.DataFrame] = None,  # 누적 데이터프레임3
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    해외주식 TWAP, VWAP 주문에 대한 체결내역 조회 API로 지정가 주문번호조회 API를 수행 후 조회해야합니다
    
    Args:
        cano (str): [필수] 계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 01)
        ord_dt (str): 주문일자
        ord_gno_brno (str): 주문채번지점번호
        odno (str): 주문번호 (ex. 지정가주문번호 TTTC6058R에서 조회된 주문번호 입력)
        ttlz_icld_yn (str): 집계포함여부
        NK200 (str): 연속조회키200
        FK200 (str): 연속조회조건200
        tr_cont (str): 연속거래여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        dataframe3 (Optional[pd.DataFrame]): 누적 데이터프레임3
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output, output3) 체결내역 데이터
        
    Example:
        >>> result, result3 = inquire_algo_ccnl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod)
        >>> print(result)
        >>> print(result3)
    """

    if cano == "":
        raise ValueError("cano is required")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            dataframe = pd.DataFrame()
        if dataframe3 is None:
            dataframe3 = pd.DataFrame()
        return dataframe, dataframe3

    api_url = "/uapi/overseas-stock/v1/trading/inquire-algo-ccnl"


    tr_id = "TTTS6059R"  # 해외주식 지정가체결내역조회

    params = {
        "CANO": cano,  # 계좌번호
        "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
        "ORD_DT": ord_dt,  # 주문일자
        "ORD_GNO_BRNO": ord_gno_brno,  # 주문채번지점번호
        "ODNO": odno,  # 주문번호
        "TTLZ_ICLD_YN": ttlz_icld_yn,  # 집계포함여부
        "CTX_AREA_NK200": NK200,  # 연속조회키200
        "CTX_AREA_FK200": FK200  # 연속조회조건200
    }
    
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        current_data3 = pd.DataFrame(res.getBody().output3)
            
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data
            
        if dataframe3 is not None:
            dataframe3 = pd.concat([dataframe3, current_data3], ignore_index=True)
        else:
            dataframe3 = current_data3
            
        tr_cont = res.getHeader().tr_cont
        NK200 = res.getBody().ctx_area_nk200
        FK200 = res.getBody().ctx_area_fk200
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return inquire_algo_ccnl(
                cano, acnt_prdt_cd, ord_dt, ord_gno_brno, odno, ttlz_icld_yn, 
                NK200, FK200, "N", dataframe, dataframe3, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe, dataframe3
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 잔고 [v1_해외주식-006]
##############################################################################################

def inquire_balance(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ovrs_excg_cd: str,  # 해외거래소코드
    tr_crcy_cd: str,  # 거래통화코드
    FK200: str,  # 연속조회검색조건200
    NK200: str,  # 연속조회키200
    env_dv: str = "real",  # 실전모의구분
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 잔고[v1_해외주식-006]
    해외주식 잔고 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ovrs_excg_cd (str): [모의] NASD : 나스닥 NYSE : 뉴욕  AMEX : 아멕스  [실전] NASD : 미국전체 NAS : 나스닥 NYSE : 뉴욕  AMEX : 아멕스  [모의/실전 공통] SEHK : 홍콩 SHAA : 중국상해 SZAA : 중국심천 TKSE : 일본 HASE : 베트남 하노이 VNSE : 베트남 호치민
        tr_crcy_cd (str): USD : 미국달러 HKD : 홍콩달러 CNY : 중국위안화 JPY : 일본엔화 VND : 베트남동
        FK200 (str): 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK200값 : 다음페이지 조회시(2번째부터)
        NK200 (str): 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK200값 : 다음페이지 조회시(2번째부터)
        env_dv (str): 실전모의구분 (real:실전, demo:모의)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식 잔고 데이터
        
    Example:
        >>> df1, df2 = inquire_balance(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ovrs_excg_cd="NASD",
        ...     tr_crcy_cd="USD",
        ...     FK200="",
        ...     NK200=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '810XXXXX')")
        raise ValueError("cano is required. (e.g. '810XXXXX')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")
    if not ovrs_excg_cd:
        logger.error("ovrs_excg_cd is required. (e.g. 'NASD')")
        raise ValueError("ovrs_excg_cd is required. (e.g. 'NASD')")
    if not tr_crcy_cd:
        logger.error("tr_crcy_cd is required. (e.g. 'USD')")
        raise ValueError("tr_crcy_cd is required. (e.g. 'USD')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real":
        api_url = "/uapi/overseas-stock/v1/trading/inquire-balance"

        tr_id = "TTTS3012R"  # 실전투자용 TR ID
    elif env_dv == "demo":
        tr_id = "VTTS3012R"  # 모의투자용 TR ID
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "TR_CRCY_CD": tr_crcy_cd,
        "CTX_AREA_FK200": FK200,
        "CTX_AREA_NK200": NK200,
    }

    res = ka._url_fetch(api_url=api_url, ptr_id=tr_id, tr_cont=tr_cont, params=params)

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
        tr_cont, FK200, NK200 = res.getHeader().tr_cont, res.getBody().ctx_area_fk200, res.getBody().ctx_area_nk200
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_balance(
                cano,
                acnt_prdt_cd,
                ovrs_excg_cd,
                tr_crcy_cd,
                FK200,
                NK200,
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
# [해외주식] 주문/계좌 > 해외주식 주문체결내역 [v1_해외주식-007]
##############################################################################################

def inquire_ccnl(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    pdno: str,  # 상품번호
    ord_strt_dt: str,  # 주문시작일자
    ord_end_dt: str,  # 주문종료일자
    sll_buy_dvsn: str,  # 매도매수구분
    ccld_nccs_dvsn: str,  # 체결미체결구분
    ovrs_excg_cd: str,  # 해외거래소코드
    sort_sqn: str,  # 정렬순서
    ord_dt: str,  # 주문일자
    ord_gno_brno: str,  # 주문채번지점번호
    odno: str,  # 주문번호
    NK200: str,  # 연속조회키200
    FK200: str,  # 연속조회검색조건200
    env_dv: str = "real",  # 실전모의구분
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 주문체결내역[v1_해외주식-007]
    해외주식 주문체결내역 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        pdno (str): 전종목일 경우 "%" 입력 ※ 모의투자계좌의 경우 ""(전체 조회)만 가능
        ord_strt_dt (str): YYYYMMDD 형식 (현지시각 기준)
        ord_end_dt (str): YYYYMMDD 형식 (현지시각 기준)
        sll_buy_dvsn (str): 00 : 전체  01 : 매도  02 : 매수 ※ 모의투자계좌의 경우 "00"(전체 조회)만 가능
        ccld_nccs_dvsn (str): 00 : 전체  01 : 체결  02 : 미체결 ※ 모의투자계좌의 경우 "00"(전체 조회)만 가능
        ovrs_excg_cd (str): 전종목일 경우 "%" 입력 NASD : 미국시장 전체(나스닥, 뉴욕, 아멕스) NYSE : 뉴욕 AMEX : 아멕스 SEHK : 홍콩  SHAA : 중국상해 SZAA : 중국심천 TKSE : 일본 HASE : 베트남 하노이 VNSE : 베트남 호치민 ※ 모의투자계좌의 경우 ""(전체 조회)만 가능
        sort_sqn (str): DS : 정순 AS : 역순  ※ 모의투자계좌의 경우 정렬순서 사용불가(Default : DS(정순))
        ord_dt (str): "" (Null 값 설정)
        ord_gno_brno (str): "" (Null 값 설정)
        odno (str): "" (Null 값 설정) ※ 주문번호로 검색 불가능합니다. 반드시 ""(Null 값 설정) 바랍니다.
        NK200 (str): 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK200값 : 다음페이지 조회시(2번째부터)
        FK200 (str): 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK200값 : 다음페이지 조회시(2번째부터)
        env_dv (str): 실전모의구분 (real:실전, demo:모의)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외주식 주문체결내역 데이터
        
    Example:
        >>> df = inquire_ccnl(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     pdno="%",
        ...     ord_strt_dt="20211027",
        ...     ord_end_dt="20211027",
        ...     sll_buy_dvsn="00",
        ...     ccld_nccs_dvsn="00",
        ...     ovrs_excg_cd="%",
        ...     sort_sqn="DS",
        ...     ord_dt="",
        ...     ord_gno_brno="02111",
        ...     odno="",
        ...     NK200="",
        ...     FK200=""
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '810XXXXX')")
        raise ValueError("cano is required. (e.g. '810XXXXX')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")
    if not ord_strt_dt:
        logger.error("ord_strt_dt is required. (e.g. '20211027')")
        raise ValueError("ord_strt_dt is required. (e.g. '20211027')")
    if not ord_end_dt:
        logger.error("ord_end_dt is required. (e.g. '20211027')")
        raise ValueError("ord_end_dt is required. (e.g. '20211027')")
    if not sll_buy_dvsn:
        logger.error("sll_buy_dvsn is required. (e.g. '00')")
        raise ValueError("sll_buy_dvsn is required. (e.g. '00')")
    if not ccld_nccs_dvsn:
        logger.error("ccld_nccs_dvsn is required. (e.g. '00')")
        raise ValueError("ccld_nccs_dvsn is required. (e.g. '00')")
    if not ovrs_excg_cd:
        logger.error("ovrs_excg_cd is required. (e.g. 'NASD')")
        raise ValueError("ovrs_excg_cd is required. (e.g. 'NASD')")
    if not sort_sqn:
        logger.error("sort_sqn is required. (e.g. 'DS')")
        raise ValueError("sort_sqn is required. (e.g. 'DS')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real":
        api_url = "/uapi/overseas-stock/v1/trading/inquire-ccnl"

        tr_id = "TTTS3035R"  # 실전투자용 TR ID
    elif env_dv == "demo":
        tr_id = "VTTS3035R"  # 모의투자용 TR ID
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "ORD_STRT_DT": ord_strt_dt,
        "ORD_END_DT": ord_end_dt,
        "SLL_BUY_DVSN": sll_buy_dvsn,
        "CCLD_NCCS_DVSN": ccld_nccs_dvsn,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "SORT_SQN": sort_sqn,
        "ORD_DT": ord_dt,
        "ORD_GNO_BRNO": ord_gno_brno,
        "ODNO": odno,
        "CTX_AREA_NK200": NK200,
        "CTX_AREA_FK200": FK200,
    }

    res = ka._url_fetch(api_url=api_url, ptr_id=tr_id, tr_cont=tr_cont, params=params)

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
            
        tr_cont, NK200, FK200 = res.getHeader().tr_cont, res.getBody().ctx_area_nk200, res.getBody().ctx_area_fk200
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_ccnl(
                cano,
                acnt_prdt_cd,
                pdno,
                ord_strt_dt,
                ord_end_dt,
                sll_buy_dvsn,
                ccld_nccs_dvsn,
                ovrs_excg_cd,
                sort_sqn,
                ord_dt,
                ord_gno_brno,
                odno,
                NK200,
                FK200,
                env_dv,
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
# [해외주식] 주문/계좌 > 해외주식 미체결내역 [v1_해외주식-005]
##############################################################################################

def inquire_nccs(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ovrs_excg_cd: str,  # 해외거래소코드
    sort_sqn: str,  # 정렬순서
    FK200: str,  # 연속조회검색조건200
    NK200: str,  # 연속조회키200
    env_dv: str = "real",  # 실전모의구분
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 미체결내역[v1_해외주식-005]
    해외주식 미체결내역 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ovrs_excg_cd (str): NASD : 나스닥 NYSE : 뉴욕  AMEX : 아멕스 SEHK : 홍콩 SHAA : 중국상해 SZAA : 중국심천 TKSE : 일본 HASE : 베트남 하노이 VNSE : 베트남 호치민  * NASD 인 경우만 미국전체로 조회되며 나머지 거래소 코드는 해당 거래소만 조회됨 * 공백 입력 시 다음조회가 불가능하므로, 반드시 거래소코드 입력해야 함
        sort_sqn (str): DS : 정순 그외 : 역순  [header tr_id: TTTS3018R] ""(공란)
        FK200 (str): 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK200값 : 다음페이지 조회시(2번째부터)
        NK200 (str): 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK200값 : 다음페이지 조회시(2번째부터)
        env_dv (str): 실전모의구분 (real:실전, demo:모의)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외주식 미체결내역 데이터
        
    Example:
        >>> df = inquire_nccs(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ovrs_excg_cd="NYSE",
        ...     sort_sqn="DS",
        ...     FK200="",
        ...     NK200=""
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '810XXXXX')")
        raise ValueError("cano is required. (e.g. '810XXXXX')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")
    if not ovrs_excg_cd:
        logger.error("ovrs_excg_cd is required. (e.g. 'NYSE')")
        raise ValueError("ovrs_excg_cd is required. (e.g. 'NYSE')")
    if not sort_sqn:
        logger.error("sort_sqn is required. (e.g. 'DS')")
        raise ValueError("sort_sqn is required. (e.g. 'DS')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    api_url = "/uapi/overseas-stock/v1/trading/inquire-nccs"

    
    tr_id = "TTTS3018R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "SORT_SQN": sort_sqn,
        "CTX_AREA_FK200": FK200,
        "CTX_AREA_NK200": NK200,
    }

    res = ka._url_fetch(api_url=api_url, ptr_id=tr_id, tr_cont=tr_cont, params=params)

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
            
        tr_cont, NK200, FK200 = res.getHeader().tr_cont, res.getBody().ctx_area_nk200, res.getBody().ctx_area_fk200
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_nccs(
                cano=cano,
                acnt_prdt_cd=acnt_prdt_cd,
                ovrs_excg_cd=ovrs_excg_cd,
                sort_sqn=sort_sqn,
                FK200=FK200,
                NK200=NK200,
                env_dv=env_dv,
                tr_cont="N",
                dataframe=dataframe,
                depth=depth + 1,
                max_depth=max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        # 이미 수집된 데이터가 있으면 그것을 반환, 없으면 빈 DataFrame 반환
        if dataframe is not None and not dataframe.empty:
            logger.info("Returning already collected data due to API error.")
            return dataframe
        else:
            return pd.DataFrame()

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 결제기준잔고 [해외주식-064]
##############################################################################################

def inquire_paymt_stdr_balance(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    bass_dt: str,  # 기준일자
    wcrc_frcr_dvsn_cd: str,  # 원화외화구분코드
    inqr_dvsn_cd: str,  # 조회구분코드
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    dataframe3: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output3)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 결제기준잔고[해외주식-064]
    해외주식 결제기준잔고 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 종합계좌번호
        acnt_prdt_cd (str): 계좌상품코드
        bass_dt (str): 기준일자
        wcrc_frcr_dvsn_cd (str): 원화외화구분코드 (01: 원화기준, 02: 외화기준)
        inqr_dvsn_cd (str): 조회구분코드 (00: 전체, 01: 일반, 02: 미니스탁)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        dataframe3 (Optional[pd.DataFrame]): 누적 데이터프레임 (output3)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: 해외주식 결제기준잔고 데이터
        
    Example:
        >>> df1, df2, df3 = inquire_paymt_stdr_balance(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     bass_dt="20230630",
        ...     wcrc_frcr_dvsn_cd="01",
        ...     inqr_dvsn_cd="00"
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '12345678')")
        raise ValueError("cano is required. (e.g. '12345678')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")
    if not bass_dt:
        logger.error("bass_dt is required. (e.g. '20230630')")
        raise ValueError("bass_dt is required. (e.g. '20230630')")
    if not wcrc_frcr_dvsn_cd:
        logger.error("wcrc_frcr_dvsn_cd is required. (e.g. '01')")
        raise ValueError("wcrc_frcr_dvsn_cd is required. (e.g. '01')")
    if not inqr_dvsn_cd:
        logger.error("inqr_dvsn_cd is required. (e.g. '00')")
        raise ValueError("inqr_dvsn_cd is required. (e.g. '00')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame(), dataframe3 if dataframe3 is not None else pd.DataFrame()
    
    api_url = "/uapi/overseas-stock/v1/trading/inquire-paymt-stdr-balance"

    
    tr_id = "CTRP6010R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "BASS_DT": bass_dt,
        "WCRC_FRCR_DVSN_CD": wcrc_frcr_dvsn_cd,
        "INQR_DVSN_CD": inqr_dvsn_cd,
    }

    res = ka._url_fetch(api_url=api_url, ptr_id=tr_id, tr_cont=tr_cont, params=params)

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
        # output3 처리
        if hasattr(res.getBody(), 'output3'):
            output_data = res.getBody().output3
            if output_data:
                # output1은 단일 객체, output2는 배열일 수 있음
                if isinstance(output_data, list):
                    current_data3 = pd.DataFrame(output_data)
                else:
                    # 단일 객체인 경우 리스트로 감싸서 DataFrame 생성
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
            return inquire_paymt_stdr_balance(
                cano=cano,
                acnt_prdt_cd=acnt_prdt_cd,
                bass_dt=bass_dt,
                wcrc_frcr_dvsn_cd=wcrc_frcr_dvsn_cd,
                inqr_dvsn_cd=inqr_dvsn_cd,
                dataframe1=dataframe1,
                dataframe2=dataframe2,
                dataframe3=dataframe3,
                tr_cont="N",
                depth=depth + 1,
                max_depth=max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2, dataframe3
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        # 이미 수집된 데이터가 있으면 그것을 반환, 없으면 빈 DataFrame 반환
        if dataframe1 is not None and not dataframe1.empty:
            logger.info("Returning already collected data due to API error.")
            return dataframe1, dataframe2 if dataframe2 is not None else pd.DataFrame(), dataframe3 if dataframe3 is not None else pd.DataFrame()
        else:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 기간손익 [v1_해외주식-032]
##############################################################################################

def inquire_period_profit(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ovrs_excg_cd: str,  # 해외거래소코드
    natn_cd: str,  # 국가코드
    crcy_cd: str,  # 통화코드
    pdno: str,  # 상품번호
    inqr_strt_dt: str,  # 조회시작일자
    inqr_end_dt: str,  # 조회종료일자
    wcrc_frcr_dvsn_cd: str,  # 원화외화구분코드
    FK200: str,  # 연속조회검색조건200
    NK200: str,  # 연속조회키200
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 기간손익[v1_해외주식-032]
    해외주식 기간손익 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ovrs_excg_cd (str): 공란 : 전체,  NASD : 미국, SEHK : 홍콩, SHAA : 중국, TKSE : 일본, HASE : 베트남
        natn_cd (str): 공란(Default)
        crcy_cd (str): 공란 : 전체 USD : 미국달러, HKD : 홍콩달러, CNY : 중국위안화,  JPY : 일본엔화, VND : 베트남동
        pdno (str): 공란 : 전체
        inqr_strt_dt (str): YYYYMMDD
        inqr_end_dt (str): YYYYMMDD
        wcrc_frcr_dvsn_cd (str): 01 : 외화, 02 : 원화
        FK200 (str): 연속조회검색조건200
        NK200 (str): 연속조회키200
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식 기간손익 데이터
        
    Example:
        >>> df1, df2 = inquire_period_profit(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ovrs_excg_cd="NASD",
        ...     natn_cd="",
        ...     crcy_cd="USD",
        ...     pdno="",
        ...     inqr_strt_dt="20230101",
        ...     inqr_end_dt="20231231",
        ...     wcrc_frcr_dvsn_cd="01",
        ...     FK200="",
        ...     NK200=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '12345678')")
        raise ValueError("cano is required. (e.g. '12345678')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")
    if not ovrs_excg_cd:
        logger.error("ovrs_excg_cd is required. (e.g. 'NASD')")
        raise ValueError("ovrs_excg_cd is required. (e.g. 'NASD')")
    if not crcy_cd:
        logger.error("crcy_cd is required. (e.g. 'USD')")
        raise ValueError("crcy_cd is required. (e.g. 'USD')")
    if not inqr_strt_dt:
        logger.error("inqr_strt_dt is required. (e.g. '20230101')")
        raise ValueError("inqr_strt_dt is required. (e.g. '20230101')")
    if not inqr_end_dt:
        logger.error("inqr_end_dt is required. (e.g. '20231231')")
        raise ValueError("inqr_end_dt is required. (e.g. '20231231')")
    if not wcrc_frcr_dvsn_cd:
        logger.error("wcrc_frcr_dvsn_cd is required. (e.g. '01')")
        raise ValueError("wcrc_frcr_dvsn_cd is required. (e.g. '01')")


    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    api_url = "/uapi/overseas-stock/v1/trading/inquire-period-profit"

    
    tr_id = "TTTS3039R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "NATN_CD": natn_cd,
        "CRCY_CD": crcy_cd,
        "PDNO": pdno,
        "INQR_STRT_DT": inqr_strt_dt,
        "INQR_END_DT": inqr_end_dt,
        "WCRC_FRCR_DVSN_CD": wcrc_frcr_dvsn_cd,
        "CTX_AREA_FK200": FK200,
        "CTX_AREA_NK200": NK200,
    }

    res = ka._url_fetch(api_url=api_url, ptr_id=tr_id, tr_cont=tr_cont, params=params)

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
        
        tr_cont, NK200, FK200 = res.getHeader().tr_cont, res.getBody().ctx_area_nk200, res.getBody().ctx_area_fk200
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_period_profit(
                cano=cano,
                acnt_prdt_cd=acnt_prdt_cd,
                ovrs_excg_cd=ovrs_excg_cd,
                natn_cd=natn_cd,
                crcy_cd=crcy_cd,
                pdno=pdno,
                inqr_strt_dt=inqr_strt_dt,
                inqr_end_dt=inqr_end_dt,
                wcrc_frcr_dvsn_cd=wcrc_frcr_dvsn_cd,
                FK200=FK200,
                NK200=NK200,
                dataframe1=dataframe1,
                dataframe2=dataframe2,
                tr_cont="N",
                depth=depth + 1,
                max_depth=max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        # 이미 수집된 데이터가 있으면 그것을 반환, 없으면 빈 DataFrame 반환
        if dataframe1 is not None and not dataframe1.empty:
            logger.info("Returning already collected data due to API error.")
            return dataframe1, dataframe2 if dataframe2 is not None else pd.DataFrame()
        else:
            return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 일별거래내역 [해외주식-063]
##############################################################################################

def inquire_period_trans(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    erlm_strt_dt: str,  # 등록시작일자
    erlm_end_dt: str,  # 등록종료일자
    ovrs_excg_cd: str,  # 해외거래소코드
    pdno: str,  # 상품번호
    sll_buy_dvsn_cd: str,  # 매도매수구분코드
    loan_dvsn_cd: str,  # 대출구분코드
    FK100: str,  # 연속조회검색조건100
    NK100: str,  # 연속조회키100
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 일별거래내역[해외주식-063]
    해외주식 일별거래내역 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 종합계좌번호
        acnt_prdt_cd (str): 계좌상품코드
        erlm_strt_dt (str): 등록시작일자 (예: 20240420)
        erlm_end_dt (str): 등록종료일자 (예: 20240520)
        ovrs_excg_cd (str): 해외거래소코드
        pdno (str): 상품번호
        sll_buy_dvsn_cd (str): 매도매수구분코드 (00: 전체, 01: 매도, 02: 매수)
        loan_dvsn_cd (str): 대출구분코드
        FK100 (str): 연속조회검색조건100
        NK100 (str): 연속조회키100
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식 일별거래내역 데이터
        
    Example:
        >>> df1, df2 = inquire_period_trans(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     erlm_strt_dt="20240420",
        ...     erlm_end_dt="20240520",
        ...     ovrs_excg_cd="NAS",
        ...     pdno="",
        ...     sll_buy_dvsn_cd="00",
        ...     loan_dvsn_cd="",
        ...     FK100="",
        ...     NK100=""
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '12345678')")
        raise ValueError("cano is required. (e.g. '12345678')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")
    if not erlm_strt_dt:
        logger.error("erlm_strt_dt is required. (e.g. '20240420')")
        raise ValueError("erlm_strt_dt is required. (e.g. '20240420')")
    if not erlm_end_dt:
        logger.error("erlm_end_dt is required. (e.g. '20240520')")
        raise ValueError("erlm_end_dt is required. (e.g. '20240520')")
    if not ovrs_excg_cd:
        logger.error("ovrs_excg_cd is required. (e.g. 'NAS')")
        raise ValueError("ovrs_excg_cd is required. (e.g. 'NAS')")
    if not sll_buy_dvsn_cd:
        logger.error("sll_buy_dvsn_cd is required. (e.g. '00')")
        raise ValueError("sll_buy_dvsn_cd is required. (e.g. '00')")

    
    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()
    
    api_url = "/uapi/overseas-stock/v1/trading/inquire-period-trans"

    
    tr_id = "CTOS4001R"

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "ERLM_STRT_DT": erlm_strt_dt,
        "ERLM_END_DT": erlm_end_dt,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "PDNO": pdno,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "LOAN_DVSN_CD": loan_dvsn_cd,
        "CTX_AREA_FK100": FK100,
        "CTX_AREA_NK100": NK100,
    }

    res = ka._url_fetch(api_url=api_url, ptr_id=tr_id, tr_cont=tr_cont, params=params)

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
        
        tr_cont, NK100, FK100 = res.getHeader().tr_cont, res.getBody().ctx_area_nk100, res.getBody().ctx_area_fk100
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_period_trans(
                cano=cano,
                acnt_prdt_cd=acnt_prdt_cd,
                erlm_strt_dt=erlm_strt_dt,
                erlm_end_dt=erlm_end_dt,
                ovrs_excg_cd=ovrs_excg_cd,
                pdno=pdno,
                sll_buy_dvsn_cd=sll_buy_dvsn_cd,
                loan_dvsn_cd=loan_dvsn_cd,
                FK100=FK100,
                NK100=NK100,
                dataframe1=dataframe1,
                dataframe2=dataframe2,
                tr_cont="N",
                depth=depth + 1,
                max_depth=max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        # 이미 수집된 데이터가 있으면 그것을 반환, 없으면 빈 DataFrame 반환
        if dataframe1 is not None and not dataframe1.empty:
            logger.info("Returning already collected data due to API error.")
            return dataframe1, dataframe2 if dataframe2 is not None else pd.DataFrame()
        else:
            return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 체결기준현재잔고 [v1_해외주식-008]
##############################################################################################

def inquire_present_balance(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    wcrc_frcr_dvsn_cd: str,  # 원화외화구분코드
    natn_cd: str,  # 국가코드
    tr_mket_cd: str,  # 거래시장코드
    inqr_dvsn_cd: str,  # 조회구분코드
    env_dv: str = "real",  # 실전모의구분
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    dataframe3: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output3)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 체결기준현재잔고[v1_해외주식-008]
    해외주식 체결기준현재잔고 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        wcrc_frcr_dvsn_cd (str): 01 : 원화  02 : 외화
        natn_cd (str): 000 전체 840 미국 344 홍콩 156 중국 392 일본 704 베트남
        tr_mket_cd (str): [Request body NATN_CD 000 설정] 00 : 전체  [Request body NATN_CD 840 설정] 00 : 전체 01 : 나스닥(NASD) 02 : 뉴욕거래소(NYSE) 03 : 미국(PINK SHEETS) 04 : 미국(OTCBB) 05 : 아멕스(AMEX)  [Request body NATN_CD 156 설정] 00 : 전체 01 : 상해B 02 : 심천B 03 : 상해A 04 : 심천A  [Request body NATN_CD 392 설정] 01 : 일본  [Request body NATN_CD 704 설정] 01 : 하노이거래 02 : 호치민거래소  [Request body NATN_CD 344 설정] 01 : 홍콩 02 : 홍콩CNY 03 : 홍콩USD
        inqr_dvsn_cd (str): 00 : 전체  01 : 일반해외주식  02 : 미니스탁
        env_dv (str): 실전모의구분 (real:실전, demo:모의)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        dataframe3 (Optional[pd.DataFrame]): 누적 데이터프레임 (output3)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: 해외주식 체결기준현재잔고 데이터
        
    Example:
        >>> df1, df2, df3 = inquire_present_balance(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     wcrc_frcr_dvsn_cd="01",
        ...     natn_cd="000",
        ...     tr_mket_cd="00",
        ...     inqr_dvsn_cd="00"
        ... )
        >>> print(df1)
        >>> print(df2)
        >>> print(df3)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '810XXXXX')")
        raise ValueError("cano is required. (e.g. '810XXXXX')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")
    if not wcrc_frcr_dvsn_cd:
        logger.error("wcrc_frcr_dvsn_cd is required. (e.g. '01')")
        raise ValueError("wcrc_frcr_dvsn_cd is required. (e.g. '01')")
    if not natn_cd:
        logger.error("natn_cd is required. (e.g. '000')")
        raise ValueError("natn_cd is required. (e.g. '000')")
    if not tr_mket_cd:
        logger.error("tr_mket_cd is required. (e.g. '00')")
        raise ValueError("tr_mket_cd is required. (e.g. '00')")
    if not inqr_dvsn_cd:
        logger.error("inqr_dvsn_cd is required. (e.g. '00')")
        raise ValueError("inqr_dvsn_cd is required. (e.g. '00')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame(), dataframe3 if dataframe3 is not None else pd.DataFrame()
    
    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real":
        api_url = "/uapi/overseas-stock/v1/trading/inquire-present-balance"

        tr_id = "CTRP6504R"  # 실전투자용 TR ID
    elif env_dv == "demo":
        tr_id = "VTRP6504R"  # 모의투자용 TR ID
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "WCRC_FRCR_DVSN_CD": wcrc_frcr_dvsn_cd,
        "NATN_CD": natn_cd,
        "TR_MKET_CD": tr_mket_cd,
        "INQR_DVSN_CD": inqr_dvsn_cd,
    }

    res = ka._url_fetch(api_url=api_url, ptr_id=tr_id, tr_cont=tr_cont, params=params)

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
            return inquire_present_balance(
                cano=cano,
                acnt_prdt_cd=acnt_prdt_cd,
                wcrc_frcr_dvsn_cd=wcrc_frcr_dvsn_cd,
                natn_cd=natn_cd,
                tr_mket_cd=tr_mket_cd,
                inqr_dvsn_cd=inqr_dvsn_cd,
                env_dv=env_dv,
                dataframe1=dataframe1,
                dataframe2=dataframe2,
                dataframe3=dataframe3,
                tr_cont="N",
                depth=depth + 1,
                max_depth=max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2, dataframe3
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        # 이미 수집된 데이터가 있으면 그것을 반환, 없으면 빈 DataFrame 반환
        if dataframe1 is not None and not dataframe1.empty:
            logger.info("Returning already collected data due to API error.")
            return dataframe1, dataframe2 if dataframe2 is not None else pd.DataFrame(), dataframe3 if dataframe3 is not None else pd.DataFrame()
        else:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 매수가능금액조회 [해외주식-014]
##############################################################################################

def inquire_psamount(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ovrs_excg_cd: str,  # 해외거래소코드
    ovrs_ord_unpr: str,  # 해외주문단가
    item_cd: str,  # 종목코드
    env_dv: str = "real",  # 실전모의구분
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 매수가능금액조회[v1_해외주식-014]
    해외주식 매수가능금액조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ovrs_excg_cd (str): NASD : 나스닥 / NYSE : 뉴욕 / AMEX : 아멕스 SEHK : 홍콩 / SHAA : 중국상해 / SZAA : 중국심천 TKSE : 일본 / HASE : 하노이거래소 / VNSE : 호치민거래소
        ovrs_ord_unpr (str): 해외주문단가 (23.8) 정수부분 23자리, 소수부분 8자리
        item_cd (str): 종목코드
        env_dv (str): 실전모의구분 (real:실전, demo:모의)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 해외주식 매수가능금액조회 데이터
        
    Example:
        >>> df = inquire_psamount(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ovrs_excg_cd="NASD",
        ...     ovrs_ord_unpr="1.4",
        ...     item_cd="QQQ"
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '81019777')")
        raise ValueError("cano is required. (e.g. '81019777')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")
    if not ovrs_excg_cd:
        logger.error("ovrs_excg_cd is required. (e.g. 'NASD')")
        raise ValueError("ovrs_excg_cd is required. (e.g. 'NASD')")
    if not ovrs_ord_unpr:
        logger.error("ovrs_ord_unpr is required. (e.g. '1.4')")
        raise ValueError("ovrs_ord_unpr is required. (e.g. '1.4')")
    if not item_cd:
        logger.error("item_cd is required. (e.g. 'QQQ')")
        raise ValueError("item_cd is required. (e.g. 'QQQ')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real":
        api_url = "/uapi/overseas-stock/v1/trading/inquire-psamount"

        tr_id = "TTTS3007R"  # 실전투자용 TR ID
    elif env_dv == "demo":
        tr_id = "VTTS3007R"  # 모의투자용 TR ID
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "OVRS_ORD_UNPR": ovrs_ord_unpr,
        "ITEM_CD": item_cd,
    }

    res = ka._url_fetch(api_url=api_url, ptr_id=tr_id, tr_cont=tr_cont, params=params)

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
                cano=cano,
                acnt_prdt_cd=acnt_prdt_cd,
                ovrs_excg_cd=ovrs_excg_cd,
                ovrs_ord_unpr=ovrs_ord_unpr,
                item_cd=item_cd,
                env_dv=env_dv,
                tr_cont="N",
                dataframe=dataframe,
                depth=depth + 1,
                max_depth=max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame()

##############################################################################################
# [해외주식] 시세분석 > 해외주식 시가총액순위[해외주식-047]
##############################################################################################

def market_cap(
    excd: str,  # 거래소명
    vol_rang: str,  # 거래량조건
    keyb: str = "",  # NEXT KEY BUFF
    auth: str = "",  # 사용자권한정보
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 output1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 output2
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    해외주식 시가총액순위 조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        keyb (str): NEXT KEY BUFF (ex. "")
        auth (str): 사용자권한정보 (ex. "")
        tr_cont (str): 연속거래여부 (ex. "")
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 output1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 output2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 시가총액순위 데이터 (output1, output2)
        
    Example:
        >>> df1, df2 = market_cap(excd="SZS", vol_rang="1")
        >>> print(df1)
        >>> print(df2)
    """

    if excd == "":
        raise ValueError("excd is required (e.g. 'NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄')")
    
    if vol_rang == "":
        raise ValueError("vol_rang is required (e.g. '0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None or dataframe2 is None:
            return pd.DataFrame(), pd.DataFrame()
        else:
            return dataframe1, dataframe2

    api_url = "/uapi/overseas-stock/v1/ranking/market-cap"


    tr_id = "HHDFS76350100"  # 해외주식 시가총액순위

    params = {
        "EXCD": excd,  # 거래소명
        "VOL_RANG": vol_rang,  # 거래량조건
        "KEYB": keyb,  # NEXT KEY BUFF
        "AUTH": auth,  # 사용자권한정보
    }
    
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 처리
        current_data1 = pd.DataFrame(res.getBody().output1, index=[0])
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
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return market_cap(
                excd, vol_rang, keyb, auth, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외주식] 시세분석 > 해외주식 신고/신저가[해외주식-042]
##############################################################################################

def new_highlow(
    excd: str,  # [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
    mixn: str,  # [필수] N분전콤보값 (ex. 0:1분전, 1:2분전, 2:3분전, 3:5분전, 4:10분전, 5:15분전, 6:20분전, 7:30분전, 8:60분전, 9:120분전)
    vol_rang: str,  # [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
    gubn: str,  # [필수] 신고/신저 구분 (ex. 0:신저,1:신고)
    gubn2: str,  # [필수] 일시돌파/돌파 구분 (ex. 0:일시돌파0, 1:돌파유지1)
    keyb: str = "",  # NEXT KEY BUFF
    auth: str = "",  # 사용자권한정보
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 output1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 output2
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 시세분석 > 해외주식 신고/신저가[해외주식-042]
    해외주식 신고/신저가 정보를 조회하여 DataFrame으로 반환합니다.
    
    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        mixn (str): [필수] N분전콤보값 (ex. 0:1분전, 1:2분전, 2:3분전, 3:5분전, 4:10분전, 5:15분전, 6:20분전, 7:30분전, 8:60분전, 9:120분전)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        gubn (str): [필수] 신고/신저 구분 (ex. 0:신저,1:신고)
        gubn2 (str): [필수] 일시돌파/돌파 구분 (ex. 0:일시돌파0, 1:돌파유지1)
        keyb (str): NEXT KEY BUFF
        auth (str): 사용자권한정보
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 output1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 output2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> output1, output2 = new_highlow(excd="AMS", mixn="0", vol_rang="0", gubn="1", gubn2="1")
        >>> print(output1)
        >>> print(output2)
    """

    if excd == "":
        raise ValueError("excd is required (e.g. 'NYS')")
    
    if mixn == "":
        raise ValueError("mixn is required (e.g. '0')")
    
    if vol_rang == "":
        raise ValueError("vol_rang is required (e.g. '0')")
        
    if gubn == "":
        raise ValueError("gubn is required (e.g. '1')")
        
    if gubn2 == "":
        raise ValueError("gubn2 is required (e.g. '1')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    api_url = "/uapi/overseas-stock/v1/ranking/new-highlow"


    tr_id = "HHDFS76300000"  # 해외주식 신고/신저가

    params = {
        "EXCD": excd,
        "MIXN": mixn,
        "VOL_RANG": vol_rang,
        "GUBN": gubn,
        "GUBN2": gubn2,
        "KEYB": keyb,
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
            return new_highlow(
                excd, mixn, vol_rang, gubn, gubn2, keyb, auth, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 주문 [v1_해외주식-001]
##############################################################################################

def order(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ovrs_excg_cd: str,  # 해외거래소코드
    pdno: str,  # 상품번호
    ord_qty: str,  # 주문수량
    ovrs_ord_unpr: str,  # 해외주문단가
    ord_dv: str,  # 주문구분 (buy: 매수, sell: 매도)
    ctac_tlno: str,  # 연락전화번호
    mgco_aptm_odno: str,  # 운용사지정주문번호
    ord_svr_dvsn_cd: str,  # 주문서버구분코드
    ord_dvsn: str,  # 주문구분
    env_dv: str = "real",  # 실전모의구분

) -> Optional[pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 주문[v1_해외주식-001]
    해외주식 주문 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ovrs_excg_cd (str): NASD : 나스닥 NYSE : 뉴욕 AMEX : 아멕스 SEHK : 홍콩 SHAA : 중국상해 SZAA : 중국심천 TKSE : 일본 HASE : 베트남 하노이 VNSE : 베트남 호치민
        pdno (str): 종목코드
        ord_qty (str): 주문수량 (해외거래소 별 최소 주문수량 및 주문단위 확인 필요)
        ovrs_ord_unpr (str): 1주당 가격 * 시장가의 경우 1주당 가격을 공란으로 비우지 않음 "0"으로 입력
        ord_dv (str): 주문구분 (buy: 매수, sell: 매도)
        ctac_tlno (str): 
        mgco_aptm_odno (str): 
        ord_svr_dvsn_cd (str): "0"(Default)
        ord_dvsn (str): [Header tr_id TTTT1002U(미국 매수 주문)] 00 : 지정가 32 : LOO(장개시지정가) 34 : LOC(장마감지정가) * 모의투자 VTTT1002U(미국 매수 주문)로는 00:지정가만 가능  [Header tr_id TTTT1006U(미국 매도 주문)] 00 : 지정가 31 : MOO(장개시시장가) 32 : LOO(장개시지정가) 33 : MOC(장마감시장가) 34 : LOC(장마감지정가) * 모의투자 VTTT1006U(미국 매도 주문)로는 00:지정가만 가능  [Header tr_id TTTS1001U(홍콩 매도 주문)] 00 : 지정가 50 : 단주지정가 * 모의투자 VTTS1001U(홍콩 매도 주문)로는 00:지정가만 가능  [그외 tr_id] 제거
        env_dv (str): 실전모의구분 (real:실전, demo:모의)
        
    Returns:
        Optional[pd.DataFrame]: 해외주식 주문 데이터
        
    Example:
        >>> df = order(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ovrs_excg_cd="NASD",
        ...     pdno="AAPL",
        ...     ord_qty="1",
        ...     ovrs_ord_unpr="145.00",
        ...     ord_dv="buy",
        ...     ctac_tlno="",
        ...     mgco_aptm_odno="",
        ...     ord_svr_dvsn_cd="0",
        ...     ord_dvsn="00",
        ...     env_dv="real"
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '810XXXXX')")
        raise ValueError("cano is required. (e.g. '810XXXXX')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")
    if not ovrs_excg_cd:
        logger.error("ovrs_excg_cd is required. (e.g. 'NASD')")
        raise ValueError("ovrs_excg_cd is required. (e.g. 'NASD')")
    if not pdno:
        logger.error("pdno is required. (e.g. 'AAPL')")
        raise ValueError("pdno is required. (e.g. 'AAPL')")
    if not ord_qty:
        logger.error("ord_qty is required. (e.g. '1')")
        raise ValueError("ord_qty is required. (e.g. '1')")
    if not ovrs_ord_unpr:
        logger.error("ovrs_ord_unpr is required. (e.g. '145.00')")
        raise ValueError("ovrs_ord_unpr is required. (e.g. '145.00')")
    if not ord_dv:
        logger.error("ord_dv is required. (e.g. 'buy' or 'sell')")
        raise ValueError("ord_dv is required. (e.g. 'buy' or 'sell')")
    if not ord_svr_dvsn_cd:
        logger.error("ord_svr_dvsn_cd is required. (e.g. '0')")
        raise ValueError("ord_svr_dvsn_cd is required. (e.g. '0')")
    if not ord_dvsn:
        logger.error("ord_dvsn is required. (e.g. '00')")
        raise ValueError("ord_dvsn is required. (e.g. '00')")

    # TR ID 설정 (매수/매도 및 거래소별)
    if ord_dv == "buy":
        if ovrs_excg_cd in ("NASD", "NYSE", "AMEX"):
            api_url = "/uapi/overseas-stock/v1/trading/order"

            tr_id = "TTTT1002U"  # 미국 매수 주문 [모의투자] VTTT1002U
        elif ovrs_excg_cd == "SEHK":
            tr_id = "TTTS1002U"  # 홍콩 매수 주문 [모의투자] VTTS1002U
        elif ovrs_excg_cd == "SHAA":
            tr_id = "TTTS0202U"  # 중국상해 매수 주문 [모의투자] VTTS0202U
        elif ovrs_excg_cd == "SZAA":
            tr_id = "TTTS0305U"  # 중국심천 매수 주문 [모의투자] VTTS0305U
        elif ovrs_excg_cd == "TKSE":
            tr_id = "TTTS0308U"  # 일본 매수 주문 [모의투자] VTTS0308U
        elif ovrs_excg_cd in ("HASE", "VNSE"):
            tr_id = "TTTS0311U"  # 베트남(하노이,호치민) 매수 주문 [모의투자] VTTS0311U
        else:
            logger.error("ovrs_excg_cd is required. (e.g. 'NASD', 'NYSE', 'AMEX', 'SEHK', 'SHAA', 'SZAA', 'TKSE', 'HASE', 'VNSE')")
            raise ValueError("ovrs_excg_cd is required. (e.g. 'NASD', 'NYSE', 'AMEX', 'SEHK', 'SHAA', 'SZAA', 'TKSE', 'HASE', 'VNSE')")
        sll_type = ""
    elif ord_dv == "sell":
        if ovrs_excg_cd in ("NASD", "NYSE", "AMEX"):
            tr_id = "TTTT1006U"  # 미국 매도 주문 [모의투자] VTTT1006U
        elif ovrs_excg_cd == "SEHK":
            tr_id = "TTTS1001U"  # 홍콩 매도 주문 [모의투자] VTTS1001U
        elif ovrs_excg_cd == "SHAA":
            tr_id = "TTTS1005U"  # 중국상해 매도 주문 [모의투자] VTTS1005U
        elif ovrs_excg_cd == "SZAA":
            tr_id = "TTTS0304U"  # 중국심천 매도 주문 [모의투자] VTTS0304U
        elif ovrs_excg_cd == "TKSE":
            tr_id = "TTTS0307U"  # 일본 매도 주문 [모의투자] VTTS0307U
        elif ovrs_excg_cd in ("HASE", "VNSE"):
            tr_id = "TTTS0310U"  # 베트남(하노이,호치민) 매도 주문 [모의투자] VTTS0310U
        else:
            logger.error("ovrs_excg_cd is required. (e.g. 'NASD', 'NYSE', 'AMEX', 'SEHK', 'SHAA', 'SZAA', 'TKSE', 'HASE', 'VNSE')")
            raise ValueError("ovrs_excg_cd is required. (e.g. 'NASD', 'NYSE', 'AMEX', 'SEHK', 'SHAA', 'SZAA', 'TKSE', 'HASE', 'VNSE')")
        sll_type = "00"
    else:
        logger.error("ord_dv is required. (e.g. 'buy' or 'sell')")
        raise ValueError("ord_dv is required. (e.g. 'buy' or 'sell')")

    # 모의투자인 경우 TR ID 앞에 V 붙이기
    if env_dv == "demo":
        tr_id = "V" + tr_id[1:]
    elif env_dv != "real":
        logger.error("env_dv can only be 'real' or 'demo'")
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "PDNO": pdno,
        "ORD_QTY": ord_qty,
        "OVRS_ORD_UNPR": ovrs_ord_unpr,
        "CTAC_TLNO": ctac_tlno,
        "MGCO_APTM_ODNO": mgco_aptm_odno,
        "SLL_TYPE": sll_type,
        "ORD_SVR_DVSN_CD": ord_svr_dvsn_cd,
        "ORD_DVSN": ord_dvsn,
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
# [해외주식] 주문/계좌 > 해외주식 예약주문접수[v1_해외주식-002]
##############################################################################################

def order_resv(
    env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
    ord_dv: str,  # [필수] 매도매수구분 (ex. usBuy:미국매수, usSell:미국매도, asia:아시아)
    cano: str,  # [필수] 종합계좌번호 (ex. 12345678)
    acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 01)
    pdno: str,  # [필수] 상품번호
    ovrs_excg_cd: str,  # [필수] 해외거래소코드 (ex. NASD:나스닥, NYSE:뉴욕, AMEX:아멕스, SEHK:홍콩, SHAA:상해, SZAA:심천, TKSE:일본, HASE:하노이, VNSE:호치민)
    ft_ord_qty: str,  # [필수] FT주문수량
    ft_ord_unpr3: str,  # [필수] FT주문단가3
    sll_buy_dvsn_cd: Optional[str] = "",  # 매도매수구분코드 (ex. 아시아인경우만 사용, 01:매도,02:매수)
    rvse_cncl_dvsn_cd: Optional[str] = "",  # 정정취소구분코드 (ex. 아시아인경우만 사용, 00:매도/매수)
    prdt_type_cd: Optional[str] = "",  # 상품유형코드 (ex. 아시아인경우만 사용)
    ord_svr_dvsn_cd: Optional[str] = "",  # 주문서버구분코드 (ex. 0)
    rsvn_ord_rcit_dt: Optional[str] = "",  # 예약주문접수일자 (ex. 아시아인경우만 사용)
    ord_dvsn: Optional[str] = "",  # 주문구분 (ex. 미국 매수/매도인 경우만 사용)
    ovrs_rsvn_odno: Optional[str] = "",  # 해외예약주문번호 (ex. 아이사인 경우만 사용)
    algo_ord_tmd_dvsn_cd: Optional[str] = ""  # 알고리즘주문시간구분코드 (ex. TWAP, VWAP 주문에서만 사용, 02로 고정)
) -> pd.DataFrame:
    """
    미국거래소 운영시간 외 미국주식을 예약 매매하기 위한 API입니다.

    * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
    https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp

    ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)

    * 아래 각 국가의 시장별 예약주문 접수 가능 시간을 확인하시길 바랍니다.

    미국 예약주문 접수시간
    1) 10:00 ~ 23:20 / 10:00 ~ 22:20 (서머타임 시)
    2) 주문제한 : 16:30 ~ 16:45 경까지 (사유 : 시스템 정산작업시간)
    3) 23:30 정규장으로 주문 전송 (서머타임 시 22:30 정규장 주문 전송)
    4) 미국 거래소 운영시간(한국시간 기준) : 23:30 ~ 06:00 (썸머타임 적용 시 22:30 ~ 05:00)

    홍콩 예약주문 접수시간
    1) 09:00 ~ 10:20 접수, 10:30 주문전송
    2) 10:40 ~ 13:50 접수, 14:00 주문전송

    중국 예약주문 접수시간
    1) 09:00 ~ 10:20 접수, 10:30 주문전송
    2) 10:40 ~ 13:50 접수, 14:00 주문전송

    일본 예약주문 접수시간
    1) 09:10 ~ 12:20 까지 접수, 12:30 주문전송

    베트남 예약주문 접수시간
    1) 09:00 ~ 11:00 까지 접수, 11:15 주문전송
    2) 11:20 ~ 14:50 까지 접수, 15:00 주문전송

    * 예약주문 유의사항
    1) 예약주문 유효기간 : 당일
    - 미국장 마감 후, 미체결주문은 자동취소
    - 미국휴장 시, 익 영업일로 이전
    (미국예약주문화면에서 취소 가능)
    2) 증거금 및 잔고보유 : 체크 안함
    3) 주문전송 불가사유
    - 매수증거금 부족: 수수료 포함 매수금액부족, 환전, 시세이용료 출금, 인출에 의한 증거금 부족
    - 기타 매수증거금 부족, 매도가능수량 부족, 주권변경 등 권리발생으로 인한 주문불가사유 발생
    4) 지정가주문만 가능
    * 단 미국 예약매도주문(TTTT3016U)의 경우, MOO(장개시시장가)로 주문 접수 가능
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        ord_dv (str): [필수] 매도매수구분 (ex. usBuy:미국매수, usSell:미국매도, asia:아시아)
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 01)
        pdno (str): [필수] 상품번호
        ovrs_excg_cd (str): [필수] 해외거래소코드 (ex. NASD:나스닥, NYSE:뉴욕, AMEX:아멕스, SEHK:홍콩, SHAA:상해, SZAA:심천, TKSE:일본, HASE:하노이, VNSE:호치민)
        ft_ord_qty (str): [필수] FT주문수량
        ft_ord_unpr3 (str): [필수] FT주문단가3
        sll_buy_dvsn_cd (Optional[str]): 매도매수구분코드 (ex. 아시아인경우만 사용, 01:매도,02:매수)
        rvse_cncl_dvsn_cd (Optional[str]): 정정취소구분코드 (ex. 아시아인경우만 사용, 00:매도/매수)
        prdt_type_cd (Optional[str]): 상품유형코드 (ex. 아시아인경우만 사용)
        ord_svr_dvsn_cd (Optional[str]): 주문서버구분코드 (ex. 0)
        rsvn_ord_rcit_dt (Optional[str]): 예약주문접수일자 (ex. 아시아인경우만 사용)
        ord_dvsn (Optional[str]): 주문구분 (ex. 미국 매수/매도인 경우만 사용)
        ovrs_rsvn_odno (Optional[str]): 해외예약주문번호 (ex. 아이사인 경우만 사용)
        algo_ord_tmd_dvsn_cd (Optional[str]): 알고리즘주문시간구분코드 (ex. TWAP, VWAP 주문에서만 사용, 02로 고정)

    Returns:
        pd.DataFrame: 해외주식 예약주문접수 결과 데이터
        
    Example:
        >>> df = order_resv(env_dv="real", ord_dv="usBuy", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, pdno="TSLA", ovrs_excg_cd="NASD", ft_ord_qty="1", ft_ord_unpr3="900")
        >>> print(df)
    """

    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")
    
    if ord_dv == "":
        raise ValueError("ord_dv is required (e.g. 'usBuy', 'usSell', 'asia')")
    
    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '01')")
    
    if pdno == "":
        raise ValueError("pdno is required")
    
    if ovrs_excg_cd == "":
        raise ValueError("ovrs_excg_cd is required (e.g. 'NASD', 'NYSE', 'AMEX', 'SEHK', 'SHAA', 'SZAA', 'TKSE', 'HASE', 'VNSE')")
    
    if ft_ord_qty == "":
        raise ValueError("ft_ord_qty is required")
    
    if ft_ord_unpr3 == "":
        raise ValueError("ft_ord_unpr3 is required")

    # tr_id 설정
    if env_dv == "real":
        if ord_dv == "usBuy":
            api_url = "/uapi/overseas-stock/v1/trading/order-resv"

            tr_id = "TTTT3014U"
        elif ord_dv == "usSell":
            tr_id = "TTTT3016U"
        elif ord_dv == "asia":
            tr_id = "TTTS3013U"
        else:
            raise ValueError("ord_dv can only be 'usBuy', 'usSell' or 'asia'")
    elif env_dv == "demo":
        if ord_dv == "usBuy":
            tr_id = "VTTT3014U"
        elif ord_dv == "usSell":
            tr_id = "VTTT3016U"
        elif ord_dv == "asia":
            tr_id = "VTTS3013U"
        else:
            raise ValueError("ord_dv can only be 'usBuy', 'usSell' or 'asia'")
    else:
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "FT_ORD_QTY": ft_ord_qty,
        "FT_ORD_UNPR3": ft_ord_unpr3
    }
    
    # 옵션 파라미터 추가
    if sll_buy_dvsn_cd:
        params["SLL_BUY_DVSN_CD"] = sll_buy_dvsn_cd
    if rvse_cncl_dvsn_cd:
        params["RVSE_CNCL_DVSN_CD"] = rvse_cncl_dvsn_cd
    if prdt_type_cd:
        params["PRDT_TYPE_CD"] = prdt_type_cd
    if ord_svr_dvsn_cd:
        params["ORD_SVR_DVSN_CD"] = ord_svr_dvsn_cd
    if rsvn_ord_rcit_dt:
        params["RSVN_ORD_RCIT_DT"] = rsvn_ord_rcit_dt
    if ord_dvsn:
        params["ORD_DVSN"] = ord_dvsn
    if ovrs_rsvn_odno:
        params["OVRS_RSVN_ODNO"] = ovrs_rsvn_odno
    if algo_ord_tmd_dvsn_cd:
        params["ALGO_ORD_TMD_DVSN_CD"] = algo_ord_tmd_dvsn_cd
    
    res = ka._url_fetch(api_url, tr_id, "", params, postFlag=True)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output, index=[0])
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 예약주문접수취소[v1_해외주식-004]
##############################################################################################

def order_resv_ccnl(
    env_dv: str,  # [필수] 실전모의구분 (ex. real:실전, demo:모의)
    nat_dv: str,  # [필수] 국가구분 (ex. us:미국)
    cano: str,    # [필수] 종합계좌번호 (ex. 12345678)
    acnt_prdt_cd: str,  # [필수] 계좌상품코드 (ex. 01)
    rsyn_ord_rcit_dt: str,  # [필수] 해외주문접수일자
    ovrs_rsvn_odno: str     # [필수] 해외예약주문번호 (ex. 해외주식_예약주문접수 API Output ODNO(주문번호) 참고)
) -> pd.DataFrame:
    """
    접수된 미국주식 예약주문을 취소하기 위한 API입니다.
    (해외주식 예약주문접수 시 Return 받은 ODNO를 참고하여 API를 호출하세요.)

    * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
    https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp

    ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
    (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)
    
    Args:
        env_dv (str): [필수] 실전모의구분 (ex. real:실전, demo:모의)
        nat_dv (str): [필수] 국가구분 (ex. us:미국)
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 01)
        rsyn_ord_rcit_dt (str): [필수] 해외주문접수일자
        ovrs_rsvn_odno (str): [필수] 해외예약주문번호 (ex. 해외주식_예약주문접수 API Output ODNO(주문번호) 참고)

    Returns:
        pd.DataFrame: 해외주식 예약주문접수취소 결과 데이터
        
    Example:
        >>> df = order_resv_ccnl(env_dv="real", nat_dv="us", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, rsyn_ord_rcit_dt="20220810", ovrs_rsvn_odno="0030008244")
        >>> print(df)
    """

    if env_dv == "":
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")
    
    if nat_dv == "":
        raise ValueError("nat_dv is required (e.g. 'us')")
    
    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '01')")
    
    if rsyn_ord_rcit_dt == "":
        raise ValueError("rsyn_ord_rcit_dt is required")
    
    if ovrs_rsvn_odno == "":
        raise ValueError("ovrs_rsvn_odno is required")

    # tr_id 설정
    if env_dv == "real":
        if nat_dv == "us":
            api_url = "/uapi/overseas-stock/v1/trading/order-resv-ccnl"

            tr_id = "TTTT3017U"
        else:
            raise ValueError("nat_dv can only be 'us'")
    elif env_dv == "demo":
        if nat_dv == "us":
            tr_id = "VTTT3017U"
        else:
            raise ValueError("nat_dv can only be 'us'")
    else:
        raise ValueError("env_dv is required (e.g. 'real' or 'demo')")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "RSYN_ORD_RCIT_DT": rsyn_ord_rcit_dt,
        "OVRS_RSVN_ODNO": ovrs_rsvn_odno
    }
    
    res = ka._url_fetch(api_url, tr_id, "", params)
    
    if res.isOK():
        # output은 object 자료형이므로 DataFrame으로 변환
        current_data = pd.DataFrame([res.getBody().output])
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 예약주문조회[v1_해외주식-013]
##############################################################################################

def order_resv_list(
    nat_dv: str,  # 국가구분코드
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    inqr_strt_dt: str,  # 조회시작일자
    inqr_end_dt: str,  # 조회종료일자
    inqr_dvsn_cd: str,  # 조회구분코드
    ovrs_excg_cd: str,  # 해외거래소코드
    prdt_type_cd: str = "",  # 상품유형코드
    FK200: str = "",  # 연속조회검색조건200
    NK200: str = "",  # 연속조회키200
    tr_cont: str = "",  # 연속거래여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> pd.DataFrame:
    """
    해외주식 예약주문 조회 API입니다.
    ※ 모의투자는 사용 불가합니다.

    * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
    https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp
    
    Args:
        nat_dv (str): [필수] 국가구분코드 (ex. us:미국, asia:아시아)
        cano (str): [필수] 종합계좌번호 (ex. 12345678)
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 01)
        inqr_strt_dt (str): [필수] 조회시작일자 (ex. 20250101)
        inqr_end_dt (str): [필수] 조회종료일자 (ex. 20251231)
        inqr_dvsn_cd (str): [필수] 조회구분코드 (ex. 00:전체, 01:일반해외주식, 02:미니스탁)
        ovrs_excg_cd (str): [필수] 해외거래소코드 (ex. NASD:나스닥, NYSE:뉴욕, AMEX:아멕스, SEHK:홍콩, SHAA:상해, SZAA:심천, TKSE:일본, HASE:하노이, VNSE:호치민)
        prdt_type_cd (str): 상품유형코드
        FK200 (str): 연속조회검색조건200
        NK200 (str): 연속조회키200
        tr_cont (str): 연속거래여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한
        
    Returns:
        pd.DataFrame: 해외주식 예약주문조회 데이터
        
    Example:
        >>> df = order_resv_list(nat_dv="us", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, inqr_strt_dt="20250101", inqr_end_dt="20251231", inqr_dvsn_cd="00", ovrs_excg_cd="NASD")
        >>> print(df)
    """
    
    if nat_dv == "":
        raise ValueError("nat_dv is required (e.g. 'us' or 'asia')")
    
    if cano == "":
        raise ValueError("cano is required (e.g. '12345678')")
    
    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '01')")
    
    if inqr_strt_dt == "":
        raise ValueError("inqr_strt_dt is required (e.g. '20250101')")
    
    if inqr_end_dt == "":
        raise ValueError("inqr_end_dt is required (e.g. '20251231')")
    
    if inqr_dvsn_cd == "":
        raise ValueError("inqr_dvsn_cd is required (e.g. '00')")
    
    if ovrs_excg_cd == "":
        raise ValueError("ovrs_excg_cd is required (e.g. 'NASD')")
    
    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe is None:
            return pd.DataFrame()
        else:
            return dataframe

    # tr_id 설정
    if nat_dv == "us":
        api_url = "/uapi/overseas-stock/v1/trading/order-resv-list"

        tr_id = "TTTT3039R"
    elif nat_dv == "asia":
        tr_id = "TTTS3014R"
    else:
        raise ValueError("nat_dv can only be 'us' or 'asia'")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "INQR_STRT_DT": inqr_strt_dt,
        "INQR_END_DT": inqr_end_dt,
        "INQR_DVSN_CD": inqr_dvsn_cd,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "PRDT_TYPE_CD": prdt_type_cd,
        "CTX_AREA_FK200": FK200,
        "CTX_AREA_NK200": NK200
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
            return order_resv_list(
                nat_dv, cano, acnt_prdt_cd, inqr_strt_dt, inqr_end_dt, 
                inqr_dvsn_cd, ovrs_excg_cd, prdt_type_cd, FK200, NK200, 
                "N", dataframe, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe
    else:
        res.printError(url=api_url)
        return pd.DataFrame()

################################################################################
# [해외주식] 주문/계좌 > 해외주식 정정취소주문[v1_해외주식-003]
################################################################################

def order_rvsecncl(
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        ovrs_excg_cd: str,  # 해외거래소코드
        pdno: str,  # 상품번호
        orgn_odno: str,  # 원주문번호
        rvse_cncl_dvsn_cd: str,  # 정정취소구분코드
        ord_qty: str,  # 주문수량
        ovrs_ord_unpr: str,  # 해외주문단가
        mgco_aptm_odno: str,  # 운용사지정주문번호
        ord_svr_dvsn_cd: str,  # 주문서버구분코드
        env_dv: str = "real",  # 실전모의구분

) -> Optional[pd.DataFrame]:
    """
    [해외주식] 주문/계좌 
    해외주식 정정취소주문[v1_해외주식-003]
    해외주식 정정취소주문 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 계좌번호 체계(8-2)의 앞 8자리
        acnt_prdt_cd (str): 계좌번호 체계(8-2)의 뒤 2자리
        ovrs_excg_cd (str): NASD : 나스닥  NYSE : 뉴욕  AMEX : 아멕스 SEHK : 홍콩 SHAA : 중국상해 SZAA : 중국심천 TKSE : 일본 HASE : 베트남 하노이 VNSE : 베트남 호치민
        pdno (str): 상품번호
        orgn_odno (str): 정정 또는 취소할 원주문번호 (해외주식_주문 API ouput ODNO  or 해외주식 미체결내역 API output ODNO 참고)
        rvse_cncl_dvsn_cd (str): 01 : 정정  02 : 취소
        ord_qty (str): 주문수량
        ovrs_ord_unpr (str): 취소주문 시, "0" 입력
        mgco_aptm_odno (str): 운용사지정주문번호
        ord_svr_dvsn_cd (str): "0"(Default)
        env_dv (str): 실전모의구분 (real:실전, demo:모의)
        
    Returns:
        Optional[pd.DataFrame]: 해외주식 정정취소주문 데이터
        
    Example:
        >>> df = order_rvsecncl(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ovrs_excg_cd="NYSE",
        ...     pdno="BA",
        ...     orgn_odno="30135009",
        ...     rvse_cncl_dvsn_cd="01",
        ...     ord_qty="1",
        ...     ovrs_ord_unpr="226.00",
        ...     mgco_aptm_odno="",
        ...     ord_svr_dvsn_cd="0",
        ...     env_dv="real"
        ... )
        >>> print(df)
    """
    # [필수 파라미터 검증]
    if not cano:
        logger.error("cano is required. (e.g. '810XXXXX')")
        raise ValueError("cano is required. (e.g. '810XXXXX')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")
    if not ovrs_excg_cd:
        logger.error("ovrs_excg_cd is required. (e.g. 'NYSE')")
        raise ValueError("ovrs_excg_cd is required. (e.g. 'NYSE')")
    if not pdno:
        logger.error("pdno is required. (e.g. 'BA')")
        raise ValueError("pdno is required. (e.g. 'BA')")
    if not orgn_odno:
        logger.error("orgn_odno is required. (e.g. '30135009')")
        raise ValueError("orgn_odno is required. (e.g. '30135009')")
    if not rvse_cncl_dvsn_cd:
        logger.error("rvse_cncl_dvsn_cd is required. (e.g. '01')")
        raise ValueError("rvse_cncl_dvsn_cd is required. (e.g. '01')")
    if not ord_qty:
        logger.error("ord_qty is required. (e.g. '1')")
        raise ValueError("ord_qty is required. (e.g. '1')")
    if not ovrs_ord_unpr:
        logger.error("ovrs_ord_unpr is required. (e.g. '226.00')")
        raise ValueError("ovrs_ord_unpr is required. (e.g. '226.00')")
    
    # TR ID 설정 (모의투자 지원 로직)
    if env_dv == "real":
        api_url = "/uapi/overseas-stock/v1/trading/order-rvsecncl"

        tr_id = "TTTT1004U"  # 실전투자용 TR ID
    elif env_dv == "demo":
        tr_id = "VTTT1004U"  # 모의투자용 TR ID
    else:
        raise ValueError("env_dv can only be 'real' or 'demo'")

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "OVRS_EXCG_CD": ovrs_excg_cd,
        "PDNO": pdno,
        "ORGN_ODNO": orgn_odno,
        "RVSE_CNCL_DVSN_CD": rvse_cncl_dvsn_cd,
        "ORD_QTY": ord_qty,
        "OVRS_ORD_UNPR": ovrs_ord_unpr,
        "MGCO_APTM_ODNO": mgco_aptm_odno,
        "ORD_SVR_DVSN_CD": ord_svr_dvsn_cd,
    }

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
# [해외주식] 시세분석 > 해외주식 가격급등락[해외주식-038]
##############################################################################################

def price_fluct(
    excd: str,  # [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
    gubn: str,  # [필수] 급등/급락구분 (ex. 0:급락, 1:급등)
    mixn: str,  # [필수] N분전콤보값 (ex. 0:1분전, 1:2분전, 2:3분전, 3:5분전, 4:10분전, 5:15분전, 6:20분전, 7:30분전, 8:60분전, 9:120분전)
    vol_rang: str,  # [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
    keyb: str = "",  # NEXT KEY BUFF
    auth: str = "",  # 사용자권한정보
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 시세분석 > 해외주식 가격급등락[해외주식-038]
    해외주식 가격급등락 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        gubn (str): [필수] 급등/급락구분 (ex. 0:급락, 1:급등)
        mixn (str): [필수] N분전콤보값 (ex. 0:1분전, 1:2분전, 2:3분전, 3:5분전, 4:10분전, 5:15분전, 6:20분전, 7:30분전, 8:60분전, 9:120분전)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        keyb (str): NEXT KEY BUFF
        auth (str): 사용자권한정보
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식 가격급등락 데이터 (output1, output2)
        
    Example:
        >>> df1, df2 = price_fluct(excd="NAS", gubn="0", mixn="0", vol_rang="0")
        >>> print(df1)
        >>> print(df2)
    """

    if excd == "":
        raise ValueError("excd is required (e.g. 'NAS')")
    
    if gubn == "":
        raise ValueError("gubn is required (e.g. '0' or '1')")
    
    if mixn == "":
        raise ValueError("mixn is required (e.g. '0')")
    
    if vol_rang == "":
        raise ValueError("vol_rang is required (e.g. '0')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    api_url = "/uapi/overseas-stock/v1/ranking/price-fluct"


    tr_id = "HHDFS76260000"  # 해외주식 가격급등락

    params = {
        "EXCD": excd,
        "GUBN": gubn,
        "MIXN": mixn,
        "VOL_RANG": vol_rang,
        "KEYB": keyb,
        "AUTH": auth
    }
    
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 처리
        current_data1 = pd.DataFrame(res.getBody().output1, index=[0])
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
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return price_fluct(
                excd, gubn, mixn, vol_rang, keyb, auth, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외주식] 시세분석 > 해외주식 거래증가율순위[해외주식-045]
##############################################################################################

def trade_growth(
    excd: str,  # [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
    nday: str,  # [필수] N일자값 (ex. 0:당일, 1:2일, 2:3일, 3:5일, 4:10일, 5:20일전, 6:30일, 7:60일, 8:120일, 9:1년)
    vol_rang: str,  # [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
    auth: str = "",  # 사용자권한정보
    keyb: str = "",  # NEXT KEY BUFF
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 기본시세 > 해외주식 거래증가율순위[해외주식-045]
    해외주식 거래증가율순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        nday (str): [필수] N일자값 (ex. 0:당일, 1:2일, 2:3일, 3:5일, 4:10일, 5:20일전, 6:30일, 7:60일, 8:120일, 9:1년)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        auth (str): 사용자권한정보
        keyb (str): NEXT KEY BUFF
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 데이터프레임 튜플
        
    Example:
        >>> df1, df2 = trade_growth(excd="NAS", nday="0", vol_rang="0")
        >>> print(df1)
        >>> print(df2)
    """

    if excd == "":
        raise ValueError("excd is required (e.g. 'NYS')")
    
    if nday == "":
        raise ValueError("nday is required (e.g. '0')")
    
    if vol_rang == "":
        raise ValueError("vol_rang is required (e.g. '0')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    api_url = "/uapi/overseas-stock/v1/ranking/trade-growth"


    tr_id = "HHDFS76330000"  # 해외주식 거래증가율순위

    params = {
        "EXCD": excd,
        "NDAY": nday,
        "VOL_RANG": vol_rang,
        "AUTH": auth,
        "KEYB": keyb
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
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return trade_growth(
                excd, nday, vol_rang, auth, keyb, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외주식] 시세분석 > 해외주식 거래대금순위[해외주식-044]
##############################################################################################

def trade_pbmn(
    excd: str,  # [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
    nday: str,  # [필수] N일자값 (ex. 0:당일, 1:2일, 2:3일, 3:5일, 4:10일, 5:20일전, 6:30일, 7:60일, 8:120일, 9:1년)
    vol_rang: str,  # [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
    auth: str = "",  # 사용자권한정보
    keyb: str = "",  # NEXT KEY BUFF
    prc1: str = "",  # 현재가 필터범위 시작
    prc2: str = "",  # 현재가 필터범위 끝
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    해외주식 거래대금순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        nday (str): [필수] N일자값 (ex. 0:당일, 1:2일, 2:3일, 3:5일, 4:10일, 5:20일전, 6:30일, 7:60일, 8:120일, 9:1년)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        auth (str): 사용자권한정보
        keyb (str): NEXT KEY BUFF
        prc1 (str): 현재가 필터범위 시작
        prc2 (str): 현재가 필터범위 끝
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 거래대금순위 데이터 (output1, output2)
        
    Example:
        >>> df1, df2 = trade_pbmn(excd="NAS", nday="0", vol_rang="0")
        >>> print(df1)
        >>> print(df2)
    """

    if excd == "":
        raise ValueError("excd is required (e.g. 'NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄')")
    
    if nday == "":
        raise ValueError("nday is required (e.g. '0:당일, 1:2일, 2:3일, 3:5일, 4:10일, 5:20일전, 6:30일, 7:60일, 8:120일, 9:1년')")
    
    if vol_rang == "":
        raise ValueError("vol_rang is required (e.g. '0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None or dataframe2 is None:
            return pd.DataFrame(), pd.DataFrame()
        else:
            return dataframe1, dataframe2

    api_url = "/uapi/overseas-stock/v1/ranking/trade-pbmn"


    tr_id = "HHDFS76320010"  # 해외주식 거래대금순위

    params = {
        "EXCD": excd,  # 거래소명
        "NDAY": nday,  # N일자값
        "VOL_RANG": vol_rang,  # 거래량조건
        "AUTH": auth,  # 사용자권한정보
        "KEYB": keyb,  # NEXT KEY BUFF
        "PRC1": prc1,  # 현재가 필터범위 시작
        "PRC2": prc2,  # 현재가 필터범위 끝
    }
    
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 처리 (object 타입)
        current_data1 = pd.DataFrame([res.getBody().output1])
        
        # output2 처리 (array 타입)
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
        keyb = res.getBody().keyb if hasattr(res.getBody(), 'keyb') else ""
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return trade_pbmn(
                excd, nday, vol_rang, auth, keyb, prc1, prc2, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외주식] 시세분석 > 해외주식 거래회전율순위[해외주식-046]
##############################################################################################

def trade_turnover(
    excd: str,     # 거래소명
    nday: str,     # N분전콤보값
    vol_rang: str, # 거래량조건
    keyb: str = "",  # NEXT KEY BUFF
    auth: str = "",  # 사용자권한정보
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    depth: int = 0,         # 내부 재귀 깊이 (자동 관리)
    max_depth: int = 10     # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 시세분석 > 해외주식 거래회전율순위[해외주식-046]
    해외주식 거래회전율순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        nday (str): [필수] N분전콤보값 (ex. 0:당일, 1:2일전, 2:3일전, 3:5일전, 4:10일전, 5:20일전, 6:30일전, 7:60일전, 8:120일전, 9:1년전)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        keyb (str): NEXT KEY BUFF
        auth (str): 사용자권한정보
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 해외주식 거래회전율순위 데이터
        
    Example:
        >>> result1, result2 = trade_turnover(excd="SHS", nday="0", vol_rang="0")
        >>> print(result1)
        >>> print(result2)
    """

    # 필수 파라미터 검증
    if excd == "":
        raise ValueError("excd is required (e.g. 'NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄')")
    
    if nday == "":
        raise ValueError("nday is required (e.g. '0:당일, 1:2일전, 2:3일전, 3:5일전, 4:10일전, 5:20일전, 6:30일전, 7:60일전, 8:120일전, 9:1년전')")
    
    if vol_rang == "":
        raise ValueError("vol_rang is required (e.g. '0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상')")

    # 재귀 깊이 제한 확인
    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    api_url = "/uapi/overseas-stock/v1/ranking/trade-turnover"


    tr_id = "HHDFS76340000"  # 해외주식 거래회전율순위

    params = {
        "EXCD": excd,          # 거래소명
        "NDAY": nday,          # N분전콤보값
        "VOL_RANG": vol_rang,  # 거래량조건
        "KEYB": keyb,          # NEXT KEY BUFF
        "AUTH": auth           # 사용자권한정보
    }
    
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 처리
        current_data1 = pd.DataFrame([res.getBody().output1])
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
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return trade_turnover(
                excd, nday, vol_rang, keyb, auth, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외주식] 시세분석 > 해외주식 거래량순위[해외주식-043]
##############################################################################################

def trade_vol(
    excd: str,  # 거래소명
    nday: str,  # N분전콤보값
    vol_rang: str,  # 거래량조건
    keyb: str = "",  # NEXT KEY BUFF
    auth: str = "",  # 사용자권한정보
    prc1: str = "",  # 가격 필터 시작
    prc2: str = "",  # 가격 필터 종료
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 시세분석 > 해외주식 거래량순위[해외주식-043]
    해외주식 거래량순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        nday (str): [필수] N분전콤보값 (ex. 0:당일, 1:2일전, 2:3일전, 3:5일전, 4:10일전, 5:20일전, 6:30일전, 7:60일전, 8:120일전, 9:1년전)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        keyb (str): NEXT KEY BUFF (ex. "")
        auth (str): 사용자권한정보 (ex. "")
        prc1 (str): 가격 필터 시작 (ex. "")
        prc2 (str): 가격 필터 종료 (ex. "")
        tr_cont (str): 연속거래여부 (ex. "")
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식 거래량순위 데이터 (output1, output2)
        
    Example:
        >>> df1, df2 = trade_vol(excd="NYS", nday="0", vol_rang="0")
        >>> print(df1)
        >>> print(df2)
    """

    # 필수 파라미터 검증
    if excd == "":
        raise ValueError("excd is required (e.g. 'NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄')")
    
    if nday == "":
        raise ValueError("nday is required (e.g. '0:당일, 1:2일전, 2:3일전, 3:5일전, 4:10일전, 5:20일전, 6:30일전, 7:60일전, 8:120일전, 9:1년전')")
    
    if vol_rang == "":
        raise ValueError("vol_rang is required (e.g. '0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    api_url = "/uapi/overseas-stock/v1/ranking/trade-vol"


    tr_id = "HHDFS76310010"  # 해외주식 거래량순위

    params = {
        "EXCD": excd,
        "NDAY": nday,
        "VOL_RANG": vol_rang,
        "KEYB": keyb,
        "AUTH": auth,
        "PRC1": prc1,
        "PRC2": prc2
    }
    
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 처리
        current_data1 = pd.DataFrame(res.getBody().output1, index=[0])
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
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return trade_vol(
                excd, nday, vol_rang, keyb, auth, prc1, prc2, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외주식] 시세분석 > 해외주식 상승률/하락률[해외주식-041]
##############################################################################################

def updown_rate(
    excd: str,  # [필수] 거래소명
    nday: str,  # [필수] N일자값  
    gubn: str,  # [필수] 상승율/하락율 구분
    vol_rang: str,  # [필수] 거래량조건
    auth: str = "",  # 사용자권한정보
    keyb: str = "",  # NEXT KEY BUFF
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    해외주식 상승률/하락률 순위를 조회합니다.
    
    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        nday (str): [필수] N일자값 (ex. 0:당일, 1:2일, 2:3일, 3:5일, 4:10일, 5:20일전, 6:30일, 7:60일, 8:120일, 9:1년)
        gubn (str): [필수] 상승율/하락율 구분 (ex. 0:하락율, 1:상승율)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        auth (str): 사용자권한정보
        keyb (str): NEXT KEY BUFF
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 상승률/하락률 순위 데이터
        
    Example:
        >>> df1, df2 = updown_rate(excd="NYS", nday="0", gubn="1", vol_rang="0")
        >>> print(df1)
        >>> print(df2)
    """

    # 필수 파라미터 검증
    if excd == "":
        raise ValueError("excd is required (e.g. 'NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄')")
    
    if nday == "":
        raise ValueError("nday is required (e.g. '0:당일, 1:2일, 2:3일, 3:5일, 4:10일, 5:20일전, 6:30일, 7:60일, 8:120일, 9:1년')")
    
    if gubn == "":
        raise ValueError("gubn is required (e.g. '0:하락율, 1:상승율')")
    
    if vol_rang == "":
        raise ValueError("vol_rang is required (e.g. '0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None and dataframe2 is None:
            return pd.DataFrame(), pd.DataFrame()
        else:
            return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()

    api_url = "/uapi/overseas-stock/v1/ranking/updown-rate"


    tr_id = "HHDFS76290000"

    params = {
        "EXCD": excd,
        "NDAY": nday,
        "GUBN": gubn,
        "VOL_RANG": vol_rang,
        "AUTH": auth,
        "KEYB": keyb
    }
    
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 처리
        current_data1 = pd.DataFrame([res.getBody().output1])
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
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return updown_rate(
                excd, nday, gubn, vol_rang, auth, keyb, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외주식] 시세분석 > 해외주식 매수체결강도상위[해외주식-040]
##############################################################################################

def volume_power(
    excd: str,  # [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
    nday: str,  # [필수] N일자값 (ex. 0:당일, 1:2일, 2:3일, 3:5일, 4:10일, 5:20일전, 6:30일, 7:60일, 8:120일, 9:1년)
    vol_rang: str,  # [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
    auth: str = "",  # 사용자권한정보
    keyb: str = "",  # NEXT KEY BUFF
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # output1 누적 데이터프레임
    dataframe2: Optional[pd.DataFrame] = None,  # output2 누적 데이터프레임
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 시세분석 > 해외주식 매수체결강도상위[해외주식-040]
    
    해외주식 매수 체결강도 상위 종목을 조회합니다.
    
    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        nday (str): [필수] N일자값 (ex. 0:당일, 1:2일, 2:3일, 3:5일, 4:10일, 5:20일전, 6:30일, 7:60일, 8:120일, 9:1년)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        auth (str): 사용자권한정보
        keyb (str): NEXT KEY BUFF
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): output1 누적 데이터프레임
        dataframe2 (Optional[pd.DataFrame]): output2 누적 데이터프레임
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> df1, df2 = volume_power(excd="HKS", nday="0", vol_rang="0")
        >>> print(df1)
        >>> print(df2)
    """

    if excd == "":
        raise ValueError("excd is required (e.g. 'HKS')")
    
    if nday == "":
        raise ValueError("nday is required (e.g. '0')")
    
    if vol_rang == "":
        raise ValueError("vol_rang is required (e.g. '0')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    api_url = "/uapi/overseas-stock/v1/ranking/volume-power"


    tr_id = "HHDFS76280000"

    params = {
        "EXCD": excd,
        "NDAY": nday,
        "VOL_RANG": vol_rang,
        "AUTH": auth,
        "KEYB": keyb
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
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return volume_power(
                excd, nday, vol_rang, auth, keyb, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [해외주식] 시세분석 > 해외주식 거래량급증[해외주식-039]
##############################################################################################

def volume_surge(
    excd: str,  # [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
    mixn: str,  # [필수] N분전콤보값 (ex. 0:1분전, 1:2분전, 2:3분전, 3:5분전, 4:10분전, 5:15분전, 6:20분전, 7:30분전, 8:60분전, 9:120분전)
    vol_rang: str,  # [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
    keyb: str = "",  # NEXT KEY BUFF
    auth: str = "",  # 사용자권한정보
    tr_cont: str = "",  # 연속거래여부
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임1
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임2
    depth: int = 0,  # 내부 재귀깊이 (자동관리)
    max_depth: int = 10  # 최대 재귀 횟수 제한
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [해외주식] 시세분석 > 해외주식 거래량급증[해외주식-039]
    해외주식 거래량급증 정보를 조회합니다.
    
    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        mixn (str): [필수] N분전콤보값 (ex. 0:1분전, 1:2분전, 2:3분전, 3:5분전, 4:10분전, 5:15분전, 6:20분전, 7:30분전, 8:60분전, 9:120분전)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        keyb (str): NEXT KEY BUFF
        auth (str): 사용자권한정보
        tr_cont (str): 연속거래여부
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임1
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임2
        depth (int): 내부 재귀깊이 (자동관리)
        max_depth (int): 최대 재귀 횟수 제한

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
        
    Example:
        >>> df1, df2 = volume_surge(excd="NYS", mixn="0", vol_rang="0")
        >>> print(df1)
        >>> print(df2)
    """

    if excd == "":
        raise ValueError("excd is required (e.g. 'NYS')")
    
    if mixn == "":
        raise ValueError("mixn is required (e.g. '0')")
    
    if vol_rang == "":
        raise ValueError("vol_rang is required (e.g. '0')")

    if depth > max_depth:
        logging.warning("Max recursive depth reached.")
        if dataframe1 is None:
            dataframe1 = pd.DataFrame()
        if dataframe2 is None:
            dataframe2 = pd.DataFrame()
        return dataframe1, dataframe2

    api_url = "/uapi/overseas-stock/v1/ranking/volume-surge"


    tr_id = "HHDFS76270000"  # 해외주식 거래량급증

    params = {
        "EXCD": excd,  # 거래소명
        "MIXN": mixn,  # N분전콤보값
        "VOL_RANG": vol_rang,  # 거래량조건
        "KEYB": keyb,  # NEXT KEY BUFF
        "AUTH": auth   # 사용자권한정보
    }
    
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)
    
    if res.isOK():
        # output1 처리
        current_data1 = pd.DataFrame(res.getBody().output1, index=[0])
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
        
        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logging.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return volume_surge(
                excd, mixn, vol_rang, keyb, auth, "N", dataframe1, dataframe2, depth + 1, max_depth
            )
        else:
            logging.info("Data fetch complete.")
            return dataframe1, dataframe2
    else:
        res.printError(url=api_url)
        return pd.DataFrame(), pd.DataFrame()

