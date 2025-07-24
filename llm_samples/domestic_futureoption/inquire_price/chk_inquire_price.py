"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_price import inquire_price

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 기본시세 > 선물옵션 시세[v1_국내선물-006]
##############################################################################################

COLUMN_MAPPING = {
    'hts_kor_isnm': 'HTS 한글 종목명',
    'futs_prpr': '선물 현재가',
    'futs_prdy_vrss': '선물 전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'futs_prdy_clpr': '선물 전일 종가',
    'futs_prdy_ctrt': '선물 전일 대비율',
    'acml_vol': '누적 거래량',
    'acml_tr_pbmn': '누적 거래 대금',
    'hts_otst_stpl_qty': 'HTS 미결제 약정 수량',
    'otst_stpl_qty_icdc': '미결제 약정 수량 증감',
    'futs_oprc': '선물 시가2',
    'futs_hgpr': '선물 최고가',
    'futs_lwpr': '선물 최저가',
    'futs_mxpr': '선물 상한가',
    'futs_llam': '선물 하한가',
    'basis': '베이시스',
    'futs_sdpr': '선물 기준가',
    'hts_thpr': 'HTS 이론가',
    'dprt': '괴리율',
    'crbr_aply_mxpr': '서킷브레이커 적용 상한가',
    'crbr_aply_llam': '서킷브레이커 적용 하한가',
    'futs_last_tr_date': '선물 최종 거래 일자',
    'hts_rmnn_dynu': 'HTS 잔존 일수',
    'futs_lstn_medm_hgpr': '선물 상장 중 최고가',
    'futs_lstn_medm_lwpr': '선물 상장 중 최저가',
    'delta_val': '델타 값',
    'gama': '감마',
    'theta': '세타',
    'vega': '베가',
    'rho': '로우',
    'hist_vltl': '역사적 변동성',
    'hts_ints_vltl': 'HTS 내재 변동성',
    'mrkt_basis': '시장 베이시스',
    'acpr': '행사가',
    'bstp_cls_code': '업종 구분 코드',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'bstp_nmix_prpr': '업종 지수 현재가',
    'prdy_vrss_sign': '전일 대비 부호',
    'bstp_nmix_prdy_vrss': '업종 지수 전일 대비',
    'bstp_nmix_prdy_ctrt': '업종 지수 전일 대비율'
}

NUMERIC_COLUMNS = []


def main():
    """
    선물옵션 시세 조회 테스트 함수
    
    이 함수는 선물옵션 시세 API를 호출하여 결과를 출력합니다.
    테스트 데이터로 101S09 종목을 사용합니다.
    
    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 인증 토큰 발급
    ka.auth()

    # case1 조회
    logging.info("=== case1 조회 ===")
    try:
        result1, result2, result3 = inquire_price(
            fid_cond_mrkt_div_code="F",
            fid_input_iscd="101W09",
            env_dv="real"
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # output1 처리
    logging.info("=== output1 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())

    # 컬럼명 한글 변환
    result1 = result1.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result1)

    # output2 처리
    logging.info("=== output2 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result2.columns.tolist())

    # 컬럼명 한글 변환
    result2 = result2.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result2)

    # output3 처리
    logging.info("=== output3 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result3.columns.tolist())

    # 컬럼명 한글 변환
    result3 = result3.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result3.columns:
            result3[col] = pd.to_numeric(result3[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result3)


if __name__ == "__main__":
    main()
