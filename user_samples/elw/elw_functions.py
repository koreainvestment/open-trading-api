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
# [국내주식] ELW시세 - ELW 비교대상종목조회[국내주식-183]
##############################################################################################

def compare_stocks(
    fid_cond_scr_div_code: str,  # 조건화면분류코드
    fid_input_iscd: str,  # 입력종목코드
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 비교대상종목조회[국내주식-183]
    ELW 비교대상종목조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_scr_div_code (str): 조건화면분류코드 (예: '11517')
        fid_input_iscd (str): 입력종목코드 (예: '005930')
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (기본값: None)
        depth (int): 현재 재귀 깊이 (기본값: 0)
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 비교대상종목조회 데이터
        
    Example:
        >>> df = compare_stocks('11517', '005930')
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '11517')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '11517')")
    
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '005930')")
        raise ValueError("fid_input_iscd is required. (e.g. '005930')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()



    tr_id = "FHKEW151701C0"



    api_url = "/uapi/elw/v1/quotations/compare-stocks"




    params = {
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
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
            return compare_stocks(
                fid_cond_scr_div_code,
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
# [국내주식] ELW시세 - ELW 종목검색[국내주식-166]
##############################################################################################

def cond_search(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드 (필수)
    fid_cond_scr_div_code: str,  # 조건화면분류코드 (필수)
    fid_rank_sort_cls_code: str,  # 순위정렬구분코드 (필수)
    fid_input_cnt_1: str,  # 입력수1 (필수)
    fid_rank_sort_cls_code_2: Optional[str] = "",  # 순위정렬구분코드2 (선택)
    fid_input_cnt_2: Optional[str] = "",  # 입력수2 (선택)
    fid_rank_sort_cls_code_3: Optional[str] = "",  # 순위정렬구분코드3 (선택)
    fid_input_cnt_3: Optional[str] = "",  # 입력수3 (선택)
    fid_trgt_cls_code: Optional[str] = "",  # 대상구분코드 (선택)
    fid_input_iscd: Optional[str] = "",  # 입력종목코드 (선택 - 전체 허용)
    fid_unas_input_iscd: Optional[str] = "",  # 기초자산입력종목코드 (선택)
    fid_mrkt_cls_code: Optional[str] = "",  # 시장구분코드 (선택 - 전체 허용)
    fid_input_date_1: Optional[str] = "",  # 입력날짜1 (선택 - 전체 허용)
    fid_input_date_2: Optional[str] = "",  # 입력날짜2 (선택 - 전체 허용)
    fid_input_iscd_2: Optional[str] = "",  # 입력종목코드2 (선택)
    fid_etc_cls_code: Optional[str] = "",  # 기타구분코드 (선택 - 전체 허용)
    fid_input_rmnn_dynu_1: Optional[str] = "",  # 입력잔존일수1 (선택 - 이상값)
    fid_input_rmnn_dynu_2: Optional[str] = "",  # 입력잔존일수2 (선택 - 이하값)
    fid_prpr_cnt1: Optional[str] = "",  # 현재가수1 (선택 - 이상값)
    fid_prpr_cnt2: Optional[str] = "",  # 현재가수2 (선택 - 이하값)
    fid_rsfl_rate1: Optional[str] = "",  # 등락비율1 (선택 - 이상값)
    fid_rsfl_rate2: Optional[str] = "",  # 등락비율2 (선택 - 이하값)
    fid_vol1: Optional[str] = "",  # 거래량1 (선택 - 이상값)
    fid_vol2: Optional[str] = "",  # 거래량2 (선택 - 이하값)
    fid_aply_rang_prc_1: Optional[str] = "",  # 적용범위가격1 (선택)
    fid_aply_rang_prc_2: Optional[str] = "",  # 적용범위가격2 (선택)
    fid_lvrg_val1: Optional[str] = "",  # 레버리지값1 (선택)
    fid_lvrg_val2: Optional[str] = "",  # 레버리지값2 (선택)
    fid_vol3: Optional[str] = "",  # 거래량3 (선택)
    fid_vol4: Optional[str] = "",  # 거래량4 (선택)
    fid_ints_vltl1: Optional[str] = "",  # 내재변동성1 (선택 - 이상값)
    fid_ints_vltl2: Optional[str] = "",  # 내재변동성2 (선택 - 이하값)
    fid_prmm_val1: Optional[str] = "",  # 프리미엄값1 (선택 - 이상값)
    fid_prmm_val2: Optional[str] = "",  # 프리미엄값2 (선택 - 이하값)
    fid_gear1: Optional[str] = "",  # 기어링1 (선택 - 이상값)
    fid_gear2: Optional[str] = "",  # 기어링2 (선택 - 이하값)
    fid_prls_qryr_rate1: Optional[str] = "",  # 손익분기비율1 (선택 - 이상값)
    fid_prls_qryr_rate2: Optional[str] = "",  # 손익분기비율2 (선택 - 이하값)
    fid_delta1: Optional[str] = "",  # 델타1 (선택 - 이상값)
    fid_delta2: Optional[str] = "",  # 델타2 (선택 - 이하값)
    fid_acpr1: Optional[str] = "",  # 행사가1 (선택)
    fid_acpr2: Optional[str] = "",  # 행사가2 (선택)
    fid_stck_cnvr_rate1: Optional[str] = "",  # 주식전환비율1 (선택 - 이상값)
    fid_stck_cnvr_rate2: Optional[str] = "",  # 주식전환비율2 (선택 - 이하값)
    fid_div_cls_code: Optional[str] = "",  # 분류구분코드 (선택)
    fid_prit1: Optional[str] = "",  # 패리티1 (선택 - 이상값)
    fid_prit2: Optional[str] = "",  # 패리티2 (선택 - 이하값)
    fid_cfp1: Optional[str] = "",  # 자본지지점1 (선택 - 이상값)
    fid_cfp2: Optional[str] = "",  # 자본지지점2 (선택 - 이하값)
    fid_input_nmix_price_1: Optional[str] = "",  # 지수가격1 (선택 - 이상값)
    fid_input_nmix_price_2: Optional[str] = "",  # 지수가격2 (선택 - 이하값)
    fid_egea_val1: Optional[str] = "",  # E기어링값1 (선택 - 이상값)
    fid_egea_val2: Optional[str] = "",  # E기어링값2 (선택 - 이하값)
    fid_input_dvdn_ert: Optional[str] = "",  # 배당수익율 (선택 - 이상값)
    fid_input_hist_vltl: Optional[str] = "",  # 역사적변동성 (선택 - 이하값)
    fid_theta1: Optional[str] = "",  # 세타1 (선택 - 이상값)
    fid_theta2: Optional[str] = "",  # 세타2 (선택 - 이하값)
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이
) -> pd.DataFrame:
    """
    ELW 종목검색 API를 호출하여 조건에 맞는 ELW 종목 정보를 조회합니다.
    
    한국투자 HTS(eFriend Plus) > [0291] ELW 종목검색 화면의 기능을 API로 구현한 함수입니다.
    다양한 조건을 설정하여 ELW 종목을 검색하고, 한 번의 호출에 최대 100건까지 조회 가능합니다.
    연속 조회를 통해 전체 데이터를 수집할 수 있습니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건시장분류코드 (ELW의 경우 "W" 입력)
        fid_cond_scr_div_code (str): 조건화면분류코드 (화면번호 "11510" 입력)
        fid_rank_sort_cls_code (str): 순위정렬구분코드 
            - 0: 정렬안함, 1: 종목코드, 2: 현재가, 3: 대비율, 4: 거래량
            - 5: 행사가격, 6: 전환비율, 7: 상장일, 8: 만기일, 9: 잔존일수, 10: 레버리지
        fid_input_cnt_1 (str): 정렬1기준 (1: 상위, 2: 하위)
        나머지 파라미터들: 대부분 선택사항으로 빈 문자열("")로 설정 가능
        tr_cont (str): 연속 거래 여부 (초기 조회시 공백, 연속 조회시 "N")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (재귀 호출용)
        depth (int): 현재 재귀 깊이 (재귀 호출 횟수 추적)
        max_depth (int): 최대 재귀 깊이 (무한 재귀 방지, 기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 종목검색 결과 데이터프레임
            - 성공시: ELW 종목 정보가 포함된 DataFrame 반환
            - 실패시: 빈 DataFrame 반환
            - API 오류시: None 반환
        
    Raises:
        ValueError: 필수 파라미터가 누락되거나 잘못된 값이 입력된 경우
        
    Example:
        >>> # 기본 ELW 검색 (전체 종목)
        >>> df = cond_search(
        ...     fid_cond_mrkt_div_code="W",
        ...     fid_cond_scr_div_code="11510", 
        ...     fid_rank_sort_cls_code="0",
        ...     fid_input_cnt_1="1",
        ...     fid_rank_sort_cls_code_2="",
        ...     fid_input_cnt_2="",
        ...     fid_rank_sort_cls_code_3="",
        ...     fid_input_cnt_3="",
        ...     fid_trgt_cls_code="",
        ...     fid_input_iscd="",
        ...     fid_unas_input_iscd="",
        ...     fid_mrkt_cls_code="",
        ...     fid_input_date_1="",
        ...     fid_input_date_2="",
        ...     fid_input_iscd_2="",
        ...     fid_etc_cls_code="",
        ...     # 나머지 모든 파라미터는 빈 문자열
        ...     **{param: "" for param in [
        ...         "fid_input_rmnn_dynu_1", "fid_input_rmnn_dynu_2",
        ...         "fid_prpr_cnt1", "fid_prpr_cnt2", "fid_rsfl_rate1", "fid_rsfl_rate2",
        ...         "fid_vol1", "fid_vol2", "fid_aply_rang_prc_1", "fid_aply_rang_prc_2",
        ...         "fid_lvrg_val1", "fid_lvrg_val2", "fid_vol3", "fid_vol4",
        ...         "fid_ints_vltl1", "fid_ints_vltl2", "fid_prmm_val1", "fid_prmm_val2",
        ...         "fid_gear1", "fid_gear2", "fid_prls_qryr_rate1", "fid_prls_qryr_rate2",
        ...         "fid_delta1", "fid_delta2", "fid_acpr1", "fid_acpr2",
        ...         "fid_stck_cnvr_rate1", "fid_stck_cnvr_rate2", "fid_div_cls_code",
        ...         "fid_prit1", "fid_prit2", "fid_cfp1", "fid_cfp2",
        ...         "fid_input_nmix_price_1", "fid_input_nmix_price_2",
        ...         "fid_egea_val1", "fid_egea_val2", "fid_input_dvdn_ert",
        ...         "fid_input_hist_vltl", "fid_theta1", "fid_theta2"
        ...     ]}
        ... )
        >>> print(df.head())
    """
    
    # 필수 파라미터 검증 (최소한으로 축소)
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")
    
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '11510')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '11510')")
    
    if fid_rank_sort_cls_code is None:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '0')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '0')")
    
    if not fid_input_cnt_1:
        logger.error("fid_input_cnt_1 is required. (e.g. '1')")
        raise ValueError("fid_input_cnt_1 is required. (e.g. '1')")
    
    # 최대 재귀 깊이 체크 (무한 재귀 방지)
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    # API 호출 정보 설정

    # 요청 파라미터 설정

    tr_id = "FHKEW15100000"

    api_url = "/uapi/elw/v1/quotations/cond-search"


    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_INPUT_CNT_1": fid_input_cnt_1,
        "FID_RANK_SORT_CLS_CODE_2": fid_rank_sort_cls_code_2,
        "FID_INPUT_CNT_2": fid_input_cnt_2,
        "FID_RANK_SORT_CLS_CODE_3": fid_rank_sort_cls_code_3,
        "FID_INPUT_CNT_3": fid_input_cnt_3,
        "FID_TRGT_CLS_CODE": fid_trgt_cls_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_UNAS_INPUT_ISCD": fid_unas_input_iscd,
        "FID_MRKT_CLS_CODE": fid_mrkt_cls_code,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_DATE_2": fid_input_date_2,
        "FID_INPUT_ISCD_2": fid_input_iscd_2,
        "FID_ETC_CLS_CODE": fid_etc_cls_code,
        "FID_INPUT_RMNN_DYNU_1": fid_input_rmnn_dynu_1,
        "FID_INPUT_RMNN_DYNU_2": fid_input_rmnn_dynu_2,
        "FID_PRPR_CNT1": fid_prpr_cnt1,
        "FID_PRPR_CNT2": fid_prpr_cnt2,
        "FID_RSFL_RATE1": fid_rsfl_rate1,
        "FID_RSFL_RATE2": fid_rsfl_rate2,
        "FID_VOL1": fid_vol1,
        "FID_VOL2": fid_vol2,
        "FID_APLY_RANG_PRC_1": fid_aply_rang_prc_1,
        "FID_APLY_RANG_PRC_2": fid_aply_rang_prc_2,
        "FID_LVRG_VAL1": fid_lvrg_val1,
        "FID_LVRG_VAL2": fid_lvrg_val2,
        "FID_VOL3": fid_vol3,
        "FID_VOL4": fid_vol4,
        "FID_INTS_VLTL1": fid_ints_vltl1,
        "FID_INTS_VLTL2": fid_ints_vltl2,
        "FID_PRMM_VAL1": fid_prmm_val1,
        "FID_PRMM_VAL2": fid_prmm_val2,
        "FID_GEAR1": fid_gear1,
        "FID_GEAR2": fid_gear2,
        "FID_PRLS_QRYR_RATE1": fid_prls_qryr_rate1,
        "FID_PRLS_QRYR_RATE2": fid_prls_qryr_rate2,
        "FID_DELTA1": fid_delta1,
        "FID_DELTA2": fid_delta2,
        "FID_ACPR1": fid_acpr1,
        "FID_ACPR2": fid_acpr2,
        "FID_STCK_CNVR_RATE1": fid_stck_cnvr_rate1,
        "FID_STCK_CNVR_RATE2": fid_stck_cnvr_rate2,
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_PRIT1": fid_prit1,
        "FID_PRIT2": fid_prit2,
        "FID_CFP1": fid_cfp1,
        "FID_CFP2": fid_cfp2,
        "FID_INPUT_NMIX_PRICE_1": fid_input_nmix_price_1,
        "FID_INPUT_NMIX_PRICE_2": fid_input_nmix_price_2,
        "FID_EGEA_VAL1": fid_egea_val1,
        "FID_EGEA_VAL2": fid_egea_val2,
        "FID_INPUT_DVDN_ERT": fid_input_dvdn_ert,
        "FID_INPUT_HIST_VLTL": fid_input_hist_vltl,
        "FID_THETA1": fid_theta1,
        "FID_THETA2": fid_theta2,
    }

    # API 호출 정보 로그
    logger.info("ELW 종목검색 API 호출 시작 (depth: %d)", depth)
    
    # API 호출 실행
    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    # API 응답 처리
    if res.isOK():
        # 응답 데이터 처리
        if hasattr(res.getBody(), 'output'):
            output_data = res.getBody().output
            # 단일 객체인 경우 리스트로 변환
            if not isinstance(output_data, list):
                output_data = [output_data]
            current_data = pd.DataFrame(output_data)
            logger.info("API 호출 성공: %d건의 데이터를 수신했습니다.", len(current_data))
        else:
            current_data = pd.DataFrame()
            logger.warning("API 응답에서 output 데이터를 찾을 수 없습니다.")
            
        # 데이터프레임 누적 처리
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data
            
        # 연속 조회 여부 확인
        tr_cont = res.getHeader().tr_cont
        
        # 연속 데이터가 있는 경우 재귀 호출
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()  # API 호출 간격 조절
            return cond_search(
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_rank_sort_cls_code,
                fid_input_cnt_1,
                fid_rank_sort_cls_code_2,
                fid_input_cnt_2,
                fid_rank_sort_cls_code_3,
                fid_input_cnt_3,
                fid_trgt_cls_code,
                fid_input_iscd,
                fid_unas_input_iscd,
                fid_mrkt_cls_code,
                fid_input_date_1,
                fid_input_date_2,
                fid_input_iscd_2,
                fid_etc_cls_code,
                fid_input_rmnn_dynu_1,
                fid_input_rmnn_dynu_2,
                fid_prpr_cnt1,
                fid_prpr_cnt2,
                fid_rsfl_rate1,
                fid_rsfl_rate2,
                fid_vol1,
                fid_vol2,
                fid_aply_rang_prc_1,
                fid_aply_rang_prc_2,
                fid_lvrg_val1,
                fid_lvrg_val2,
                fid_vol3,
                fid_vol4,
                fid_ints_vltl1,
                fid_ints_vltl2,
                fid_prmm_val1,
                fid_prmm_val2,
                fid_gear1,
                fid_gear2,
                fid_prls_qryr_rate1,
                fid_prls_qryr_rate2,
                fid_delta1,
                fid_delta2,
                fid_acpr1,
                fid_acpr2,
                fid_stck_cnvr_rate1,
                fid_stck_cnvr_rate2,
                fid_div_cls_code,
                fid_prit1,
                fid_prit2,
                fid_cfp1,
                fid_cfp2,
                fid_input_nmix_price_1,
                fid_input_nmix_price_2,
                fid_egea_val1,
                fid_egea_val2,
                fid_input_dvdn_ert,
                fid_input_hist_vltl,
                fid_theta1,
                fid_theta2,
                "N", dataframe, depth + 1, max_depth
            )
        else:
            # 데이터 수집 완료
            logger.info("Data fetch complete.")
            total_records = len(dataframe) if dataframe is not None else 0
            logger.info("총 %d건의 ELW 종목 데이터를 수집했습니다.", total_records)
            return dataframe
    else:
        # API 호출 실패 처리
        error_code = res.getErrorCode()
        error_message = res.getErrorMessage()
        logger.error("API call failed: %s - %s", error_code, error_message)
        res.printError(api_url)
        return pd.DataFrame()  # 빈 데이터프레임 반환

