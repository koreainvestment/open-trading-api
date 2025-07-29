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
from ksdinfo_mand_deposit import ksdinfo_mand_deposit

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 종목정보 > 예탁원정보(의무예치일정) [국내주식-153]
##############################################################################################

COLUMN_MAPPING = {
    'sht_cd': '종목코드',
    'stk_qty': '주식수',
    'depo_date': '예치일',
    'depo_reason': '사유',
    'tot_issue_qty_per_rate': '총발행주식수대비비율(%)'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 종목정보
    예탁원정보(의무예치일정)[국내주식-153]

    예탁원정보(의무예치일정) 테스트 함수
    
    Parameters:
        - t_dt (str): 조회일자To (~ 일자)
        - sht_cd (str): 종목코드 (공백: 전체,  특정종목 조회시 : 종목코드)
        - f_dt (str): 조회일자From (일자 ~)
        - cts (str): CTS (공백)
    Returns:
        - DataFrame: 예탁원정보(의무예치일정) 결과
    
    Example:
        >>> df = ksdinfo_mand_deposit(t_dt="20250131", sht_cd="", f_dt="20250101", cts="")
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
        result = ksdinfo_mand_deposit(
            t_dt="20250131",  # 조회일자To
            sht_cd="",  # 종목코드
            f_dt="20250101",  # 조회일자From
            cts="",  # CTS
        )
        
        if result is None or result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return
        
        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())

        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)

        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
        
        # 결과 출력
        logger.info("=== 예탁원정보(의무예치일정) 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
