"""
Created on 2025-07-09
@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from index_ccnl import index_ccnl

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 > 국내지수 실시간체결 [실시간-026]
##############################################################################################

COLUMN_MAPPING = {
    "bstp_cls_code": "업종 구분 코드",
    "bsop_hour": "영업 시간",
    "prpr_nmix": "현재가 지수",
    "prdy_vrss_sign": "전일 대비 부호",
    "bstp_nmix_prdy_vrss": "업종 지수 전일 대비",
    "acml_vol": "누적 거래량",
    "acml_tr_pbmn": "누적 거래 대금",
    "pcas_vol": "건별 거래량",
    "pcas_tr_pbmn": "건별 거래 대금",
    "prdy_ctrt": "전일 대비율",
    "oprc_nmix": "시가 지수",
    "nmix_hgpr": "지수 최고가",
    "nmix_lwpr": "지수 최저가",
    "oprc_vrss_nmix_prpr": "시가 대비 지수 현재가",
    "oprc_vrss_nmix_sign": "시가 대비 지수 부호",
    "hgpr_vrss_nmix_prpr": "최고가 대비 지수 현재가",
    "hgpr_vrss_nmix_sign": "최고가 대비 지수 부호",
    "lwpr_vrss_nmix_prpr": "최저가 대비 지수 현재가",
    "lwpr_vrss_nmix_sign": "최저가 대비 지수 부호",
    "prdy_clpr_vrss_oprc_rate": "전일 종가 대비 시가2 비율",
    "prdy_clpr_vrss_hgpr_rate": "전일 종가 대비 최고가 비율",
    "prdy_clpr_vrss_lwpr_rate": "전일 종가 대비 최저가 비율",
    "uplm_issu_cnt": "상한 종목 수",
    "ascn_issu_cnt": "상승 종목 수",
    "stnr_issu_cnt": "보합 종목 수",
    "down_issu_cnt": "하락 종목 수",
    "lslm_issu_cnt": "하한 종목 수",
    "qtqt_ascn_issu_cnt": "기세 상승 종목수",
    "qtqt_down_issu_cnt": "기세 하락 종목수",
    "tick_vrss": "TICK대비"
}
NUMERIC_COLUMNS = [
    "현재가 지수", "업종 지수 전일 대비", "누적 거래량", "누적 거래 대금", "건별 거래량", "건별 거래 대금",
    "전일 대비율", "시가 지수", "지수 최고가", "지수 최저가", "시가 대비 지수 현재가",
    "최고가 대비 지수 현재가", "최저가 대비 지수 현재가", "전일 종가 대비 시가2 비율",
    "전일 종가 대비 최고가 비율", "전일 종가 대비 최저가 비율", "상한 종목 수", "상승 종목 수",
    "보합 종목 수", "하락 종목 수", "하한 종목 수", "기세 상승 종목수", "기세 하락 종목수", "TICK대비"
]


def main():
    """
    국내지수 실시간체결
    
    [참고자료]
종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

[호출 데이터]
헤더와 바디 값을 합쳐 JSON 형태로 전송합니다.

[응답 데이터]
1. 정상 등록 여부 (JSON)
- JSON["body"]["msg1"] - 정상 응답 시, SUBSCRIBE SUCCESS
- JSON["body"]["output"]["iv"] - 실시간 결과 복호화에 필요한 AES256 IV (Initialize Vector)
- JSON["body"]["output"]["key"] - 실시간 결과 복호화에 필요한 AES256 Key

2. 실시간 결과 응답 ( | 로 구분되는 값)
ex) 0|H0STCNT0|004|005930^123929^73100^5^...
- 암호화 유무 : 0 암호화 되지 않은 데이터 / 1 암호화된 데이터
- TR_ID : 등록한 tr_id (ex. H0STCNT0)
- 데이터 건수 : (ex. 001 인 경우 데이터 건수 1건, 004인 경우 데이터 건수 4건)
- 응답 데이터 : 아래 response 데이터 참조 ( ^로 구분됨)
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
    kws.subscribe(request=index_ccnl, data=["0001", "0128"])

    # 결과 표시
    def on_result(ws, tr_id: str, result: pd.DataFrame, data_map: dict):
        try:
            # 컬럼 매핑
            result.rename(columns=COLUMN_MAPPING, inplace=True)

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
