"""
Created on 2025-07-09
@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from elw_asking_price import elw_asking_price

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 컬럼명 매핑
COLUMN_MAP = {
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
    "askp10": "매도호가10",
    "bidp1": "매수호가1",
    "bidp2": "매수호가2",
    "bidp3": "매수호가3",
    "bidp4": "매수호가4",
    "bidp5": "매수호가5",
    "bidp6": "매수호가6",
    "bidp7": "매수호가7",
    "bidp8": "매수호가8",
    "bidp9": "매수호가9",
    "bidp10": "매수호가10",
    "askp_rsqn1": "매도호가잔량1",
    "askp_rsqn2": "매도호가잔량2",
    "askp_rsqn3": "매도호가잔량3",
    "askp_rsqn4": "매도호가잔량4",
    "askp_rsqn5": "매도호가잔량5",
    "askp_rsqn6": "매도호가잔량6",
    "askp_rsqn7": "매도호가잔량7",
    "askp_rsqn8": "매도호가잔량8",
    "askp_rsqn9": "매도호가잔량9",
    "askp_rsqn10": "매도호가잔량10",
    "bidp_rsqn1": "매수호가잔량1",
    "bidp_rsqn2": "매수호가잔량2",
    "bidp_rsqn3": "매수호가잔량3",
    "bidp_rsqn4": "매수호가잔량4",
    "bidp_rsqn5": "매수호가잔량5",
    "bidp_rsqn6": "매수호가잔량6",
    "bidp_rsqn7": "매수호가잔량7",
    "bidp_rsqn8": "매수호가잔량8",
    "bidp_rsqn9": "매수호가잔량9",
    "bidp_rsqn10": "매수호가잔량10",
    "total_askp_rsqn": "총매도호가잔량",
    "total_bidp_rsqn": "총매수호가잔량",
    "antc_cnpr": "예상체결가",
    "antc_cnqn": "예상체결량",
    "antc_cntg_vrss_sign": "예상체결대비부호",
    "antc_cntg_vrss": "예상체결대비",
    "antc_cntg_prdy_ctrt": "예상체결전일대비율",
    "lp_askp_rsqn1": "LP매도호가잔량1",
    "lp_askp_rsqn2": "LP매도호가잔량2",
    "lp_askp_rsqn3": "LP매도호가잔량3",
    "lp_bidp_rsqn4": "LP매수호가잔량4",
    "lp_askp_rsqn4": "LP매도호가잔량4",
    "lp_bidp_rsqn5": "LP매수호가잔량5",
    "lp_askp_rsqn5": "LP매도호가잔량5",
    "lp_bidp_rsqn6": "LP매수호가잔량6",
    "lp_askp_rsqn6": "LP매도호가잔량6",
    "lp_bidp_rsqn7": "LP매수호가잔량7",
    "lp_askp_rsqn7": "LP매도호가잔량7",
    "lp_askp_rsqn8": "LP매도호가잔량8",
    "lp_bidp_rsqn8": "LP매수호가잔량8",
    "lp_askp_rsqn9": "LP매도호가잔량9",
    "lp_bidp_rsqn9": "LP매수호가잔량9",
    "lp_askp_rsqn10": "LP매도호가잔량10",
    "lp_bidp_rsqn10": "LP매수호가잔량10",
    "lp_bidp_rsqn1": "LP매수호가잔량1",
    "lp_total_askp_rsqn": "LP총매도호가잔량",
    "lp_bidp_rsqn2": "LP매수호가잔량2",
    "lp_total_bidp_rsqn": "LP총매수호가잔량",
    "lp_bidp_rsqn3": "LP매수호가잔량3",
    "antc_vol": "예상거래량"
}

# 숫자형 컬럼 리스트 (문자열 컬럼 제외)
NUMERIC_COLUMNS = [
    "askp1", "askp2", "askp3", "askp4", "askp5", "askp6", "askp7", "askp8", "askp9", "askp10",
    "bidp1", "bidp2", "bidp3", "bidp4", "bidp5", "bidp6", "bidp7", "bidp8", "bidp9", "bidp10",
    "askp_rsqn1", "askp_rsqn2", "askp_rsqn3", "askp_rsqn4", "askp_rsqn5", 
    "askp_rsqn6", "askp_rsqn7", "askp_rsqn8", "askp_rsqn9", "askp_rsqn10",
    "bidp_rsqn1", "bidp_rsqn2", "bidp_rsqn3", "bidp_rsqn4", "bidp_rsqn5",
    "bidp_rsqn6", "bidp_rsqn7", "bidp_rsqn8", "bidp_rsqn9", "bidp_rsqn10",
    "total_askp_rsqn", "total_bidp_rsqn", "antc_cnpr", "antc_cnqn", "antc_cntg_vrss", "antc_cntg_prdy_ctrt",
    "lp_askp_rsqn1", "lp_askp_rsqn2", "lp_askp_rsqn3", "lp_bidp_rsqn4", "lp_askp_rsqn4",
    "lp_bidp_rsqn5", "lp_askp_rsqn5", "lp_bidp_rsqn6", "lp_askp_rsqn6", "lp_bidp_rsqn7",
    "lp_askp_rsqn7", "lp_askp_rsqn8", "lp_bidp_rsqn8", "lp_askp_rsqn9", "lp_bidp_rsqn9",
    "lp_askp_rsqn10", "lp_bidp_rsqn10", "lp_bidp_rsqn1", "lp_total_askp_rsqn", "lp_bidp_rsqn2",
    "lp_total_bidp_rsqn", "lp_bidp_rsqn3", "antc_vol"
]


def main():
    """
    ELW 실시간호가
    
    ELW 실시간호가 API입니다.

