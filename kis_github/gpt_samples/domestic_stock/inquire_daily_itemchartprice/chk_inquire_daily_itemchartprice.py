"""
Created on 20250101 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_daily_itemchartprice import inquire_daily_itemchartprice

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 기본시세 > 국내주식기간별시세(일/주/월/년)[v1_국내주식-016]
##############################################################################################

COLUMN_MAPPING = {
    'prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비율',
    'stck_prdy_clpr': '주식 전일 종가',
    'acml_vol': '누적 거래량',
    'acml_tr_pbmn': '누적 거래 대금',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'stck_prpr': '주식 현재가',
    'stck_shrn_iscd': '주식 단축 종목코드',
    'prdy_vol': '전일 거래량',
    'stck_mxpr': '주식 상한가',
    'stck_llam': '주식 하한가',
    'stck_oprc': '주식 시가2',
    'stck_hgpr': '주식 최고가',
    'stck_lwpr': '주식 최저가',
    'stck_prdy_oprc': '주식 전일 시가',
    'stck_prdy_hgpr': '주식 전일 최고가',
    'stck_prdy_lwpr': '주식 전일 최저가',
    'askp': '매도호가',
    'bidp': '매수호가',
    'prdy_vrss_vol': '전일 대비 거래량',
    'vol_tnrt': '거래량 회전율',
    'stck_fcam': '주식 액면가',
    'lstn_stcn': '상장 주수',
    'cpfn': '자본금',
    'hts_avls': 'HTS 시가총액',
    'per': 'PER',
    'eps': 'EPS',
    'pbr': 'PBR',
    'itewhol_loan_rmnd_ratem': '전체 융자 잔고 비율',
    'stck_bsop_date': '주식 영업 일자',
    'stck_clpr': '주식 종가',
    'stck_oprc': '주식 시가2',
    'stck_hgpr': '주식 최고가',
    'stck_lwpr': '주식 최저가',
    'acml_vol': '누적 거래량',
    'acml_tr_pbmn': '누적 거래 대금',
    'flng_cls_code': '락 구분 코드',
    'prtt_rate': '분할 비율',
    'mod_yn': '변경 여부',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_vrss': '전일 대비',
    'revl_issu_reas': '재평가사유코드'
}

NUMERIC_COLUMNS = []


def main():
    """
    국내주식기간별시세(일/주/월/년) 조회 테스트 함수
    
    이 함수는 국내주식기간별시세(일/주/월/년) API를 호출하여 결과를 출력합니다.
    
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
        result1, result2 = inquire_daily_itemchartprice(
            env_dv="real",
            fid_cond_mrkt_div_code="J",
            fid_input_iscd="005930",
            fid_input_date_1="20220101",
            fid_input_date_2="20220809",
            fid_period_div_code="D",
            fid_org_adj_prc="1"
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # output1 처리
    logging.info("=== output1 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    result1 = result1.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result1)

    # output2 처리
    logging.info("=== output2 결과 ===")
    logging.info("사용 가능한 컬럼: %s" % result2.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    result2 = result2.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result2)


if __name__ == "__main__":
    main()
