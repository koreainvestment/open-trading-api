"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from program_trade_by_stock import program_trade_by_stock

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 종목별 프로그램매매추이(체결)[v1_국내주식-044]
##############################################################################################

COLUMN_MAPPING = {
    'bsop_hour': '영업 시간',
    'stck_prpr': '주식 현재가',
    'prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비율',
    'acml_vol': '누적 거래량',
    'whol_smtn_seln_vol': '전체 합계 매도 거래량',
    'whol_smtn_shnu_vol': '전체 합계 매수2 거래량',
    'whol_smtn_ntby_qty': '전체 합계 순매수 수량',
    'whol_smtn_seln_tr_pbmn': '전체 합계 매도 거래 대금',
    'whol_smtn_shnu_tr_pbmn': '전체 합계 매수2 거래 대금',
    'whol_smtn_ntby_tr_pbmn': '전체 합계 순매수 거래 대금',
    'whol_ntby_vol_icdc': '전체 순매수 거래량 증감',
    'whol_ntby_tr_pbmn_icdc': '전체 순매수 거래 대금 증감'
}

NUMERIC_COLUMNS = []


def main():
    """
    종목별 프로그램매매추이(체결) 조회 테스트 함수
    
    이 함수는 종목별 프로그램매매추이(체결) API를 호출하여 결과를 출력합니다.
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

    # 종목별 프로그램매매추이 조회
    logging.info("=== 종목별 프로그램매매추이(체결) 조회 ===")
    try:
        result = program_trade_by_stock(fid_cond_mrkt_div_code="J", fid_input_iscd="005930")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력

    result = result.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에 number 자료형 명시 없음)
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result)


if __name__ == "__main__":
    main()
