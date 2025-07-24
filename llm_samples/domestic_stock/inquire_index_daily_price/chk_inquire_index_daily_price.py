# -*- coding: utf-8 -*-
"""
Created on 2025-06-17

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from inquire_index_daily_price import inquire_index_daily_price

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 업종/기타 > 국내업종 일자별지수 [v1_국내주식-065]
##############################################################################################

# 통합 컬럼 매핑 (모든 output에서 공통 사용)
COLUMN_MAPPING = {
    'bstp_nmix_prpr': '업종 지수 현재가',
    'bstp_nmix_prdy_vrss': '업종 지수 전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'bstp_nmix_prdy_ctrt': '업종 지수 전일 대비율',
    'acml_vol': '누적 거래량',
    'acml_tr_pbmn': '누적 거래 대금',
    'bstp_nmix_oprc': '업종 지수 시가2',
    'bstp_nmix_hgpr': '업종 지수 최고가',
    'bstp_nmix_lwpr': '업종 지수 최저가',
    'prdy_vol': '전일 거래량',
    'ascn_issu_cnt': '상승 종목 수',
    'down_issu_cnt': '하락 종목 수',
    'stnr_issu_cnt': '보합 종목 수',
    'uplm_issu_cnt': '상한 종목 수',
    'lslm_issu_cnt': '하한 종목 수',
    'prdy_tr_pbmn': '전일 거래 대금',
    'dryy_bstp_nmix_hgpr_date': '연중업종지수최고가일자',
    'dryy_bstp_nmix_hgpr': '연중업종지수최고가',
    'dryy_bstp_nmix_lwpr': '연중업종지수최저가',
    'dryy_bstp_nmix_lwpr_date': '연중업종지수최저가일자',
    'stck_bsop_date': '주식 영업 일자',
    'bstp_nmix_prpr': '업종 지수 현재가',
    'prdy_vrss_sign': '전일 대비 부호',
    'bstp_nmix_prdy_vrss': '업종 지수 전일 대비',
    'bstp_nmix_prdy_ctrt': '업종 지수 전일 대비율',
    'bstp_nmix_oprc': '업종 지수 시가2',
    'bstp_nmix_hgpr': '업종 지수 최고가',
    'bstp_nmix_lwpr': '업종 지수 최저가',
    'acml_vol_rlim': '누적 거래량 비중',
    'acml_vol': '누적 거래량',
    'acml_tr_pbmn': '누적 거래 대금',
    'invt_new_psdg': '투자 신 심리도',
    'd20_dsrt': '20일 이격도'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 업종/기타
    국내업종 일자별지수[v1_국내주식-065]

    국내업종 일자별지수 테스트 함수
    
    Parameters:
        - fid_period_div_code (str): FID 기간 분류 코드 (일/주/월 구분코드 ( D:일별 , W:주별, M:월별 ))
        - fid_cond_mrkt_div_code (str): FID 조건 시장 분류 코드 (시장구분코드 (업종 U))
        - fid_input_iscd (str): FID 입력 종목코드 (코스피(0001), 코스닥(1001), 코스피200(2001) ... 포탈 (FAQ : 종목정보 다운로드(국내) - 업종코드 참조))
        - fid_input_date_1 (str): FID 입력 날짜1 (입력 날짜(ex. 20240223))

    Returns:
        - Tuple[DataFrame, ...]: 국내업종 일자별지수 결과
    
    Example:
        >>> df1, df2 = inquire_index_daily_price(fid_period_div_code="D", fid_cond_mrkt_div_code="U", fid_input_iscd="0001", fid_input_date_1="20250101")
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
        
        # API 호출        
        result1, result2 = inquire_index_daily_price(
            fid_period_div_code="D",  # FID 기간 분류 코드
            fid_cond_mrkt_div_code="U",  # FID 조건 시장 분류 코드
            fid_input_iscd="0001",  # FID 입력 종목코드
            fid_input_date_1="20250101",  # FID 입력 날짜1
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

            for col in NUMERIC_COLUMNS:
                if col in result1.columns:
                    result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

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

            for col in NUMERIC_COLUMNS:
                if col in result2.columns:
                    result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

            logger.info("output2 결과:")
            print(result2)
        else:
            logger.info("output2 데이터가 없습니다.")

        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
