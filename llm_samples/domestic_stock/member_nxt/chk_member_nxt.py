"""
Created on 2025-07-08
@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from member_nxt import member_nxt

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간회원사 (NXT)
##############################################################################################


COLUMN_MAPPING = {
    "MKSC_SHRN_ISCD": "유가증권 단축 종목코드",
    "SELN2_MBCR_NAME1": "매도2 회원사명1",
    "SELN2_MBCR_NAME2": "매도2 회원사명2",
    "SELN2_MBCR_NAME3": "매도2 회원사명3",
    "SELN2_MBCR_NAME4": "매도2 회원사명4",
    "SELN2_MBCR_NAME5": "매도2 회원사명5",
    "BYOV_MBCR_NAME1": "매수 회원사명1",
    "BYOV_MBCR_NAME2": "매수 회원사명2",
    "BYOV_MBCR_NAME3": "매수 회원사명3",
    "BYOV_MBCR_NAME4": "매수 회원사명4",
    "BYOV_MBCR_NAME5": "매수 회원사명5",
    "TOTAL_SELN_QTY1": "총 매도 수량1",
    "TOTAL_SELN_QTY2": "총 매도 수량2",
    "TOTAL_SELN_QTY3": "총 매도 수량3",
    "TOTAL_SELN_QTY4": "총 매도 수량4",
    "TOTAL_SELN_QTY5": "총 매도 수량5",
    "TOTAL_SHNU_QTY1": "총 매수2 수량1",
    "TOTAL_SHNU_QTY2": "총 매수2 수량2",
    "TOTAL_SHNU_QTY3": "총 매수2 수량3",
    "TOTAL_SHNU_QTY4": "총 매수2 수량4",
    "TOTAL_SHNU_QTY5": "총 매수2 수량5",
    "SELN_MBCR_GLOB_YN_1": "매도거래원구분1",
    "SELN_MBCR_GLOB_YN_2": "매도거래원구분2",
    "SELN_MBCR_GLOB_YN_3": "매도거래원구분3",
    "SELN_MBCR_GLOB_YN_4": "매도거래원구분4",
    "SELN_MBCR_GLOB_YN_5": "매도거래원구분5",
    "SHNU_MBCR_GLOB_YN_1": "매수거래원구분1",
    "SHNU_MBCR_GLOB_YN_2": "매수거래원구분2",
    "SHNU_MBCR_GLOB_YN_3": "매수거래원구분3",
    "SHNU_MBCR_GLOB_YN_4": "매수거래원구분4",
    "SHNU_MBCR_GLOB_YN_5": "매수거래원구분5",
    "SELN_MBCR_NO1": "매도거래원코드1",
    "SELN_MBCR_NO2": "매도거래원코드2",
    "SELN_MBCR_NO3": "매도거래원코드3",
    "SELN_MBCR_NO4": "매도거래원코드4",
    "SELN_MBCR_NO5": "매도거래원코드5",
    "SHNU_MBCR_NO1": "매수거래원코드1",
    "SHNU_MBCR_NO2": "매수거래원코드2",
    "SHNU_MBCR_NO3": "매수거래원코드3",
    "SHNU_MBCR_NO4": "매수거래원코드4",
    "SHNU_MBCR_NO5": "매수거래원코드5",
    "SELN_MBCR_RLIM1": "매도 회원사 비중1",
    "SELN_MBCR_RLIM2": "매도 회원사 비중2",
    "SELN_MBCR_RLIM3": "매도 회원사 비중3",
    "SELN_MBCR_RLIM4": "매도 회원사 비중4",
    "SELN_MBCR_RLIM5": "매도 회원사 비중5",
    "SHNU_MBCR_RLIM1": "매수2 회원사 비중1",
    "SHNU_MBCR_RLIM2": "매수2 회원사 비중2",
    "SHNU_MBCR_RLIM3": "매수2 회원사 비중3",
    "SHNU_MBCR_RLIM4": "매수2 회원사 비중4",
    "SHNU_MBCR_RLIM5": "매수2 회원사 비중5",
    "SELN_QTY_ICDC1": "매도 수량 증감1",
    "SELN_QTY_ICDC2": "매도 수량 증감2",
    "SELN_QTY_ICDC3": "매도 수량 증감3",
    "SELN_QTY_ICDC4": "매도 수량 증감4",
    "SELN_QTY_ICDC5": "매도 수량 증감5",
    "SHNU_QTY_ICDC1": "매수2 수량 증감1",
    "SHNU_QTY_ICDC2": "매수2 수량 증감2",
    "SHNU_QTY_ICDC3": "매수2 수량 증감3",
    "SHNU_QTY_ICDC4": "매수2 수량 증감4",
    "SHNU_QTY_ICDC5": "매수2 수량 증감5",
    "GLOB_TOTAL_SELN_QTY": "외국계 총 매도 수량",
    "GLOB_TOTAL_SHNU_QTY": "외국계 총 매수2 수량",
    "GLOB_TOTAL_SELN_QTY_ICDC": "외국계 총 매도 수량 증감",
    "GLOB_TOTAL_SHNU_QTY_ICDC": "외국계 총 매수2 수량 증감",
    "GLOB_NTBY_QTY": "외국계 순매수 수량",
    "GLOB_SELN_RLIM": "외국계 매도 비중",
    "GLOB_SHNU_RLIM": "외국계 매수2 비중",
    "SELN2_MBCR_ENG_NAME1": "매도2 영문회원사명1",
    "SELN2_MBCR_ENG_NAME2": "매도2 영문회원사명2",
    "SELN2_MBCR_ENG_NAME3": "매도2 영문회원사명3",
    "SELN2_MBCR_ENG_NAME4": "매도2 영문회원사명4",
    "SELN2_MBCR_ENG_NAME5": "매도2 영문회원사명5",
    "BYOV_MBCR_ENG_NAME1": "매수 영문회원사명1",
    "BYOV_MBCR_ENG_NAME2": "매수 영문회원사명2",
    "BYOV_MBCR_ENG_NAME3": "매수 영문회원사명3",
    "BYOV_MBCR_ENG_NAME4": "매수 영문회원사명4",
    "BYOV_MBCR_ENG_NAME5": "매수 영문회원사명5"
}

NUMERIC_COLUMNS = [
    "총 매도 수량1", "총 매도 수량2", "총 매도 수량3", "총 매도 수량4", "총 매도 수량5",
    "총 매수2 수량1", "총 매수2 수량2", "총 매수2 수량3", "총 매수2 수량4", "총 매수2 수량5",
    "매도 수량 증감1", "매도 수량 증감2", "매도 수량 증감3", "매도 수량 증감4", "매도 수량 증감5",
    "매수2 수량 증감1", "매수2 수량 증감2", "매수2 수량 증감3", "매수2 수량 증감4", "매수2 수량 증감5",
    "외국계 총 매도 수량", "외국계 총 매수2 수량", "외국계 총 매도 수량 증감", "외국계 총 매수2 수량 증감",
    "외국계 순매수 수량"
]


def main():
    """
    국내주식 실시간회원사 (NXT)
    
    국내주식 실시간회원사 (NXT) API입니다.
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 인증 토큰 발급
    ka.auth()
    ka.auth_ws()

    # 인증(auth_ws()) 이후에 선언
    kws = ka.KISWebSocket(api_url="/tryitout")

    # 조회
    kws.subscribe(request=member_nxt, data=["005930", "000660"])

    # 결과 표시
    def on_result(ws, tr_id: str, result: pd.DataFrame, data_map: dict):
        try:
            # 컬럼 매핑

            # 컬럼명 매핑
            result = result.rename(columns=COLUMN_MAPPING)

            # 숫자형 컬럼 변환
            for col in NUMERIC_COLUMNS:
                if col in result.columns:
                    result[col] = pd.to_numeric(result[col], errors='coerce')

            logging.info("결과:")
            print(result)
        except Exception as e:
            logging.error(f"결과 처리 중 오류: {e}")
            logging.error(f"받은 데이터: {result}")

    kws.start(on_result=on_result)


if __name__ == "__main__":
    main()
