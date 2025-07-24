"""
Created on 20250601
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from krx_ngt_futures_ccnl import krx_ngt_futures_ccnl

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 실시간시세 > KRX야간선물 실시간종목체결 [실시간-064]
##############################################################################################

COLUMN_MAPPING = {
    "futs_shrn_iscd": "선물 단축 종목코드",
    "bsop_hour": "영업 시간",
    "futs_prdy_vrss": "선물 전일 대비",
    "prdy_vrss_sign": "전일 대비 부호",
    "futs_prdy_ctrt": "선물 전일 대비율",
    "futs_prpr": "선물 현재가",
    "futs_oprc": "선물 시가2",
    "futs_hgpr": "선물 최고가",
    "futs_lwpr": "선물 최저가",
    "last_cnqn": "최종 거래량",
    "acml_vol": "누적 거래량",
    "acml_tr_pbmn": "누적 거래 대금",
    "hts_thpr": "HTS 이론가",
    "mrkt_basis": "시장 베이시스",
    "dprt": "괴리율",
    "nmsc_fctn_stpl_prc": "근월물 약정가",
    "fmsc_fctn_stpl_prc": "원월물 약정가",
    "spead_prc": "스프레드1",
    "hts_otst_stpl_qty": "HTS 미결제 약정 수량",
    "otst_stpl_qty_icdc": "미결제 약정 수량 증감",
    "oprc_hour": "시가 시간",
    "oprc_vrss_prpr_sign": "시가2 대비 현재가 부호",
    "oprc_vrss_nmix_prpr": "시가 대비 지수 현재가",
    "hgpr_hour": "최고가 시간",
    "hgpr_vrss_prpr_sign": "최고가 대비 현재가 부호",
    "hgpr_vrss_nmix_prpr": "최고가 대비 지수 현재가",
    "lwpr_hour": "최저가 시간",
    "lwpr_vrss_prpr_sign": "최저가 대비 현재가 부호",
    "lwpr_vrss_nmix_prpr": "최저가 대비 지수 현재가",
    "shnu_rate": "매수2 비율",
    "cttr": "체결강도",
    "esdg": "괴리도",
    "otst_stpl_rgbf_qty_icdc": "미결제 약정 직전 수량 증감",
    "thpr_basis": "이론 베이시스",
    "futs_askp1": "선물 매도호가1",
    "futs_bidp1": "선물 매수호가1",
    "askp_rsqn1": "매도호가 잔량1",
    "bidp_rsqn1": "매수호가 잔량1",
    "seln_cntg_csnu": "매도 체결 건수",
    "shnu_cntg_csnu": "매수 체결 건수",
    "ntby_cntg_csnu": "순매수 체결 건수",
    "seln_cntg_smtn": "총 매도 수량",
    "shnu_cntg_smtn": "총 매수 수량",
    "total_askp_rsqn": "총 매도호가 잔량",
    "total_bidp_rsqn": "총 매수호가 잔량",
    "prdy_vol_vrss_acml_vol_rate": "전일 거래량 대비 등락율",
    "dynm_mxpr": "실시간상한가",
    "dynm_llam": "실시간하한가",
    "dynm_prc_limt_yn": "실시간가격제한구분"
}

NUMERIC_COLUMNS = []


def main():
    """
    [국내선물옵션] 실시간시세 > KRX야간선물 실시간종목체결

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
    kws.subscribe(request=krx_ngt_futures_ccnl, data=["101W9000"])

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
