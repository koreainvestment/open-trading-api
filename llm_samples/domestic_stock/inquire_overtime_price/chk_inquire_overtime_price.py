"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_overtime_price import inquire_overtime_price

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 기본시세 > 국내주식 시간외현재가[국내주식-076]
##############################################################################################

COLUMN_MAPPING = {
    'bstp_kor_isnm': '업종 한글 종목명',
    'mang_issu_cls_name': '관리 종목 구분 명',
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
    'marg_rate': '증거금 비율',
    'ovtm_untp_antc_cnpr': '시간외 단일가 예상 체결가',
    'ovtm_untp_antc_cntg_vrss': '시간외 단일가 예상 체결 대비',
    'ovtm_untp_antc_cntg_vrss_sign': '시간외 단일가 예상 체결 대비',
    'ovtm_untp_antc_cntg_ctrt': '시간외 단일가 예상 체결 대비율',
    'ovtm_untp_antc_cnqn': '시간외 단일가 예상 체결량',
    'crdt_able_yn': '신용 가능 여부',
    'new_lstn_cls_name': '신규 상장 구분 명',
    'sltr_yn': '정리매매 여부',
    'mang_issu_yn': '관리 종목 여부',
    'mrkt_warn_cls_code': '시장 경고 구분 코드',
    'trht_yn': '거래정지 여부',
    'vlnt_deal_cls_name': '임의 매매 구분 명',
    'ovtm_untp_sdpr': '시간외 단일가 기준가',
    'mrkt_warn_cls_name': '시장 경구 구분 명',
    'revl_issu_reas_name': '재평가 종목 사유 명',
    'insn_pbnt_yn': '불성실 공시 여부',
    'flng_cls_name': '락 구분 이름',
    'rprs_mrkt_kor_name': '대표 시장 한글 명',
    'ovtm_vi_cls_code': '시간외단일가VI적용구분코드',
    'bidp': '매수호가',
    'askp': '매도호가'
}

NUMERIC_COLUMNS = [
    '시간외 단일가 현재가', '시간외 단일가 전일 대비율', '시간외 단일가 거래량',
    '시간외 단일가 거래 대금', '시간외 단일가 상한가', '시간외 단일가 하한가',
    '시간외 단일가 시가2', '시간외 단일가 최고가', '시간외 단일가 최저가',
    '증거금 비율', '시간외 단일가 예상 체결가', '시간외 단일가 예상 체결 대비율',
    '시간외 단일가 예상 체결량'
]


def main():
    """
    국내주식 시간외현재가 조회 테스트 함수
    
    이 함수는 국내주식 시간외현재가 API를 호출하여 결과를 출력합니다.
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
        result = inquire_overtime_price(fid_cond_mrkt_div_code="J", fid_input_iscd="005930")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    result = result.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에서 number로 명시된 컬럼만)
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result)


if __name__ == "__main__":
    main()
