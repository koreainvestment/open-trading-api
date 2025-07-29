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
from market_time import market_time

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물옵션 장운영시간 [해외선물-030]
##############################################################################################

# 상수 정의
COLUMN_MAPPING = {
    'fm_pdgr_cd': 'FM상품군코드',
    'fm_pdgr_name': 'FM상품군명',
    'fm_excg_cd': 'FM거래소코드',
    'fm_excg_name': 'FM거래소명',
    'fuop_dvsn_name': '선물옵션구분명',
    'fm_clas_cd': 'FM클래스코드',
    'fm_clas_name': 'FM클래스명',
    'am_mkmn_strt_tmd': '오전장운영시작시각',
    'am_mkmn_end_tmd': '오전장운영종료시각',
    'pm_mkmn_strt_tmd': '오후장운영시작시각',
    'pm_mkmn_end_tmd': '오후장운영종료시각',
    'mkmn_nxdy_strt_tmd': '장운영익일시작시각',
    'mkmn_nxdy_end_tmd': '장운영익일종료시각',
    'base_mket_strt_tmd': '기본시장시작시각',
    'base_mket_end_tmd': '기본시장종료시각'
}

NUMERIC_COLUMNS = []

def main():
    """
    [해외선물옵션] 기본시세
    해외선물옵션 장운영시간[해외선물-030]

    해외선물옵션 장운영시간 테스트 함수
    
    Parameters:
        - fm_pdgr_cd (str): FM상품군코드 (공백)
        - fm_clas_cd (str): FM클래스코드 ('공백(전체), 001(통화), 002(금리), 003(지수), 004(농산물),005(축산물),006(금속),007(에너지)')
        - fm_excg_cd (str): FM거래소코드 ('CME(CME), EUREX(EUREX), HKEx(HKEx), ICE(ICE), SGX(SGX), OSE(OSE), ASX(ASX), CBOE(CBOE), MDEX(MDEX), NYSE(NYSE), BMF(BMF),FTX(FTX), HNX(HNX), ETC(기타)')
        - opt_yn (str): 옵션여부 (%(전체), N(선물), Y(옵션))
        - ctx_area_nk200 (str): 연속조회키200 ()
        - ctx_area_fk200 (str): 연속조회검색조건200 ()

    Returns:
        - DataFrame: 해외선물옵션 장운영시간 결과
    
    Example:
        >>> df = market_time(fm_pdgr_cd="", fm_clas_cd="", fm_excg_cd="CME", opt_yn="N", ctx_area_nk200="", ctx_area_fk200="")
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
        result = market_time(
            fm_pdgr_cd="",
            fm_clas_cd="",
            fm_excg_cd="CME",
            opt_yn="%",
            ctx_area_nk200="",
            ctx_area_fk200=""
        )
        
        if result is None or result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return
        
        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())

        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)
        
        # 숫자형 컬럼 처리
        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
        
        # 결과 출력
        logger.info("=== 해외선물옵션 장운영시간 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
