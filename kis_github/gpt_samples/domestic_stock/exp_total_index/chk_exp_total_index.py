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
from exp_total_index import exp_total_index

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 업종/기타 > 국내주식 예상체결 전체지수[국내주식-122]
##############################################################################################

# 통합 컬럼 매핑 (모든 output에서 공통 사용)
COLUMN_MAPPING = {
    'bstp_nmix_prpr': '업종 지수 현재가',
    'bstp_nmix_prdy_vrss': '업종 지수 전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비율',
    'acml_vol': '누적 거래량',
    'ascn_issu_cnt': '상승 종목 수',
    'down_issu_cnt': '하락 종목 수',
    'stnr_issu_cnt': '보합 종목 수',
    'bstp_cls_code': '업종 구분 코드',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'bstp_nmix_prpr': '업종 지수 현재가',
    'bstp_nmix_prdy_vrss': '업종 지수 전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'bstp_nmix_prdy_ctrt': '업종 지수 전일 대비율',
    'acml_vol': '누적 거래량',
    'nmix_sdpr': '지수 기준가',
    'ascn_issu_cnt': '상승 종목 수',
    'stnr_issu_cnt': '보합 종목 수',
    'down_issu_cnt': '하락 종목 수'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 업종/기타
    국내주식 예상체결 전체지수[국내주식-122]

    국내주식 예상체결 전체지수 테스트 함수
    
    Parameters:
        - fid_mrkt_cls_code (str): 시장 구분 코드 (0:전체 K:거래소 Q:코스닥)
        - fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (시장구분코드 (업종 U))
        - fid_cond_scr_div_code (str): 조건 화면 분류 코드 (Unique key(11175))
        - fid_input_iscd (str): 입력 종목코드 (0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100)
        - fid_mkop_cls_code (str): 장운영 구분 코드 (1:장시작전, 2:장마감)

    Returns:
        - Tuple[DataFrame, ...]: 국내주식 예상체결 전체지수 결과
    
    Example:
        >>> df1, df2 = exp_total_index(fid_mrkt_cls_code="0", fid_cond_mrkt_div_code="U", fid_cond_scr_div_code="11175", fid_input_iscd="0000", fid_mkop_cls_code="1")
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
        result1, result2 = exp_total_index(
            fid_mrkt_cls_code="0",  # 시장 구분 코드
            fid_cond_mrkt_div_code="U",  # 조건 시장 분류 코드
            fid_cond_scr_div_code="11175",  # 조건 화면 분류 코드
            fid_input_iscd="0000",  # 입력 종목코드
            fid_mkop_cls_code="1",  # 장운영 구분 코드
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
