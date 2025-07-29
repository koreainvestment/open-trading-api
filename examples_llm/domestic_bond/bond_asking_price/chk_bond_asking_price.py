"""
Created on 2025-07-09
@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from bond_asking_price import bond_asking_price

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [장내채권] 실시간시세 > 일반채권 실시간호가 [실시간-053]
##############################################################################################

COLUMN_MAPPING = {
    "stnd_iscd": "표준종목코드",
    "stck_cntg_hour": "주식체결시간",
    "askp_ert1": "매도호가수익률1",
    "bidp_ert1": "매수호가수익률1",
    "askp1": "매도호가1",
    "bidp1": "매수호가1",
    "askp_rsqn1": "매도호가잔량1",
    "bidp_rsqn1": "매수호가잔량1",
    "askp_ert2": "매도호가수익률2",
    "bidp_ert2": "매수호가수익률2",
    "askp2": "매도호가2",
    "bidp2": "매수호가2",
    "askp_rsqn2": "매도호가잔량2",
    "bidp_rsqn2": "매수호가잔량2",
    "askp_ert3": "매도호가수익률3",
    "bidp_ert3": "매수호가수익률3",
    "askp3": "매도호가3",
    "bidp3": "매수호가3",
    "askp_rsqn3": "매도호가잔량3",
    "bidp_rsqn3": "매수호가잔량3",
    "askp_ert4": "매도호가수익률4",
    "bidp_ert4": "매수호가수익률4",
    "askp4": "매도호가4",
    "bidp4": "매수호가4",
    "askp_rsqn4": "매도호가잔량4",
    "bidp_rsqn4": "매수호가잔량4",
    "askp_ert5": "매도호가수익률5",
    "bidp_ert5": "매수호가수익률5",
    "askp5": "매도호가5",
    "bidp5": "매수호가5",
    "askp_rsqn52": "매도호가잔량5",
    "bidp_rsqn53": "매수호가잔량5",
    "total_askp_rsqn": "총매도호가잔량",
    "total_bidp_rsqn": "총매수호가잔량"
}

NUMERIC_COLUMNS = [
    "매도호가수익률1", "매수호가수익률1", "매도호가1", "매수호가1", "매도호가잔량1", "매수호가잔량1",
    "매도호가수익률2", "매수호가수익률2", "매도호가2", "매수호가2", "매도호가잔량2", "매수호가잔량2",
    "매도호가수익률3", "매수호가수익률3", "매도호가3", "매수호가3", "매도호가잔량3", "매수호가잔량3",
    "매도호가수익률4", "매수호가수익률4", "매도호가4", "매수호가4", "매도호가잔량4", "매수호가잔량4",
    "매도호가수익률5", "매수호가수익률5", "매도호가5", "매수호가5", "매도호가잔량5", "매수호가잔량5",
    "총매도호가잔량", "총매수호가잔량"
]


def main():
    """
    일반채권 실시간호가
    
    일반채권 실시간호가 API입니다.

[참고자료]
채권 종목코드 마스터파일은 "KIS포털 - API문서 - 종목정보파일 - 장내채권 - 채권코드" 참고 부탁드립니다.

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
    kws.subscribe(request=bond_asking_price, data=["KR103502GA34", "KR6095572D81"])

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
