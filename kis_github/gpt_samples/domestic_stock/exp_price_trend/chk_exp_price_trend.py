"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""
import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from exp_price_trend import exp_price_trend

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 국내주식 예상체결가 추이[국내주식-118]
##############################################################################################

COLUMN_MAPPING = {
    'rprs_mrkt_kor_name': '대표 시장 한글 명',
    'antc_cnpr': '예상 체결가',
    'antc_cntg_vrss_sign': '예상 체결 대비 부호',
    'antc_cntg_vrss': '예상 체결 대비',
    'antc_cntg_prdy_ctrt': '예상 체결 전일 대비율',
    'antc_vol': '예상 거래량',
    'antc_tr_pbmn': '예상 거래대금',
    'stck_bsop_date': '주식 영업 일자',
    'stck_cntg_hour': '주식 체결 시간',
    'stck_prpr': '주식 현재가',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_vrss': '전일 대비',
    'prdy_ctrt': '전일 대비율',
    'acml_vol': '누적 거래량'
}

NUMERIC_COLUMNS = []


def main():
    """
    국내주식 예상체결가 추이 조회 테스트 함수
    
    이 함수는 국내주식 예상체결가 추이 API를 호출하여 결과를 출력합니다.
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

    # case1 테스트
    logging.info("=== Case1: 삼성전자 예상체결가 추이 조회 ===")
    try:
        output1, output2 = exp_price_trend(
            fid_cond_mrkt_div_code="J",
            fid_input_iscd="005930",
            fid_mkop_cls_code="0"
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # output1 처리
    logging.info("=== Output1 결과 ===")
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
    logging.info("=== Output2 결과 ===")
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
