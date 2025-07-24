"""
Created on 20250601
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

from stock_futures_realtime_conclusion import stock_futures_realtime_conclusion

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 실시간시세 > 주식선물 실시간체결가 [실시간-029]
##############################################################################################

COLUMN_MAPPING = {
    "futs_shrn_iscd": "선물단축종목코드",
    "bsop_hour": "영업시간",
    "stck_prpr": "주식현재가",
    "prdy_vrss_sign": "전일대비부호",
    "prdy_vrss": "전일대비",
    "futs_prdy_ctrt": "선물전일대비율",
    "stck_oprc": "주식시가2",
    "stck_hgpr": "주식최고가",
    "stck_lwpr": "주식최저가",
    "last_cnqn": "최종거래량",
    "acml_vol": "누적거래량",
    "acml_tr_pbmn": "누적거래대금",
    "hts_thpr": "HTS이론가",
    "mrkt_basis": "시장베이시스",
    "dprt": "괴리율",
    "nmsc_fctn_stpl_prc": "근월물약정가",
    "fmsc_fctn_stpl_prc": "원월물약정가",
    "spead_prc": "스프레드1",
    "hts_otst_stpl_qty": "HTS미결제약정수량",
    "otst_stpl_qty_icdc": "미결제약정수량증감",
    "oprc_hour": "시가시간",
    "oprc_vrss_prpr_sign": "시가2대비현재가부호",
    "oprc_vrss_prpr": "시가2대비현재가",
    "hgpr_hour": "최고가시간",
    "hgpr_vrss_prpr_sign": "최고가대비현재가부호",
    "hgpr_vrss_prpr": "최고가대비현재가",
    "lwpr_hour": "최저가시간",
    "lwpr_vrss_prpr_sign": "최저가대비현재가부호",
    "lwpr_vrss_prpr": "최저가대비현재가",
    "shnu_rate": "매수2비율",
    "cttr": "체결강도",
    "esdg": "괴리도",
    "otst_stpl_rgbf_qty_icdc": "미결제약정직전수량증감",
    "thpr_basis": "이론베이시스",
    "askp1": "매도호가1",
    "bidp1": "매수호가1",
    "askp_rsqn1": "매도호가잔량1",
    "bidp_rsqn1": "매수호가잔량1",
    "seln_cntg_csnu": "매도체결건수",
    "shnu_cntg_csnu": "매수체결건수",
    "ntby_cntg_csnu": "순매수체결건수",
    "seln_cntg_smtn": "총매도수량",
    "shnu_cntg_smtn": "총매수수량",
    "total_askp_rsqn": "총매도호가잔량",
    "total_bidp_rsqn": "총매수호가잔량",
    "prdy_vol_vrss_acml_vol_rate": "전일거래량대비등락율",
    "dynm_mxpr": "실시간상한가",
    "dynm_llam": "실시간하한가",
    "dynm_prc_limt_yn": "실시간가격제한구분"
}

NUMERIC_COLUMNS = []


def main():
    """
   주식선물 실시간체결가

    Returns:
        None
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
    kws.subscribe(request=stock_futures_realtime_conclusion, data=["111W08"])

    # 결과 표시
    def on_result(ws, tr_id: str, result: pd.DataFrame, data_map: dict):

        result = result.rename(columns=COLUMN_MAPPING)

        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

        logging.info("결과:")
        print(result)

    kws.start(on_result=on_result)


if __name__ == "__main__":
    main()
