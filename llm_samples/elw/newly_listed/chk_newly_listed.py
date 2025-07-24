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
from newly_listed import newly_listed

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] ELW시세 - ELW 신규상장종목[국내주식-181]
##############################################################################################

COLUMN_MAPPING = {
    'elw_shrn_iscd': 'ELW단축종목코드',
    'unas_isnm': '기초자산종목명',
    'lstn_stcn': '상장주수',
    'acpr': '행사가',
    'stck_last_tr_date': '주식최종거래일자',
    'elw_ko_barrier': '조기종료발생기준가격'
}

NUMERIC_COLUMNS = [
    '상장주수', '행사가'
]

def main():
    """
    [국내주식] ELW시세
    ELW 신규상장종목[국내주식-181]

    ELW 신규상장종목 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건시장분류코드 (시장구분코드 (W))
        - fid_cond_scr_div_code (str): 조건화면분류코드 (Unique key(11548))
        - fid_div_cls_code (str): 분류구분코드 (전체(02), 콜(00), 풋(01))
        - fid_unas_input_iscd (str): 기초자산입력종목코드 ('ex) 000000(전체), 2001(코스피200) , 3003(코스닥150), 005930(삼성전자) ')
        - fid_input_iscd_2 (str): 입력종목코드2 ('00003(한국투자증권), 00017(KB증권),  00005(미래에셋증권)')
        - fid_input_date_1 (str): 입력날짜1 (날짜 (ex) 20240402))
        - fid_blng_cls_code (str): 결재방법 (0(전체), 1(일반), 2(조기종료))
    Returns:
        - DataFrame: ELW 신규상장종목 결과
    
    Example:
        >>> df = newly_listed(fid_cond_mrkt_div_code="W", fid_cond_scr_div_code="11548", fid_div_cls_code="02", fid_unas_input_iscd="000000", fid_input_iscd_2="00003", fid_input_date_1="20240402", fid_blng_cls_code="0")
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
        result = newly_listed(
            fid_cond_mrkt_div_code="W",  # 조건시장분류코드
            fid_cond_scr_div_code="11548",  # 조건화면분류코드
            fid_div_cls_code="02",  # 분류구분코드
            fid_unas_input_iscd="000000",  # 기초자산입력종목코드
            fid_input_iscd_2="00003",  # 입력종목코드2
            fid_input_date_1="20250601",  # 입력날짜1
            fid_blng_cls_code="0",  # 결제방법
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
        logger.info("=== ELW 신규상장종목 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
