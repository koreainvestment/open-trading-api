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
from search_contract_detail import search_contract_detail

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물 상품기본정보[해외선물-023]
##############################################################################################

# 컬럼명 매핑
COLUMN_MAPPING = {
    'exch_cd': '거래소코드',
    'clas_cd': '품목종류',
    'crc_cd': '거래통화',
    'sttl_price': '정산가',
    'sttl_date': '정산일',
    'trst_mgn': '증거금',
    'disp_digit': '가격표시진법',
    'tick_sz': '틱사이즈',
    'tick_val': '틱가치',
    'mrkt_open_date': '장개시일자',
    'mrkt_open_time': '장개시시각',
    'mrkt_close_date': '장마감일자',
    'mrkt_close_time': '장마감시각',
    'trd_fr_date': '상장일',
    'expr_date': '만기일',
    'trd_to_date': '최종거래일',
    'remn_cnt': '잔존일수',
    'stat_tp': '매매여부',
    'ctrt_size': '계약크기',
    'stl_tp': '최종결제구분',
    'frst_noti_date': '최초식별일',
    'sub_exch_nm': '서브거래소코드'
}

# 숫자형 컬럼
NUMERIC_COLUMNS = ['정산가', '증거금', '틱사이즈', '틱가치', '잔존일수', '계약크기']

def main():
    """
    [해외선물옵션] 기본시세
    해외선물 상품기본정보[해외선물-023]

    해외선물 상품기본정보 테스트 함수
    
    Parameters:
        - qry_cnt (str): 요청개수 (1~32 사이의 값)
        - srs_cd_01 (str): 종목코드 1 (예: BONU25)
        - srs_cd_02 (str): 종목코드 2
        - ...
        - srs_cd_32 (str): 종목코드 32 (최대 32개 종목코드까지 조회 가능)

    Returns:
        - DataFrame: 해외선물 상품기본정보 결과
    
    Example:
        >>> df = search_contract_detail(qry_cnt="1", srs_cd_01="BONU25", srs_cd_02="BONU25", srs_cd_03="BONU25")
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
        result = search_contract_detail(
            qry_cnt="3",
            srs_cd_01="BONU25",
            srs_cd_02="BONU25",
            srs_cd_03="BONU25"
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
        logger.info("=== 해외선물 상품기본정보 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
