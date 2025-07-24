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
from inquire_time_indexchartprice import inquire_time_indexchartprice

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 기본시세 > 업종 분봉조회[v1_국내주식-045]
##############################################################################################

# 통합 컬럼 매핑 (모든 output에서 공통 사용)
COLUMN_MAPPING = {
    'Output1': '응답상세',
    'bstp_nmix_prdy_vrss': '업종 지수 전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'bstp_nmix_prdy_ctrt': '업종 지수 전일 대비율',
    'prdy_nmix': '전일 지수',
    'acml_vol': '누적 거래량',
    'acml_tr_pbmn': '누적 거래 대금',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'bstp_nmix_prpr': '업종 지수 현재가',
    'bstp_cls_code': '업종 구분 코드',
    'prdy_vol': '전일 거래량',
    'bstp_nmix_oprc': '업종 지수 시가2',
    'bstp_nmix_hgpr': '업종 지수 최고가',
    'bstp_nmix_lwpr': '업종 지수 최저가',
    'futs_prdy_oprc': '선물 전일 시가',
    'futs_prdy_hgpr': '선물 전일 최고가',
    'futs_prdy_lwpr': '선물 전일 최저가',
    'Output2': '응답상세2',
    'stck_bsop_date': '주식 영업 일자',
    'stck_cntg_hour': '주식 체결 시간',
    'bstp_nmix_prpr': '업종 지수 현재가',
    'bstp_nmix_oprc': '업종 지수 시가2',
    'bstp_nmix_hgpr': '업종 지수 최고가',
    'bstp_nmix_lwpr': '업종 지수 최저가',
    'cntg_vol': '체결 거래량',
    'acml_tr_pbmn': '누적 거래 대금'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 업종/기타
    업종 분봉조회[v1_국내주식-045]

    업종 분봉조회 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): FID 조건 시장 분류 코드 (U)
        - fid_etc_cls_code (str): FID 기타 구분 코드 (0: 기본 1:장마감,시간외 제외)
        - fid_input_iscd (str): FID 입력 종목코드 (0001 : 종합 0002 : 대형주 ... 포탈 (FAQ : 종목정보 다운로드(국내) - 업종코드 참조))
        - fid_input_hour_1 (str): FID 입력 시간1 (30, 60 -> 1분, 600-> 10분, 3600 -> 1시간)
        - fid_pw_data_incu_yn (str): FID 과거 데이터 포함 여부 (Y (과거) / N (당일))

    Returns:
        - Tuple[DataFrame, ...]: 업종 분봉조회 결과
    
    Example:
        >>> df1, df2 = inquire_time_indexchartprice(fid_cond_mrkt_div_code="U", fid_etc_cls_code="0", fid_input_iscd="0001", fid_input_hour_1="60", fid_pw_data_incu_yn="Y")
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
        result1, result2 = inquire_time_indexchartprice(
            fid_cond_mrkt_div_code="U",  # FID 조건 시장 분류 코드
            fid_etc_cls_code="0",  # FID 기타 구분 코드
            fid_input_iscd="0001",  # FID 입력 종목코드
            fid_input_hour_1="60",  # FID 입력 시간1
            fid_pw_data_incu_yn="Y",  # FID 과거 데이터 포함 여부
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
