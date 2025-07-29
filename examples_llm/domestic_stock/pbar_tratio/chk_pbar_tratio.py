"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from pbar_tratio import pbar_tratio

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 국내주식 매물대/거래비중 [국내주식-196]
##############################################################################################

COLUMN_MAPPING = {
    'rprs_mrkt_kor_name': '대표시장한글명',
    'stck_shrn_iscd': '주식단축종목코드',
    'hts_kor_isnm': 'HTS한글종목명',
    'stck_prpr': '주식현재가',
    'prdy_vrss_sign': '전일대비부호',
    'prdy_vrss': '전일대비',
    'prdy_ctrt': '전일대비율',
    'acml_vol': '누적거래량',
    'prdy_vol': '전일거래량',
    'wghn_avrg_stck_prc': '가중평균주식가격',
    'lstn_stcn': '상장주수',
    'data_rank': '데이터순위',
    'stck_prpr': '주식현재가',
    'cntg_vol': '체결거래량',
    'acml_vol_rlim': '누적거래량비중'
}

NUMERIC_COLUMNS = []


def main():
    """
    국내주식 매물대/거래비중 조회 테스트 함수
    
    이 함수는 국내주식 매물대/거래비중 API를 호출하여 결과를 출력합니다.
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
        result1, result2 = pbar_tratio(
            fid_cond_mrkt_div_code="J",
            fid_input_iscd="005930",
            fid_cond_scr_div_code="20113"
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # output1 결과 처리
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

    # output2 결과 처리
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
