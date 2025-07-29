"""
Created on 2025-07-09
@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from elw_ccnl import elw_ccnl

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 - ELW 실시간체결가[실시간-061]
##############################################################################################

COLUMN_MAPPING = {
    "mksc_shrn_iscd": "유가증권단축종목코드",
    "stck_cntg_hour": "주식체결시간",
    "stck_prpr": "주식현재가",
    "prdy_vrss_sign": "전일대비부호",
    "prdy_vrss": "전일대비",
    "prdy_ctrt": "전일대비율",
    "wghn_avrg_stck_prc": "가중평균주식가격",
    "stck_oprc": "주식시가2",
    "stck_hgpr": "주식최고가",
    "stck_lwpr": "주식최저가",
    "askp1": "매도호가1",
    "bidp1": "매수호가1",
    "cntg_vol": "체결거래량",
    "acml_vol": "누적거래량",
    "acml_tr_pbmn": "누적거래대금",
    "seln_cntg_csnu": "매도체결건수",
    "shnu_cntg_csnu": "매수체결건수",
    "ntby_cntg_csnu": "순매수체결건수",
    "cttr": "체결강도",
    "seln_cntg_smtn": "총매도수량",
    "shnu_cntg_smtn": "총매수수량",
    "cntg_cls_code": "체결구분코드",
    "shnu_rate": "매수2비율",
    "prdy_vol_vrss_acml_vol_rate": "전일거래량대비등락율",
    "oprc_hour": "시가시간",
    "oprc_vrss_prpr_sign": "시가2대비현재가부호",
    "oprc_vrss_prpr": "시가2대비현재가",
    "hgpr_vrss_prpr_sign": "최고가대비현재가부호",
    "hgpr_vrss_prpr": "최고가대비현재가",
    "lwpr_vrss_prpr_sign": "최저가대비현재가부호",
    "lwpr_vrss_prpr": "최저가대비현재가",
    "bsop_date": "기준일자",
    "new_mkop_cls_code": "신규시장분류코드",
    "trht_yn": "거래정지여부",
    "askp_rsqn1": "매도호가잔량1",
    "bidp_rsqn1": "매수호가잔량1",
    "total_askp_rsqn": "총매도호가잔량",
    "total_bidp_rsqn": "총매수호가잔량",
    "vol_rate": "거래량비율",
    "prdy_vrss_vol_rate": "전일대비거래량비율",
    "askp_rsqn_icdc": "매도호가잔량증감",
    "bidp_rsqn_icdc": "매수호가잔량증감",
    "hour_cls_code": "시간구분코드",
    "mrkt_trtm_cls_code": "시장거래시간구분코드",
    "vi_cls_code": "VI구분코드",
    "timr_val": "시간가치값",
    "parity": "패리티",
    "prm_val": "프리미엄값",
    "gear": "기어링",
    "bep_rate": "손익분기비율",
    "itmv_val": "내재가치값",
    "prm_rate": "프리미엄비율",
    "sppt_pnt": "자본지지점",
    "lvrg_val": "레버리지값",
    "delta": "델타",
    "gamma": "감마",
    "vega": "베가",
    "theta": "세타",
    "rho": "로우",
    "hts_antc_vol": "HTS내재변동성",
    "hts_theo_prc": "HTS이론가",
    "vol_tnrt": "거래량회전율",
    "prdy_smns_hour_acml_vol": "전일동시간누적거래량",
    "prdy_smns_hour_acml_vol_rate": "전일동시간누적거래량비율",
    "apprch_rate": "접근도",
    "lp_hvol": "LP보유량",
    "lp_hldn_rate": "LP보유비율",
    "lp_ntby_qty": "LP순매도량"
}

NUMERIC_COLUMNS = [
    "주식현재가", "전일대비", "전일대비율", "가중평균주식가격", "주식시가2", "주식최고가", "주식최저가",
    "매도호가1", "매수호가1", "체결거래량", "누적거래량", "누적거래대금", "매도체결건수", "매수체결건수",
    "순매수체결건수", "체결강도", "총매도수량", "총매수수량", "매수2비율", "전일거래량대비등락율",
    "시가2대비현재가", "최고가대비현재가", "최저가대비현재가", "매도호가잔량1", "매수호가잔량1",
    "총매도호가잔량", "총매수호가잔량", "시간가치값", "패리티", "프리미엄값", "기어링", "손익분기비율",
    "내재가치값", "프리미엄비율", "자본지지점", "레버리지값", "델타", "감마", "베가", "세타", "로우",
    "HTS내재변동성", "HTS이론가", "거래량회전율", "전일동시간누적거래량", "전일동시간누적거래량비율",
    "접근도", "LP보유량", "LP보유비율", "LP순매도량"
]

def main():
    """
    ELW 실시간체결가
    
    ELW 실시간체결가 API입니다.

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

    # API 호출
    logger.info("API 호출")
    kws.subscribe(request=elw_ccnl, data=["57LA24","57L739","57L650","57L966","52L181","57LB38"])

    # 결과 표시
    def on_result(ws, tr_id: str, result: pd.DataFrame, data_map: dict):
        try:
            # 한글 컬럼명으로 변환
            result = result.rename(columns=COLUMN_MAPPING)

            # 숫자형 컬럼 소수점 둘째자리까지 표시
            for col in NUMERIC_COLUMNS:
                if col in result.columns:
                    result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
            
            logging.info("결과:")
            print(result)
        except Exception as e:
            logging.error(f"결과 처리 중 오류: {e}")
            logging.error(f"받은 데이터: {result}")

    kws.start(on_result=on_result)


if __name__ == "__main__":
    main()