"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from exp_closing_price import exp_closing_price

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 기본시세 > 국내주식 장마감 예상체결가[국내주식-120]
##############################################################################################

COLUMN_MAPPING = {
    'stck_shrn_iscd': '주식 단축 종목코드',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'stck_prpr': '주식 현재가',
    'prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비율',
    'sdpr_vrss_prpr': '기준가 대비 현재가',
    'sdpr_vrss_prpr_rate': '기준가 대비 현재가 비율',
    'cntg_vol': '체결 거래량'
}

NUMERIC_COLUMNS = ['전일 대비율', '기준가 대비 현재가 비율']


def main():
    """
    국내주식 장마감 예상체결가 조회 테스트 함수
    
    이 함수는 국내주식 장마감 예상체결가 API를 호출하여 결과를 출력합니다.
    
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
        result = exp_closing_price(
            fid_cond_mrkt_div_code="J",
            fid_input_iscd="0001",
            fid_rank_sort_cls_code="0",
            fid_cond_scr_div_code="11173",
            fid_blng_cls_code="0"
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())

    # 컬럼명 한글 변환
    result = result.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result)


if __name__ == "__main__":
    main()
