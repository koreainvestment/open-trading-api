"""
Created on 20250112
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_price import inquire_price

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 기본시세 > 주식현재가 시세[v1_국내주식-008]
##############################################################################################

COLUMN_MAPPING = {
    'iscd_stat_cls_code': '종목 상태 구분 코드',
    'marg_rate': '증거금 비율',
    'rprs_mrkt_kor_name': '대표 시장 한글 명',
    'new_hgpr_lwpr_cls_code': '신 고가 저가 구분 코드',
    'bstp_kor_isnm': '업종 한글 종목명',
    'temp_stop_yn': '임시 정지 여부',
    'oprc_rang_cont_yn': '시가 범위 연장 여부',
    'clpr_rang_cont_yn': '종가 범위 연장 여부',
    'crdt_able_yn': '신용 가능 여부',
    'grmn_rate_cls_code': '보증금 비율 구분 코드',
    'elw_pblc_yn': 'ELW 발행 여부',
    'stck_prpr': '주식 현재가',
    'prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비율',
    'acml_tr_pbmn': '누적 거래 대금',
    'acml_vol': '누적 거래량',
    'prdy_vrss_vol_rate': '전일 대비 거래량 비율',
    'stck_oprc': '주식 시가2',
    'stck_hgpr': '주식 최고가',
    'stck_lwpr': '주식 최저가',
    'stck_mxpr': '주식 상한가',
    'stck_llam': '주식 하한가',
    'stck_sdpr': '주식 기준가',
    'wghn_avrg_stck_prc': '가중 평균 주식 가격',
    'hts_frgn_ehrt': 'HTS 외국인 소진율',
    'frgn_ntby_qty': '외국인 순매수 수량',
    'pgtr_ntby_qty': '프로그램매매 순매수 수량',
    'pvt_scnd_dmrs_prc': '피벗 2차 디저항 가격',
    'pvt_frst_dmrs_prc': '피벗 1차 디저항 가격',
    'pvt_pont_val': '피벗 포인트 값',
    'pvt_frst_dmsp_prc': '피벗 1차 디지지 가격',
    'pvt_scnd_dmsp_prc': '피벗 2차 디지지 가격',
    'dmrs_val': '디저항 값',
    'dmsp_val': '디지지 값',
    'cpfn': '자본금',
    'rstc_wdth_prc': '제한 폭 가격',
    'stck_fcam': '주식 액면가',
    'stck_sspr': '주식 대용가',
    'aspr_unit': '호가단위',
    'hts_deal_qty_unit_val': 'HTS 매매 수량 단위 값',
    'lstn_stcn': '상장 주수',
    'hts_avls': 'HTS 시가총액',
    'per': 'PER',
    'pbr': 'PBR',
    'stac_month': '결산 월',
    'vol_tnrt': '거래량 회전율',
    'eps': 'EPS',
    'bps': 'BPS',
    'd250_hgpr': '250일 최고가',
    'd250_hgpr_date': '250일 최고가 일자',
    'd250_hgpr_vrss_prpr_rate': '250일 최고가 대비 현재가 비율',
    'd250_lwpr': '250일 최저가',
    'd250_lwpr_date': '250일 최저가 일자',
    'd250_lwpr_vrss_prpr_rate': '250일 최저가 대비 현재가 비율',
    'stck_dryy_hgpr': '주식 연중 최고가',
    'dryy_hgpr_vrss_prpr_rate': '연중 최고가 대비 현재가 비율',
    'dryy_hgpr_date': '연중 최고가 일자',
    'stck_dryy_lwpr': '주식 연중 최저가',
    'dryy_lwpr_vrss_prpr_rate': '연중 최저가 대비 현재가 비율',
    'dryy_lwpr_date': '연중 최저가 일자',
    'w52_hgpr': '52주일 최고가',
    'w52_hgpr_vrss_prpr_ctrt': '52주일 최고가 대비 현재가 대비',
    'w52_hgpr_date': '52주일 최고가 일자',
    'w52_lwpr': '52주일 최저가',
    'w52_lwpr_vrss_prpr_ctrt': '52주일 최저가 대비 현재가 대비',
    'w52_lwpr_date': '52주일 최저가 일자',
    'whol_loan_rmnd_rate': '전체 융자 잔고 비율',
    'ssts_yn': '공매도가능여부',
    'stck_shrn_iscd': '주식 단축 종목코드',
    'fcam_cnnm': '액면가 통화명',
    'cpfn_cnnm': '자본금 통화명',
    'apprch_rate': '접근도',
    'frgn_hldn_qty': '외국인 보유 수량',
    'vi_cls_code': 'VI적용구분코드',
    'ovtm_vi_cls_code': '시간외단일가VI적용구분코드',
    'last_ssts_cntg_qty': '최종 공매도 체결 수량',
    'invt_caful_yn': '투자유의여부',
    'mrkt_warn_cls_code': '시장경고코드',
    'short_over_yn': '단기과열여부',
    'sltr_yn': '정리매매여부',
    'mang_issu_cls_code': '관리종목여부'
}

NUMERIC_COLUMNS = []


def main():
    """
    주식현재가 시세 조회 테스트 함수
    
    이 함수는 주식현재가 시세 API를 호출하여 결과를 출력합니다.
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
        result = inquire_price(env_dv="real", fid_cond_mrkt_div_code="J", fid_input_iscd="005930")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    result = result.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에 number 타입이 명시되지 않음)
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result)


if __name__ == "__main__":
    main()
