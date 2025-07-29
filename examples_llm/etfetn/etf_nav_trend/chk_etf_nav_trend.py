"""
Created on 2025-07-09
@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from etf_nav_trend import etf_nav_trend

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 > 국내ETF NAV추이[실시간-051]
##############################################################################################

# 컬럼명 매핑
COLUMN_MAPPING = {
    "rt_cd": "성공 실패 여부",
    "msg_cd": "응답코드",
    "mksc_shrn_iscd": "유가증권단축종목코드",
    "nav": "NAV",
    "nav_prdy_vrss_sign": "NAV전일대비부호",
    "nav_prdy_vrss": "NAV전일대비",
    "nav_prdy_ctrt": "NAV전일대비율",
    "oprc_nav": "NAV시가",
    "hprc_nav": "NAV고가",
    "lprc_nav": "NAV저가"
}

# 숫자형 컬럼
NUMERIC_COLUMNS = ["NAV", "NAV전일대비", "NAV전일대비율", "NAV시가", "NAV고가", "NAV저가"]

def main():
    """
    국내ETF NAV추이
    
    [참고자료]
종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
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
    kws.subscribe(request=etf_nav_trend, data=["069500"])

    # 결과 표시
    def on_result(ws, tr_id: str, result: pd.DataFrame, data_map: dict):
        try:
            # 한글 컬럼명으로 변환
            result.rename(columns=COLUMN_MAPPING, inplace=True)

            # 숫자형 컬럼 소수점 둘째자리까지 표시
            for col in NUMERIC_COLUMNS:
                if col in result.columns:
                    result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

            logging.info("API 호출")
            print(result)
        except Exception as e:
            logging.error(f"결과 처리 중 오류: {e}")
            logging.error(f"받은 데이터: {result}")

    kws.start(on_result=on_result)


if __name__ == "__main__":
    main()