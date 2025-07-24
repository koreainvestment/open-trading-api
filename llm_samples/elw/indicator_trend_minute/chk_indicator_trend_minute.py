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
from indicator_trend_minute import indicator_trend_minute

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] ELW시세 - ELW 투자지표추이(분별)[국내주식-174]
##############################################################################################

COLUMN_MAPPING = {
    'stck_bsop_date': '주식영업일자',
    'stck_cntg_hour': '주식체결시간',
    'elw_prpr': 'ELW현재가',
    'elw_oprc': 'ELW시가2',
    'elw_hgpr': 'ELW최고가',
    'elw_lwpr': 'ELW최저가',
    'lvrg_val': '레버리지값',
    'gear': '기어링',
    'prmm_val': '프리미엄값',
    'invl_val': '내재가치값',
    'prit': '패리티',
    'acml_vol': '누적거래량',
    'cntg_vol': '체결거래량'
}

NUMERIC_COLUMNS = [
    'ELW현재가', 'ELW시가2', 'ELW최고가', 'ELW최저가', '레버리지값', '기어링', 
    '프리미엄값', '내재가치값', '패리티', '누적거래량', '체결거래량'
]

def main():
    """
    [국내주식] ELW시세
    ELW 투자지표추이(분별)[국내주식-174]

    ELW 투자지표추이(분별) 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건시장분류코드 (시장구분코드 (W))
        - fid_input_iscd (str): 입력종목코드 (ex) 58J297(KBJ297삼성전자콜))
        - fid_hour_cls_code (str): 시간구분코드 ('60(1분), 180(3분), 300(5분), 600(10분), 1800(30분), 3600(60분), 7200(60분) ')
        - fid_pw_data_incu_yn (str): 과거데이터 포함 여부 (N(과거데이터포함X),Y(과거데이터포함O))
    Returns:
        - DataFrame: ELW 투자지표추이(분별) 결과
    
    Example:
        >>> df = indicator_trend_minute(fid_cond_mrkt_div_code="W", fid_input_iscd="58J297", fid_hour_cls_code="60", fid_pw_data_incu_yn="N")
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
        result = indicator_trend_minute(
            fid_cond_mrkt_div_code="W",  # 조건시장분류코드
            fid_input_iscd="57LA50",  # 입력종목코드
            fid_hour_cls_code="60",  # 시간구분코드
            fid_pw_data_incu_yn="N",  # 과거데이터 포함 여부
        )
        
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
        logger.info("=== ELW 투자지표추이(분별) 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
