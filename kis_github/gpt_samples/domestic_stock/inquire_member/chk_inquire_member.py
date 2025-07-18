"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_member import inquire_member

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 기본시세 > 주식현재가 회원사[v1_국내주식-013]
##############################################################################################

COLUMN_MAPPING = {
    'seln_mbcr_no1': '매도 회원사 번호1',
    'seln_mbcr_no2': '매도 회원사 번호2',
    'seln_mbcr_no3': '매도 회원사 번호3',
    'seln_mbcr_no4': '매도 회원사 번호4',
    'seln_mbcr_no5': '매도 회원사 번호5',
    'seln_mbcr_name1': '매도 회원사 명1',
    'seln_mbcr_name2': '매도 회원사 명2',
    'seln_mbcr_name3': '매도 회원사 명3',
    'seln_mbcr_name4': '매도 회원사 명4',
    'seln_mbcr_name5': '매도 회원사 명5',
    'total_seln_qty1': '총 매도 수량1',
    'total_seln_qty2': '총 매도 수량2',
    'total_seln_qty3': '총 매도 수량3',
    'total_seln_qty4': '총 매도 수량4',
    'total_seln_qty5': '총 매도 수량5',
    'seln_mbcr_rlim1': '매도 회원사 비중1',
    'seln_mbcr_rlim2': '매도 회원사 비중2',
    'seln_mbcr_rlim3': '매도 회원사 비중3',
    'seln_mbcr_rlim4': '매도 회원사 비중4',
    'seln_mbcr_rlim5': '매도 회원사 비중5',
    'seln_qty_icdc1': '매도 수량 증감1',
    'seln_qty_icdc2': '매도 수량 증감2',
    'seln_qty_icdc3': '매도 수량 증감3',
    'seln_qty_icdc4': '매도 수량 증감4',
    'seln_qty_icdc5': '매도 수량 증감5',
    'shnu_mbcr_no1': '매수2 회원사 번호1',
    'shnu_mbcr_no2': '매수2 회원사 번호2',
    'shnu_mbcr_no3': '매수2 회원사 번호3',
    'shnu_mbcr_no4': '매수2 회원사 번호4',
    'shnu_mbcr_no5': '매수2 회원사 번호5',
    'shnu_mbcr_name1': '매수2 회원사 명1',
    'shnu_mbcr_name2': '매수2 회원사 명2',
    'shnu_mbcr_name3': '매수2 회원사 명3',
    'shnu_mbcr_name4': '매수2 회원사 명4',
    'shnu_mbcr_name5': '매수2 회원사 명5',
    'total_shnu_qty1': '총 매수2 수량1',
    'total_shnu_qty2': '총 매수2 수량2',
    'total_shnu_qty3': '총 매수2 수량3',
    'total_shnu_qty4': '총 매수2 수량4',
    'total_shnu_qty5': '총 매수2 수량5',
    'shnu_mbcr_rlim1': '매수2 회원사 비중1',
    'shnu_mbcr_rlim2': '매수2 회원사 비중2',
    'shnu_mbcr_rlim3': '매수2 회원사 비중3',
    'shnu_mbcr_rlim4': '매수2 회원사 비중4',
    'shnu_mbcr_rlim5': '매수2 회원사 비중5',
    'shnu_qty_icdc1': '매수2 수량 증감1',
    'shnu_qty_icdc2': '매수2 수량 증감2',
    'shnu_qty_icdc3': '매수2 수량 증감3',
    'shnu_qty_icdc4': '매수2 수량 증감4',
    'shnu_qty_icdc5': '매수2 수량 증감5',
    'glob_total_seln_qty': '외국계 총 매도 수량',
    'glob_seln_rlim': '외국계 매도 비중',
    'glob_ntby_qty': '외국계 순매수 수량',
    'glob_total_shnu_qty': '외국계 총 매수2 수량',
    'glob_shnu_rlim': '외국계 매수2 비중',
    'seln_mbcr_glob_yn_1': '매도 회원사 외국계 여부1',
    'seln_mbcr_glob_yn_2': '매도 회원사 외국계 여부2',
    'seln_mbcr_glob_yn_3': '매도 회원사 외국계 여부3',
    'seln_mbcr_glob_yn_4': '매도 회원사 외국계 여부4',
    'seln_mbcr_glob_yn_5': '매도 회원사 외국계 여부5',
    'shnu_mbcr_glob_yn_1': '매수2 회원사 외국계 여부1',
    'shnu_mbcr_glob_yn_2': '매수2 회원사 외국계 여부2',
    'shnu_mbcr_glob_yn_3': '매수2 회원사 외국계 여부3',
    'shnu_mbcr_glob_yn_4': '매수2 회원사 외국계 여부4',
    'shnu_mbcr_glob_yn_5': '매수2 회원사 외국계 여부5',
    'glob_total_seln_qty_icdc': '외국계 총 매도 수량 증감',
    'glob_total_shnu_qty_icdc': '외국계 총 매수2 수량 증감'
}

NUMERIC_COLUMNS = []


def main():
    """
    주식현재가 회원사 조회 테스트 함수
    
    이 함수는 주식현재가 회원사 API를 호출하여 결과를 출력합니다.
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
        result = inquire_member(env_dv="real", fid_cond_mrkt_div_code="J", fid_input_iscd="005930")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())

    # 컬럼명 한글 변환
    result = result.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에 number 자료형 명시된 필드 없음)
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result)


if __name__ == "__main__":
    main()
