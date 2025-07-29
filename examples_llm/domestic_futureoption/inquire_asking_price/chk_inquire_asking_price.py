"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""
import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_asking_price import inquire_asking_price

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 기본시세 > 선물옵션 시세호가[v1_국내선물-007]
##############################################################################################

COLUMN_MAPPING = {
    'hts_kor_isnm': 'HTS 한글 종목명',
    'futs_prpr': '선물 현재가',
    'prdy_vrss_sign': '전일 대비 부호',
    'futs_prdy_vrss': '선물 전일 대비',
    'futs_prdy_ctrt': '선물 전일 대비율',
    'acml_vol': '누적 거래량',
    'futs_prdy_clpr': '선물 전일 종가',
    'futs_shrn_iscd': '선물 단축 종목코드',
    'futs_askp1': '선물 매도호가1',
    'futs_askp2': '선물 매도호가2',
    'futs_askp3': '선물 매도호가3',
    'futs_askp4': '선물 매도호가4',
    'futs_askp5': '선물 매도호가5',
    'futs_bidp1': '선물 매수호가1',
    'futs_bidp2': '선물 매수호가2',
    'futs_bidp3': '선물 매수호가3',
    'futs_bidp4': '선물 매수호가4',
    'futs_bidp5': '선물 매수호가5',
    'askp_rsqn1': '매도호가 잔량1',
    'askp_rsqn2': '매도호가 잔량2',
    'askp_rsqn3': '매도호가 잔량3',
    'askp_rsqn4': '매도호가 잔량4',
    'askp_rsqn5': '매도호가 잔량5',
    'bidp_rsqn1': '매수호가 잔량1',
    'bidp_rsqn2': '매수호가 잔량2',
    'bidp_rsqn3': '매수호가 잔량3',
    'bidp_rsqn4': '매수호가 잔량4',
    'bidp_rsqn5': '매수호가 잔량5',
    'askp_csnu1': '매도호가 건수1',
    'askp_csnu2': '매도호가 건수2',
    'askp_csnu3': '매도호가 건수3',
    'askp_csnu4': '매도호가 건수4',
    'askp_csnu5': '매도호가 건수5',
    'bidp_csnu1': '매수호가 건수1',
    'bidp_csnu2': '매수호가 건수2',
    'bidp_csnu3': '매수호가 건수3',
    'bidp_csnu4': '매수호가 건수4',
    'bidp_csnu5': '매수호가 건수5',
    'total_askp_rsqn': '총 매도호가 잔량',
    'total_bidp_rsqn': '총 매수호가 잔량',
    'total_askp_csnu': '총 매도호가 건수',
    'total_bidp_csnu': '총 매수호가 건수',
    'aspr_acpt_hour': '호가 접수 시간'
}

NUMERIC_COLUMNS = []


def main():
    """
    선물옵션 시세호가 조회 테스트 함수
    
    이 함수는 선물옵션 시세호가 API를 호출하여 결과를 출력합니다.
    
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
        result1, result2 = inquire_asking_price(fid_cond_mrkt_div_code="F", fid_input_iscd="101W09", env_dv="real")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # output1 결과 처리
    logging.info("=== output1 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())

    # 컬럼명 한글 변환

    result1 = result1.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에 number 자료형이 명시된 필드 없음)

    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result1)

    # output2 결과 처리
    logging.info("=== output2 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result2.columns.tolist())

    # 컬럼명 한글 변환
    result2 = result2.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에 number 자료형이 명시된 필드 없음)
    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result2)


if __name__ == "__main__":
    main()
