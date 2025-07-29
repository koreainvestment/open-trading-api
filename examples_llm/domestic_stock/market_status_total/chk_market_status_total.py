"""
Created on 2025-07-08
@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from market_status_total import market_status_total

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 장운영정보(통합)
##############################################################################################

COLUMN_MAPPING = {
    "TRHT_YN": "거래정지 여부",
    "TR_SUSP_REAS_CNTT": "거래 정지 사유 내용",
    "MKOP_CLS_CODE": "장운영 구분 코드",
    "ANTC_MKOP_CLS_CODE": "예상 장운영 구분 코드",
    "MRKT_TRTM_CLS_CODE": "임의연장구분코드",
    "DIVI_APP_CLS_CODE": "동시호가배분처리구분코드",
    "ISCD_STAT_CLS_CODE": "종목상태구분코드",
    "VI_CLS_CODE": "VI적용구분코드",
    "OVTM_VI_CLS_CODE": "시간외단일가VI적용구분코드",
    "EXCH_CLS_CODE": "거래소 구분코드"
}

NUMERIC_COLUMNS = []


def main():
    """
    국내주식 장운영정보 (통합)
    
    국내주식 장운영정보 (통합) API입니다.
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
    kws.subscribe(request=market_status_total, data=["158430"])

    # 결과 표시
    def on_result(ws, tr_id: str, result: pd.DataFrame, data_map: dict):
        try:
            # 컬럼 매핑
            result.rename(columns=COLUMN_MAPPING, inplace=True)

            for col in NUMERIC_COLUMNS:
                if col in result.columns:
                    result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

            logging.info("결과:")
            print(result)
        except Exception as e:
            logging.error(f"결과 처리 중 오류: {e}")
            logging.error(f"받은 데이터: {result}")

    kws.start(on_result=on_result)


if __name__ == "__main__":
    main()
