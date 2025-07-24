# -*- coding: utf-8 -*-
"""
Created on 2025-06-20

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from inquire_psbl_order import inquire_psbl_order

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [장내채권] 주문/계좌 > 장내채권 매수가능조회 [국내주식-199]
##############################################################################################

COLUMN_MAPPING = {
    'ord_psbl_cash': '주문가능현금',
    'ord_psbl_sbst': '주문가능대용',
    'ruse_psbl_amt': '재사용가능금액',
    'bond_ord_unpr2': '채권주문단가2',
    'buy_psbl_amt': '매수가능금액',
    'buy_psbl_qty': '매수가능수량',
    'cma_evlu_amt': 'CMA평가금액'
}

NUMERIC_COLUMNS = []

def main():
    """
    [장내채권] 주문/계좌
    장내채권 매수가능조회[국내주식-199]

    장내채권 매수가능조회 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호
        - acnt_prdt_cd (str): 계좌상품코드
        - pdno (str): 채권종목코드(ex KR2033022D33)
        - bond_ord_unpr (str): 채권주문단가
    Returns:
        - DataFrame: 장내채권 매수가능조회 결과
    
    Example:
        >>> df = inquire_psbl_order(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, pdno="KR2033022D33", bond_ord_unpr="1000")
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

        # kis_auth 모듈에서 계좌 정보 가져오기
        trenv = ka.getTREnv()

        # API 호출
        logger.info("API 호출 시작: 장내채권 매수가능조회")
        result = inquire_psbl_order(
            cano=trenv.my_acct,  # 종합계좌번호
            acnt_prdt_cd=trenv.my_prod,  # 계좌상품코드
            pdno="KR2033022D33",  # 채권종목코드(ex KR2033022D33)
            bond_ord_unpr="1000",  # 채권주문단가
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
        logger.info("=== 장내채권 매수가능조회 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)

    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise


if __name__ == "__main__":
    main()
