"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_overtime_asking_price import inquire_overtime_asking_price

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 기본시세 > 국내주식 시간외호가[국내주식-077]
##############################################################################################

COLUMN_MAPPING = {
    'ovtm_untp_last_hour': '시간외 단일가 최종 시간',
    'ovtm_untp_askp1': '시간외 단일가 매도호가1',
    'ovtm_untp_askp2': '시간외 단일가 매도호가2',
    'ovtm_untp_askp3': '시간외 단일가 매도호가3',
    'ovtm_untp_askp4': '시간외 단일가 매도호가4',
    'ovtm_untp_askp5': '시간외 단일가 매도호가5',
    'ovtm_untp_askp6': '시간외 단일가 매도호가6',
    'ovtm_untp_askp7': '시간외 단일가 매도호가7',
    'ovtm_untp_askp8': '시간외 단일가 매도호가8',
    'ovtm_untp_askp9': '시간외 단일가 매도호가9',
    'ovtm_untp_askp10': '시간외 단일가 매도호가10',
    'ovtm_untp_bidp1': '시간외 단일가 매수호가1',
    'ovtm_untp_bidp2': '시간외 단일가 매수호가2',
    'ovtm_untp_bidp3': '시간외 단일가 매수호가3',
    'ovtm_untp_bidp4': '시간외 단일가 매수호가4',
    'ovtm_untp_bidp5': '시간외 단일가 매수호가5',
    'ovtm_untp_bidp6': '시간외 단일가 매수호가6',
    'ovtm_untp_bidp7': '시간외 단일가 매수호가7',
    'ovtm_untp_bidp8': '시간외 단일가 매수호가8',
    'ovtm_untp_bidp9': '시간외 단일가 매수호가9',
    'ovtm_untp_bidp10': '시간외 단일가 매수호가10',
    'ovtm_untp_askp_icdc1': '시간외 단일가 매도호가 증감1',
    'ovtm_untp_askp_icdc2': '시간외 단일가 매도호가 증감2',
    'ovtm_untp_askp_icdc3': '시간외 단일가 매도호가 증감3',
    'ovtm_untp_askp_icdc4': '시간외 단일가 매도호가 증감4',
    'ovtm_untp_askp_icdc5': '시간외 단일가 매도호가 증감5',
    'ovtm_untp_askp_icdc6': '시간외 단일가 매도호가 증감6',
    'ovtm_untp_askp_icdc7': '시간외 단일가 매도호가 증감7',
    'ovtm_untp_askp_icdc8': '시간외 단일가 매도호가 증감8',
    'ovtm_untp_askp_icdc9': '시간외 단일가 매도호가 증감9',
    'ovtm_untp_askp_icdc10': '시간외 단일가 매도호가 증감10',
    'ovtm_untp_bidp_icdc1': '시간외 단일가 매수호가 증감1',
    'ovtm_untp_bidp_icdc2': '시간외 단일가 매수호가 증감2',
    'ovtm_untp_bidp_icdc3': '시간외 단일가 매수호가 증감3',
    'ovtm_untp_bidp_icdc4': '시간외 단일가 매수호가 증감4',
    'ovtm_untp_bidp_icdc5': '시간외 단일가 매수호가 증감5',
    'ovtm_untp_bidp_icdc6': '시간외 단일가 매수호가 증감6',
    'ovtm_untp_bidp_icdc7': '시간외 단일가 매수호가 증감7',
    'ovtm_untp_bidp_icdc8': '시간외 단일가 매수호가 증감8',
    'ovtm_untp_bidp_icdc9': '시간외 단일가 매수호가 증감9',
    'ovtm_untp_bidp_icdc10': '시간외 단일가 매수호가 증감10',
    'ovtm_untp_askp_rsqn1': '시간외 단일가 매도호가 잔량1',
    'ovtm_untp_askp_rsqn2': '시간외 단일가 매도호가 잔량2',
    'ovtm_untp_askp_rsqn3': '시간외 단일가 매도호가 잔량3',
    'ovtm_untp_askp_rsqn4': '시간외 단일가 매도호가 잔량4',
    'ovtm_untp_askp_rsqn5': '시간외 단일가 매도호가 잔량5',
    'ovtm_untp_askp_rsqn6': '시간외 단일가 매도호가 잔량6',
    'ovtm_untp_askp_rsqn7': '시간외 단일가 매도호가 잔량7',
    'ovtm_untp_askp_rsqn8': '시간외 단일가 매도호가 잔량8',
    'ovtm_untp_askp_rsqn9': '시간외 단일가 매도호가 잔량9',
    'ovtm_untp_askp_rsqn10': '시간외 단일가 매도호가 잔량10',
    'ovtm_untp_bidp_rsqn1': '시간외 단일가 매수호가 잔량1',
    'ovtm_untp_bidp_rsqn': '시간외 단일가 매수호가 잔량2',
    'ovtm_untp_bidp_rsqn3': '시간외 단일가 매수호가 잔량3',
    'ovtm_untp_bidp_rsqn4': '시간외 단일가 매수호가 잔량4',
    'ovtm_untp_bidp_rsqn5': '시간외 단일가 매수호가 잔량5',
    'ovtm_untp_bidp_rsqn6': '시간외 단일가 매수호가 잔량6',
    'ovtm_untp_bidp_rsqn7': '시간외 단일가 매수호가 잔량7',
    'ovtm_untp_bidp_rsqn8': '시간외 단일가 매수호가 잔량8',
    'ovtm_untp_bidp_rsqn9': '시간외 단일가 매수호가 잔량9',
    'ovtm_untp_bidp_rsqn10': '시간외 단일가 매수호가 잔량10',
    'ovtm_untp_total_askp_rsqn': '시간외 단일가 총 매도호가 잔량',
    'ovtm_untp_total_bidp_rsqn': '시간외 단일가 총 매수호가 잔량',
    'ovtm_untp_total_askp_rsqn_icdc': '시간외 단일가 총 매도호가 잔량',
    'ovtm_untp_total_bidp_rsqn_icdc': '시간외 단일가 총 매수호가 잔량',
    'ovtm_untp_ntby_bidp_rsqn': '시간외 단일가 순매수 호가 잔량',
    'total_askp_rsqn': '총 매도호가 잔량',
    'total_bidp_rsqn': '총 매수호가 잔량',
    'total_askp_rsqn_icdc': '총 매도호가 잔량 증감',
    'total_bidp_rsqn_icdc': '총 매수호가 잔량 증감',
    'ovtm_total_askp_rsqn': '시간외 총 매도호가 잔량',
    'ovtm_total_bidp_rsqn': '시간외 총 매수호가 잔량',
    'ovtm_total_askp_icdc': '시간외 총 매도호가 증감',
    'ovtm_total_bidp_icdc': '시간외 총 매수호가 증감'
}

NUMERIC_COLUMNS = ['시간외 단일가 매도호가1', '시간외 단일가 매도호가2', '시간외 단일가 매도호가3',
                   '시간외 단일가 매도호가4', '시간외 단일가 매도호가5', '시간외 단일가 매도호가6',
                   '시간외 단일가 매도호가7', '시간외 단일가 매도호가8', '시간외 단일가 매도호가9',
                   '시간외 단일가 매도호가10', '시간외 단일가 매수호가1', '시간외 단일가 매수호가2',
                   '시간외 단일가 매수호가3', '시간외 단일가 매수호가4', '시간외 단일가 매수호가5',
                   '시간외 단일가 매수호가6', '시간외 단일가 매수호가7', '시간외 단일가 매수호가8',
                   '시간외 단일가 매수호가9', '시간외 단일가 매수호가10']


def main():
    """
    국내주식 시간외호가 조회 테스트 함수
    
    이 함수는 국내주식 시간외호가 API를 호출하여 결과를 출력합니다.
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
        result = inquire_overtime_asking_price(fid_cond_mrkt_div_code="J", fid_input_iscd="005930")
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
