import logging
import sys
import time
from typing import Optional

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


##############################################################################################
# [국내주식] 순위분석 > 국내주식 재무비율 순위[v1_국내주식-092]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/ranking/finance-ratio"

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
    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

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
        res.printError(API_URL)
        return pd.DataFrame()
