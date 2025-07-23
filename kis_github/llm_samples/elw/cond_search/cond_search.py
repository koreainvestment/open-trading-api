"""
Created on 2025-06-19

@author: LaivData jjlee with cursor
"""

import logging
import time
from typing import Optional
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] ELW시세 - ELW 종목검색[국내주식-166]
##############################################################################################

# 상수 정의
API_URL = "/uapi/elw/v1/quotations/cond-search"


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
    tr_id = "FHKEW15100000"

    # 요청 파라미터 설정
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
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

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
        res.printError(API_URL)
        return pd.DataFrame()  # 빈 데이터프레임 반환
