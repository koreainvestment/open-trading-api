"""
Created on 20250601 
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
# [국내주식] 기본시세 > ETF/ETN 현재가[v1_국내주식-068]
##############################################################################################

# 컬럼명 매핑
COLUMN_MAPPING = {
    'stck_prpr': '주식 현재가',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_vrss': '전일 대비',
    'prdy_ctrt': '전일 대비율',
    'acml_vol': '누적 거래량',
    'prdy_vol': '전일 거래량',
    'stck_mxpr': '주식 상한가',
    'stck_llam': '주식 하한가',
    'stck_prdy_clpr': '주식 전일 종가',
    'stck_oprc': '주식 시가2',
    'prdy_clpr_vrss_oprc_rate': '전일 종가 대비 시가2 비율',
    'stck_hgpr': '주식 최고가',
    'prdy_clpr_vrss_hgpr_rate': '전일 종가 대비 최고가 비율',
    'stck_lwpr': '주식 최저가',
    'prdy_clpr_vrss_lwpr_rate': '전일 종가 대비 최저가 비율',
    'prdy_last_nav': '전일 최종 NAV',
    'nav': 'NAV',
    'nav_prdy_vrss': 'NAV 전일 대비',
    'nav_prdy_vrss_sign': 'NAV 전일 대비 부호',
    'nav_prdy_ctrt': 'NAV 전일 대비율',
    'trc_errt': '추적 오차율',
    'stck_sdpr': '주식 기준가',
    'stck_sspr': '주식 대용가',
    'nmix_ctrt': '지수 대비율',
    'etf_crcl_stcn': 'ETF 유통 주수',
    'etf_ntas_ttam': 'ETF 순자산 총액',
    'etf_frcr_ntas_ttam': 'ETF 외화 순자산 총액',
    'frgn_limt_rate': '외국인 한도 비율',
    'frgn_oder_able_qty': '외국인 주문 가능 수량',
    'etf_cu_unit_scrt_cnt': 'ETF CU 단위 증권 수',
    'etf_cnfg_issu_cnt': 'ETF 구성 종목 수',
    'etf_dvdn_cycl': 'ETF 배당 주기',
    'crcd': '통화 코드',
    'etf_crcl_ntas_ttam': 'ETF 유통 순자산 총액',
    'etf_frcr_crcl_ntas_ttam': 'ETF 외화 유통 순자산 총액',
    'etf_frcr_last_ntas_wrth_val': 'ETF 외화 최종 순자산 가치 값',
    'lp_oder_able_cls_code': 'LP 주문 가능 구분 코드',
    'stck_dryy_hgpr': '주식 연중 최고가',
    'dryy_hgpr_vrss_prpr_rate': '연중 최고가 대비 현재가 비율',
    'dryy_hgpr_date': '연중 최고가 일자',
    'stck_dryy_lwpr': '주식 연중 최저가',
    'dryy_lwpr_vrss_prpr_rate': '연중 최저가 대비 현재가 비율',
    'dryy_lwpr_date': '연중 최저가 일자',
    'bstp_kor_isnm': '업종 한글 종목명',
    'vi_cls_code': 'VI적용구분코드',
    'lstn_stcn': '상장 주수',
    'frgn_hldn_qty': '외국인 보유 수량',
    'frgn_hldn_qty_rate': '외국인 보유 수량 비율',
    'etf_trc_ert_mltp': 'ETF 추적 수익률 배수',
    'dprt': '괴리율',
    'mbcr_name': '회원사 명',
    'stck_lstn_date': '주식 상장 일자',
    'mtrt_date': '만기 일자',
    'shrg_type_code': '분배금형태코드',
    'lp_hldn_rate': 'LP 보유 비율',
    'etf_trgt_nmix_bstp_code': 'ETF대상지수업종코드',
    'etf_div_name': 'ETF 분류 명',
    'etf_rprs_bstp_kor_isnm': 'ETF 대표 업종 한글 종목명',
    'lp_hldn_vol': 'ETN LP 보유량'
}

# 숫자형 컬럼
NUMERIC_COLUMNS = []

def main():
    """
    ETF/ETN 현재가 조회 테스트 함수
    
    이 함수는 ETF/ETN 현재가 API를 호출하여 결과를 출력합니다.
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
    logging.info("API 호출")
    try:
        result = inquire_price(fid_cond_mrkt_div_code="J", fid_input_iscd="005930")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return
    
    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())
    
    # 한글 컬럼명으로 변환
    result = result.rename(columns=COLUMN_MAPPING)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result)

if __name__ == "__main__":
    main() 