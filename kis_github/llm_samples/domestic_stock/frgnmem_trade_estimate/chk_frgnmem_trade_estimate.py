"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from frgnmem_trade_estimate import frgnmem_trade_estimate

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 외국계 매매종목 가집계 [국내주식-161]
##############################################################################################

COLUMN_MAPPING = {
    'stck_shrn_iscd': '주식단축종목코드',
    'hts_kor_isnm': 'HTS한글종목명',
    'glob_ntsl_qty': '외국계순매도수량',
    'stck_prpr': '주식현재가',
    'prdy_vrss': '전일대비',
    'prdy_vrss_sign': '전일대비부호',
    'prdy_ctrt': '전일대비율',
    'acml_vol': '누적거래량',
    'glob_total_seln_qty': '외국계총매도수량',
    'glob_total_shnu_qty': '외국계총매수2수량'
}

NUMERIC_COLUMNS = []


def main():
    """
    외국계 매매종목 가집계 조회 테스트 함수
    
    이 함수는 외국계 매매종목 가집계 API를 호출하여 결과를 출력합니다.
    
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
        result = frgnmem_trade_estimate(
            fid_cond_mrkt_div_code="J",
            fid_cond_scr_div_code="16441",
            fid_input_iscd="0000",
            fid_rank_sort_cls_code="0",
            fid_rank_sort_cls_code_2="0"
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    result = result.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result)


if __name__ == "__main__":
    main()
