"""
Created on 20250129
@author: LaivData SJPark with cursor
"""
import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from foreign_institution_total import foreign_institution_total

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 국내기관_외국인 매매종목가집계[국내주식-037]
##############################################################################################

COLUMN_MAPPING = {
    'hts_kor_isnm': 'HTS 한글 종목명',
    'mksc_shrn_iscd': '유가증권 단축 종목코드',
    'ntby_qty': '순매수 수량',
    'stck_prpr': '주식 현재가',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_vrss': '전일 대비',
    'prdy_ctrt': '전일 대비율',
    'acml_vol': '누적 거래량',
    'frgn_ntby_qty': '외국인 순매수 수량',
    'orgn_ntby_qty': '기관계 순매수 수량',
    'ivtr_ntby_qty': '투자신탁 순매수 수량',
    'bank_ntby_qty': '은행 순매수 수량',
    'insu_ntby_qty': '보험 순매수 수량',
    'mrbn_ntby_qty': '종금 순매수 수량',
    'fund_ntby_qty': '기금 순매수 수량',
    'etc_orgt_ntby_vol': '기타 단체 순매수 거래량',
    'etc_corp_ntby_vol': '기타 법인 순매수 거래량',
    'frgn_ntby_tr_pbmn': '외국인 순매수 거래 대금',
    'orgn_ntby_tr_pbmn': '기관계 순매수 거래 대금',
    'ivtr_ntby_tr_pbmn': '투자신탁 순매수 거래 대금',
    'bank_ntby_tr_pbmn': '은행 순매수 거래 대금',
    'insu_ntby_tr_pbmn': '보험 순매수 거래 대금',
    'mrbn_ntby_tr_pbmn': '종금 순매수 거래 대금',
    'fund_ntby_tr_pbmn': '기금 순매수 거래 대금',
    'etc_orgt_ntby_tr_pbmn': '기타 단체 순매수 거래 대금',
    'etc_corp_ntby_tr_pbmn': '기타 법인 순매수 거래 대금'
}

NUMERIC_COLUMNS = []


def main():
    """
    국내기관_외국인 매매종목가집계 조회 테스트 함수
    
    이 함수는 국내기관_외국인 매매종목가집계 API를 호출하여 결과를 출력합니다.
    
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
        result = foreign_institution_total(
            fid_cond_mrkt_div_code="V",
            fid_cond_scr_div_code="16449",
            fid_input_iscd="0000",
            fid_div_cls_code="0",
            fid_rank_sort_cls_code="0",
            fid_etc_cls_code="0"
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
