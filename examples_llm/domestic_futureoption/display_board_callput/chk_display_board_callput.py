"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""
import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from display_board_callput import display_board_callput

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 기본시세 > 국내옵션전광판_콜풋[국내선물-022]
##############################################################################################

# 컬럼명 한글 변환 및 데이터 출력
COLUMN_MAPPING = {
    'acpr': '행사가',
    'unch_prpr': '환산 현재가',
    'optn_shrn_iscd': '옵션 단축 종목코드',
    'optn_prpr': '옵션 현재가',
    'optn_prdy_vrss': '옵션 전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'optn_prdy_ctrt': '옵션 전일 대비율',
    'optn_bidp': '옵션 매수호가',
    'optn_askp': '옵션 매도호가',
    'tmvl_val': '시간가치 값',
    'nmix_sdpr': '지수 기준가',
    'acml_vol': '누적 거래량',
    'seln_rsqn': '매도 잔량',
    'shnu_rsqn': '매수2 잔량',
    'acml_tr_pbmn': '누적 거래 대금',
    'hts_otst_stpl_qty': 'HTS 미결제 약정 수량',
    'otst_stpl_qty_icdc': '미결제 약정 수량 증감',
    'delta_val': '델타 값',
    'gama': '감마',
    'vega': '베가',
    'theta': '세타',
    'rho': '로우',
    'hts_ints_vltl': 'HTS 내재 변동성',
    'invl_val': '내재가치 값',
    'esdg': '괴리도',
    'dprt': '괴리율',
    'hist_vltl': '역사적 변동성',
    'hts_thpr': 'HTS 이론가',
    'optn_oprc': '옵션 시가2',
    'optn_hgpr': '옵션 최고가',
    'optn_lwpr': '옵션 최저가',
    'optn_mxpr': '옵션 상한가',
    'optn_llam': '옵션 하한가',
    'atm_cls_name': 'ATM 구분 명',
    'rgbf_vrss_icdc': '직전 대비 증감',
    'total_askp_rsqn': '총 매도호가 잔량',
    'total_bidp_rsqn': '총 매수호가 잔량',
    'futs_antc_cnpr': '선물예상체결가',
    'futs_antc_cntg_vrss': '선물예상체결대비',
    'antc_cntg_vrss_sign': '예상 체결 대비 부호',
    'antc_cntg_prdy_ctrt': '예상 체결 전일 대비율',
}

NUMERIC_COLUMNS = []


def main():
    """
    국내옵션전광판_콜풋 조회 테스트 함수
    
    이 함수는 국내옵션전광판_콜풋 API를 호출하여 결과를 출력합니다.
    
    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 인증 토큰 발급
    ka.auth()

    # Case1 테스트
    logging.info("=== Case1 테스트 ===")
    try:
        result1, result2 = display_board_callput(
            fid_cond_mrkt_div_code="O",
            fid_cond_scr_div_code="20503",
            fid_mrkt_cls_code="CO",
            fid_mtrt_cnt="202508",
            fid_mrkt_cls_code1="PO"
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # Output1 처리
    logging.info("=== Output1 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())

    result1 = result1.rename(columns=COLUMN_MAPPING)

    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result1)

    # Output2 처리
    logging.info("=== Output2 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result2.columns.tolist())

    result2 = result2.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에 number 자료형 없음)

    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result2)


if __name__ == "__main__":
    main()
