"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_asking_price_exp_ccn import inquire_asking_price_exp_ccn

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 기본시세 > 주식현재가 호가/예상체결[v1_국내주식-011]
##############################################################################################

COLUMN_MAPPING = {
    'aspr_acpt_hour': '호가 접수 시간',
    'askp1': '매도호가1',
    'askp2': '매도호가2',
    'askp3': '매도호가3',
    'askp4': '매도호가4',
    'askp5': '매도호가5',
    'askp6': '매도호가6',
    'askp7': '매도호가7',
    'askp8': '매도호가8',
    'askp9': '매도호가9',
    'askp10': '매도호가10',
    'bidp1': '매수호가1',
    'bidp2': '매수호가2',
    'bidp3': '매수호가3',
    'bidp4': '매수호가4',
    'bidp5': '매수호가5',
    'bidp6': '매수호가6',
    'bidp7': '매수호가7',
    'bidp8': '매수호가8',
    'bidp9': '매수호가9',
    'bidp10': '매수호가10',
    'askp_rsqn1': '매도호가 잔량1',
    'askp_rsqn2': '매도호가 잔량2',
    'askp_rsqn3': '매도호가 잔량3',
    'askp_rsqn4': '매도호가 잔량4',
    'askp_rsqn5': '매도호가 잔량5',
    'askp_rsqn6': '매도호가 잔량6',
    'askp_rsqn7': '매도호가 잔량7',
    'askp_rsqn8': '매도호가 잔량8',
    'askp_rsqn9': '매도호가 잔량9',
    'askp_rsqn10': '매도호가 잔량10',
    'bidp_rsqn1': '매수호가 잔량1',
    'bidp_rsqn2': '매수호가 잔량2',
    'bidp_rsqn3': '매수호가 잔량3',
    'bidp_rsqn4': '매수호가 잔량4',
    'bidp_rsqn5': '매수호가 잔량5',
    'bidp_rsqn6': '매수호가 잔량6',
    'bidp_rsqn7': '매수호가 잔량7',
    'bidp_rsqn8': '매수호가 잔량8',
    'bidp_rsqn9': '매수호가 잔량9',
    'bidp_rsqn10': '매수호가 잔량10',
    'askp_rsqn_icdc1': '매도호가 잔량 증감1',
    'askp_rsqn_icdc2': '매도호가 잔량 증감2',
    'askp_rsqn_icdc3': '매도호가 잔량 증감3',
    'askp_rsqn_icdc4': '매도호가 잔량 증감4',
    'askp_rsqn_icdc5': '매도호가 잔량 증감5',
    'askp_rsqn_icdc6': '매도호가 잔량 증감6',
    'askp_rsqn_icdc7': '매도호가 잔량 증감7',
    'askp_rsqn_icdc8': '매도호가 잔량 증감8',
    'askp_rsqn_icdc9': '매도호가 잔량 증감9',
    'askp_rsqn_icdc10': '매도호가 잔량 증감10',
    'bidp_rsqn_icdc1': '매수호가 잔량 증감1',
    'bidp_rsqn_icdc2': '매수호가 잔량 증감2',
    'bidp_rsqn_icdc3': '매수호가 잔량 증감3',
    'bidp_rsqn_icdc4': '매수호가 잔량 증감4',
    'bidp_rsqn_icdc5': '매수호가 잔량 증감5',
    'bidp_rsqn_icdc6': '매수호가 잔량 증감6',
    'bidp_rsqn_icdc7': '매수호가 잔량 증감7',
    'bidp_rsqn_icdc8': '매수호가 잔량 증감8',
    'bidp_rsqn_icdc9': '매수호가 잔량 증감9',
    'bidp_rsqn_icdc10': '매수호가 잔량 증감10',
    'total_askp_rsqn': '총 매도호가 잔량',
    'total_bidp_rsqn': '총 매수호가 잔량',
    'total_askp_rsqn_icdc': '총 매도호가 잔량 증감',
    'total_bidp_rsqn_icdc': '총 매수호가 잔량 증감',
    'ovtm_total_askp_icdc': '시간외 총 매도호가 증감',
    'ovtm_total_bidp_icdc': '시간외 총 매수호가 증감',
    'ovtm_total_askp_rsqn': '시간외 총 매도호가 잔량',
    'ovtm_total_bidp_rsqn': '시간외 총 매수호가 잔량',
    'ntby_aspr_rsqn': '순매수 호가 잔량',
    'new_mkop_cls_code': '신 장운영 구분 코드',
    'antc_mkop_cls_code': '예상 장운영 구분 코드',
    'stck_prpr': '주식 현재가',
    'stck_oprc': '주식 시가2',
    'stck_hgpr': '주식 최고가',
    'stck_lwpr': '주식 최저가',
    'stck_sdpr': '주식 기준가',
    'antc_cnpr': '예상 체결가',
    'antc_cntg_vrss_sign': '예상 체결 대비 부호',
    'antc_cntg_vrss': '예상 체결 대비',
    'antc_cntg_prdy_ctrt': '예상 체결 전일 대비율',
    'antc_vol': '예상 거래량',
    'stck_shrn_iscd': '주식 단축 종목코드',
    'vi_cls_code': 'VI적용구분코드'
}

NUMERIC_COLUMNS = []


def main():
    """
    주식현재가 호가/예상체결 조회 테스트 함수
    
    이 함수는 주식현재가 호가/예상체결 API를 호출하여 결과를 출력합니다.
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
        result1, result2 = inquire_asking_price_exp_ccn(env_dv="real", fid_cond_mrkt_div_code="J",
                                                        fid_input_iscd="005930")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # output1 (호가정보) 처리
    logging.info("=== output1 (호가정보) ===")
    logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())

    # 컬럼명 한글 변환
    result1 = result1.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result1)

    # output2 (예상체결정보) 처리
    logging.info("=== output2 (예상체결정보) ===")
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
