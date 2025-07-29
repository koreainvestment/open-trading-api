"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_time_itemchartprice import inquire_time_itemchartprice

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 기본시세 > 주식당일분봉조회[v1_국내주식-022]
##############################################################################################

COLUMN_MAPPING = {
    'prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비율',
    'stck_prdy_clpr': '전일대비 종가',
    'acml_vol': '누적 거래량',
    'acml_tr_pbmn': '누적 거래대금',
    'hts_kor_isnm': '한글 종목명',
    'stck_prpr': '주식 현재가',
    'stck_bsop_date': '주식 영업일자',
    'stck_cntg_hour': '주식 체결시간',
    'stck_prpr': '주식 현재가',
    'stck_oprc': '주식 시가',
    'stck_hgpr': '주식 최고가',
    'stck_lwpr': '주식 최저가',
    'cntg_vol': '체결 거래량',
    'acml_tr_pbmn': '누적 거래대금'
}

NUMERIC_COLUMNS = []


def main():
    """
    주식당일분봉조회 테스트 함수
    
    이 함수는 주식당일분봉조회 API를 호출하여 결과를 출력합니다.
    테스트 데이터로 삼성전자(005930)를 사용합니다.
    
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
        output1, output2 = inquire_time_itemchartprice(env_dv="real", fid_cond_mrkt_div_code="J",
                                                       fid_input_iscd="005930", fid_input_hour_1="093000",
                                                       fid_pw_data_incu_yn="Y")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # output1 block
    logging.info("사용 가능한 컬럼 (output1): %s", output1.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    output1 = output1.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in output1.columns:
            output1[col] = pd.to_numeric(output1[col], errors='coerce').round(2)

    logging.info("결과 (output1):")
    print(output1)

    # output2 block
    logging.info("사용 가능한 컬럼 (output2): %s", output2.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    output2 = output2.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in output2.columns:
            output2[col] = pd.to_numeric(output2[col], errors='coerce').round(2)

    logging.info("결과 (output2):")
    print(output2)


if __name__ == "__main__":
    main()
