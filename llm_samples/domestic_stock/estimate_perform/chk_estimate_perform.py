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
from estimate_perform import estimate_perform

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 종목정보 > 국내주식 종목추정실적[국내주식-187]
##############################################################################################

# 통합 컬럼 매핑 (모든 output에서 공통 사용)
COLUMN_MAPPING = {
    'sht_cd': 'ELW단축종목코드',
    'item_kor_nm': 'HTS한글종목명',
    'estdate': '전일대비부호',
    'capital': '누적거래량',
    'forn_item_lmtrt': '행사가',
    'data1': 'DATA1',
    'data2': 'DATA2',
    'data3': 'DATA3',
    'data4': 'DATA4',
    'data5': 'DATA5',
    'output3': '응답상세',
    'data1': 'DATA1',
    'data2': 'DATA2',
    'data3': 'DATA3',
    'data4': 'DATA4',
    'data5': 'DATA5',
    'output4': '응답상세',
    'dt': '결산년월'
}

NUMERIC_COLUMNS = []


def main():
    """
    [국내주식] 종목정보
    국내주식 종목추정실적[국내주식-187]

    국내주식 종목추정실적 테스트 함수
    
    Parameters:
        - sht_cd (str): 종목코드 (ex) 265520)

    Returns:
        - Tuple[DataFrame, ...]: 국내주식 종목추정실적 결과
    
    Example:
        >>> df1, df2, df3, df4 = estimate_perform(sht_cd="265520")
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
        logger.info("API 호출 시작: 국내주식 종목추정실적")
        result1, result2, result3, result4 = estimate_perform(
            sht_cd="265520",  # 종목코드
        )

        # 결과 확인
        results = [result1, result2, result3, result4]
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

        # output3 결과 처리
        logger.info("=== output3 조회 ===")
        if not result3.empty:
            logger.info("사용 가능한 컬럼: %s", result3.columns.tolist())

            # 통합 컬럼명 한글 변환 (필요한 컬럼만 자동 매핑됨)
            result3 = result3.rename(columns=COLUMN_MAPPING)

            for col in NUMERIC_COLUMNS:
                if col in result3.columns:
                    result3[col] = pd.to_numeric(result3[col], errors='coerce').round(2)

            logger.info("output3 결과:")
            print(result3)
        else:
            logger.info("output3 데이터가 없습니다.")

        # output4 결과 처리
        logger.info("=== output4 조회 ===")
        if not result4.empty:
            logger.info("사용 가능한 컬럼: %s", result4.columns.tolist())

            # 통합 컬럼명 한글 변환 (필요한 컬럼만 자동 매핑됨)
            result4 = result4.rename(columns=COLUMN_MAPPING)

            for col in NUMERIC_COLUMNS:
                if col in result4.columns:
                    result4[col] = pd.to_numeric(result4[col], errors='coerce').round(2)

            logger.info("output4 결과:")
            print(result4)
        else:
            logger.info("output4 데이터가 없습니다.")


    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise


if __name__ == "__main__":
    main()
