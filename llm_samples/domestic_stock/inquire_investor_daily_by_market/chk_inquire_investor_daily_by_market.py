"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_investor_daily_by_market import inquire_investor_daily_by_market

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 시장별 투자자매매동향(일별) [국내주식-075]
##############################################################################################

COLUMN_MAPPING = {
    'stck_bsop_date': '주식 영업 일자',
    'bstp_nmix_prpr': '업종 지수 현재가',
    'bstp_nmix_prdy_vrss': '업종 지수 전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'bstp_nmix_prdy_ctrt': '업종 지수 전일 대비율',
    'bstp_nmix_oprc': '업종 지수 시가2',
    'bstp_nmix_hgpr': '업종 지수 최고가',
    'bstp_nmix_lwpr': '업종 지수 최저가',
    'stck_prdy_clpr': '주식 전일 종가',
    'frgn_ntby_qty': '외국인 순매수 수량',
    'frgn_reg_ntby_qty': '외국인 등록 순매수 수량',
    'frgn_nreg_ntby_qty': '외국인 비등록 순매수 수량',
    'prsn_ntby_qty': '개인 순매수 수량',
    'orgn_ntby_qty': '기관계 순매수 수량',
    'scrt_ntby_qty': '증권 순매수 수량',
    'ivtr_ntby_qty': '투자신탁 순매수 수량',
    'pe_fund_ntby_vol': '사모 펀드 순매수 거래량',
    'bank_ntby_qty': '은행 순매수 수량',
    'insu_ntby_qty': '보험 순매수 수량',
    'mrbn_ntby_qty': '종금 순매수 수량',
    'fund_ntby_qty': '기금 순매수 수량',
    'etc_ntby_qty': '기타 순매수 수량',
    'etc_orgt_ntby_vol': '기타 단체 순매수 거래량',
    'etc_corp_ntby_vol': '기타 법인 순매수 거래량',
    'frgn_ntby_tr_pbmn': '외국인 순매수 거래 대금',
    'frgn_reg_ntby_pbmn': '외국인 등록 순매수 대금',
    'frgn_nreg_ntby_pbmn': '외국인 비등록 순매수 대금',
    'prsn_ntby_tr_pbmn': '개인 순매수 거래 대금',
    'orgn_ntby_tr_pbmn': '기관계 순매수 거래 대금',
    'scrt_ntby_tr_pbmn': '증권 순매수 거래 대금',
    'ivtr_ntby_tr_pbmn': '투자신탁 순매수 거래 대금',
    'pe_fund_ntby_tr_pbmn': '사모 펀드 순매수 거래 대금',
    'bank_ntby_tr_pbmn': '은행 순매수 거래 대금',
    'insu_ntby_tr_pbmn': '보험 순매수 거래 대금',
    'mrbn_ntby_tr_pbmn': '종금 순매수 거래 대금',
    'fund_ntby_tr_pbmn': '기금 순매수 거래 대금',
    'etc_ntby_tr_pbmn': '기타 순매수 거래 대금',
    'etc_orgt_ntby_tr_pbmn': '기타 단체 순매수 거래 대금',
    'etc_corp_ntby_tr_pbmn': '기타 법인 순매수 거래 대금'
}

NUMERIC_COLUMNS = []


def main():
    """
    시장별 투자자매매동향(일별) 조회 테스트 함수
    
    이 함수는 시장별 투자자매매동향(일별) API를 호출하여 결과를 출력합니다.
    테스트 데이터로 업종 코드 0001, 날짜 20240517, 코스피 시장을 사용합니다.
    
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
        result = inquire_investor_daily_by_market(
            fid_cond_mrkt_div_code="U",
            fid_input_iscd="0001",
            fid_input_date_1="20250701",
            fid_input_iscd_1="KSP",
            fid_input_date_2="20250701",
            fid_input_iscd_2="0001",
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    result = result.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에 자료형이 number로 명시된 필드가 없음)
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result)


if __name__ == "__main__":
    main()
