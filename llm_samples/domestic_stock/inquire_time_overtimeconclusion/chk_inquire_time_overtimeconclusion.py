"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_time_overtimeconclusion import inquire_time_overtimeconclusion

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 기본시세 > 주식현재가 시간외시간별체결[v1_국내주식-025]
##############################################################################################

COLUMN_MAPPING = {
    'ovtm_untp_prpr': '시간외 단일가 현재가',
    'ovtm_untp_prdy_vrss': '시간외 단일가 전일 대비',
    'ovtm_untp_prdy_vrss_sign': '시간외 단일가 전일 대비 부호',
    'ovtm_untp_prdy_ctrt': '시간외 단일가 전일 대비율',
    'ovtm_untp_vol': '시간외 단일가 거래량',
    'ovtm_untp_tr_pbmn': '시간외 단일가 거래 대금',
    'ovtm_untp_mxpr': '시간외 단일가 상한가',
    'ovtm_untp_llam': '시간외 단일가 하한가',
    'ovtm_untp_oprc': '시간외 단일가 시가2',
    'ovtm_untp_hgpr': '시간외 단일가 최고가',
    'ovtm_untp_lwpr': '시간외 단일가 최저가',
    'ovtm_untp_antc_cnpr': '시간외 단일가 예상 체결가',
    'ovtm_untp_antc_cntg_vrss': '시간외 단일가 예상 체결 대비',
    'ovtm_untp_antc_cntg_vrss_sign': '시간외 단일가 예상 체결 대비 부호',
    'ovtm_untp_antc_cntg_ctrt': '시간외 단일가 예상 체결 대비율',
    'ovtm_untp_antc_vol': '시간외 단일가 예상 거래량',
    'uplm_sign': '상한 부호',
    'lslm_sign': '하한 부호',
    'stck_cntg_hour': '주식 체결 시간',
    'stck_prpr': '주식 현재가',
    'prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비율',
    'askp': '매도호가',
    'bidp': '매수호가',
    'acml_vol': '누적 거래량',
    'cntg_vol': '체결 거래량'
}

NUMERIC_COLUMNS = ['시간외 단일가 현재가', '시간외 단일가 전일 대비', '시간외 단일가 전일 대비율',
                   '시간외 단일가 거래량', '시간외 단일가 거래 대금', '시간외 단일가 시가2',
                   '시간외 단일가 최고가', '시간외 단일가 최저가', '시간외 단일가 예상 체결가',
                   '시간외 단일가 예상 체결 대비', '시간외 단일가 예상 체결 대비율', '시간외 단일가 예상 거래량', '주식 현재가', '전일 대비', '전일 대비율', '매도호가',
                   '매수호가', '누적 거래량', '체결 거래량']


def main():
    """
    주식현재가 시간외시간별체결 조회 테스트 함수
    
    이 함수는 주식현재가 시간외시간별체결 API를 호출하여 결과를 출력합니다.
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
    logging.info("=== case1 테스트 ===")
    try:
        result1, result2 = inquire_time_overtimeconclusion(env_dv="real", fid_cond_mrkt_div_code="J",
                                                           fid_input_iscd="005930", fid_hour_cls_code="1")
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
