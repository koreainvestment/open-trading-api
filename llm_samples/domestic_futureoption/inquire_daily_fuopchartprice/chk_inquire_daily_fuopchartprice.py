"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_daily_fuopchartprice import inquire_daily_fuopchartprice

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 기본시세 > 선물옵션기간별시세(일/주/월/년)[v1_국내선물-008]
##############################################################################################

COLUMN_MAPPING = {
    'futs_prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'futs_prdy_ctrt': '선물 전일 대비율',
    'futs_prdy_clpr': '선물 전일 종가',
    'acml_vol': '누적 거래량',
    'acml_tr_pbmn': '누적 거래 대금',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'futs_prpr': '현재가',
    'futs_shrn_iscd': '단축 종목코드',
    'prdy_vol': '전일 거래량',
    'futs_mxpr': '상한가',
    'futs_llam': '하한가',
    'futs_oprc': '시가',
    'futs_hgpr': '최고가',
    'futs_lwpr': '최저가',
    'futs_prdy_oprc': '전일 시가',
    'futs_prdy_hgpr': '전일 최고가',
    'futs_prdy_lwpr': '전일 최저가',
    'futs_askp': '매도호가',
    'futs_bidp': '매수호가',
    'basis': '베이시스',
    'kospi200_nmix': 'KOSPI200 지수',
    'kospi200_prdy_vrss': 'KOSPI200 전일 대비',
    'kospi200_prdy_ctrt': 'KOSPI200 전일 대비율',
    'kospi200_prdy_vrss_sign': '전일 대비 부호',
    'hts_otst_stpl_qty': 'HTS 미결제 약정 수량',
    'otst_stpl_qty_icdc': '미결제 약정 수량 증감',
    'tday_rltv': '당일 체결강도',
    'hts_thpr': 'HTS 이론가',
    'dprt': '괴리율',
    'stck_bsop_date': '영업 일자',
    'futs_prpr': '현재가',
    'futs_oprc': '시가',
    'futs_hgpr': '최고가',
    'futs_lwpr': '최저가',
    'acml_vol': '누적 거래량',
    'acml_tr_pbmn': '누적 거래 대금',
    'mod_yn': '변경 여부'
}

NUMERIC_COLUMNS = []


def main():
    """
    선물옵션기간별시세 조회 테스트 함수
    
    이 함수는 선물옵션기간별시세 API를 호출하여 결과를 출력합니다.
    
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
        output1, output2 = inquire_daily_fuopchartprice(
            fid_cond_mrkt_div_code="F",
            fid_input_iscd="101S09",
            fid_input_date_1="20220301",
            fid_input_date_2="20220810",
            fid_period_div_code="D",
            env_dv="real"
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # output1 처리
    logging.info("=== output1 결과 ===")
    logging.info("사용 가능한 컬럼: %s", output1.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    output1 = output1.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in output1.columns:
            output1[col] = pd.to_numeric(output1[col], errors='coerce').round(2)

    logging.info("결과:")
    print(output1)

    # output2 처리
    logging.info("=== output2 결과 ===")
    logging.info("사용 가능한 컬럼: %s" % output2.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    output2 = output2.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in output2.columns:
            output2[col] = pd.to_numeric(output2[col], errors='coerce').round(2)

    logging.info("결과:")
    print(output2)


if __name__ == "__main__":
    main()
