# -*- coding: utf-8 -*-
"""
Created on 2025-07-03

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from inquire_asking_price import inquire_asking_price

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

COLUMN_MAPPING = {
    'rsym': '실시간조회종목코드',
    'zdiv': '소수점자리수',
    'curr': '통화',
    'base': '전일종가',
    'open': '시가',
    'high': '고가',
    'low': '저가',
    'last': '현재가',
    'dymd': '호가일자',
    'dhms': '호가시간',
    'bvol': '매수호가총잔량',
    'avol': '매도호가총잔량',
    'bdvl': '매수호가총잔량대비',
    'advl': '매도호가총잔량대비',
    'code': '종목코드',
    'ropen': '시가율',
    'rhigh': '고가율',
    'rlow': '저가율',
    'rclose': '현재가율',
    'pbid1': '매수호가가격1',
    'pask1': '매도호가가격1',
    'vbid1': '매수호가잔량1',
    'vask1': '매도호가잔량1',
    'dbid1': '매수호가대비1',
    'dask1': '매도호가대비1',
    'output3': '응답상세',
    'vstm': 'VCMStart시간',
    'vetm': 'VCMEnd시간',
    'csbp': 'CAS/VCM기준가',
    'cshi': 'CAS/VCMHighprice',
    'cslo': 'CAS/VCMLowprice',
    'iep': 'IEP',
    'iev': 'IEV'
}

def main():
    """
    [해외주식] 기본시세
    해외주식 현재가 1호가[해외주식-033]

    해외주식 현재가 1호가 테스트 함수
    
    Parameters:
        - auth (str): 사용자권한정보 (공백)
        - excd (str): 거래소코드 (NYS : 뉴욕 NAS : 나스닥 AMS : 아멕스  HKS : 홍콩 SHS : 상해  SZS : 심천 HSX : 호치민 HNX : 하노이 TSE : 도쿄  BAY : 뉴욕(주간) BAQ : 나스닥(주간) BAA : 아멕스(주간))
        - symb (str): 종목코드 (종목코드 예)TSLA)

    Returns:
        - DataFrame: 해외주식 현재가 1호가 결과
    
    Example:
        >>> df1, df2, df3 = inquire_asking_price(auth="", excd="NYS", symb="TSLA")
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

        # 해외주식 현재가 1호가 파라미터 설정
        logger.info("API 파라미터 설정 중...")
        auth = ""  # 사용자권한정보
        excd = "NAS"  # 거래소코드
        symb = "TSLA"  # 종목코드

        
        # API 호출
        logger.info("API 호출 시작: 해외주식 현재가 1호가")
        result1, result2, result3 = inquire_asking_price(
            auth=auth,  # 사용자권한정보
            excd=excd,  # 거래소코드
            symb=symb,  # 종목코드
        )
        
        # 결과 확인
        results = [result1, result2, result3]
        if all(result is None or result.empty for result in results):
            logger.warning("조회된 데이터가 없습니다.")
            return
        

        # output1 결과 처리
        logger.info("=== output1 조회 ===")
        if not result1.empty:
            logger.info("사용 가능한 컬럼: %s", result1.columns.tolist())
            
            # 통합 컬럼명 한글 변환 (필요한 컬럼만 자동 매핑됨)
            result1 = result1.rename(columns=COLUMN_MAPPING)
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
            logger.info("output3 결과:")
            print(result3)
        else:
            logger.info("output3 데이터가 없습니다.")

        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
