"""
Created on 2025-06-18

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from compare_stocks import compare_stocks

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] ELW시세 - ELW 비교대상종목조회[국내주식-183]
##############################################################################################

COLUMN_MAPPING = {
    'elw_shrn_iscd': 'ELW단축종목코드',
    'elw_kor_isnm': 'ELW한글종목명'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] ELW시세
    ELW 비교대상종목조회[국내주식-183]

    ELW 비교대상종목조회 테스트 함수
    
    Parameters:
        - fid_cond_scr_div_code (str): 조건화면분류코드 (11517(Primary key))
        - fid_input_iscd (str): 입력종목코드 (종목코드(ex)005930(삼성전자)))
    Returns:
        - DataFrame: ELW 비교대상종목조회 결과
    
    Example:
        >>> df = compare_stocks(fid_cond_scr_div_code="11517", fid_input_iscd="005930")
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

        # 인라인 코드로 파라미터 직접 전달
        logger.info("API 호출 ")
        result = compare_stocks(fid_cond_scr_div_code="11517", fid_input_iscd="005930")
        
        if result is None or result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return
        
        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())

        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)
        
        # 숫자형 컬럼 소수점 둘째자리까지 표시
        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
                
        # 결과 출력
        logger.info("=== ELW 비교대상종목조회 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
