# -*- coding: utf-8 -*-
"""
Created on 2025-06-19

@author: LaivData jjlee with cursor
"""
import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from inquire_asking_price import inquire_asking_price

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [장내채권] 기본시세 > 장내채권현재가(호가) [국내주식-132]
##############################################################################################

COLUMN_MAPPING = {
    'aspr_acpt_hour': '호가 접수 시간',
    'bond_askp1': '채권 매도호가1',
    'bond_askp2': '채권 매도호가2',
    'bond_askp3': '채권 매도호가3',
    'bond_askp4': '채권 매도호가4',
    'bond_askp5': '채권 매도호가5',
    'bond_bidp1': '채권 매수호가1',
    'bond_bidp2': '채권 매수호가2',
    'bond_bidp3': '채권 매수호가3',
    'bond_bidp4': '채권 매수호가4',
    'bond_bidp5': '채권 매수호가5',
    'askp_rsqn1': '매도호가 잔량1',
    'askp_rsqn2': '매도호가 잔량2',
    'askp_rsqn3': '매도호가 잔량3',
    'askp_rsqn4': '매도호가 잔량4',
    'askp_rsqn5': '매도호가 잔량5',
    'bidp_rsqn1': '매수호가 잔량1',
    'bidp_rsqn2': '매수호가 잔량2',
    'bidp_rsqn3': '매수호가 잔량3',
    'bidp_rsqn4': '매수호가 잔량4',
    'bidp_rsqn5': '매수호가 잔량5',
    'total_askp_rsqn': '총 매도호가 잔량',
    'total_bidp_rsqn': '총 매수호가 잔량',
    'ntby_aspr_rsqn': '순매수 호가 잔량',
    'seln_ernn_rate1': '매도 수익 비율1',
    'seln_ernn_rate2': '매도 수익 비율2',
    'seln_ernn_rate3': '매도 수익 비율3',
    'seln_ernn_rate4': '매도 수익 비율4',
    'seln_ernn_rate5': '매도 수익 비율5',
    'shnu_ernn_rate1': '매수2 수익 비율1',
    'shnu_ernn_rate2': '매수2 수익 비율2',
    'shnu_ernn_rate3': '매수2 수익 비율3',
    'shnu_ernn_rate4': '매수2 수익 비율4',
    'shnu_ernn_rate5': '매수2 수익 비율5'
}

NUMERIC_COLUMNS = []

def main():
    """
    [장내채권] 기본시세
    장내채권현재가(호가)[국내주식-132]

    장내채권현재가(호가) 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 시장 분류 코드 (B 입력)
        - fid_input_iscd (str): 채권종목코드
    Returns:
        - DataFrame: 장내채권현재가(호가) 결과
    
    Example:
        >>> df = inquire_asking_price(fid_cond_mrkt_div_code="B", fid_input_iscd="KR2033022D33")
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
        logger.info("API 호출 시작: 장내채권현재가(호가)")
        result = inquire_asking_price(
            fid_cond_mrkt_div_code="B",  # 시장 분류 코드
            fid_input_iscd="KR2033022D33",  # 채권종목코드
        )

        if result is None or result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return

        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())

        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)

        # 숫자형 컬럼 변환
        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce')

        # 결과 출력
        logger.info("=== 장내채권현재가(호가) 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)

    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise


if __name__ == "__main__":
    main()
