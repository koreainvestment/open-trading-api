"""
Created on 20250114
@author: LaivData SJPark with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_component_stock_price import inquire_component_stock_price

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 기본시세 > ETF 구성종목시세[국내주식-073]
##############################################################################################

# 컬럼명 매핑
COLUMN_MAPPING = {
    'stck_prpr': '매매 일자',
    'prdy_vrss': '주식 현재가',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비',
    'etf_cnfg_issu_avls': '전일 대비율',
    'nav': '누적 거래량',
    'nav_prdy_vrss_sign': '결제 일자',
    'nav_prdy_vrss': '전체 융자 신규 주수',
    'nav_prdy_ctrt': '전체 융자 상환 주수',  
    'etf_ntas_ttam': '전체 융자 잔고 주수',
    'prdy_clpr_nav': '전체 융자 신규 금액',
    'oprc_nav': '전체 융자 상환 금액',
    'hprc_nav': '전체 융자 잔고 금액',
    'lprc_nav': '전체 융자 잔고 비율',
    'etf_cu_unit_scrt_cnt': '전체 융자 공여율',
    'etf_cnfg_issu_cnt': '전체 대주 신규 주수',
    'stck_shrn_iscd': '주식 단축 종목코드',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'acml_vol': '누적 거래량',
    'acml_tr_pbmn': '누적 거래 대금',
    'tday_rsfl_rate': '당일 등락 비율',
    'prdy_vrss_vol': '전일 대비 거래량',
    'tr_pbmn_tnrt': '거래대금회전율',
    'hts_avls': 'HTS 시가총액',
    'etf_vltn_amt': 'ETF구성종목내평가금액',
    'etf_cnfg_issu_rlim': 'ETF구성종목비중'
}

# 숫자형 컬럼
NUMERIC_COLUMNS = ['주식 현재가', '전일 대비', '전일 대비율', '누적 거래량', '전체 융자 신규 주수', 
                   '전체 융자 상환 주수', '전체 융자 잔고 주수', '전체 융자 신규 금액', '전체 융자 상환 금액', 
                   '전체 융자 잔고 금액', '전체 융자 잔고 비율', '전체 융자 공여율', '전체 대주 신규 주수',
                   '누적 거래 대금', '당일 등락 비율', '전일 대비 거래량', '거래대금회전율', 'HTS 시가총액', 
                   'ETF구성종목시가총액', 'ETF구성종목비중', 'ETF구성종목내평가금액']

def main():
    """
    ETF 구성종목시세 조회 테스트 함수
    
    이 함수는 ETF 구성종목시세 API를 호출하여 결과를 출력합니다.
    테스트 데이터로 KODEX 200 ETF(069500)를 사용합니다.
    
    Returns:
        None
    """
    
    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시
    
    # 인증 토큰 발급
    ka.auth()
    
    # API 호출
    logging.info("API 호출")
    try:
        result1, result2 = inquire_component_stock_price(fid_cond_mrkt_div_code="J", fid_input_iscd="069500", fid_cond_scr_div_code="11216")
    except ValueError as e:
        logging.error("에러 발생: %s", str(e))
        return
        
    # output1 결과 처리
    logging.info("=== output1 조회 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())
    
    # 한글 컬럼명으로 변환
    result1 = result1.rename(columns=COLUMN_MAPPING)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result1)
    
    # output2 결과 처리
    logging.info("=== output2 조회 결과 ===") 
    logging.info("사용 가능한 컬럼: %s", result2.columns.tolist())
    
    # 한글 컬럼명으로 변환
    result2 = result2.rename(columns=COLUMN_MAPPING)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result2)

if __name__ == "__main__":
    main() 