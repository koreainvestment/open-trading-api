# -*- coding: utf-8 -*-
"""
Created on 2025-07-01

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from investor_unpd_trend import investor_unpd_trend

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물 미결제추이 [v1_해외선물-029]
##############################################################################################

# 상수 정의
COLUMN_MAPPING = {
    'row_cnt': '응답레코드카운트',
    'prod_iscd': '상품',
    'cftc_iscd': 'CFTC코드',
    'bsop_date': '일자',
    'bidp_spec': '매수투기',
    'askp_spec': '매도투기',
    'spread_spec': '스프레드투기',
    'bidp_hedge': '매수헤지',
    'askp_hedge': '매도헤지',
    'hts_otst_smtn': '미결제합계',
    'bidp_missing': '매수누락',
    'askp_missing': '매도누락',
    'bidp_spec_cust': '매수투기고객',
    'askp_spec_cust': '매도투기고객',
    'spread_spec_cust': '스프레드투기고객',
    'bidp_hedge_cust': '매수헤지고객',
    'askp_hedge_cust': '매도헤지고객',
    'cust_smtn': '고객합계'
}

NUMERIC_COLUMNS = ['응답레코드카운트', '매수투기', '매도투기', '스프레드투기', '매수헤지', '매도헤지', '미결제합계', 
                   '매수누락', '매도누락', '매수투기고객', '매도투기고객', '스프레드투기고객', '매수헤지고객', 
                   '매도헤지고객', '고객합계']

def main():
    """
    [해외선물옵션] 기본시세
    해외선물 미결제추이[해외선물-029]

    해외선물 미결제추이 테스트 함수
    
    Parameters:
        - prod_iscd (str): 상품 (금리 (GE, ZB, ZF,ZN,ZT), 금속(GC, PA, PL,SI, HG), 농산물(CC, CT,KC, OJ, SB, ZC,ZL, ZM, ZO, ZR, ZS, ZW), 에너지(CL, HO, NG, WBS), 지수(ES, NQ, TF, YM, VX), 축산물(GF, HE, LE), 통화(6A, 6B, 6C, 6E, 6J, 6N, 6S, DX))
        - bsop_date (str): 일자 (기준일(ex)20240513))
        - upmu_gubun (str): 구분 (0(수량), 1(증감))
        - cts_key (str): CTS_KEY (공백)

    Returns:
        - DataFrame: 해외선물 미결제추이 결과
    
    Example:
        >>> df1, df2 = investor_unpd_trend(prod_iscd="GE", bsop_date="20240513", upmu_gubun="0", cts_key="")
    """
    try:
        # pandas 출력 옵션 설정
        pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
        pd.set_option('display.width', None)  # 출력 너비 제한 해제
        pd.set_option('display.max_rows', None)  # 모든 행 표시

        # 토큰 발급
        ka.auth()

        # API 호출
        logger.info("API 호출")
        result1, result2 = investor_unpd_trend(
            prod_iscd="CL",
            bsop_date="20250630",
            upmu_gubun="0",
            cts_key=""
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
            
            # 숫자형 컬럼 처리
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
            
            # 숫자형 컬럼 처리
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
