"""
Created on 2025-07-09
@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from exp_ccnl_nxt import exp_ccnl_nxt

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간예상체결 (NXT)
##############################################################################################

COLUMN_MAPPING = {
    "MKSC_SHRN_ISCD": "유가증권단축종목코드",
    "STCK_CNTG_HOUR": "주식체결시간",
    "STCK_PRPR": "주식현재가",
    "PRDY_VRSS_SIGN": "전일대비구분",
    "PRDY_VRSS": "전일대비",
    "PRDY_CTRT": "등락율",
    "WGHN_AVRG_STCK_PRC": "가중평균주식가격",
    "STCK_OPRC": "시가",
    "STCK_HGPR": "고가",
    "STCK_LWPR": "저가",
    "ASKP1": "매도호가",
    "BIDP1": "매수호가",
    "CNTG_VOL": "거래량",
    "ACML_VOL": "누적거래량",
    "ACML_TR_PBMN": "누적거래대금",
    "SELN_CNTG_CSNU": "매도체결건수",
    "SHNU_CNTG_CSNU": "매수체결건수",
    "NTBY_CNTG_CSNU": "순매수체결건수",
    "CTTR": "체결강도",
    "SELN_CNTG_SMTN": "총매도수량",
    "SHNU_CNTG_SMTN": "총매수수량",
    "CNTG_CLS_CODE": "체결구분",
    "SHNU_RATE": "매수비율",
    "PRDY_VOL_VRSS_ACML_VOL_RATE": "전일거래량대비등락율",
    "OPRC_HOUR": "시가시간",
    "OPRC_VRSS_PRPR_SIGN": "시가대비구분",
    "OPRC_VRSS_PRPR": "시가대비",
    "HGPR_HOUR": "최고가시간",
    "HGPR_VRSS_PRPR_SIGN": "고가대비구분",
    "HGPR_VRSS_PRPR": "고가대비",
    "LWPR_HOUR": "최저가시간",
    "LWPR_VRSS_PRPR_SIGN": "저가대비구분",
    "LWPR_VRSS_PRPR": "저가대비",
    "BSOP_DATE": "영업일자",
    "NEW_MKOP_CLS_CODE": "신장운영구분코드",
    "TRHT_YN": "거래정지여부",
    "ASKP_RSQN1": "매도호가잔량1",
    "BIDP_RSQN1": "매수호가잔량1",
    "TOTAL_ASKP_RSQN": "총매도호가잔량",
    "TOTAL_BIDP_RSQN": "총매수호가잔량",
    "VOL_TNRT": "거래량회전율",
    "PRDY_SMNS_HOUR_ACML_VOL": "전일동시간누적거래량",
    "PRDY_SMNS_HOUR_ACML_VOL_RATE": "전일동시간누적거래량비율",
    "HOUR_CLS_CODE": "시간구분코드",
    "MRKT_TRTM_CLS_CODE": "임의종료구분코드",
    "VI_STND_PRC": "VI 상태값"
}

NUMERIC_COLUMNS = [
    "주식현재가", "전일대비", "등락율", "가중평균주식가격", "시가", "고가", "저가",
    "매도호가", "매수호가", "거래량", "누적거래량", "누적거래대금", "매도체결건수",
    "매수체결건수", "순매수체결건수", "체결강도", "총매도수량", "총매수수량", "매수비율",
    "전일거래량대비등락율", "시가대비", "고가대비", "저가대비", "매도호가잔량1",
    "매수호가잔량1", "총매도호가잔량", "총매수호가잔량", "거래량회전율", "전일동시간누적거래량",
    "전일동시간누적거래량비율", "VI 상태값"
]


def main():
    """
    국내주식 실시간예상체결 (NXT)
    
    국내주식 실시간예상체결 (NXT) API입니다.
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
    kws.subscribe(
        request=exp_ccnl_nxt,
        data=["005930", "000660", "005380"]
    )

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
