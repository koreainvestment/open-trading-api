"""
Created on 2025-07-09
@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from asking_price_krx import asking_price_krx

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간 호가 (KRX) [H0STASP0]
##############################################################################################

COLUMN_MAPPING = {
    "MKSC_SHRN_ISCD": "유가증권 단축 종목코드",
    "BSOP_HOUR": "영업 시간",
    "HOUR_CLS_CODE": "시간 구분 코드",
    "ASKP1": "매도호가1",
    "ASKP2": "매도호가2",
    "ASKP3": "매도호가3",
    "ASKP4": "매도호가4",
    "ASKP5": "매도호가5",
    "ASKP6": "매도호가6",
    "ASKP7": "매도호가7",
    "ASKP8": "매도호가8",
    "ASKP9": "매도호가9",
    "ASKP10": "매도호가10",
    "BIDP1": "매수호가1",
    "BIDP2": "매수호가2",
    "BIDP3": "매수호가3",
    "BIDP4": "매수호가4",
    "BIDP5": "매수호가5",
    "BIDP6": "매수호가6",
    "BIDP7": "매수호가7",
    "BIDP8": "매수호가8",
    "BIDP9": "매수호가9",
    "BIDP10": "매수호가10",
    "ASKP_RSQN1": "매도호가 잔량1",
    "ASKP_RSQN2": "매도호가 잔량2",
    "ASKP_RSQN3": "매도호가 잔량3",
    "ASKP_RSQN4": "매도호가 잔량4",
    "ASKP_RSQN5": "매도호가 잔량5",
    "ASKP_RSQN6": "매도호가 잔량6",
    "ASKP_RSQN7": "매도호가 잔량7",
    "ASKP_RSQN8": "매도호가 잔량8",
    "ASKP_RSQN9": "매도호가 잔량9",
    "ASKP_RSQN10": "매도호가 잔량10",
    "BIDP_RSQN1": "매수호가 잔량1",
    "BIDP_RSQN2": "매수호가 잔량2",
    "BIDP_RSQN3": "매수호가 잔량3",
    "BIDP_RSQN4": "매수호가 잔량4",
    "BIDP_RSQN5": "매수호가 잔량5",
    "BIDP_RSQN6": "매수호가 잔량6",
    "BIDP_RSQN7": "매수호가 잔량7",
    "BIDP_RSQN8": "매수호가 잔량8",
    "BIDP_RSQN9": "매수호가 잔량9",
    "BIDP_RSQN10": "매수호가 잔량10",
    "TOTAL_ASKP_RSQN": "총 매도호가 잔량",
    "TOTAL_BIDP_RSQN": "총 매수호가 잔량",
    "OVTM_TOTAL_ASKP_RSQN": "시간외 총 매도호가 잔량",
    "OVTM_TOTAL_BIDP_RSQN": "시간외 총 매수호가 잔량",
    "ANTC_CNPR": "예상 체결가",
    "ANTC_CNQN": "예상 체결량",
    "ANTC_VOL": "예상 거래량",
    "ANTC_CNTG_VRSS": "예상 체결 대비",
    "ANTC_CNTG_VRSS_SIGN": "예상 체결 대비 부호",
    "ANTC_CNTG_PRDY_CTRT": "예상 체결 전일 대비율",
    "ACML_VOL": "누적 거래량",
    "TOTAL_ASKP_RSQN_ICDC": "총 매도호가 잔량 증감",
    "TOTAL_BIDP_RSQN_ICDC": "총 매수호가 잔량 증감",
    "OVTM_TOTAL_ASKP_ICDC": "시간외 총 매도호가 증감",
    "OVTM_TOTAL_BIDP_ICDC": "시간외 총 매수호가 증감",
    "STCK_DEAL_CLS_CODE": "주식 매매 구분 코드"
}

NUMERIC_COLUMNS = [
    "매도호가1", "매도호가2", "매도호가3", "매도호가4", "매도호가5",
    "매도호가6", "매도호가7", "매도호가8", "매도호가9", "매도호가10",
    "매수호가1", "매수호가2", "매수호가3", "매수호가4", "매수호가5",
    "매수호가6", "매수호가7", "매수호가8", "매수호가9", "매수호가10",
    "매도호가 잔량1", "매도호가 잔량2", "매도호가 잔량3", "매도호가 잔량4", "매도호가 잔량5",
    "매도호가 잔량6", "매도호가 잔량7", "매도호가 잔량8", "매도호가 잔량9", "매도호가 잔량10",
    "매수호가 잔량1", "매수호가 잔량2", "매수호가 잔량3", "매수호가 잔량4", "매수호가 잔량5",
    "매수호가 잔량6", "매수호가 잔량7", "매수호가 잔량8", "매수호가 잔량9", "매수호가 잔량10",
    "총 매도호가 잔량", "총 매수호가 잔량", "시간외 총 매도호가 잔량", "시간외 총 매수호가 잔량",
    "예상 체결가", "예상 체결량", "예상 거래량", "예상 체결 대비", "예상 체결 전일 대비율",
    "누적 거래량", "총 매도호가 잔량 증감", "총 매수호가 잔량 증감", "시간외 총 매도호가 증감", "시간외 총 매수호가 증감"
]


def main():
    """
    국내주식 실시간호가 (KRX)
    
    [참고자료]
실시간시세(웹소켓) 파이썬 샘플코드는 한국투자증권 Github 참고 부탁드립니다.
https://github.com/koreainvestment/open-trading-api/blob/main/websocket/python/ws_domestic_overseas_all.py

실시간시세(웹소켓) API 사용방법에 대한 자세한 설명은 한국투자증권 Wikidocs 참고 부탁드립니다.
https://wikidocs.net/book/7847 (국내주식 업데이트 완료, 추후 해외주식·국내선물옵션 업데이트 예정)

[호출 데이터]
헤더와 바디 값을 합쳐 JSON 형태로 전송합니다.

[응답 데이터]
1. 정상 등록 여부 (JSON)
- JSON["body"]["msg1"] - 정상 응답 시, SUBSCRIBE SUCCESS
- JSON["body"]["output"]["iv"] - 실시간 결과 복호화에 필요한 AES256 IV (Initialize Vector)
- JSON["body"]["output"]["key"] - 실시간 결과 복호화에 필요한 AES256 Key

2. 실시간 결과 응답 ( | 로 구분되는 값)
- 암호화 유무 : 0 암호화 되지 않은 데이터 / 1 암호화된 데이터
- TR_ID : 등록한 tr_id
- 데이터 건수 : (ex. 001 데이터 건수를 참조하여 활용)
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
    kws.subscribe(request=asking_price_krx, data=["005930", "000660"])

    # 결과 표시
    def on_result(ws, tr_id: str, result: pd.DataFrame, data_map: dict):
        try:
            # 컬럼명 매핑
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
