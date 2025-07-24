"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_time_fuopchartprice import inquire_time_fuopchartprice

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 기본시세 > 선물옵션 분봉조회[v1_국내선물-012]
##############################################################################################

COLUMN_MAPPING = {
    'futs_prdy_vrss': '선물 전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'futs_prdy_ctrt': '선물 전일 대비율',
    'futs_prdy_clpr': '선물 전일 종가',
    'prdy_nmix': '전일 지수',
    'acml_vol': '누적 거래량',
    'acml_tr_pbmn': '누적 거래 대금',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'futs_prpr': '선물 현재가',
    'futs_shrn_iscd': '선물 단축 종목코드',
    'prdy_vol': '전일 거래량',
    'futs_mxpr': '선물 상한가',
    'futs_llam': '선물 하한가',
    'futs_oprc': '선물 시가2',
    'futs_hgpr': '선물 최고가',
    'futs_lwpr': '선물 최저가',
    'futs_prdy_oprc': '선물 전일 시가',
    'futs_prdy_hgpr': '선물 전일 최고가',
    'futs_prdy_lwpr': '선물 전일 최저가',
    'futs_askp': '선물 매도호가',
    'futs_bidp': '선물 매수호가',
    'basis': '베이시스',
    'kospi200_nmix': 'KOSPI200 지수',
    'kospi200_prdy_vrss': 'KOSPI200 전일 대비',
    'kospi200_prdy_ctrt': 'KOSPI200 전일 대비율',
    'kospi200_prdy_vrss_sign': 'KOSPI200 전일 대비 부호',
    'hts_otst_stpl_qty': 'HTS 미결제 약정 수량',
    'otst_stpl_qty_icdc': '미결제 약정 수량 증감',
    'tday_rltv': '당일 체결강도',
    'hts_thpr': 'HTS 이론가',
    'dprt': '괴리율',
    'stck_bsop_date': '주식 영업 일자',
    'stck_cntg_hour': '주식 체결 시간',
    'futs_prpr': '선물 현재가',
    'futs_oprc': '선물 시가2',
    'futs_hgpr': '선물 최고가',
    'futs_lwpr': '선물 최저가',
    'cntg_vol': '체결 거래량',
    'acml_tr_pbmn': '누적 거래 대금'
}

NUMERIC_COLUMNS = []


def main():
    """
    선물옵션 분봉조회 테스트 함수
    
    이 함수는 선물옵션 분봉조회 API를 호출하여 결과를 출력합니다.
    
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
        result1, result2 = inquire_time_fuopchartprice(
            fid_cond_mrkt_div_code="F",
            fid_input_iscd="101T12",
            fid_hour_cls_code="60",
            fid_pw_data_incu_yn="Y",
            fid_fake_tick_incu_yn="N",
            fid_input_date_1="20230901",
            fid_input_hour_1="100000"
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
    logging.info("사용 가능한 컬럼: %s" % result2.columns.tolist())

    # 컬럼명 한글 변환
    result2 = result2.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result2)


if __name__ == "__main__":
    main()
