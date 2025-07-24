# -*- coding: utf-8 -*-
"""
Created on 2025-06-18

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from sensitivity_trend_ccnl import sensitivity_trend_ccnl

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] ELW시세 - ELW 민감도 추이(체결)[국내주식-175]
##############################################################################################

COLUMN_MAPPING = {
    'stck_cntg_hour': '주식체결시간',
    'elw_prpr': 'ELW현재가',
    'prdy_vrss': '전일대비',
    'prdy_vrss_sign': '전일대비부호',
    'prdy_ctrt': '전일대비율',
    'hts_thpr': 'hts 이론가',
    'delta_val': '델타 값',
    'gama': '감마',
    'theta': '세타',
    'vega': '베가',
    'rho': '로우'
}

NUMERIC_COLUMNS = [
    'ELW현재가', '전일대비', '전일대비율', 'hts 이론가', '델타 값', 
    '감마', '세타', '베가', '로우'
]

def main():
    """
    [국내주식] ELW시세
    ELW 민감도 추이(체결)[국내주식-175]

    ELW 민감도 추이(체결) 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건시장분류코드 (시장구분코드 (W))
        - fid_input_iscd (str): 입력종목코드 (ex) 58J297(KBJ297삼성전자콜))
    Returns:
        - DataFrame: ELW 민감도 추이(체결) 결과
    
    Example:
        >>> df = sensitivity_trend_ccnl(fid_cond_mrkt_div_code="W", fid_input_iscd="58J297")
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
        logger.info("API 호출")
        result = sensitivity_trend_ccnl(
            fid_cond_mrkt_div_code="W",  # 조건시장분류코드
            fid_input_iscd="57LA50",  # 입력종목코드
        )
        
        if result is None or result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return
        
        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())

        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)
        
        # 숫자 컬럼 처리
        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
        
        # 결과 출력
        logger.info("=== ELW 민감도 추이(체결) 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
