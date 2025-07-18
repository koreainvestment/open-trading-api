"""
Created on 20250601
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from index_option_realtime_conclusion import index_option_realtime_conclusion

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 실시간시세 > 지수옵션 실시간체결가[실시간-014]
##############################################################################################

COLUMN_MAPPING = {
    "optn_shrn_iscd": "옵션 단축 종목코드",
    "bsop_hour": "영업 시간",
    "optn_prpr": "옵션 현재가",
    "prdy_vrss_sign": "전일 대비 부호",
    "optn_prdy_vrss": "옵션 전일 대비",
    "prdy_ctrt": "전일 대비율",
    "optn_oprc": "옵션 시가2",
    "optn_hgpr": "옵션 최고가",
    "optn_lwpr": "옵션 최저가",
    "last_cnqn": "최종 거래량",
    "acml_vol": "누적 거래량",
    "acml_tr_pbmn": "누적 거래 대금",
    "hts_thpr": "HTS 이론가",
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
    "prmm_val": "프리미엄 값",
    "invl_val": "내재가치 값",
    "tmvl_val": "시간가치 값",
    "delta": "델타",
    "gama": "감마",
    "vega": "베가",
    "theta": "세타",
    "rho": "로우",
    "hts_ints_vltl": "HTS 내재 변동성",
    "esdg": "괴리도",
    "otst_stpl_rgbf_qty_icdc": "미결제 약정 직전 수량 증감",
    "thpr_basis": "이론 베이시스",
    "unas_hist_vltl": "역사적변동성",
    "cttr": "체결강도",
    "dprt": "괴리율",
    "mrkt_basis": "시장 베이시스",
    "optn_askp1": "옵션 매도호가1",
    "optn_bidp1": "옵션 매수호가1",
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
    "avrg_vltl": "평균 변동성",
    "dscs_lrqn_vol": "협의대량누적 거래량",
    "dynm_mxpr": "실시간상한가",
    "dynm_llam": "실시간하한가",
    "dynm_prc_limt_yn": "실시간가격제한구분"
}

NUMERIC_COLUMNS = []


def main():
    """
   지수옵션 실시간체결가

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
    kws.subscribe(request=index_option_realtime_conclusion, data=["201W08427"])

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
