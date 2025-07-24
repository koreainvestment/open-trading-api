"""
Created on 20250113 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from capture_uplowprice import capture_uplowprice

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 국내주식 상하한가 포착 [국내주식-190]
##############################################################################################

COLUMN_MAPPING = {
    'mksc_shrn_iscd': '유가증권단축종목코드',
    'hts_kor_isnm': 'HTS한글종목명',
    'stck_prpr': '주식현재가',
    'prdy_vrss_sign': '전일대비부호',
    'prdy_vrss': '전일대비',
    'prdy_ctrt': '전일대비율',
    'acml_vol': '누적거래량',
    'total_askp_rsqn': '총매도호가잔량',
    'total_bidp_rsqn': '총매수호가잔량',
    'askp_rsqn1': '매도호가잔량1',
    'bidp_rsqn1': '매수호가잔량1',
    'prdy_vol': '전일거래량',
    'seln_cnqn': '매도체결량',
    'shnu_cnqn': '매수2체결량',
    'stck_llam': '주식하한가',
    'stck_mxpr': '주식상한가',
    'prdy_vrss_vol_rate': '전일대비거래량비율'
}

NUMERIC_COLUMNS = []


def main():
    """
    국내주식 상하한가 포착 조회 테스트 함수
    
    이 함수는 국내주식 상하한가 포착 API를 호출하여 결과를 출력합니다.
    
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
        result = capture_uplowprice(
            fid_cond_mrkt_div_code="J",
            fid_cond_scr_div_code="11300",
            fid_prc_cls_code="0",
            fid_div_cls_code="0",
            fid_input_iscd="0000"
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
