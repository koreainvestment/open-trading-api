"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_investor import inquire_investor

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 기본시세 > 주식현재가 투자자[v1_국내주식-012]
##############################################################################################

COLUMN_MAPPING = {
    'stck_bsop_date': '주식 영업 일자',
    'stck_clpr': '주식 종가',
    'prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prsn_ntby_qty': '개인 순매수 수량',
    'frgn_ntby_qty': '외국인 순매수 수량',
    'orgn_ntby_qty': '기관계 순매수 수량',
    'prsn_ntby_tr_pbmn': '개인 순매수 거래 대금',
    'frgn_ntby_tr_pbmn': '외국인 순매수 거래 대금',
    'orgn_ntby_tr_pbmn': '기관계 순매수 거래 대금',
    'prsn_shnu_vol': '개인 매수2 거래량',
    'frgn_shnu_vol': '외국인 매수2 거래량',
    'orgn_shnu_vol': '기관계 매수2 거래량',
    'prsn_shnu_tr_pbmn': '개인 매수2 거래 대금',
    'frgn_shnu_tr_pbmn': '외국인 매수2 거래 대금',
    'orgn_shnu_tr_pbmn': '기관계 매수2 거래 대금',
    'prsn_seln_vol': '개인 매도 거래량',
    'frgn_seln_vol': '외국인 매도 거래량',
    'orgn_seln_vol': '기관계 매도 거래량',
    'prsn_seln_tr_pbmn': '개인 매도 거래 대금',
    'frgn_seln_tr_pbmn': '외국인 매도 거래 대금',
    'orgn_seln_tr_pbmn': '기관계 매도 거래 대금'
}

NUMERIC_COLUMNS = []

def main():
    """
    주식현재가 투자자 조회 테스트 함수
    
    이 함수는 주식현재가 투자자 API를 호출하여 결과를 출력합니다.
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
        result = inquire_investor(env_dv="real", fid_cond_mrkt_div_code="J", fid_input_iscd="005930")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return
    
    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())
    
    # 컬럼명 한글 변환 및 데이터 출력
    result = result.rename(columns=COLUMN_MAPPING)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에 자료형이 명시되지 않았으므로 NUMERIC_COLUMNS는 빈 리스트)
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result)

if __name__ == "__main__":
    main() 