[참고자료]
실시간시세(웹소켓) 파이썬 샘플코드는 한국투자증권 Github 참고 부탁드립니다.
https://github.com/koreainvestment/open-trading-api/blob/main/websocket/python/ws_domestic_overseas_all.py

실시간시세(웹소켓) API 사용방법에 대한 자세한 설명은 한국투자증권 Wikidocs 참고 부탁드립니다.
https://wikidocs.net/book/7847 (국내주식 업데이트 완료, 추후 해외주식·국내선물옵션 업데이트 예정)

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
    kws.subscribe(request=elw_asking_price, data=["57LA24","57L739","57L650","57L966","52L181","57LB38"])

    # 결과 표시
    def on_result(ws, tr_id: str, result: pd.DataFrame, data_map: dict):
        try:            
            # 안전한 컬럼명 매핑 (존재하는 컬럼에 대해서만 한글명 적용)
            if not result.empty:
                # 컬럼명 매핑
                existing_columns = {col: COLUMN_MAP[col] for col in result.columns if col in COLUMN_MAP}
                if existing_columns:
                    result = result.rename(columns=existing_columns)
                    logging.info(f"컬럼명 매핑 완료: {len(existing_columns)}개 컬럼")
                
                # 안전한 숫자형 컬럼 변환 (존재하는 컬럼에 대해서만 적용)
                numeric_columns_to_convert = [col for col in NUMERIC_COLUMNS if col in result.columns]
                if numeric_columns_to_convert:
                    for col in numeric_columns_to_convert:
                        try:
                            # 한글명으로 변환된 컬럼이 있는지 확인
                            tarcol = COLUMN_MAP.get(col, col)
                            if tarcol in result.columns:
                                result[tarcol] = pd.to_numeric(result[tarcol], errors='coerce')
                        except Exception as e:
                            logging.warning(f"컬럼 '{col}' 숫자 변환 실패: {e}")
                    logging.info(f"숫자형 변환 완료: {len(numeric_columns_to_convert)}개 컬럼")
            
            logging.info("결과:")
            print(result)
        except Exception as e:
            logging.error(f"결과 처리 중 오류: {e}")
            logging.error(f"받은 데이터: {result}")

    kws.start(on_result=on_result)


if __name__ == "__main__":
    main()