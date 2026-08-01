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
# [국내주식] 순위분석 > 등락률 순위[v1_국내주식-088]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/ranking/fluctuation"

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

    res = ka._url_fetch(API_URL, tr_id, tr_cont, params)

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
        res.printError(API_URL)
        return pd.DataFrame()