##############################################################################################
# [국내주식] ELW시세 - ELW 만기예정/만기종목[국내주식-184]
##############################################################################################

def expiration_stocks(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_cond_scr_div_code: str,  # 조건화면분류코드
    fid_input_date_1: str,  # 입력날짜1
    fid_input_date_2: str,  # 입력날짜2
    fid_div_cls_code: str,  # 분류구분코드
    fid_etc_cls_code: str,  # 기타구분코드
    fid_unas_input_iscd: str,  # 기초자산입력종목코드
    fid_input_iscd_2: str,  # 발행회사코드
    fid_blng_cls_code: str,  # 결제방법
    fid_input_option_1: str,  # 입력옵션1
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 만기예정_만기종목[국내주식-184]
    ELW 만기예정_만기종목 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): W 입력
        fid_cond_scr_div_code (str): 11547 입력
        fid_input_date_1 (str): 입력날짜 ~ (ex) 20240402)
        fid_input_date_2 (str): ~입력날짜 (ex) 20240408)
        fid_div_cls_code (str): 0(콜),1(풋),2(전체)
        fid_etc_cls_code (str): 공백 입력
        fid_unas_input_iscd (str): 000000(전체), 2001(KOSPI 200), 기초자산코드(종목코드 ex. 삼성전자-005930)
        fid_input_iscd_2 (str): 00000(전체), 00003(한국투자증권), 00017(KB증권), 00005(미래에셋증권)
        fid_blng_cls_code (str): 0(전체),1(일반),2(조기종료)
        fid_input_option_1 (str): 공백 입력
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 만기예정_만기종목 데이터
        
    Example:
        >>> df = expiration_stocks(
        ...     fid_cond_mrkt_div_code='W',
        ...     fid_cond_scr_div_code='11547',
        ...     fid_input_date_1='20240402',
        ...     fid_input_date_2='20240408',
        ...     fid_div_cls_code='0',
        ...     fid_etc_cls_code='',
        ...     fid_unas_input_iscd='000000',
        ...     fid_input_iscd_2='00000',
        ...     fid_blng_cls_code='0',
        ...     fid_input_option_1='',
        ... )
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")
    
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '11547')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '11547')")
    
    if not fid_input_date_1:
        logger.error("fid_input_date_1 is required. (e.g. '20240402')")
        raise ValueError("fid_input_date_1 is required. (e.g. '20240402')")
    
    if not fid_input_date_2:
        logger.error("fid_input_date_2 is required. (e.g. '20240408')")
        raise ValueError("fid_input_date_2 is required. (e.g. '20240408')")
    
    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")
    
    if not fid_unas_input_iscd:
        logger.error("fid_unas_input_iscd is required. (e.g. '000000')")
        raise ValueError("fid_unas_input_iscd is required. (e.g. '000000')")
    
    if not fid_input_iscd_2:
        logger.error("fid_input_iscd_2 is required. (e.g. '00000')")
        raise ValueError("fid_input_iscd_2 is required. (e.g. '00000')")
    
    if not fid_blng_cls_code:
        logger.error("fid_blng_cls_code is required. (e.g. '0')")
        raise ValueError("fid_blng_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    

    tr_id = "FHKEW154700C0"

    

    api_url = "/uapi/elw/v1/quotations/expiration-stocks"


    

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_INPUT_DATE_2": fid_input_date_2,
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_ETC_CLS_CODE": fid_etc_cls_code,
        "FID_UNAS_INPUT_ISCD": fid_unas_input_iscd,
        "FID_INPUT_ISCD_2": fid_input_iscd_2,
        "FID_BLNG_CLS_CODE": fid_blng_cls_code,
        "FID_INPUT_OPTION_1": fid_input_option_1,
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
            return expiration_stocks(
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_input_date_1,
                fid_input_date_2,
                fid_div_cls_code,
                fid_etc_cls_code,
                fid_unas_input_iscd,
                fid_input_iscd_2,
                fid_blng_cls_code,
                fid_input_option_1,
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
# [국내주식] ELW시세 - ELW 지표순위[국내주식-169]
##############################################################################################

def indicator(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_cond_scr_div_code: str,  # 조건화면분류코드
    fid_unas_input_iscd: str,  # 기초자산입력종목코드
    fid_input_iscd: str,  # 발행사
    fid_div_cls_code: str,  # 콜풋구분코드
    fid_input_price_1: str,  # 가격(이상)
    fid_input_price_2: str,  # 가격(이하)
    fid_input_vol_1: str,  # 거래량(이상)
    fid_input_vol_2: str,  # 거래량(이하)
    fid_rank_sort_cls_code: str,  # 순위정렬구분코드
    fid_blng_cls_code: str,  # 결재방법
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 지표순위[국내주식-169]
    ELW 지표순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건시장분류코드 (필수)
        fid_cond_scr_div_code (str): 조건화면분류코드 (필수)
        fid_unas_input_iscd (str): 기초자산입력종목코드 (필수)
        fid_input_iscd (str): 발행사 (필수)
        fid_div_cls_code (str): 콜풋구분코드 (필수)
        fid_input_price_1 (str): 가격(이상) (필수)
        fid_input_price_2 (str): 가격(이하) (필수)
        fid_input_vol_1 (str): 거래량(이상) (필수)
        fid_input_vol_2 (str): 거래량(이하) (필수)
        fid_rank_sort_cls_code (str): 순위정렬구분코드 (필수)
        fid_blng_cls_code (str): 결재방법 (필수)
        tr_cont (str): 연속 거래 여부 (옵션)
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (옵션)
        depth (int): 현재 재귀 깊이 (옵션)
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 지표순위 데이터
        
    Example:
        >>> df = indicator(
        ...     fid_cond_mrkt_div_code='W',
        ...     fid_cond_scr_div_code='20279',
        ...     fid_unas_input_iscd='000000',
        ...     fid_input_iscd='00000',
        ...     fid_div_cls_code='0',
        ...     fid_input_price_1='1000',
        ...     fid_input_price_2='5000',
        ...     fid_input_vol_1='100',
        ...     fid_input_vol_2='1000',
        ...     fid_rank_sort_cls_code='0',
        ...     fid_blng_cls_code='0'
        ... )
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")
    
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20279')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20279')")
    
    if not fid_unas_input_iscd:
        logger.error("fid_unas_input_iscd is required. (e.g. '000000')")
        raise ValueError("fid_unas_input_iscd is required. (e.g. '000000')")
    
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '00000')")
        raise ValueError("fid_input_iscd is required. (e.g. '00000')")
    
    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")
    
    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '0')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '0')")
    
    if not fid_blng_cls_code:
        logger.error("fid_blng_cls_code is required. (e.g. '0')")
        raise ValueError("fid_blng_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    

    tr_id = "FHPEW02790000"

    

    api_url = "/uapi/elw/v1/ranking/indicator"


    

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_UNAS_INPUT_ISCD": fid_unas_input_iscd,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_INPUT_PRICE_1": fid_input_price_1,
        "FID_INPUT_PRICE_2": fid_input_price_2,
        "FID_INPUT_VOL_1": fid_input_vol_1,
        "FID_INPUT_VOL_2": fid_input_vol_2,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_BLNG_CLS_CODE": fid_blng_cls_code,
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
            return indicator(
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_unas_input_iscd,
                fid_input_iscd,
                fid_div_cls_code,
                fid_input_price_1,
                fid_input_price_2,
                fid_input_vol_1,
                fid_input_vol_2,
                fid_rank_sort_cls_code,
                fid_blng_cls_code,
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
# [국내주식] ELW시세 - ELW 투자지표추이(체결)[국내주식-172]
##############################################################################################

def indicator_trend_ccnl(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_input_iscd: str,  # 입력종목코드
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 투자지표추이(체결)[국내주식-172]
    ELW 투자지표추이(체결) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건시장분류코드 (필수)
        fid_input_iscd (str): 입력종목코드 (필수)
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (기본값: None)
        depth (int): 현재 재귀 깊이 (기본값: 0)
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 투자지표추이(체결) 데이터
        
    Example:
        >>> df = indicator_trend_ccnl("W", "58J297")
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")
    
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '58J297')")
        raise ValueError("fid_input_iscd is required. (e.g. '58J297')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    

    tr_id = "FHPEW02740100"

    

    api_url = "/uapi/elw/v1/quotations/indicator-trend-ccnl"


    

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
            return indicator_trend_ccnl(
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
# [국내주식] ELW시세 - ELW 투자지표추이(일별)[국내주식-173]
##############################################################################################

def indicator_trend_daily(
    fid_cond_mrkt_div_code: str,  # 시장 분류 코드 (예: 'W')
    fid_input_iscd: str,  # 종목코드 (6자리)
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 투자지표추이(일별)[국내주식-173]
    ELW 투자지표추이(일별) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 시장 분류 코드 (예: 'W')
        fid_input_iscd (str): 종목코드 (6자리, 예: '57K281')
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 투자지표추이(일별) 데이터
        
    Example:
        >>> df = indicator_trend_daily('W', '57K281')
    """
    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '57K281')")
        raise ValueError("fid_input_iscd is required. (e.g. '57K281')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    

    tr_id = "FHPEW02740200"

    

    api_url = "/uapi/elw/v1/quotations/indicator-trend-daily"


    

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
            
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data
            
        tr_cont = res.getHeader().tr_cont
        
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return indicator_trend_daily(
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
# [국내주식] ELW시세 - ELW 투자지표추이(분별)[국내주식-174]
##############################################################################################

def indicator_trend_minute(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_input_iscd: str,  # 입력종목코드
    fid_hour_cls_code: str,  # 시간구분코드
    fid_pw_data_incu_yn: str,  # 과거데이터 포함 여부
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 투자지표추이(분별)[국내주식-174]
    ELW 투자지표추이(분별) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 시장구분코드 (W)
        fid_input_iscd (str): 입력종목코드 예시: 58J297(KBJ297삼성전자콜)
        fid_hour_cls_code (str): 시간구분코드 예시: '60(1분), 180(3분), 300(5분), 600(10분), 1800(30분), 3600(60분), 7200(60분)'
        fid_pw_data_incu_yn (str): 과거데이터 포함 여부 예시: N(과거데이터포함X), Y(과거데이터포함O)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 투자지표추이(분별) 데이터
        
    Example:
        >>> df = indicator_trend_minute(
        ...     fid_cond_mrkt_div_code='W',
        ...     fid_input_iscd='58J297',
        ...     fid_hour_cls_code='60',
        ...     fid_pw_data_incu_yn='N'
        ... )
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '58J297')")
        raise ValueError("fid_input_iscd is required. (e.g. '58J297')")

    if not fid_hour_cls_code:
        logger.error("fid_hour_cls_code is required. (e.g. '60')")
        raise ValueError("fid_hour_cls_code is required. (e.g. '60')")

    if not fid_pw_data_incu_yn:
        logger.error("fid_pw_data_incu_yn is required. (e.g. 'N')")
        raise ValueError("fid_pw_data_incu_yn is required. (e.g. 'N')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # API 호출 URL 및 거래 ID 설정

    # 요청 파라미터 설정

    tr_id = "FHPEW02740300"

    api_url = "/uapi/elw/v1/quotations/indicator-trend-minute"


    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_HOUR_CLS_CODE": fid_hour_cls_code,
        "FID_PW_DATA_INCU_YN": fid_pw_data_incu_yn,
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
            return indicator_trend_minute(
                fid_cond_mrkt_div_code,
                fid_input_iscd,
                fid_hour_cls_code,
                fid_pw_data_incu_yn,
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
# [국내주식] ELW시세 - ELW LP매매추이[국내주식-182]
##############################################################################################

def lp_trade_trend(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_input_iscd: str,  # 입력종목코드
    dataframe1: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output1)
    dataframe2: Optional[pd.DataFrame] = None,  # 누적 데이터프레임 (output2)
    tr_cont: str = "",
    depth: int = 0,
    max_depth: int = 10
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    [국내주식] ELW시세 
    ELW LP매매추이[국내주식-182]
    ELW LP매매추이 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 시장구분(W)
        fid_input_iscd (str): 입력종목코드(ex 52K577(미래 K577KOSDAQ150콜)
        dataframe1 (Optional[pd.DataFrame]): 누적 데이터프레임 (output1)
        dataframe2 (Optional[pd.DataFrame]): 누적 데이터프레임 (output2)
        tr_cont (str): 연속 거래 여부
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: ELW LP매매추이 데이터
        
    Example:
        >>> df1, df2 = lp_trade_trend("W", "52K577")
        >>> print(df1)
        >>> print(df2)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")
    
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '52K577')")
        raise ValueError("fid_input_iscd is required. (e.g. '52K577')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe1 if dataframe1 is not None else pd.DataFrame(), dataframe2 if dataframe2 is not None else pd.DataFrame()

    

    tr_id = "FHPEW03760000"

    

    api_url = "/uapi/elw/v1/quotations/lp-trade-trend"


    

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
    }

    res = ka._url_fetch(api_url, tr_id, tr_cont, params)

    if res.isOK():
        # output1 처리
        if hasattr(res.getBody(), 'output1'):
            output_data = res.getBody().output1
            if output_data:
                current_data1 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe1 = pd.concat([dataframe1, current_data1], ignore_index=True) if dataframe1 is not None else current_data1
            else:
                dataframe1 = dataframe1 if dataframe1 is not None else pd.DataFrame()
        else:
            dataframe1 = dataframe1 if dataframe1 is not None else pd.DataFrame()

        # output2 처리
        if hasattr(res.getBody(), 'output2'):
            output_data = res.getBody().output2
            if output_data:
                current_data2 = pd.DataFrame(output_data if isinstance(output_data, list) else [output_data])
                dataframe2 = pd.concat([dataframe2, current_data2], ignore_index=True) if dataframe2 is not None else current_data2
            else:
                dataframe2 = dataframe2 if dataframe2 is not None else pd.DataFrame()
        else:
            dataframe2 = dataframe2 if dataframe2 is not None else pd.DataFrame()

        tr_cont = res.getHeader().tr_cont
        
        if tr_cont in ["M", "F"]:
            logger.info("Calling next page...")
            ka.smart_sleep()
            return lp_trade_trend(
                fid_cond_mrkt_div_code,
                fid_input_iscd,
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
# [국내주식] ELW시세 - ELW 신규상장종목[국내주식-181]
##############################################################################################

def newly_listed(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_cond_scr_div_code: str,  # 조건화면분류코드
    fid_div_cls_code: str,  # 분류구분코드
    fid_unas_input_iscd: str,  # 기초자산입력종목코드
    fid_input_iscd_2: str,  # 입력종목코드2
    fid_input_date_1: str,  # 입력날짜1
    fid_blng_cls_code: str,  # 결재방법
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 신규상장종목[국내주식-181]
    ELW 신규상장종목 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 시장구분코드 (W)
        fid_cond_scr_div_code (str): Unique key(11548)
        fid_div_cls_code (str): 전체(02), 콜(00), 풋(01)
        fid_unas_input_iscd (str): 'ex) 000000(전체), 2001(코스피200) , 3003(코스닥150), 005930(삼성전자) '
        fid_input_iscd_2 (str): '00003(한국투자증권), 00017(KB증권),  00005(미래에셋증권)'
        fid_input_date_1 (str): 날짜 (ex) 20240402)
        fid_blng_cls_code (str): 0(전체), 1(일반), 2(조기종료)
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 신규상장종목 데이터
        
    Example:
        >>> df = newly_listed(
        ...     fid_cond_mrkt_div_code='W',
        ...     fid_cond_scr_div_code='11548',
        ...     fid_div_cls_code='02',
        ...     fid_unas_input_iscd='000000',
        ...     fid_input_iscd_2='00003',
        ...     fid_input_date_1='20240402',
        ...     fid_blng_cls_code='0'
        ... )
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")
    
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '11548')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '11548')")
    
    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '02')")
        raise ValueError("fid_div_cls_code is required. (e.g. '02')")
    
    if not fid_unas_input_iscd:
        logger.error("fid_unas_input_iscd is required. (e.g. '000000')")
        raise ValueError("fid_unas_input_iscd is required. (e.g. '000000')")
    
    if not fid_input_iscd_2:
        logger.error("fid_input_iscd_2 is required. (e.g. '00003')")
        raise ValueError("fid_input_iscd_2 is required. (e.g. '00003')")
    
    if not fid_input_date_1:
        logger.error("fid_input_date_1 is required. (e.g. '20240402')")
        raise ValueError("fid_input_date_1 is required. (e.g. '20240402')")
    
    if not fid_blng_cls_code:
        logger.error("fid_blng_cls_code is required. (e.g. '0')")
        raise ValueError("fid_blng_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    

    tr_id = "FHKEW154800C0"

    

    api_url = "/uapi/elw/v1/quotations/newly-listed"


    

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_UNAS_INPUT_ISCD": fid_unas_input_iscd,
        "FID_INPUT_ISCD_2": fid_input_iscd_2,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_BLNG_CLS_CODE": fid_blng_cls_code,
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
            
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data
            
        tr_cont = res.getHeader().tr_cont
        
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return newly_listed(
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_div_cls_code,
                fid_unas_input_iscd,
                fid_input_iscd_2,
                fid_input_date_1,
                fid_blng_cls_code,
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
# [국내주식] ELW시세 - ELW 당일급변종목[국내주식-171]
##############################################################################################

def quick_change(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_cond_scr_div_code: str,  # 조건화면분류코드
    fid_unas_input_iscd: str,  # 기초자산입력종목코드
    fid_input_iscd: str,  # 발행사
    fid_mrkt_cls_code: str,  # 시장구분코드
    fid_input_price_1: str,  # 가격(이상)
    fid_input_price_2: str,  # 가격(이하)
    fid_input_vol_1: str,  # 거래량(이상)
    fid_input_vol_2: str,  # 거래량(이하)
    fid_hour_cls_code: str,  # 시간구분코드
    fid_input_hour_1: str,  # 입력 일 또는 분
    fid_input_hour_2: str,  # 기준시간(분 선택 시)
    fid_rank_sort_cls_code: str,  # 순위정렬구분코드
    fid_blng_cls_code: str,  # 결재방법
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 당일급변종목[국내주식-171]
    ELW 당일급변종목 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건시장분류코드 (필수)
        fid_cond_scr_div_code (str): 조건화면분류코드 (필수)
        fid_unas_input_iscd (str): 기초자산입력종목코드 (필수)
        fid_input_iscd (str): 발행사 (필수)
        fid_mrkt_cls_code (str): 시장구분코드 (필수)
        fid_input_price_1 (str): 가격(이상) (필수)
        fid_input_price_2 (str): 가격(이하) (필수)
        fid_input_vol_1 (str): 거래량(이상) (필수)
        fid_input_vol_2 (str): 거래량(이하) (필수)
        fid_hour_cls_code (str): 시간구분코드 (필수)
        fid_input_hour_1 (str): 입력 일 또는 분 (필수)
        fid_input_hour_2 (str): 기준시간(분 선택 시) (필수)
        fid_rank_sort_cls_code (str): 순위정렬구분코드 (필수)
        fid_blng_cls_code (str): 결재방법 (필수)
        tr_cont (str): 연속 거래 여부 (옵션)
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (옵션)
        depth (int): 현재 재귀 깊이 (옵션)
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 당일급변종목 데이터
        
    Example:
        >>> df = quick_change(
        ...     fid_cond_mrkt_div_code='W',
        ...     fid_cond_scr_div_code='20287',
        ...     fid_unas_input_iscd='000000',
        ...     fid_input_iscd='00000',
        ...     fid_mrkt_cls_code='A',
        ...     fid_input_price_1='1000',
        ...     fid_input_price_2='5000',
        ...     fid_input_vol_1='10000',
        ...     fid_input_vol_2='50000',
        ...     fid_hour_cls_code='1',
        ...     fid_input_hour_1='10',
        ...     fid_input_hour_2='30',
        ...     fid_rank_sort_cls_code='1',
        ...     fid_blng_cls_code='0'
        ... )
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20287')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20287')")
    if not fid_unas_input_iscd:
        logger.error("fid_unas_input_iscd is required. (e.g. '000000')")
        raise ValueError("fid_unas_input_iscd is required. (e.g. '000000')")
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '00000')")
        raise ValueError("fid_input_iscd is required. (e.g. '00000')")
    if not fid_mrkt_cls_code:
        logger.error("fid_mrkt_cls_code is required. (e.g. 'A')")
        raise ValueError("fid_mrkt_cls_code is required. (e.g. 'A')")
    if not fid_hour_cls_code:
        logger.error("fid_hour_cls_code is required. (e.g. '1')")
        raise ValueError("fid_hour_cls_code is required. (e.g. '1')")
    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '1')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '1')")
    if not fid_blng_cls_code:
        logger.error("fid_blng_cls_code is required. (e.g. '0')")
        raise ValueError("fid_blng_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()



    tr_id = "FHPEW02870000"



    api_url = "/uapi/elw/v1/ranking/quick-change"




    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_UNAS_INPUT_ISCD": fid_unas_input_iscd,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_MRKT_CLS_CODE": fid_mrkt_cls_code,
        "FID_INPUT_PRICE_1": fid_input_price_1,
        "FID_INPUT_PRICE_2": fid_input_price_2,
        "FID_INPUT_VOL_1": fid_input_vol_1,
        "FID_INPUT_VOL_2": fid_input_vol_2,
        "FID_HOUR_CLS_CODE": fid_hour_cls_code,
        "FID_INPUT_HOUR_1": fid_input_hour_1,
        "FID_INPUT_HOUR_2": fid_input_hour_2,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_BLNG_CLS_CODE": fid_blng_cls_code,
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
            return quick_change(
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_unas_input_iscd,
                fid_input_iscd,
                fid_mrkt_cls_code,
                fid_input_price_1,
                fid_input_price_2,
                fid_input_vol_1,
                fid_input_vol_2,
                fid_hour_cls_code,
                fid_input_hour_1,
                fid_input_hour_2,
                fid_rank_sort_cls_code,
                fid_blng_cls_code,
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
# [국내주식] ELW시세 - ELW 민감도 순위[국내주식-170]
##############################################################################################

def sensitivity(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_cond_scr_div_code: str,  # 조건화면분류코드
    fid_unas_input_iscd: str,  # 기초자산입력종목코드
    fid_input_iscd: str,  # 입력종목코드
    fid_div_cls_code: str,  # 콜풋구분코드
    fid_input_price_1: str,  # 가격(이상)
    fid_input_price_2: str,  # 가격(이하)
    fid_input_vol_1: str,  # 거래량(이상)
    fid_input_vol_2: str,  # 거래량(이하)
    fid_rank_sort_cls_code: str,  # 순위정렬구분코드
    fid_input_rmnn_dynu_1: str,  # 잔존일수(이상)
    fid_input_date_1: str,  # 조회기준일
    fid_blng_cls_code: str,  # 결재방법
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 민감도 순위[국내주식-170]
    ELW 민감도 순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건시장분류코드
        fid_cond_scr_div_code (str): 조건화면분류코드
        fid_unas_input_iscd (str): 기초자산입력종목코드
        fid_input_iscd (str): 입력종목코드
        fid_div_cls_code (str): 콜풋구분코드
        fid_input_price_1 (str): 가격(이상)
        fid_input_price_2 (str): 가격(이하)
        fid_input_vol_1 (str): 거래량(이상)
        fid_input_vol_2 (str): 거래량(이하)
        fid_rank_sort_cls_code (str): 순위정렬구분코드
        fid_input_rmnn_dynu_1 (str): 잔존일수(이상)
        fid_input_date_1 (str): 조회기준일
        fid_blng_cls_code (str): 결재방법
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 민감도 순위 데이터
        
    Example:
        >>> df = sensitivity(
                fid_cond_mrkt_div_code='W',
                fid_cond_scr_div_code='20285',
                fid_unas_input_iscd='000000',
                fid_input_iscd='00000',
                fid_div_cls_code='0',
                fid_input_price_1='0',
                fid_input_price_2='100000',
                fid_input_vol_1='0',
                fid_input_vol_2='1000000',
                fid_rank_sort_cls_code='0',
                fid_input_rmnn_dynu_1='0',
                fid_input_date_1='20230101',
                fid_blng_cls_code='0'
            )
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")
    
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20285')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20285')")
    
    if not fid_unas_input_iscd:
        logger.error("fid_unas_input_iscd is required. (e.g. '000000')")
        raise ValueError("fid_unas_input_iscd is required. (e.g. '000000')")
    
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '00000')")
        raise ValueError("fid_input_iscd is required. (e.g. '00000')")
    
    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")

    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '0')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '0')")
    
    if not fid_blng_cls_code:
        logger.error("fid_blng_cls_code is required. (e.g. '0')")
        raise ValueError("fid_blng_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    

    tr_id = "FHPEW02850000"

    

    api_url = "/uapi/elw/v1/ranking/sensitivity"


    

    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_UNAS_INPUT_ISCD": fid_unas_input_iscd,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_INPUT_PRICE_1": fid_input_price_1,
        "FID_INPUT_PRICE_2": fid_input_price_2,
        "FID_INPUT_VOL_1": fid_input_vol_1,
        "FID_INPUT_VOL_2": fid_input_vol_2,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_INPUT_RMNN_DYNU_1": fid_input_rmnn_dynu_1,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_BLNG_CLS_CODE": fid_blng_cls_code,
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
            return sensitivity(
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_unas_input_iscd,
                fid_input_iscd,
                fid_div_cls_code,
                fid_input_price_1,
                fid_input_price_2,
                fid_input_vol_1,
                fid_input_vol_2,
                fid_rank_sort_cls_code,
                fid_input_rmnn_dynu_1,
                fid_input_date_1,
                fid_blng_cls_code,
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
# [국내주식] ELW시세 - ELW 민감도 추이(체결)[국내주식-175]
##############################################################################################

def sensitivity_trend_ccnl(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_input_iscd: str,  # 입력종목코드
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 민감도 추이(체결)[국내주식-175]
    ELW 민감도 추이(체결) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건시장분류코드 (필수)
        fid_input_iscd (str): 입력종목코드 (필수)
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (기본값: None)
        depth (int): 현재 재귀 깊이 (기본값: 0)
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 민감도 추이(체결) 데이터
        
    Example:
        >>> df = sensitivity_trend_ccnl('W', '58J297')
        >>> print(df)
    """
    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")
    
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '58J297')")
        raise ValueError("fid_input_iscd is required. (e.g. '58J297')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    

    tr_id = "FHPEW02830100"

    

    api_url = "/uapi/elw/v1/quotations/sensitivity-trend-ccnl"


    

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
            return sensitivity_trend_ccnl(
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
# [국내주식] ELW시세 - ELW 민감도 추이(일별)[국내주식-176]
##############################################################################################

def sensitivity_trend_daily(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_input_iscd: str,  # 입력종목코드
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 민감도 추이(일별)[국내주식-176]
    ELW 민감도 추이(일별) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건시장분류코드 (필수)
        fid_input_iscd (str): 입력종목코드 (필수)
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (기본값: None)
        depth (int): 현재 재귀 깊이 (기본값: 0)
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 민감도 추이(일별) 데이터
        
    Example:
        >>> df = sensitivity_trend_daily("W", "58J438")
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")
    
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '58J438')")
        raise ValueError("fid_input_iscd is required. (e.g. '58J438')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # API 호출 URL 및 거래 ID 설정

    # 요청 파라미터 설정

    tr_id = "FHPEW02830200"

    api_url = "/uapi/elw/v1/quotations/sensitivity-trend-daily"


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
            return sensitivity_trend_daily(
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
# [국내주식] ELW시세 - ELW 기초자산 목록조회[국내주식-185]
##############################################################################################

def udrl_asset_list(
    fid_cond_scr_div_code: str,  # 조건화면분류코드
    fid_rank_sort_cls_code: str,  # 순위정렬구분코드
    fid_input_iscd: str,  # 입력종목코드
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 기초자산 목록조회[국내주식-185]
    ELW 기초자산 목록조회 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_scr_div_code (str): 조건화면분류코드, 예: '11541'
        fid_rank_sort_cls_code (str): 순위정렬구분코드, 예: '0', '1', '2', '3', '4', '5', '6'
        fid_input_iscd (str): 입력종목코드, 예: '00000', '00003', '00017', '00005'
        tr_cont (str): 연속 거래 여부, 기본값은 공백
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 기초자산 목록조회 데이터
        
    Example:
        >>> df = udrl_asset_list('11541', '0', '00000')
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '11541')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '11541')")

    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '0')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '0')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '00000')")
        raise ValueError("fid_input_iscd is required. (e.g. '00000')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()



    tr_id = "FHKEW154100C0"



    api_url = "/uapi/elw/v1/quotations/udrl-asset-list"




    params = {
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
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
            
        if dataframe is not None:
            dataframe = pd.concat([dataframe, current_data], ignore_index=True)
        else:
            dataframe = current_data
            
        tr_cont = res.getHeader().tr_cont
        
        if tr_cont == "M":
            logger.info("Calling next page...")
            ka.smart_sleep()
            return udrl_asset_list(
                fid_cond_scr_div_code,
                fid_rank_sort_cls_code,
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
# [국내주식] ELW시세 - ELW 기초자산별 종목시세[국내주식-186]
##############################################################################################

def udrl_asset_price(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_cond_scr_div_code: str,  # 조건화면분류코드
    fid_mrkt_cls_code: str,  # 시장구분코드
    fid_input_iscd: str,  # 입력종목코드
    fid_unas_input_iscd: str,  # 기초자산입력종목코드
    fid_vol_cnt: str,  # 거래량수
    fid_trgt_exls_cls_code: str,  # 대상제외구분코드
    fid_input_price_1: str,  # 입력가격1
    fid_input_price_2: str,  # 입력가격2
    fid_input_vol_1: str,  # 입력거래량1
    fid_input_vol_2: str,  # 입력거래량2
    fid_input_rmnn_dynu_1: str,  # 입력잔존일수1
    fid_input_rmnn_dynu_2: str,  # 입력잔존일수2
    fid_option: str,  # 옵션
    fid_input_option_1: str,  # 입력옵션1
    fid_input_option_2: str,  # 입력옵션2
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 기초자산별 종목시세[국내주식-186]
    ELW 기초자산별 종목시세 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 시장구분(W)
        fid_cond_scr_div_code (str): Uniquekey(11541)
        fid_mrkt_cls_code (str): 전체(A),콜(C),풋(P)
        fid_input_iscd (str): '00000(전체), 00003(한국투자증권) , 00017(KB증권), 00005(미래에셋주식회사)'
        fid_unas_input_iscd (str): 기초자산입력종목코드
        fid_vol_cnt (str): 전일거래량(정수량미만)
        fid_trgt_exls_cls_code (str): 거래불가종목제외(0:미체크,1:체크)
        fid_input_price_1 (str): 가격~원이상
        fid_input_price_2 (str): 가격~월이하
        fid_input_vol_1 (str): 거래량~계약이상
        fid_input_vol_2 (str): 거래량~계약이하
        fid_input_rmnn_dynu_1 (str): 잔존일(~일이상)
        fid_input_rmnn_dynu_2 (str): 잔존일(~일이하)
        fid_option (str): 옵션상태(0:없음,1:ATM,2:ITM,3:OTM)
        fid_input_option_1 (str): 입력옵션1
        fid_input_option_2 (str): 입력옵션2
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 기초자산별 종목시세 데이터
        
    Example:
        >>> df = udrl_asset_price(
        ...     fid_cond_mrkt_div_code='W',
        ...     fid_cond_scr_div_code='11541',
        ...     fid_mrkt_cls_code='A',
        ...     fid_input_iscd='00000',
        ...     fid_unas_input_iscd='005930',
        ...     fid_vol_cnt='1000',
        ...     fid_trgt_exls_cls_code='0',
        ...     fid_input_price_1='1000',
        ...     fid_input_price_2='5000',
        ...     fid_input_vol_1='100',
        ...     fid_input_vol_2='500',
        ...     fid_input_rmnn_dynu_1='10',
        ...     fid_input_rmnn_dynu_2='20',
        ...     fid_option='0',
        ...     fid_input_option_1='',
        ...     fid_input_option_2=''
        ... )
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")

    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '11541')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '11541')")

    if not fid_mrkt_cls_code:
        logger.error("fid_mrkt_cls_code is required. (e.g. 'A')")
        raise ValueError("fid_mrkt_cls_code is required. (e.g. 'A')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '00000')")
        raise ValueError("fid_input_iscd is required. (e.g. '00000')")

    if not fid_unas_input_iscd:
        logger.error("fid_unas_input_iscd is required. (e.g. '00001')")
        raise ValueError("fid_unas_input_iscd is required. (e.g. '00001')")

    if not fid_trgt_exls_cls_code:
        logger.error("fid_trgt_exls_cls_code is required. (e.g. '0')")
        raise ValueError("fid_trgt_exls_cls_code is required. (e.g. '0')")

    if not fid_option:
        logger.error("fid_option is required. (e.g. '0')")
        raise ValueError("fid_option is required. (e.g. '0')")


    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()



    tr_id = "FHKEW154101C0"



    api_url = "/uapi/elw/v1/quotations/udrl-asset-price"




    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_MRKT_CLS_CODE": fid_mrkt_cls_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_UNAS_INPUT_ISCD": fid_unas_input_iscd,
        "FID_VOL_CNT": fid_vol_cnt,
        "FID_TRGT_EXLS_CLS_CODE": fid_trgt_exls_cls_code,
        "FID_INPUT_PRICE_1": fid_input_price_1,
        "FID_INPUT_PRICE_2": fid_input_price_2,
        "FID_INPUT_VOL_1": fid_input_vol_1,
        "FID_INPUT_VOL_2": fid_input_vol_2,
        "FID_INPUT_RMNN_DYNU_1": fid_input_rmnn_dynu_1,
        "FID_INPUT_RMNN_DYNU_2": fid_input_rmnn_dynu_2,
        "FID_OPTION": fid_option,
        "FID_INPUT_OPTION_1": fid_input_option_1,
        "FID_INPUT_OPTION_2": fid_input_option_2,
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
            return udrl_asset_price(
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_mrkt_cls_code,
                fid_input_iscd,
                fid_unas_input_iscd,
                fid_vol_cnt,
                fid_trgt_exls_cls_code,
                fid_input_price_1,
                fid_input_price_2,
                fid_input_vol_1,
                fid_input_vol_2,
                fid_input_rmnn_dynu_1,
                fid_input_rmnn_dynu_2,
                fid_option,
                fid_input_option_1,
                fid_input_option_2,
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
# [국내주식] ELW시세 - ELW 상승률순위[국내주식-167]
##############################################################################################

def updown_rate(
    fid_cond_mrkt_div_code: str,  # 사용자권한정보
    fid_cond_scr_div_code: str,  # 거래소코드
    fid_unas_input_iscd: str,  # 상승율/하락율 구분
    fid_input_iscd: str,  # N일자값
    fid_input_rmnn_dynu_1: str,  # 거래량조건
    fid_div_cls_code: str,  # NEXT KEY BUFF
    fid_input_price_1: str,  # 사용자권한정보
    fid_input_price_2: str,  # 거래소코드
    fid_input_vol_1: str,  # 상승율/하락율 구분
    fid_input_vol_2: str,  # N일자값
    fid_input_date_1: str,  # 거래량조건
    fid_rank_sort_cls_code: str,  # NEXT KEY BUFF
    fid_blng_cls_code: str,  # 사용자권한정보
    fid_input_date_2: str,  # 거래소코드
    tr_cont: str = "",
    dataframe: Optional[pd.DataFrame] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 상승률순위[국내주식-167]
    ELW 상승률순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 시장구분코드 (W)
        fid_cond_scr_div_code (str): Unique key(20277)
        fid_unas_input_iscd (str): '000000(전체), 2001(코스피200) , 3003(코스닥150), 005930(삼성전자) '
        fid_input_iscd (str): '00000(전체), 00003(한국투자증권) , 00017(KB증권), 00005(미래에셋주식회사)'
        fid_input_rmnn_dynu_1 (str): '0(전체), 1(1개월이하), 2(1개월~2개월),  3(2개월~3개월), 4(3개월~6개월), 5(6개월~9개월),6(9개월~12개월), 7(12개월이상)'
        fid_div_cls_code (str): 0(전체), 1(콜), 2(풋)
        fid_input_price_1 (str): 
        fid_input_price_2 (str): 
        fid_input_vol_1 (str): 
        fid_input_vol_2 (str): 
        fid_input_date_1 (str): 
        fid_rank_sort_cls_code (str): '0(상승율), 1(하락율), 2(시가대비상승율) , 3(시가대비하락율), 4(변동율)'
        fid_blng_cls_code (str): 0(전체)
        fid_input_date_2 (str): 
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 상승률순위 데이터
        
    Example:
        >>> df = updown_rate(
        ...     fid_cond_mrkt_div_code='W',
        ...     fid_cond_scr_div_code='20277',
        ...     fid_unas_input_iscd='000000',
        ...     fid_input_iscd='00000',
        ...     fid_input_rmnn_dynu_1='0',
        ...     fid_div_cls_code='0',
        ...     fid_input_price_1='',
        ...     fid_input_price_2='',
        ...     fid_input_vol_1='',
        ...     fid_input_vol_2='',
        ...     fid_input_date_1='1',
        ...     fid_rank_sort_cls_code='0',
        ...     fid_blng_cls_code='0',
        ...     fid_input_date_2=''
        ... )
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")

    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20277')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20277')")

    if not fid_unas_input_iscd:
        logger.error("fid_unas_input_iscd is required. (e.g. '000000')")
        raise ValueError("fid_unas_input_iscd is required. (e.g. '000000')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '00000')")
        raise ValueError("fid_input_iscd is required. (e.g. '00000')")

    if not fid_input_rmnn_dynu_1:
        logger.error("fid_input_rmnn_dynu_1 is required. (e.g. '0')")
        raise ValueError("fid_input_rmnn_dynu_1 is required. (e.g. '0')")

    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")

    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '0')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '0')")

    if not fid_blng_cls_code:
        logger.error("fid_blng_cls_code is required. (e.g. '0')")
        raise ValueError("fid_blng_cls_code is required. (e.g. '0')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()



    tr_id = "FHPEW02770000"



    api_url = "/uapi/elw/v1/ranking/updown-rate"




    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_UNAS_INPUT_ISCD": fid_unas_input_iscd,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_RMNN_DYNU_1": fid_input_rmnn_dynu_1,
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_INPUT_PRICE_1": fid_input_price_1,
        "FID_INPUT_PRICE_2": fid_input_price_2,
        "FID_INPUT_VOL_1": fid_input_vol_1,
        "FID_INPUT_VOL_2": fid_input_vol_2,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_BLNG_CLS_CODE": fid_blng_cls_code,
        "FID_INPUT_DATE_2": fid_input_date_2,
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
            return updown_rate(
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_unas_input_iscd,
                fid_input_iscd,
                fid_input_rmnn_dynu_1,
                fid_div_cls_code,
                fid_input_price_1,
                fid_input_price_2,
                fid_input_vol_1,
                fid_input_vol_2,
                fid_input_date_1,
                fid_rank_sort_cls_code,
                fid_blng_cls_code,
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
# [국내주식] ELW시세 - ELW 변동성추이(체결)[국내주식-177]
##############################################################################################

def volatility_trend_ccnl(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_input_iscd: str,  # 입력종목코드
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 변동성추이(체결)[국내주식-177]
    ELW 변동성추이(체결) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건시장분류코드 (필수)
        fid_input_iscd (str): 입력종목코드 (필수)
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (기본값: None)
        depth (int): 현재 재귀 깊이 (기본값: 0)
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 변동성추이(체결) 데이터
        
    Example:
        >>> df = volatility_trend_ccnl("W", "58J297")
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")

    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '58J297')")
        raise ValueError("fid_input_iscd is required. (e.g. '58J297')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    # API 호출 URL 및 거래 ID 설정

    # 요청 파라미터 설정

    tr_id = "FHPEW02840100"

    api_url = "/uapi/elw/v1/quotations/volatility-trend-ccnl"


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
            return volatility_trend_ccnl(
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
# [국내주식] ELW시세 - ELW 변동성추이(일별)[국내주식-178]
##############################################################################################

def volatility_trend_daily(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_input_iscd: str,  # 입력종목코드
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 변동성 추이(일별)[국내주식-178]
    ELW 변동성 추이(일별) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건시장분류코드 (예: 'W')
        fid_input_iscd (str): 입력종목코드 (예: '58J297')
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임 (기본값: None)
        depth (int): 현재 재귀 깊이 (기본값: 0)
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 변동성 추이(일별) 데이터
        
    Example:
        >>> df = volatility_trend_daily('W', '58J297')
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")
    
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '58J297')")
        raise ValueError("fid_input_iscd is required. (e.g. '58J297')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()

    

    tr_id = "FHPEW02840200"

    

    api_url = "/uapi/elw/v1/quotations/volatility-trend-daily"


    

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
            return volatility_trend_daily(
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
# [국내주식] ELW시세 - ELW 변동성추이(분별)[국내주식-179]
##############################################################################################

def volatility_trend_minute(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_input_iscd: str,  # 입력종목코드
    fid_hour_cls_code: str,  # 시간구분코드
    fid_pw_data_incu_yn: str,  # 과거데이터 포함 여부
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 변동성 추이(분별)[국내주식-179]
    ELW 변동성 추이(분별) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건시장분류코드 (예: 'W')
        fid_input_iscd (str): 입력종목코드 (예: '58J297')
        fid_hour_cls_code (str): 시간구분코드 (예: '60', '180', '300', '600', '1800', '3600')
        fid_pw_data_incu_yn (str): 과거데이터 포함 여부 ('N' 또는 'Y')
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 변동성 추이(분별) 데이터
        
    Example:
        >>> df = volatility_trend_minute(
        ...     fid_cond_mrkt_div_code='W',
        ...     fid_input_iscd='58J297',
        ...     fid_hour_cls_code='60',
        ...     fid_pw_data_incu_yn='N'
        ... )
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")
    
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '58J297')")
        raise ValueError("fid_input_iscd is required. (e.g. '58J297')")
    
    if not fid_hour_cls_code:
        logger.error("fid_hour_cls_code is required. (e.g. '60')")
        raise ValueError("fid_hour_cls_code is required. (e.g. '60')")
    
    if not fid_pw_data_incu_yn:
        logger.error("fid_pw_data_incu_yn is required. (e.g. 'N')")
        raise ValueError("fid_pw_data_incu_yn is required. (e.g. 'N')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    # API 호출 URL 및 거래 ID 설정

    # 요청 파라미터 설정

    tr_id = "FHPEW02840300"

    api_url = "/uapi/elw/v1/quotations/volatility-trend-minute"


    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_HOUR_CLS_CODE": fid_hour_cls_code,
        "FID_PW_DATA_INCU_YN": fid_pw_data_incu_yn,
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
            return volatility_trend_minute(
                fid_cond_mrkt_div_code,
                fid_input_iscd,
                fid_hour_cls_code,
                fid_pw_data_incu_yn,
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
# [국내주식] ELW시세 - ELW 변동성추이(틱)[국내주식-180]
##############################################################################################

def volatility_trend_tick(
    fid_cond_mrkt_div_code: str,  # 조건시장분류코드
    fid_input_iscd: str,  # 입력종목코드
    tr_cont: str = "",  # 연속 거래 여부
    dataframe: Optional[pd.DataFrame] = None,  # 누적 데이터프레임
    depth: int = 0,  # 현재 재귀 깊이
    max_depth: int = 10  # 최대 재귀 깊이
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 변동성 추이(틱)[국내주식-180]
    ELW 변동성 추이(틱) API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건시장분류코드 (예: 'W')
        fid_input_iscd (str): 입력종목코드 (예: '58J297')
        tr_cont (str): 연속 거래 여부 (기본값: "")
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 변동성 추이(틱) 데이터
        
    Example:
        >>> df = volatility_trend_tick('W', '58J297')
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")
    
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '58J297')")
        raise ValueError("fid_input_iscd is required. (e.g. '58J297')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()
    
    # API 호출 URL 및 거래 ID 설정

    # 요청 파라미터 설정

    tr_id = "FHPEW02840400"

    api_url = "/uapi/elw/v1/quotations/volatility-trend-tick"


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
            return volatility_trend_tick(
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
# [국내주식] ELW시세 - ELW 거래량순위[국내주식-168]
##############################################################################################

def volume_rank(
        fid_cond_mrkt_div_code: str,  # 조건시장분류코드
        fid_cond_scr_div_code: str,  # 조건화면분류코드
        fid_unas_input_iscd: str,  # 기초자산입력종목코드
        fid_input_iscd: str,  # 발행사
        fid_input_rmnn_dynu_1: str,  # 입력잔존일수
        fid_div_cls_code: str,  # 콜풋구분코드
        fid_input_price_1: str,  # 가격(이상)
        fid_input_price_2: str,  # 가격(이하)
        fid_input_vol_1: str,  # 거래량(이상)
        fid_input_vol_2: str,  # 거래량(이하)
        fid_input_date_1: str,  # 조회기준일
        fid_rank_sort_cls_code: str,  # 순위정렬구분코드
        fid_blng_cls_code: str,  # 소속구분코드
        fid_input_iscd_2: str,  # LP발행사
        fid_input_date_2: str,  # 만기일-최종거래일조회
        tr_cont: str = "",
        dataframe: Optional[pd.DataFrame] = None,
        depth: int = 0,
        max_depth: int = 10
) -> Optional[pd.DataFrame]:
    """
    [국내주식] ELW시세 
    ELW 거래량순위[국내주식-168]
    ELW 거래량순위 API를 호출하여 DataFrame으로 반환합니다.
    
    Args:
        fid_cond_mrkt_div_code (str): 조건시장분류코드 (예: 'W')
        fid_cond_scr_div_code (str): 조건화면분류코드 (예: '20278')
        fid_unas_input_iscd (str): 기초자산입력종목코드 (예: '000000')
        fid_input_iscd (str): 발행사 (예: '00000')
        fid_input_rmnn_dynu_1 (str): 입력잔존일수
        fid_div_cls_code (str): 콜풋구분코드 (예: '0')
        fid_input_price_1 (str): 가격(이상)
        fid_input_price_2 (str): 가격(이하)
        fid_input_vol_1 (str): 거래량(이상)
        fid_input_vol_2 (str): 거래량(이하)
        fid_input_date_1 (str): 조회기준일
        fid_rank_sort_cls_code (str): 순위정렬구분코드 (예: '0')
        fid_blng_cls_code (str): 소속구분코드 (예: '0')
        fid_input_iscd_2 (str): LP발행사 (예: '0000')
        fid_input_date_2 (str): 만기일-최종거래일조회
        tr_cont (str): 연속 거래 여부
        dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        depth (int): 현재 재귀 깊이
        max_depth (int): 최대 재귀 깊이 (기본값: 10)
        
    Returns:
        Optional[pd.DataFrame]: ELW 거래량순위 데이터
        
    Example:
        >>> df = volume_rank(
        ...     fid_cond_mrkt_div_code='W',
        ...     fid_cond_scr_div_code='20278',
        ...     fid_unas_input_iscd='000000',
        ...     fid_input_iscd='00000',
        ...     fid_input_rmnn_dynu_1='',
        ...     fid_div_cls_code='0',
        ...     fid_input_price_1='1000',
        ...     fid_input_price_2='5000',
        ...     fid_input_vol_1='100',
        ...     fid_input_vol_2='1000',
        ...     fid_input_date_1='20230101',
        ...     fid_rank_sort_cls_code='0',
        ...     fid_blng_cls_code='0',
        ...     fid_input_iscd_2='0000',
        ...     fid_input_date_2=''
        ... )
        >>> print(df)
    """
    # 로깅 설정
    logger = logging.getLogger(__name__)

    # 필수 파라미터 검증
    if not fid_cond_mrkt_div_code:
        logger.error("fid_cond_mrkt_div_code is required. (e.g. 'W')")
        raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'W')")
    if not fid_cond_scr_div_code:
        logger.error("fid_cond_scr_div_code is required. (e.g. '20278')")
        raise ValueError("fid_cond_scr_div_code is required. (e.g. '20278')")
    if not fid_unas_input_iscd:
        logger.error("fid_unas_input_iscd is required. (e.g. '000000')")
        raise ValueError("fid_unas_input_iscd is required. (e.g. '000000')")
    if not fid_input_iscd:
        logger.error("fid_input_iscd is required. (e.g. '00000')")
        raise ValueError("fid_input_iscd is required. (e.g. '00000')")
    if not fid_div_cls_code:
        logger.error("fid_div_cls_code is required. (e.g. '0')")
        raise ValueError("fid_div_cls_code is required. (e.g. '0')")
    if not fid_rank_sort_cls_code:
        logger.error("fid_rank_sort_cls_code is required. (e.g. '0')")
        raise ValueError("fid_rank_sort_cls_code is required. (e.g. '0')")
    if not fid_blng_cls_code:
        logger.error("fid_blng_cls_code is required. (e.g. '0')")
        raise ValueError("fid_blng_cls_code is required. (e.g. '0')")
    if not fid_input_iscd_2:
        logger.error("fid_input_iscd_2 is required. (e.g. '0000')")
        raise ValueError("fid_input_iscd_2 is required. (e.g. '0000')")

    # 최대 재귀 깊이 체크
    if depth >= max_depth:
        logger.warning("Maximum recursion depth (%d) reached. Stopping further requests.", max_depth)
        return dataframe if dataframe is not None else pd.DataFrame()



    tr_id = "FHPEW02780000"



    api_url = "/uapi/elw/v1/ranking/volume-rank"




    params = {
        "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
        "FID_UNAS_INPUT_ISCD": fid_unas_input_iscd,
        "FID_INPUT_ISCD": fid_input_iscd,
        "FID_INPUT_RMNN_DYNU_1": fid_input_rmnn_dynu_1,
        "FID_DIV_CLS_CODE": fid_div_cls_code,
        "FID_INPUT_PRICE_1": fid_input_price_1,
        "FID_INPUT_PRICE_2": fid_input_price_2,
        "FID_INPUT_VOL_1": fid_input_vol_1,
        "FID_INPUT_VOL_2": fid_input_vol_2,
        "FID_INPUT_DATE_1": fid_input_date_1,
        "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
        "FID_BLNG_CLS_CODE": fid_blng_cls_code,
        "FID_INPUT_ISCD_2": fid_input_iscd_2,
        "FID_INPUT_DATE_2": fid_input_date_2,
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
            return volume_rank(
                fid_cond_mrkt_div_code,
                fid_cond_scr_div_code,
                fid_unas_input_iscd,
                fid_input_iscd,
                fid_input_rmnn_dynu_1,
                fid_div_cls_code,
                fid_input_price_1,
                fid_input_price_2,
                fid_input_vol_1,
                fid_input_vol_2,
                fid_input_date_1,
                fid_rank_sort_cls_code,
                fid_blng_cls_code,
                fid_input_iscd_2,
                fid_input_date_2,
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

