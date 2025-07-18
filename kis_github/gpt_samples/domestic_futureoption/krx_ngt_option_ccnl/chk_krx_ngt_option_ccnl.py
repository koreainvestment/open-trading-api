"""
Created on 20250601
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from krx_ngt_option_ccnl import krx_ngt_option_ccnl

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 실시간시세 > KRX야간옵션 실시간체결가 [실시간-032]
##############################################################################################

COLUMN_MAPPING = {
    "optn_shrn_iscd": "옵션단축종목코드",
    "bsop_hour": "영업시간",
    "optn_prpr": "옵션현재가",
    "prdy_vrss_sign": "전일대비부호",
    "optn_prdy_vrss": "옵션전일대비",
    "prdy_ctrt": "전일대비율",
    "optn_oprc": "옵션시가2",
    "optn_hgpr": "옵션최고가",
    "optn_lwpr": "옵션최저가",
    "last_cnqn": "최종거래량",
    "acml_vol": "누적거래량",
    "acml_tr_pbmn": "누적거래대금",
    "hts_thpr": "HTS이론가",
    "hts_otst_stpl_qty": "HTS미결제약정수량",
    "otst_stpl_qty_icdc": "미결제약정수량증감",
    "oprc_hour": "시가시간",
    "oprc_vrss_prpr_sign": "시가2대비현재가부호",
    "oprc_vrss_nmix_prpr": "시가대비지수현재가",
    "hgpr_hour": "최고가시간",
    "hgpr_vrss_prpr_sign": "최고가대비현재가부호",
    "hgpr_vrss_nmix_prpr": "최고가대비지수현재가",
    "lwpr_hour": "최저가시간",
    "lwpr_vrss_prpr_sign": "최저가대비현재가부호",
    "lwpr_vrss_nmix_prpr": "최저가대비지수현재가",
    "shnu_rate": "매수2비율",
    "prmm_val": "프리미엄값",
    "invl_val": "내재가치값",
    "tmvl_val": "시간가치값",
    "delta": "델타",
    "gama": "감마",
    "vega": "베가",
    "theta": "세타",
    "rho": "로우",
    "hts_ints_vltl": "HTS내재변동성",
    "esdg": "괴리도",
    "otst_stpl_rgbf_qty_icdc": "미결제약정직전수량증감",
    "thpr_basis": "이론베이시스",
    "unas_hist_vltl": "역사적변동성",
    "cttr": "체결강도",
    "dprt": "괴리율",
    "mrkt_basis": "시장베이시스",
    "optn_askp1": "옵션매도호가1",
    "optn_bidp1": "옵션매수호가1",
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
    "dynm_prc_limt_yn": "실시간가격제한구분",
    "dynm_llam": "실시간하한가"
}

NUMERIC_COLUMNS = []


def main():
    """
    KRX야간옵션 실시간체결가

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
    kws.subscribe(request=krx_ngt_option_ccnl, data=["101W9000"])

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
