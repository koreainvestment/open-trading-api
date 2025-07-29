"""
Created on 2025-07-09
@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from overtime_ccnl_krx import overtime_ccnl_krx

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 시간외 실시간체결가 (KRX) [실시간-042]
##############################################################################################


COLUMN_MAPPING = {
    "mksc_shrn_iscd": "유가증권단축종목코드",
    "stck_cntg_hour": "주식체결시간",
    "stck_prpr": "주식현재가",
    "prdy_vrss_sign": "전일대비구분",
    "prdy_vrss": "전일대비",
    "prdy_ctrt": "등락율",
    "wghn_avrg_stck_prc": "가중평균주식가격",
    "stck_oprc": "시가",
    "stck_hgpr": "고가",
    "stck_lwpr": "저가",
    "askp1": "매도호가",
    "bidp1": "매수호가",
    "cntg_vol": "거래량",
    "acml_vol": "누적거래량",
    "acml_tr_pbmn": "누적거래대금",
    "seln_cntg_csnu": "매도체결건수",
    "shnu_cntg_csnu": "매수체결건수",
    "ntby_cntg_csnu": "순매수체결건수",
    "cttr": "체결강도",
    "seln_cntg_smtn": "총매도수량",
    "shnu_cntg_smtn": "총매수수량",
    "cntg_cls_code": "체결구분",
    "shnu_rate": "매수비율",
    "prdy_vol_vrss_acml_vol_rate": "전일거래량대비등락율",
    "oprc_hour": "시가시간",
    "oprc_vrss_prpr_sign": "시가대비구분",
    "oprc_vrss_prpr": "시가대비",
    "hgpr_hour": "최고가시간",
    "hgpr_vrss_prpr_sign": "고가대비구분",
    "hgpr_vrss_prpr": "고가대비",
    "lwpr_hour": "최저가시간",
    "lwpr_vrss_prpr_sign": "저가대비구분",
    "lwpr_vrss_prpr": "저가대비",
    "bsop_date": "영업일자",
    "new_mkop_cls_code": "신장운영구분코드",
    "trht_yn": "거래정지여부",
    "askp_rsqn1": "매도호가잔량1",
    "bidp_rsqn1": "매수호가잔량1",
    "total_askp_rsqn": "총매도호가잔량",
    "total_bidp_rsqn": "총매수호가잔량",
    "vol_tnrt": "거래량회전율",
    "prdy_smns_hour_acml_vol": "전일동시간누적거래량",
    "prdy_smns_hour_acml_vol_rate": "전일동시간누적거래량비율"
}

NUMERIC_COLUMNS = [
    "주식현재가", "전일대비", "등락율", "가중평균주식가격", "시가", "고가", "저가",
    "매도호가", "매수호가", "거래량", "누적거래량", "누적거래대금", "매도체결건수",
    "매수체결건수", "순매수체결건수", "체결강도", "총매도수량", "총매수수량", "매수비율",
    "전일거래량대비등락율", "시가대비", "고가대비", "저가대비", "매도호가잔량1",
    "매수호가잔량1", "총매도호가잔량", "총매수호가잔량", "거래량회전율",
    "전일동시간누적거래량", "전일동시간누적거래량비율"
]


def main():
    """
    국내주식 시간외 실시간체결가 (KRX)
    
    국내주식 시간외 실시간체결가 API입니다.
국내주식 시간외 단일가(16:00~18:00) 시간대에 실시간체결가 데이터 확인 가능합니다.

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
    kws.subscribe(request=overtime_ccnl_krx, data=["023460", "199480", "462860", "440790", "000660"])

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
