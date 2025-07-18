"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_price_2 import inquire_price_2

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 기본시세 > 주식현재가 시세2[v1_국내주식-054]
##############################################################################################

COLUMN_MAPPING = {
    'rprs_mrkt_kor_name': '대표 시장 한글 명',
    'new_hgpr_lwpr_cls_code': '신 고가 저가 구분 코드',
    'mxpr_llam_cls_code': '상하한가 구분 코드',
    'crdt_able_yn': '신용 가능 여부',
    'stck_mxpr': '주식 상한가',
    'elw_pblc_yn': 'ELW 발행 여부',
    'prdy_clpr_vrss_oprc_rate': '전일 종가 대비 시가2 비율',
    'crdt_rate': '신용 비율',
    'marg_rate': '증거금 비율',
    'lwpr_vrss_prpr': '최저가 대비 현재가',
    'lwpr_vrss_prpr_sign': '최저가 대비 현재가 부호',
    'prdy_clpr_vrss_lwpr_rate': '전일 종가 대비 최저가 비율',
    'stck_lwpr': '주식 최저가',
    'hgpr_vrss_prpr': '최고가 대비 현재가',
    'hgpr_vrss_prpr_sign': '최고가 대비 현재가 부호',
    'prdy_clpr_vrss_hgpr_rate': '전일 종가 대비 최고가 비율',
    'stck_hgpr': '주식 최고가',
    'oprc_vrss_prpr': '시가2 대비 현재가',
    'oprc_vrss_prpr_sign': '시가2 대비 현재가 부호',
    'mang_issu_yn': '관리 종목 여부',
    'divi_app_cls_code': '동시호가배분처리코드',
    'short_over_yn': '단기과열여부',
    'mrkt_warn_cls_code': '시장경고코드',
    'invt_caful_yn': '투자유의여부',
    'stange_runup_yn': '이상급등여부',
    'ssts_hot_yn': '공매도과열 여부',
    'low_current_yn': '저유동성 종목 여부',
    'vi_cls_code': 'VI적용구분코드',
    'short_over_cls_code': '단기과열구분코드',
    'stck_llam': '주식 하한가',
    'new_lstn_cls_name': '신규 상장 구분 명',
    'vlnt_deal_cls_name': '임의 매매 구분 명',
    'flng_cls_name': '락 구분 이름',
    'revl_issu_reas_name': '재평가 종목 사유 명',
    'mrkt_warn_cls_name': '시장 경고 구분 명',
    'stck_sdpr': '주식 기준가',
    'bstp_cls_code': '업종 구분 코드',
    'stck_prdy_clpr': '주식 전일 종가',
    'insn_pbnt_yn': '불성실 공시 여부',
    'fcam_mod_cls_name': '액면가 변경 구분 명',
    'stck_prpr': '주식 현재가',
    'prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비율',
    'acml_tr_pbmn': '누적 거래 대금',
    'acml_vol': '누적 거래량',
    'prdy_vrss_vol_rate': '전일 대비 거래량 비율',
    'bstp_kor_isnm': '업종 한글 종목명',
    'sltr_yn': '정리매매 여부',
    'trht_yn': '거래정지 여부',
    'oprc_rang_cont_yn': '시가 범위 연장 여부',
    'vlnt_fin_cls_code': '임의 종료 구분 코드',
    'stck_oprc': '주식 시가2',
    'prdy_vol': '전일 거래량'
}

NUMERIC_COLUMNS = []


def main():
    """
    주식현재가 시세2 조회 테스트 함수
    
    이 함수는 주식현재가 시세2 API를 호출하여 결과를 출력합니다.
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
        result = inquire_price_2(fid_cond_mrkt_div_code="J", fid_input_iscd="005930")
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
