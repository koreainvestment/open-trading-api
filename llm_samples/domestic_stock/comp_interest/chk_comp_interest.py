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
from comp_interest import comp_interest

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 업종/기타 > 금리 종합(국내채권_금리)[국내주식-155]
##############################################################################################

# 통합 컬럼 매핑 (모든 output에서 공통 사용)
COLUMN_MAPPING = {
    'bcdt_code': '자료코드',
    'hts_kor_isnm': 'HTS한글종목명',
    'bond_mnrt_prpr': '채권금리현재가',
    'prdy_vrss_sign': '전일대비부호',
    'bond_mnrt_prdy_vrss': '채권금리전일대비',
    'prdy_ctrt': '전일대비율',
    'stck_bsop_date': '주식영업일자',
    'bcdt_code': '자료코드',
    'hts_kor_isnm': 'HTS한글종목명',
    'bond_mnrt_prpr': '채권금리현재가',
    'prdy_vrss_sign': '전일대비부호',
    'bond_mnrt_prdy_vrss': '채권금리전일대비',
    'bstp_nmix_prdy_ctrt': '업종지수전일대비율',
    'stck_bsop_date': '주식영업일자'
}

NUMERIC_COLUMNS = []


def main():
    """
    [국내주식] 업종/기타
    금리 종합(국내채권_금리)[국내주식-155]

    금리 종합(국내채권_금리) 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건시장분류코드 (Unique key(I))
        - fid_cond_scr_div_code (str): 조건화면분류코드 (Unique key(20702))
        - fid_div_cls_code (str): 분류구분코드 (1: 해외금리지표)
        - fid_div_cls_code1 (str): 분류구분코드 (공백 : 전체)

    Returns:
        - Tuple[DataFrame, ...]: 금리 종합(국내채권_금리) 결과
    
    Example:
        >>> df1, df2 = comp_interest(fid_cond_mrkt_div_code="I", fid_cond_scr_div_code="20702", fid_div_cls_code="1", fid_div_cls_code1="")
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
        result1, result2 = comp_interest(
            fid_cond_mrkt_div_code="I",  # 조건시장분류코드
            fid_cond_scr_div_code="20702",  # 조건화면분류코드
            fid_div_cls_code="1",  # 분류구분코드
            fid_div_cls_code1="",  # 분류구분코드
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
