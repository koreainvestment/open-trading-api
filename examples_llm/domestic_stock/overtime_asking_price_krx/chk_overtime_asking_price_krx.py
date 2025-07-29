"""
Created on 2025-07-09
@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from overtime_asking_price_krx import overtime_asking_price_krx

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 시간외 실시간호가 (KRX) [실시간-025]
##############################################################################################

COLUMN_MAPPING = {
    "mksc_shrn_iscd": "유가증권단축종목코드",
    "bsop_hour": "영업시간",
    "hour_cls_code": "시간구분코드",
    "askp1": "매도호가1",
    "askp2": "매도호가2",
    "askp3": "매도호가3",
    "askp4": "매도호가4",
    "askp5": "매도호가5",
    "askp6": "매도호가6",
    "askp7": "매도호가7",
    "askp8": "매도호가8",
    "askp9": "매도호가9",
    "bidp1": "매수호가1",
    "bidp2": "매수호가2",
    "bidp3": "매수호가3",
    "bidp4": "매수호가4",
    "bidp5": "매수호가5",
    "bidp6": "매수호가6",
    "bidp7": "매수호가7",
    "bidp8": "매수호가8",
    "bidp9": "매수호가9",
    "askp_rsqn1": "매도호가잔량1",
    "askp_rsqn2": "매도호가잔량2",
    "askp_rsqn3": "매도호가잔량3",
    "askp_rsqn4": "매도호가잔량4",
    "askp_rsqn5": "매도호가잔량5",
    "askp_rsqn6": "매도호가잔량6",
    "askp_rsqn7": "매도호가잔량7",
    "askp_rsqn8": "매도호가잔량8",
    "askp_rsqn9": "매도호가잔량9",
    "bidp_rsqn1": "매수호가잔량1",
    "bidp_rsqn2": "매수호가잔량2",
    "bidp_rsqn3": "매수호가잔량3",
    "bidp_rsqn4": "매수호가잔량4",
    "bidp_rsqn5": "매수호가잔량5",
    "bidp_rsqn6": "매수호가잔량6",
    "bidp_rsqn7": "매수호가잔량7",
    "bidp_rsqn8": "매수호가잔량8",
    "bidp_rsqn9": "매수호가잔량9",
    "total_askp_rsqn": "총매도호가잔량",
    "total_bidp_rsqn": "총매수호가잔량",
    "ovtm_total_askp_rsqn": "시간외총매도호가잔량",
    "ovtm_total_bidp_rsqn": "시간외총매수호가잔량",
    "antc_cnpr": "예상체결가",
    "antc_cnqn": "예상체결량",
    "antc_vol": "예상거래량",
    "antc_cntg_vrss": "예상체결대비",
    "antc_cntg_vrss_sign": "예상체결대비부호",
    "antc_cntg_prdy_ctrt": "예상체결전일대비율",
    "acml_vol": "누적거래량",
    "total_askp_rsqn_icdc": "총매도호가잔량증감",
    "total_bidp_rsqn_icdc": "총매수호가잔량증감",
    "ovtm_total_askp_icdc": "시간외총매도호가증감",
    "ovtm_total_bidp_icdc": "시간외총매수호가증감"
}

NUMERIC_COLUMNS = [
    "매도호가1", "매도호가2", "매도호가3", "매도호가4", "매도호가5",
    "매도호가6", "매도호가7", "매도호가8", "매도호가9",
    "매수호가1", "매수호가2", "매수호가3", "매수호가4", "매수호가5",
    "매수호가6", "매수호가7", "매수호가8", "매수호가9",
    "매도호가잔량1", "매도호가잔량2", "매도호가잔량3", "매도호가잔량4",
    "매도호가잔량5", "매도호가잔량6", "매도호가잔량7", "매도호가잔량8",
    "매도호가잔량9", "매수호가잔량1", "매수호가잔량2", "매수호가잔량3",
    "매수호가잔량4", "매수호가잔량5", "매수호가잔량6", "매수호가잔량7",
    "매수호가잔량8", "매수호가잔량9", "총매도호가잔량", "총매수호가잔량",
    "시간외총매도호가잔량", "시간외총매수호가잔량", "예상체결가", "예상체결량",
    "예상거래량", "예상체결대비", "예상체결전일대비율", "누적거래량",
    "총매도호가잔량증감", "총매수호가잔량증감", "시간외총매도호가증감",
    "시간외총매수호가증감"
]


def main():
    """
    국내주식 시간외 실시간호가 (KRX)
    
    국내주식 시간외 실시간호가 API입니다.
국내주식 시간외 단일가(16:00~18:00) 시간대에 실시간호가 데이터 확인 가능합니다.

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
    kws.subscribe(request=overtime_asking_price_krx, data=["023460"])

    # 결과 표시
    def on_result(ws, tr_id: str, result: pd.DataFrame, data_map: dict):
        try:
            # 컬럼명 매핑 적용
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
