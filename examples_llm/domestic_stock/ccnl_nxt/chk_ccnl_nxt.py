"""
Created on 2025-07-09
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from ccnl_nxt import ccnl_nxt

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간체결가 (NXT)
##############################################################################################


# 컬럼 매핑 정의
COLUMN_MAPPING = {
    "MKSC_SHRN_ISCD": "유가증권단축종목코드",
    "BSOP_HOUR": "영업시간",
    "HOUR_CLS_CODE": "시간구분코드",
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
    "ASKP_RSQN1": "매도호가잔량1",
    "ASKP_RSQN2": "매도호가잔량2",
    "ASKP_RSQN3": "매도호가잔량3",
    "ASKP_RSQN4": "매도호가잔량4",
    "ASKP_RSQN5": "매도호가잔량5",
    "ASKP_RSQN6": "매도호가잔량6",
    "ASKP_RSQN7": "매도호가잔량7",
    "ASKP_RSQN8": "매도호가잔량8",
    "ASKP_RSQN9": "매도호가잔량9",
    "ASKP_RSQN10": "매도호가잔량10",
    "BIDP_RSQN1": "매수호가잔량1",
    "BIDP_RSQN2": "매수호가잔량2",
    "BIDP_RSQN3": "매수호가잔량3",
    "BIDP_RSQN4": "매수호가잔량4",
    "BIDP_RSQN5": "매수호가잔량5",
    "BIDP_RSQN6": "매수호가잔량6",
    "BIDP_RSQN7": "매수호가잔량7",
    "BIDP_RSQN8": "매수호가잔량8",
    "BIDP_RSQN9": "매수호가잔량9",
    "BIDP_RSQN10": "매수호가잔량10",
    "TOTAL_ASKP_RSQN": "총매도호가잔량",
    "TOTAL_BIDP_RSQN": "총매수호가잔량",
    "OVTM_TOTAL_ASKP_RSQN": "장중총매도호가잔량",
    "OVTM_TOTAL_BIDP_RSQN": "장중총매수호가잔량",
    "ANTC_CNPR": "예상체결가격",
    "ANTC_CNQN": "예상체결수량",
    "ANTC_VOL": "예상거래량",
    "ANTC_CNTG_VRSS": "예상체결대비",
    "ANTC_CNTG_VRSS_SIGN": "예상체결대비부호",
    "ANTC_CNTG_PRDY_CTRT": "예상체결전일대비율",
    "ACML_VOL": "누적거래량",
    "TOTAL_ASKP_RSQN_ICDC": "총매도호가잔량ICDC",
    "TOTAL_BIDP_RSQN_ICDC": "총매수호가잔량ICDC",
    "OVTM_TOTAL_ASKP_ICDC": "장중총매도호가ICDC",
    "OVTM_TOTAL_BIDP_ICDC": "장중총매수호가ICDC",
    "STCK_DEAL_CLS_CODE": "주식체결구분코드",
    "NMID_PRC": "정규매매가격",
    "NMID_TOTAL_RSQN": "정규매수총잔량",
    "NMID_CLS_CODE": "정규매매구분코드",
}

NUMERIC_COLUMNS = [
    "유가증권단축종목코드", "영업시간", "시간구분코드",
    "매도호가1", "매도호가2", "매도호가3", "매도호가4", "매도호가5",
    "매도호가6", "매도호가7", "매도호가8", "매도호가9", "매도호가10",
    "매수호가1", "매수호가2", "매수호가3", "매수호가4", "매수호가5",
    "매수호가6", "매수호가7", "매수호가8", "매수호가9", "매수호가10",
    "매도호가잔량1", "매도호가잔량2", "매도호가잔량3", "매도호가잔량4", "매도호가잔량5",
    "매도호가잔량6", "매도호가잔량7", "매도호가잔량8", "매도호가잔량9", "매도호가잔량10",
    "매수호가잔량1", "매수호가잔량2", "매수호가잔량3", "매수호가잔량4", "매수호가잔량5",
    "매수호가잔량6", "매수호가잔량7", "매수호가잔량8", "매수호가잔량9", "매수호가잔량10",
    "총매도호가잔량", "총매수호가잔량", "장중총매도호가잔량", "장중총매수호가잔량",
    "예상체결가격", "예상체결수량", "예상거래량", "예상체결대비", "예상체결전일대비율",
    "누적거래량", "총매도호가잔량ICDC", "총매수호가잔량ICDC", "장중총매도호가ICDC", "장중총매수호가ICDC",
    "정규매매가격", "정규매수총잔량"
]


def main():
    """
    국내주식 실시간체결가 (NXT)
    
    국내주식 실시간체결가 (NXT) API입니다.
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
    kws.subscribe(request=ccnl_nxt, data=["005930", "000660"])

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
