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

##############################################################################################
# [국내주식] 실시간시세 - ELW 실시간호가[실시간-062]
##############################################################################################

# 컬럼명 매핑
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
    "매도호가1", "매도호가2", "매도호가3", "매도호가4", "매도호가5", "매도호가6", "매도호가7", "매도호가8", "매도호가9", "매도호가10",
    "매수호가1", "매수호가2", "매수호가3", "매수호가4", "매수호가5", "매수호가6", "매수호가7", "매수호가8", "매수호가9", "매수호가10",
    "매도호가잔량1", "매도호가잔량2", "매도호가잔량3", "매도호가잔량4", "매도호가잔량5",
    "매도호가잔량6", "매도호가잔량7", "매도호가잔량8", "매도호가잔량9", "매도호가잔량10",
    "매수호가잔량1", "매수호가잔량2", "매수호가잔량3", "매수호가잔량4", "매수호가잔량5",
    "매수호가잔량6", "매수호가잔량7", "매수호가잔량8", "매수호가잔량9", "매수호가잔량10",
    "총매도호가잔량", "총매수호가잔량", "예상체결가", "예상체결량", "예상체결대비", "예상체결전일대비율",
    "LP매도호가잔량1", "LP매도호가잔량2", "LP매도호가잔량3", "LP매수호가잔량4", "LP매도호가잔량4",
    "LP매수호가잔량5", "LP매도호가잔량5", "LP매수호가잔량6", "LP매도호가잔량6", "LP매수호가잔량7",
    "LP매도호가잔량7", "LP매도호가잔량8", "LP매수호가잔량8", "LP매도호가잔량9", "LP매수호가잔량9",
    "LP매도호가잔량10", "LP매수호가잔량10", "LP매수호가잔량1", "LP총매도호가잔량", "LP매수호가잔량2",
    "LP총매수호가잔량", "LP매수호가잔량3", "예상거래량"
]


def main():
    """
    [국내주식] ELW시세
    ELW 실시간호가[H0EWASP0]
    
    ELW 실시간 호가 정보를 실시간으로 구독하는 웹소켓 API입니다.

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
    logger.info("토큰 발급 중...")
    ka.auth()
    ka.auth_ws()
    logger.info("토큰 발급 완료")

    # 인증(auth_ws()) 이후에 선언
    kws = ka.KISWebSocket(api_url="/tryitout")

    # API 호출 
    logger.info("API 호출 ")
    kws.subscribe(request=elw_asking_price, data=["57LA24","57L739","57L650","57L966","52L181","57LB38"])

    # 결과 표시
    def on_result(ws, tr_id: str, result: pd.DataFrame, data_map: dict):
        try:            
            # 안전한 컬럼명 매핑 (존재하는 컬럼에 대해서만 한글명 적용)
            if not result.empty:
                # 컬럼명 매핑
                existing_columns = {col: COLUMN_MAPPING[col] for col in result.columns if col in COLUMN_MAPPING}
                if existing_columns:
                    result = result.rename(columns=existing_columns)
                    logging.info(f"컬럼명 매핑 완료: {len(existing_columns)}개 컬럼")
                
                # 숫자형 컬럼 소수점 둘째자리까지 표시
                for col in NUMERIC_COLUMNS:
                    # 원본 컬럼명 확인
                    if col in result.columns:
                        result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
                    # 한글명으로 변환된 컬럼명 확인  
                    elif COLUMN_MAPPING.get(col) in result.columns:
                        result[COLUMN_MAPPING[col]] = pd.to_numeric(result[COLUMN_MAPPING[col]], errors='coerce').round(2)
            
            logger.info("=== ELW 실시간호가 결과 ===")
            print(result)
        except Exception as e:
            logging.error(f"결과 처리 중 오류: {e}")
            logging.error(f"받은 데이터: {result}")

    kws.start(on_result=on_result)


if __name__ == "__main__":
    main()