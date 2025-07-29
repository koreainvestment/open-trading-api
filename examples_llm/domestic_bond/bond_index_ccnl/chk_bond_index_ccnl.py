"""
Created on 2025-07-09
@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from bond_index_ccnl import bond_index_ccnl

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [장내채권] 실시간시세 > 채권지수 실시간체결가 [실시간-060]
##############################################################################################

COLUMN_MAPPING = {
    "nmix_id": "지수ID",
    "stnd_date1": "기준일자1",
    "trnm_hour": "전송시간",
    "totl_ernn_nmix_oprc": "총수익지수시가지수",
    "totl_ernn_nmix_hgpr": "총수익지수최고가",
    "totl_ernn_nmix_lwpr": "총수익지수최저가",
    "totl_ernn_nmix": "총수익지수",
    "prdy_totl_ernn_nmix": "전일총수익지수",
    "totl_ernn_nmix_prdy_vrss": "총수익지수전일대비",
    "totl_ernn_nmix_prdy_vrss_sign": "총수익지수전일대비부호",
    "totl_ernn_nmix_prdy_ctrt": "총수익지수전일대비율",
    "clen_prc_nmix": "순가격지수",
    "mrkt_prc_nmix": "시장가격지수",
    "bond_call_rnvs_nmix": "Call재투자지수",
    "bond_zero_rnvs_nmix": "Zero재투자지수",
    "bond_futs_thpr": "선물이론가격",
    "bond_avrg_drtn_val": "평균듀레이션",
    "bond_avrg_cnvx_val": "평균컨벡서티",
    "bond_avrg_ytm_val": "평균YTM",
    "bond_avrg_frdl_ytm_val": "평균선도YTM"
}

NUMERIC_COLUMNS = [
    "총수익지수시가지수", "총수익지수최고가", "총수익지수최저가", "총수익지수",
    "전일총수익지수", "총수익지수전일대비", "총수익지수전일대비율", "순가격지수",
    "시장가격지수", "Call재투자지수", "Zero재투자지수", "선물이론가격"]


def main():
    """
    채권지수 실시간체결가
    
    채권지수 실시간체결가 API입니다.

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
    # 한경채권지수: KBPR01, KBPR02, KBPR03, KBPR04
    # KIS채권지수: KISR01, MSBI07, KTBL10, MSBI09, MSBI10, CDIX01
    # 매경채권지수: MKFR01, MSBI01, MSBI03, MSBI10, CORP01
    kws.subscribe(request=bond_index_ccnl, data=[
        # 한경채권지수
        "KBPR01", "KBPR02", "KBPR03", "KBPR04",
        # KIS채권지수
        "KISR01", "MSBI07", "KTBL10", "MSBI09", "MSBI10", "CDIX01",
        # 매경채권지수
        "MKFR01", "MSBI01", "MSBI03", "MSBI10", "CORP01"
    ])

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
