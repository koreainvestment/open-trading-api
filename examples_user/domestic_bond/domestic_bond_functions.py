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
# [장내채권] 기본시세 > 장내채권 평균단가조회 [국내채권-158]
##############################################################################################

def avg_unit(
        inqr_strt_dt: str,  # 조회시작일자
        inqr_end_dt: str,  # 조회종료일자
        pdno: str,  # 상품번호
        prdt_type_cd: str,  # 상품유형코드
        vrfc_kind_cd: str,  # 검증종류코드
        NK30: str = "",  # 연속조회키30
        FK100: str = "",  # 연속조회검색조건100
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        dataframe3: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output3)
        tr_cont: str = "",
        depth: int = 0,
        max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    [장내채권] 기본시세 
    장내채권 평균단가조회[국내주식-158]
    장내채권 평균단가조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        inqr_strt_dt (str): 조회 시작 일자 (예: '20230101')
        inqr_end_dt (str): 조회 종료 일자 (예: '20230131')
        pdno (str): 상품번호, 공백: 전체, 특정종목 조회시 : 종목코드
        prdt_type_cd (str): 상품유형코드 (예: '302')
        vrfc_kind_cd (str): 검증종류코드 (예: '00')
        NK30 (str): 연속조회키30, 공백 허용
        FK100 (str): 연속조회검색조건100, 공백 허용
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        dataframe3 (Optional[pd.DataFrame]): 누적 데이터프레임 (output3)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: 장내채권 평균단가조회 데이터
        
    Example:
        >>> df1, df2, df3 = avg_unit(
        ...     inqr_strt_dt='20230101',
        ...     inqr_end_dt='20230131',
        ...     pdno='KR2033022D33',
        ...     prdt_type_cd='302',
        ...     vrfc_kind_cd='00',
        ... )
        >>> print(df1)
        >>> print(df2)
        >>> print(df3)
    """
    # 필수 파라미터 검증
    if not inqr_strt_dt:
        logger.error("inqr_strt_dt is required. (e.g. '20230101')")
        raise ValueError("inqr_strt_dt is required. (e.g. '20230101')")

    if not inqr_end_dt:
        logger.error("inqr_end_dt is required. (e.g. '20230131')")
        raise ValueError("inqr_end_dt is required. (e.g. '20230131')")

    if not prdt_type_cd:
        logger.error("prdt_type_cd is required. (e.g. '302')")
        raise ValueError("prdt_type_cd is required. (e.g. '302')")

    if not vrfc_kind_cd:
        logger.error("vrfc_kind_cd is required. (e.g. '00')")
        raise ValueError("vrfc_kind_cd is required. (e.g. '00')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return (
            dataframe1 if dataframe1 is not None else pd.DataFrame(),
            dataframe2 if dataframe2 is not None else pd.DataFrame(),
            dataframe3 if dataframe3 is not None else pd.DataFrame()
        )

    tr_id = "CTPF2005R"


    api_url = "/uapi/domestic-bond/v1/quotations/avg-unit"



    params = {
        "INQR_STRT_DT": inqr_strt_dt,
        "INQR_END_DT": inqr_end_dt,
        "PDNO": pdno,
        "PRDT_TYPE_CD": prdt_type_cd,
        "VRFC_KIND_CD": vrfc_kind_cd,
        "CTX_AREA_NK30": NK30,
        "CTX_AREA_FK100": FK100,
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # 연속조회 정보 업데이트
        tr_cont = res.getHeader().tr_cont
        NK30 = res.getBody().ctx_area_nk30
        FK100 = res.getBody().ctx_area_fk100

        # output1 데이터 처리
        current_data1 = pd.DataFrame(res.getBody().output1)
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

        # output3 데이터 처리
        current_data3 = pd.DataFrame(res.getBody().output3)
        if dataframe3 is not None:
            dataframe3 = pd.concat([dataframe3, current_data3], ignore_index=True)
        else:
            dataframe3 = current_data3

        if tr_cont in ["M", "F"]:  # 다음 페이지 존재
            logger.info("Call Next page...")
            ka.smart_sleep()  # 시스템 안정적 운영을 위한 지연
            return avg_unit(
                inqr_strt_dt,
                inqr_end_dt,
                pdno,
                prdt_type_cd,
                vrfc_kind_cd,
                NK30,
                FK100,
                dataframe1,
                dataframe2,
                dataframe3,
                "N",
                depth + 1,
                max_depth
            )
        else:
            logger.info("Data fetch complete.")
            return dataframe1, dataframe2, dataframe3
    else:
        logger.error("API call failed: %s - %s", res.getErrorCode(), res.getErrorMessage())
        res.printError(api_url)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

##############################################################################################
# [장내채권] 주문/계좌 > 장내채권 매수주문 [국내주식-124]
##############################################################################################

def buy(
        cano: str,
        acnt_prdt_cd: str,
        pdno: str,
        ord_qty2: str,
        bond_ord_unpr: str,
        samt_mket_ptci_yn: str,
        bond_rtl_mket_yn: str,
        idcr_stfno: str = "",
        mgco_aptm_odno: str = "",
        ord_svr_dvsn_cd: str = "",
        ctac_tlno: str = ""
) -> Optional[pd.DataFrame]:
    """
    [장내채권] 주문/계좌 
    장내채권 매수주문[국내주식-124]
    장내채권 매수주문 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 종합계좌번호 (8자리)
        acnt_prdt_cd (str): 계좌상품코드 (2자리)
        pdno (str): 상품번호 (12자리)
        ord_qty2 (str): 주문수량2 (19자리)
        bond_ord_unpr (str): 채권주문단가 (182자리)
        samt_mket_ptci_yn (str): 소액시장참여여부 ('Y' or 'N')
        bond_rtl_mket_yn (str): 채권소매시장여부 ('Y' or 'N')
        idcr_stfno (str, optional): 유치자직원번호 (6자리). Defaults to "".
        mgco_aptm_odno (str, optional): 운용사지정주문번호 (12자리). Defaults to "".
        ord_svr_dvsn_cd (str, optional): 주문서버구분코드. Defaults to "".
        ctac_tlno (str, optional): 연락전화번호. Defaults to "".
        
    Returns:
        Optional[pd.DataFrame]: 장내채권 매수주문 데이터
        
    Example:
        >>> df = buy(
        ...     cano=trenv.my_acct, 
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     pdno="KR1234567890", 
        ...     ord_qty2="10", 
        ...     bond_ord_unpr="10000",
        ...     samt_mket_ptci_yn="N",
        ...     bond_rtl_mket_yn="Y"
        ... )
        >>> print(df)
    """
    tr_id = "TTTC0952U"


    api_url = "/uapi/domestic-bond/v1/trading/buy"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "ORD_QTY2": ord_qty2,
        "BOND_ORD_UNPR": bond_ord_unpr,
        "SAMT_MKET_PTCI_YN": samt_mket_ptci_yn,
        "BOND_RTL_MKET_YN": bond_rtl_mket_yn,
        "IDCR_STFNO": idcr_stfno,
        "MGCO_APTM_ODNO": mgco_aptm_odno,
        "ORD_SVR_DVSN_CD": ord_svr_dvsn_cd,
        "CTAC_TLNO": ctac_tlno,
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
# [장내채권] 기본시세 > 장내채권현재가(호가) [국내주식-132]
##############################################################################################

def inquire_asking_price(
        fid_cond_mrkt_div_code: str,  # 시장 분류 코드
        fid_input_iscd: str,  # 채권종목코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [장내채권] 기본시세 
    장내채권현재가(호가)[국내주식-132]
    장내채권현재가(호가) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 시장 분류 코드 (B 입력)
        fid_input_iscd (str): 채권종목코드 (ex KR2033022D33)
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (기본값: None)
        depth (int): 현재 재귀 깊이 (기본값: 0)
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 장내채권현재가(호가) 데이터
        
    Example:
        >>> df = inquire_asking_price(fid_cond_mrkt_div_code="B", fid_input_iscd="KR2033022D33")
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'B')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'B')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. 'KR2033022D33')")
        raise ValueError("fid_input_iscd is required. (e.g. 'KR2033022D33')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHKBJ773401C0"


    api_url = "/uapi/domestic-bond/v1/quotations/inquire-asking-price"



    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
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
            return inquire_asking_price(
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
# [장내채권] 주문/계좌 > 장내채권 잔고조회 [국내주식-198]
##############################################################################################

def inquire_balance(
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        inqr_cndt: str,  # 조회조건
        pdno: str,  # 상품번호
        buy_dt: str,  # 매수일자
        FK200: str = "",  # 연속조회검색조건200
        NK200: str = "",  # 연속조회키200
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [장내채권] 주문/계좌 
    장내채권 잔고조회[국내주식-198]
    장내채권 잔고조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 종합계좌번호
        acnt_prdt_cd (str): 계좌상품코드
        inqr_cndt (str): 조회조건 (00: 전체, 01: 상품번호단위)
        pdno (str): 상품번호 (공백 허용)
        buy_dt (str): 매수일자 (공백 허용)
        FK200 (str): 연속조회검색조건200
        NK200 (str): 연속조회키200
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 장내채권 잔고조회 데이터
        
    Example:
        >>> df = inquire_balance(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     inqr_cndt='00',
        ...     pdno='',
        ...     buy_dt='',
        ... )
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not cano:
        logger.error("cano is required. (e.g. '12345678')")
        raise ValueError("cano is required. (e.g. '12345678')")

    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")

    if not inqr_cndt:
        logger.error("inqr_cndt is required. (e.g. '00')")
        raise ValueError("inqr_cndt is required. (e.g. '00')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "CTSC8407R"


    api_url = "/uapi/domestic-bond/v1/trading/inquire-balance"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "INQR_CNDT": inqr_cndt,
        "PDNO": pdno,
        "BUY_DT": buy_dt,
        "CTX_AREA_FK200": FK200,
        "CTX_AREA_NK200": NK200,
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
        NK200 = res.getBody().ctx_area_nk200
        FK200 = res.getBody().ctx_area_fk200

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_balance(
                cano,
                acnt_prdt_cd,
                inqr_cndt,
                pdno,
                buy_dt,
                FK200,
                NK200,
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
# [장내채권] 기본시세 > 장내채권현재가(체결) [국내주식-201]
##############################################################################################

def inquire_ccnl(
        fid_cond_mrkt_div_code: str,  # 조건시장분류코드
        fid_input_iscd: str,  # 입력종목코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [장내채권] 기본시세 
    장내채권현재가(체결)[국내주식-201]
    장내채권현재가(체결) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건시장분류코드 (예: 'B')
        fid_input_iscd (str): 입력종목코드 (예: 'KR2033022D33')
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (기본값: None)
        depth (int): 현재 재귀 깊이 (기본값: 0)
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 장내채권현재가(체결) 데이터
        
    Example:
        >>> df = inquire_ccnl('B', 'KR2033022D33')
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'B')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'B')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. 'KR2033022D33')")
        raise ValueError("fid_input_iscd is required. (e.g. 'KR2033022D33')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHKBJ773403C0"

    # API 요청 파라미터 설정

    api_url = "/uapi/domestic-bond/v1/quotations/inquire-ccnl"


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

        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_ccnl(
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
# [장내채권] 주문/계좌 > 장내채권 일별체결조회 [국내주식-127]
##############################################################################################

def inquire_daily_ccld(
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        inqr_strt_dt: str,  # 조회시작일자
        inqr_end_dt: str,  # 조회종료일자
        sll_buy_dvsn_cd: str,  # 매도매수구분코드
        sort_sqn_dvsn: str,  # 정렬순서구분
        pdno: str,  # 상품번호
        nccs_yn: str,  # 미체결여부
        ctx_area_nk200: str,  # 연속조회키200
        ctx_area_fk200: str,  # 연속조회검색조건200
        dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
        dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
        tr_cont: str = "",
        depth: int = 0,
        max_depth: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    [장내채권] 주문/계좌 
    장내채권 주문체결내역[국내주식-127]
    장내채권 주문체결내역 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 종합계좌번호
        acnt_prdt_cd (str): 계좌상품코드
        inqr_strt_dt (str): 조회시작일자 (1주일 이내)
        inqr_end_dt (str): 조회종료일자 (조회 당일)
        sll_buy_dvsn_cd (str): 매도매수구분코드 (%(전체), 01(매도), 02(매수))
        sort_sqn_dvsn (str): 정렬순서구분 (01(주문순서), 02(주문역순))
        pdno (str): 상품번호
        nccs_yn (str): 미체결여부 (N(전체), C(체결), Y(미체결))
        ctx_area_nk200 (str): 연속조회키200
        ctx_area_fk200 (str): 연속조회검색조건200
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 장내채권 주문체결내역 데이터
        
    Example:
        >>> df1, df2 = inquire_daily_ccld(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     inqr_strt_dt='20230101',
        ...     inqr_end_dt='20230107',
        ...     sll_buy_dvsn_cd='01',
        ...     sort_sqn_dvsn='01',
        ...     pdno='000000000001',
        ...     nccs_yn='N',
        ...     ctx_area_nk200='',
        ...     ctx_area_fk200=''
        ... )
        >>> print(df1)
        >>> print(df2)
    """
    # 필수 파라미터 검증
    if not cano:
        logger.error("cano is required. (e.g. '12345678')")
        raise ValueError("cano is required. (e.g. '12345678')")
    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")
    if not inqr_strt_dt:
        logger.error("inqr_strt_dt is required. (e.g. '20230101')")
        raise ValueError("inqr_strt_dt is required. (e.g. '20230101')")
    if not inqr_end_dt:
        logger.error("inqr_end_dt is required. (e.g. '20230107')")
        raise ValueError("inqr_end_dt is required. (e.g. '20230107')")
    if not sll_buy_dvsn_cd in ["%", "01", "02"]:
        logger.error("sll_buy_dvsn_cd is required. (e.g. '01')")
        raise ValueError("sll_buy_dvsn_cd is required. (e.g. '01')")
    if not sort_sqn_dvsn in ["01", "02"]:
        logger.error("sort_sqn_dvsn is required. (e.g. '01')")
        raise ValueError("sort_sqn_dvsn is required. (e.g. '01')")
    if not nccs_yn in ["N", "C", "Y"]:
        logger.error("nccs_yn is required. (e.g. 'N')")
        raise ValueError("nccs_yn is required. (e.g. 'N')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()

    tr_id = "CTSC8013R"


    api_url = "/uapi/domestic-bond/v1/trading/inquire-daily-ccld"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "INQR_STRT_DT": inqr_strt_dt,
        "INQR_END_DT": inqr_end_dt,
        "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
        "SORT_SQN_DVSN": sort_sqn_dvsn,
        "PDNO": pdno,
        "NCCS_YN": nccs_yn,
        "CTX_AREA_NK200": ctx_area_nk200,
        "CTX_AREA_FK200": ctx_area_fk200,
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
        ctx_area_nk200 = res.getBody().ctx_area_nk200
        ctx_area_fk200 = res.getBody().ctx_area_fk200

        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_daily_ccld(
                cano,
                acnt_prdt_cd,
                inqr_strt_dt,
                inqr_end_dt,
                sll_buy_dvsn_cd,
                sort_sqn_dvsn,
                pdno,
                nccs_yn,
                ctx_area_nk200,
                ctx_area_fk200,
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
# [장내채권] 기본시세 > 장내채권 기간별시세(일) [국내주식-159]
##############################################################################################

def inquire_daily_itemchartprice(
        fid_cond_mrkt_div_code: str,  # 조건 시장 구분 코드
        fid_input_iscd: str,  # 입력 종목코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [장내채권] 기본시세 
    장내채권 기간별시세(일)[국내주식-159]
    장내채권 기간별시세(일) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건 시장 구분 코드 (필수)
        fid_input_iscd (str): 입력 종목코드 (필수)
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (기본값: None)
        depth (int): 현재 재귀 깊이 (기본값: 0)
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 장내채권 기간별시세(일) 데이터
        
    Example:
        >>> df = inquire_daily_itemchartprice("B", "KR2033022D33")
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'B')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'B')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. 'KR2033022D33')")
        raise ValueError("fid_input_iscd is required. (e.g. 'KR2033022D33')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHKBJ773701C0"


    api_url = "/uapi/domestic-bond/v1/quotations/inquire-daily-itemchartprice"



    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
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
            return inquire_daily_itemchartprice(
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
# [장내채권] 기본시세 > 장내채권 일별시세 [국내주식-202]
##############################################################################################

def inquire_daily_price(
        fid_cond_mrkt_div_code: str,  # 조건시장분류코드
        fid_input_iscd: str,  # 입력종목코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [장내채권] 기본시세 
    장내채권현재가(일별)[국내주식-202]
    장내채권현재가(일별) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건시장분류코드 (예: 'B')
        fid_input_iscd (str): 입력종목코드 (예: 'KR2033022D33')
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (기본값: None)
        depth (int): 현재 재귀 깊이 (기본값: 0)
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 장내채권현재가(일별) 데이터
        
    Example:
        >>> df = inquire_daily_price('B', 'KR2033022D33')
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'B')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'B')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. 'KR2033022D33')")
        raise ValueError("fid_input_iscd is required. (e.g. 'KR2033022D33')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHKBJ773404C0"


    api_url = "/uapi/domestic-bond/v1/quotations/inquire-daily-price"



    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
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
            return inquire_daily_price(
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
# [장내채권] 기본시세 > 장내채권현재가(시세) [국내주식-200]
##############################################################################################

def inquire_price(
        fid_cond_mrkt_div_code: str,  # 조건시장분류코드
        fid_input_iscd: str,  # 입력종목코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [장내채권] 기본시세 
    장내채권현재가(시세)[국내주식-200]
    장내채권현재가(시세) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건시장분류코드 (예: 'B')
        fid_input_iscd (str): 입력종목코드 (예: 'KR2033022D33')
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (기본값: None)
        depth (int): 현재 재귀 깊이 (기본값: 0)
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 장내채권현재가(시세) 데이터
        
    Example:
        >>> df = inquire_price('B', 'KR2033022D33')
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'B')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'B')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. 'KR2033022D33')")
        raise ValueError("fid_input_iscd is required. (e.g. 'KR2033022D33')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "FHKBJ773400C0"


    api_url = "/uapi/domestic-bond/v1/quotations/inquire-price"



    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
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
            return inquire_price(
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
# [장내채권] 주문/계좌 > 장내채권 매수가능조회 [국내주식-199]
##############################################################################################

def inquire_psbl_order(
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        pdno: str,  # 상품번호
        bond_ord_unpr: str,  # 채권주문단가
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [장내채권] 주문/계좌 
    장내채권 매수가능조회[국내주식-199]
    장내채권 매수가능조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 종합계좌번호 (필수)
        acnt_prdt_cd (str): 계좌상품코드 (필수)
        pdno (str): 채권종목코드(ex KR2033022D33)
        bond_ord_unpr (str): 채권주문단가 (필수)
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 장내채권 매수가능조회 데이터
        
    Example:
        >>> df = inquire_psbl_order("12345678", "01", "KR2033022D33", "1000")
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not cano:
        logger.error("cano is required. (e.g. '1234567890')")
        raise ValueError("cano is required. (e.g. '1234567890')")

    if not acnt_prdt_cd:
        logger.error("acnt_prdt_cd is required. (e.g. '01')")
        raise ValueError("acnt_prdt_cd is required. (e.g. '01')")

    if not pdno:
        logger.error("pdno is required. (e.g. 'KR2033022D33')")
        raise ValueError("pdno is required. (e.g. 'KR2033022D33')")

    if not bond_ord_unpr:
        logger.error("bond_ord_unpr is required. (e.g. '1000')")
        raise ValueError("bond_ord_unpr is required. (e.g. '1000')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "TTTC8910R"


    api_url = "/uapi/domestic-bond/v1/trading/inquire-psbl-order"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "BOND_ORD_UNPR": bond_ord_unpr,
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
            return inquire_psbl_order(
                cano,
                acnt_prdt_cd,
                pdno,
                bond_ord_unpr,
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
# [장내채권] 주문/계좌 > 채권정정취소가능주문조회 [국내주식-126]
##############################################################################################

def inquire_psbl_rvsecncl(
    cano: str,  # 종합계좌번호
    acnt_prdt_cd: str,  # 계좌상품코드
    ord_dt: str,  # 주문일자
    odno: str,  # 주문번호
    ctx_area_fk200: str,  # 연속조회검색조건200
    ctx_area_nk200: str,  # 연속조회키200
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [장내채권] 주문/계좌 
    채권정정취소가능주문조회[국내주식-126]
    채권정정취소가능주문조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 종합계좌번호 (예: '12345678')
        acnt_prdt_cd (str): 계좌상품코드 (예: '01')
        ord_dt (str): 주문일자 (예: '20230101')
        odno (str): 주문번호 (예: '0000000001')
        ctx_area_fk200 (str): 연속조회검색조건200 (예: '조건값')
        ctx_area_nk200 (str): 연속조회키200 (예: '키값')
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 채권정정취소가능주문조회 데이터
        
    Example:
        >>> df = inquire_psbl_rvsecncl(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ord_dt='20230101',
        ...     odno='0000000001',
        ...     ctx_area_fk200='조건값',
        ...     ctx_area_nk200='키값'
        ... )
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
    
    tr_id = "CTSC8035R"


    api_url = "/uapi/domestic-bond/v1/trading/inquire-psbl-rvsecncl"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "ORD_DT": ord_dt,
        "ODNO": odno,
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
        ctx_area_nk200 = res.getBody().ctx_area_nk200
        ctx_area_fk200 = res.getBody().ctx_area_fk200
        
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return inquire_psbl_rvsecncl(
                cano,
                acnt_prdt_cd,
                ord_dt,
                odno,
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
# [장내채권] 기본시세 > 장내채권 발행정보 [국내주식-156]
##############################################################################################

def issue_info(
        pdno: str,  # 사용자권한정보
        prdt_type_cd: str,  # 거래소코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [장내채권] 기본시세 
    장내채권 발행정보[국내주식-156]
    장내채권 발행정보 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        pdno (str): 채권 종목번호(ex. KR6449111CB8)
        prdt_type_cd (str): Unique key(302)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 장내채권 발행정보 데이터
        
    Example:
        >>> df = issue_info("KR6449111CB8", "302")
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not pdno:
        logger.error("pdno is required. (e.g. 'KR6449111CB8')")
        raise ValueError("pdno is required. (e.g. 'KR6449111CB8')")

    if not prdt_type_cd:
        logger.error("prdt_type_cd is required. (e.g. '302')")
        raise ValueError("prdt_type_cd is required. (e.g. '302')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # API 호출 URL 및 거래 ID 설정
    tr_id = "CTPF1101R"

    # 요청 파라미터 설정

    api_url = "/uapi/domestic-bond/v1/quotations/issue-info"


    params = {
        "PDNO": pdno,
        "PRDT_TYPE_CD": prdt_type_cd,
    }

    # API 호출
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    # API 호출 성공 여부 확인
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
            return issue_info(
                pdno,
                prdt_type_cd,
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
# [장내채권] 주문/계좌 > 장내채권 정정취소주문 [국내주식-125]
##############################################################################################

def order_rvsecncl(
    cano: str,
    acnt_prdt_cd: str,
    pdno: str,
    orgn_odno: str,
    ord_qty2: str,
    bond_ord_unpr: str,
    qty_all_ord_yn: str,
    rvse_cncl_dvsn_cd: str,
    mgco_aptm_odno: str = "",
    ord_svr_dvsn_cd: str = "0",
    ctac_tlno: str = ""
) -> Optional[pd.DataFrame]:
    """
    [장내채권] 주문/계좌 
    장내채권 정정취소주문[국내주식-125]
    장내채권 정정취소주문 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 종합계좌번호
        acnt_prdt_cd (str): 계좌상품코드
        pdno (str): 상품번호
        orgn_odno (str): 원주문번호
        ord_qty2 (str): 주문수량2
        bond_ord_unpr (str): 채권주문단가
        qty_all_ord_yn (str): 잔량전부주문여부
        rvse_cncl_dvsn_cd (str): 정정취소구분코드
        mgco_aptm_odno (str, optional): 운용사지정주문번호. Defaults to "".
        ord_svr_dvsn_cd (str, optional): 주문서버구분코드. Defaults to "0".
        ctac_tlno (str, optional): 연락전화번호. Defaults to "".
        
    Returns:
        Optional[pd.DataFrame]: 장내채권 정정취소주문 데이터
        
    Example:
        >>> df = order_rvsecncl(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     pdno="KR6095572D81",
        ...     orgn_odno="0000015402",
        ...     ord_qty2="2",
        ...     bond_ord_unpr="10460",
        ...     qty_all_ord_yn="Y",
        ...     rvse_cncl_dvsn_cd="01"
        ... )
        >>> print(df)
    """
    tr_id = "TTTC0953U"


    api_url = "/uapi/domestic-bond/v1/trading/order-rvsecncl"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": pdno,
        "ORGN_ODNO": orgn_odno,
        "ORD_QTY2": ord_qty2,
        "BOND_ORD_UNPR": bond_ord_unpr,
        "QTY_ALL_ORD_YN": qty_all_ord_yn,
        "RVSE_CNCL_DVSN_CD": rvse_cncl_dvsn_cd,
        "MGCO_APTM_ODNO": mgco_aptm_odno,
        "ORD_SVR_DVSN_CD": ord_svr_dvsn_cd,
        "CTAC_TLNO": ctac_tlno
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
# [장내채권] 기본시세 > 장내채권 기본조회 [국내주식-129]
##############################################################################################

def search_bond_info(
        pdno: str,  # 상품번호
        prdt_type_cd: str,  # 상품유형코드
        tr_cont: str = "",  # 연속 거래 여부
        dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
        depth: int = 0,  # 현재 재귀 깊이
        max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [장내채권] 기본시세 
    장내채권 기본조회[국내주식-129]
    장내채권 기본조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        pdno (str): 상품번호 (필수)
        prdt_type_cd (str): 상품유형코드 (필수)
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: 장내채권 기본조회 데이터
        
    Example:
        >>> df = search_bond_info("KR2033022D33", "302")
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not pdno:
        logger.error("pdno is required. (e.g. 'KR2033022D33')")
        raise ValueError("pdno is required. (e.g. 'KR2033022D33')")

    if not prdt_type_cd:
        logger.error("prdt_type_cd is required. (e.g. '302')")
        raise ValueError("prdt_type_cd is required. (e.g. '302')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    tr_id = "CTPF1114R"


    api_url = "/uapi/domestic-bond/v1/quotations/search-bond-info"



    params = {
        "PDNO": pdno,
        "PRDT_TYPE_CD": prdt_type_cd,
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
            return search_bond_info(
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
# [장내채권] 주문/계좌 > 장내채권 매도주문 [국내주식-123]
##############################################################################################

def sell(
        cano: str,
        acnt_prdt_cd: str,
        ord_dvsn: str,
        pdno: str,
        ord_qty2: str,
        bond_ord_unpr: str,
        sprx_yn: str,
        samt_mket_ptci_yn: str,
        sll_agco_opps_sll_yn: str,
        bond_rtl_mket_yn: str,
        buy_dt: str = "",
        buy_seq: str = "",
        mgco_aptm_odno: str = "",
        ord_svr_dvsn_cd: str = "0",
        ctac_tlno: str = ""
) -> Optional[pd.DataFrame]:
    """
    [장내채권] 주문/계좌 
    장내채권 매도주문[국내주식-123]
    장내채권 매도주문 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        cano (str): 종합계좌번호
        acnt_prdt_cd (str): 계좌상품코드
        ord_dvsn (str): 주문구분
        pdno (str): 상품번호
        ord_qty2 (str): 주문수량2
        bond_ord_unpr (str): 채권주문단가
        sprx_yn (str): 분리과세여부
        samt_mket_ptci_yn (str): 소액시장참여여부
        sll_agco_opps_sll_yn (str): 매도대행사반대매도여부
        bond_rtl_mket_yn (str): 채권소매시장여부
        buy_dt (str, optional): 매수일자. Defaults to "".
        buy_seq (str, optional): 매수순번. Defaults to "".
        mgco_aptm_odno (str, optional): 운용사지정주문번호. Defaults to "".
        ord_svr_dvsn_cd (str, optional): 주문서버구분코드. Defaults to "0".
        ctac_tlno (str, optional): 연락전화번호. Defaults to "".
        
    Returns:
        Optional[pd.DataFrame]: 장내채권 매도주문 데이터
        
    Example:
        >>> df = sell(
        ...     cano=trenv.my_acct,
        ...     acnt_prdt_cd=trenv.my_prod,
        ...     ord_dvsn="01",
        ...     pdno="KR6095572D81",
        ...     ord_qty2="1",
        ...     bond_ord_unpr="10000.0",
        ...     sprx_yn="N",
        ...     samt_mket_ptci_yn="N",
        ...     sll_agco_opps_sll_yn="N",
        ...     bond_rtl_mket_yn="N"
        ... )
        >>> print(df)
    """
    tr_id = "TTTC0958U"


    api_url = "/uapi/domestic-bond/v1/trading/sell"



    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "ORD_DVSN": ord_dvsn,
        "PDNO": pdno,
        "ORD_QTY2": ord_qty2,
        "BOND_ORD_UNPR": bond_ord_unpr,
        "SPRX_YN": sprx_yn,
        "BUY_DT": buy_dt,
        "BUY_SEQ": buy_seq,
        "SAMT_MKET_PTCI_YN": samt_mket_ptci_yn,
        "SLL_AGCO_OPPS_SLL_YN": sll_agco_opps_sll_yn,
        "BOND_RTL_MKET_YN": bond_rtl_mket_yn,
        "MGCO_APTM_ODNO": mgco_aptm_odno,
        "ORD_SVR_DVSN_CD": ord_svr_dvsn_cd,
        "CTAC_TLNO": ctac_tlno
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

