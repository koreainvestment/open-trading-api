"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""
import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from display_board_top import display_board_top

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 기본시세 > 국내선물 기초자산 시세[국내선물-021]
##############################################################################################

COLUMN_MAPPING = {
    'unas_prpr': '기초자산 현재가',
    'unas_prdy_vrss': '기초자산 전일 대비',
    'unas_prdy_vrss_sign': '기초자산 전일 대비 부호',
    'unas_prdy_ctrt': '기초자산 전일 대비율',
    'unas_acml_vol': '기초자산 누적 거래량',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'futs_prpr': '선물 현재가',
    'futs_prdy_vrss': '선물 전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'futs_prdy_ctrt': '선물 전일 대비율',
    'hts_rmnn_dynu': 'HTS 잔존 일수'
}

NUMERIC_COLUMNS = []


def main():
    """
    국내선물 기초자산 시세 조회 테스트 함수
    
    이 함수는 국내선물 기초자산 시세 API를 호출하여 결과를 출력합니다.
    
    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 인증 토큰 발급
    ka.auth()

    logging.info("=== 국내선물 기초자산 시세 조회 ===")
    try:
        output1, output2 = display_board_top(fid_cond_mrkt_div_code="F", fid_input_iscd="101W09")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # output1 처리
    logging.info("=== output1 결과 ===")
    logging.info("사용 가능한 컬럼: %s", output1.columns.tolist())

    # 컬럼명 한글 변환

    output1 = output1.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시

    for col in NUMERIC_COLUMNS:
        if col in output1.columns:
            output1[col] = pd.to_numeric(output1[col], errors='coerce').round(2)

    logging.info("결과:")
    print(output1)

    # output2 처리
    logging.info("=== output2 결과 ===")
    logging.info("사용 가능한 컬럼: %s", output2.columns.tolist())

    # 컬럼명 한글 변환
    output2 = output2.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in output2.columns:
            output2[col] = pd.to_numeric(output2[col], errors='coerce').round(2)

    logging.info("결과:")
    print(output2)


if __name__ == "__main__":
    main()
