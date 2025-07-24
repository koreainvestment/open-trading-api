"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_investor_time_by_market import inquire_investor_time_by_market

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 시장별 투자자매매동향(시세)[v1_국내주식-074]
##############################################################################################

COLUMN_MAPPING = {
    'frgn_seln_vol': '외국인 매도 거래량',
    'frgn_shnu_vol': '외국인 매수2 거래량',
    'frgn_ntby_qty': '외국인 순매수 수량',
    'frgn_seln_tr_pbmn': '외국인 매도 거래 대금',
    'frgn_shnu_tr_pbmn': '외국인 매수2 거래 대금',
    'frgn_ntby_tr_pbmn': '외국인 순매수 거래 대금',
    'prsn_seln_vol': '개인 매도 거래량',
    'prsn_shnu_vol': '개인 매수2 거래량',
    'prsn_ntby_qty': '개인 순매수 수량',
    'prsn_seln_tr_pbmn': '개인 매도 거래 대금',
    'prsn_shnu_tr_pbmn': '개인 매수2 거래 대금',
    'prsn_ntby_tr_pbmn': '개인 순매수 거래 대금',
    'orgn_seln_vol': '기관계 매도 거래량',
    'orgn_shnu_vol': '기관계 매수2 거래량',
    'orgn_ntby_qty': '기관계 순매수 수량',
    'orgn_seln_tr_pbmn': '기관계 매도 거래 대금',
    'orgn_shnu_tr_pbmn': '기관계 매수2 거래 대금',
    'orgn_ntby_tr_pbmn': '기관계 순매수 거래 대금',
    'scrt_seln_vol': '증권 매도 거래량',
    'scrt_shnu_vol': '증권 매수2 거래량',
    'scrt_ntby_qty': '증권 순매수 수량',
    'scrt_seln_tr_pbmn': '증권 매도 거래 대금',
    'scrt_shnu_tr_pbmn': '증권 매수2 거래 대금',
    'scrt_ntby_tr_pbmn': '증권 순매수 거래 대금',
    'ivtr_seln_vol': '투자신탁 매도 거래량',
    'ivtr_shnu_vol': '투자신탁 매수2 거래량',
    'ivtr_ntby_qty': '투자신탁 순매수 수량',
    'ivtr_seln_tr_pbmn': '투자신탁 매도 거래 대금',
    'ivtr_shnu_tr_pbmn': '투자신탁 매수2 거래 대금',
    'ivtr_ntby_tr_pbmn': '투자신탁 순매수 거래 대금',
    'pe_fund_seln_tr_pbmn': '사모 펀드 매도 거래 대금',
    'pe_fund_seln_vol': '사모 펀드 매도 거래량',
    'pe_fund_ntby_vol': '사모 펀드 순매수 거래량',
    'pe_fund_shnu_tr_pbmn': '사모 펀드 매수2 거래 대금',
    'pe_fund_shnu_vol': '사모 펀드 매수2 거래량',
    'pe_fund_ntby_tr_pbmn': '사모 펀드 순매수 거래 대금',
    'bank_seln_vol': '은행 매도 거래량',
    'bank_shnu_vol': '은행 매수2 거래량',
    'bank_ntby_qty': '은행 순매수 수량',
    'bank_seln_tr_pbmn': '은행 매도 거래 대금',
    'bank_shnu_tr_pbmn': '은행 매수2 거래 대금',
    'bank_ntby_tr_pbmn': '은행 순매수 거래 대금',
    'insu_seln_vol': '보험 매도 거래량',
    'insu_shnu_vol': '보험 매수2 거래량',
    'insu_ntby_qty': '보험 순매수 수량',
    'insu_seln_tr_pbmn': '보험 매도 거래 대금',
    'insu_shnu_tr_pbmn': '보험 매수2 거래 대금',
    'insu_ntby_tr_pbmn': '보험 순매수 거래 대금',
    'mrbn_seln_vol': '종금 매도 거래량',
    'mrbn_shnu_vol': '종금 매수2 거래량',
    'mrbn_ntby_qty': '종금 순매수 수량',
    'mrbn_seln_tr_pbmn': '종금 매도 거래 대금',
    'mrbn_shnu_tr_pbmn': '종금 매수2 거래 대금',
    'mrbn_ntby_tr_pbmn': '종금 순매수 거래 대금',
    'fund_seln_vol': '기금 매도 거래량',
    'fund_shnu_vol': '기금 매수2 거래량',
    'fund_ntby_qty': '기금 순매수 수량',
    'fund_seln_tr_pbmn': '기금 매도 거래 대금',
    'fund_shnu_tr_pbmn': '기금 매수2 거래 대금',
    'fund_ntby_tr_pbmn': '기금 순매수 거래 대금',
    'etc_orgt_seln_vol': '기타 단체 매도 거래량',
    'etc_orgt_shnu_vol': '기타 단체 매수2 거래량',
    'etc_orgt_ntby_vol': '기타 단체 순매수 거래량',
    'etc_orgt_seln_tr_pbmn': '기타 단체 매도 거래 대금',
    'etc_orgt_shnu_tr_pbmn': '기타 단체 매수2 거래 대금',
    'etc_orgt_ntby_tr_pbmn': '기타 단체 순매수 거래 대금',
    'etc_corp_seln_vol': '기타 법인 매도 거래량',
    'etc_corp_shnu_vol': '기타 법인 매수2 거래량',
    'etc_corp_ntby_vol': '기타 법인 순매수 거래량',
    'etc_corp_seln_tr_pbmn': '기타 법인 매도 거래 대금',
    'etc_corp_shnu_tr_pbmn': '기타 법인 매수2 거래 대금',
    'etc_corp_ntby_tr_pbmn': '기타 법인 순매수 거래 대금'
}

NUMERIC_COLUMNS = []


def main():
    """
    시장별 투자자매매동향(시세) 조회 테스트 함수
    
    이 함수는 시장별 투자자매매동향(시세) API를 호출하여 결과를 출력합니다.
    
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
        result = inquire_investor_time_by_market(fid_input_iscd="999", fid_input_iscd_2="S001")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    result = result.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에 number 자료형이 명시된 필드가 없으므로 빈 리스트)
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result)


if __name__ == "__main__":
    main()
