# -*- coding: utf-8 -*-
"""
Created on 2025-06-17

@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from lendable_by_company import lendable_by_company

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 종목정보 > 당사 대주가능 종목 [국내주식-195]
##############################################################################################

# 통합 컬럼 매핑 (모든 output에서 공통 사용)
COLUMN_MAPPING = {
    'pdno': '상품번호',
    'papr': '액면가',
    'bfdy_clpr': '전일종가',
    'sbst_prvs': '대용가',
    'lmt_qty1': '한도수량1',
    'use_qty1': '사용수량1',
    'trad_psbl_qty2': '매매가능수량2',
    'rght_type_cd': '권리유형코드',
    'bass_dt': '기준일자',
    'psbl_yn': '가능여부',
    'tot_stup_lmt_qty': '총설정한도수량',
    'brch_lmt_qty': '지점한도수량',
    'rqst_psbl_qty': '신청가능수량'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 종목정보
    당사 대주가능 종목[국내주식-195]

    당사 대주가능 종목 테스트 함수
    
    Parameters:
        - excg_dvsn_cd (str): 거래소구분코드 (00(전체), 02(거래소), 03(코스닥))
        - pdno (str): 상품번호 (공백 : 전체조회, 종목코드 입력 시 해당종목만 조회)
        - thco_stln_psbl_yn (str): 당사대주가능여부 (Y)
        - inqr_dvsn_1 (str): 조회구분1 (0 : 전체조회, 1: 종목코드순 정렬)
        - ctx_area_fk200 (str): 연속조회검색조건200 (미입력 (다음조회 불가))
        - ctx_area_nk100 (str): 연속조회키100 (미입력 (다음조회 불가))

    Returns:
        - Tuple[DataFrame, ...]: 당사 대주가능 종목 결과
    
    Example:
        >>> df1, df2 = lendable_by_company(excg_dvsn_cd="00", pdno="", thco_stln_psbl_yn="Y", inqr_dvsn_1="0", ctx_area_fk200="", ctx_area_nk100="")
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
        result1, result2 = lendable_by_company(
            excg_dvsn_cd="00",  # 거래소구분코드
            pdno="",  # 상품번호
            thco_stln_psbl_yn="Y",  # 당사대주가능여부
            inqr_dvsn_1="0",  # 조회구분1
            ctx_area_fk200="",  # 연속조회검색조건200
            ctx_area_nk100="",  # 연속조회키100
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
