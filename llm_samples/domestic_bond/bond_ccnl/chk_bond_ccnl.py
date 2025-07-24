"""
Created on 2025-07-09
@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from bond_ccnl import bond_ccnl

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [장내채권] 실시간정보 > 일반채권 실시간체결가 [H0BJCNT0]
##############################################################################################

COLUMN_MAPPING = {
    "stnd_iscd": "표준종목코드",
    "bond_isnm": "채권종목명",
    "stck_cntg_hour": "주식체결시간",
    "prdy_vrss_sign": "전일대비부호",
    "prdy_vrss": "전일대비",
    "prdy_ctrt": "전일대비율",
    "stck_prpr": "현재가",
    "cntg_vol": "체결거래량",
    "stck_oprc": "시가",
    "stck_hgpr": "고가",
    "stck_lwpr": "저가",
    "stck_prdy_clpr": "전일종가",
    "bond_cntg_ert": "현재수익률",
    "oprc_ert": "시가수익률",
    "hgpr_ert": "고가수익률",
    "lwpr_ert": "저가수익률",
    "acml_vol": "누적거래량",
    "prdy_vol": "전일거래량",
    "cntg_type_cls_code": "체결유형코드"
}

NUMERIC_COLUMNS = [
    "전일대비", "전일대비율", "현재가", "체결거래량", "시가", "고가", "저가", "전일종가",
    "현재수익률", "시가수익률", "고가수익률", "저가수익률", "누적거래량", "전일거래량"
]


def main():
    """
    일반채권 실시간체결가
    
    일반채권 실시간체결가 API입니다.

[참고자료]
실시간시세(웹소켓) 파이썬 샘플코드는 한국투자증권 Github 참고 부탁드립니다.
https://github.com/koreainvestment/open-trading-api/blob/main/websocket/python/ws_domestic_overseas_all.py

실시간시세(웹소켓) API 사용방법에 대한 자세한 설명은 한국투자증권 Wikidocs 참고 부탁드립니다.
https://wikidocs.net/book/7847 (국내주식 업데이트 완료, 추후 해외주식·국내선물옵션 업데이트 예정)

채권 종목코드 마스터파일은 "포럼 &gt;  FAQ &gt; 종목정보 다운로드(국내) &gt; 장내채권 - 채권코드" 참고 부탁드립니다.

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
    kws.subscribe(request=bond_ccnl, data=["KR103502GA34", "KR6095572D81"])

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
