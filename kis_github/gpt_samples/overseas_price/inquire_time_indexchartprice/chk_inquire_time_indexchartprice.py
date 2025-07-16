# -*- coding: utf-8 -*-
"""
Created on 2025-06-30

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from inquire_time_indexchartprice import inquire_time_indexchartprice

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

COLUMN_MAPPING = {
    'ovrs_nmix_prdy_vrss': '해외 지수 전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'prdy_ctrt': '전일 대비율',
    'ovrs_nmix_prdy_clpr': '해외 지수 전일 종가',
    'acml_vol': '누적 거래량',
    'ovrs_nmix_prpr': '해외 지수 현재가',
    'stck_shrn_iscd': '주식 단축 종목코드',
    'ovrs_prod_oprc': '해외 상품 시가2',
    'ovrs_prod_hgpr': '해외 상품 최고가',
    'ovrs_prod_lwpr': '해외 상품 최저가',
    'stck_bsop_date': '주식 영업 일자',
    'stck_cntg_hour': '주식 체결 시간',
    'optn_prpr': '옵션 현재가',
    'optn_oprc': '옵션 시가2',
    'optn_hgpr': '옵션 최고가',
    'optn_lwpr': '옵션 최저가',
    'cntg_vol': '체결 거래량'
}

def main():
    """
    [해외주식] 기본시세
    해외지수분봉조회[v1_해외주식-031]

    해외지수분봉조회 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (N 해외지수 X 환율 KX 원화환율)
        - fid_input_iscd (str): 입력 종목코드 (종목번호(ex. TSLA))
        - fid_hour_cls_code (str): 시간 구분 코드 (0: 정규장, 1: 시간외)
        - fid_pw_data_incu_yn (str): 과거 데이터 포함 여부 (Y/N)

    Returns:
        - DataFrame: 해외지수분봉조회 결과
    
    Example:
        >>> df1, df2 = inquire_time_indexchartprice(fid_cond_mrkt_div_code="N", fid_input_iscd="TSLA", fid_hour_cls_code="0", fid_pw_data_incu_yn="Y")
    """
    try:
        # pandas 출력 옵션 설정
        pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
        pd.set_option('display.width', None)  # 출력 너비 제한 해제
        pd.set_option('display.max_rows', None)  # 모든 행 표시

        # 토큰 발급
        logger.info("토큰 발급 중...")
        ka.auth()
        logger.info("토큰 발급 완료")

        # 해외지수분봉조회 파라미터 설정
        logger.info("API 파라미터 설정 중...")
        fid_cond_mrkt_div_code = "N"  # 조건 시장 분류 코드
        fid_input_iscd = "SPX"  # 입력 종목코드
        fid_hour_cls_code = "0"  # 시간 구분 코드
        fid_pw_data_incu_yn = "Y"  # 과거 데이터 포함 여부

        
        # API 호출
        logger.info("API 호출 시작: 해외지수분봉조회")
        result1, result2 = inquire_time_indexchartprice(
            fid_cond_mrkt_div_code=fid_cond_mrkt_div_code,  # 조건 시장 분류 코드
            fid_input_iscd=fid_input_iscd,  # 입력 종목코드
            fid_hour_cls_code=fid_hour_cls_code,  # 시간 구분 코드
            fid_pw_data_incu_yn=fid_pw_data_incu_yn,  # 과거 데이터 포함 여부
        )
        
        # 결과 확인
        results = [result1, result2]
        if all(result is None or result.empty for result in results):
            logger.warning("조회된 데이터가 없습니다.")
            return
        

        # output1 결과 처리
        logger.info("=== output1 조회 ===")
        if not result1.empty:
            logger.info("사용 가능한 컬럼: %s", result1.columns.tolist())
            
            # 통합 컬럼명 한글 변환 (필요한 컬럼만 자동 매핑됨)
            result1 = result1.rename(columns=COLUMN_MAPPING)
            logger.info("output1 결과:")
            print(result1)
        else:
            logger.info("output1 데이터가 없습니다.")

        # output2 결과 처리
        logger.info("=== output2 조회 ===")
        if not result2.empty:
            logger.info("사용 가능한 컬럼: %s", result2.columns.tolist())
            
            # 통합 컬럼명 한글 변환 (필요한 컬럼만 자동 매핑됨)
            result2 = result2.rename(columns=COLUMN_MAPPING)
            logger.info("output2 결과:")
            print(result2)
        else:
            logger.info("output2 데이터가 없습니다.")

        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
