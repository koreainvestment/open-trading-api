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
from inquire_psbl_rvsecncl import inquire_psbl_rvsecncl

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [장내채권] 주문/계좌 > 채권정정취소가능주문조회 [국내주식-126]
##############################################################################################

COLUMN_MAPPING = {
    'odno': '주문번호',
    'pdno': '상품번호',
    'rvse_cncl_dvsn_name': '정정취소구분명',
    'ord_qty': '주문수량',
    'bond_ord_unpr': '채권주문단가',
    'ord_tmd': '주문시각',
    'tot_ccld_qty': '총체결수량',
    'tot_ccld_amt': '총체결금액',
    'ord_psbl_qty': '주문가능수량',
    'orgn_odno': '원주문번호',
    'sll_buy_dvsn_cd': '매도매수구분코드',
    'ord_dvsn_cd': '주문구분코드',
    'mgco_aptm_odno': '운용사지정주문번호',
    'samt_mket_ptci_yn': '소액시장참여여부'
}

NUMERIC_COLUMNS = []

def main():
    """
    [장내채권] 주문/계좌
    채권정정취소가능주문조회[국내주식-126]

    채권정정취소가능주문조회 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 ()
        - acnt_prdt_cd (str): 계좌상품코드 ()
        - ord_dt (str): 주문일자 ()
        - odno (str): 주문번호 ()
        - ctx_area_fk200 (str): 연속조회검색조건200 ()
        - ctx_area_nk200 (str): 연속조회키200 ()
    Returns:
        - DataFrame: 채권정정취소가능주문조회 결과
    
    Example:
        >>> df = inquire_psbl_rvsecncl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, ord_dt="20250601", odno="", ctx_area_fk200="", ctx_area_nk200="")
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
        logger.info("API 호출 시작: 채권정정취소가능주문조회")
        result = inquire_psbl_rvsecncl(
            cano=trenv.my_acct,  # 종합계좌번호
            acnt_prdt_cd=trenv.my_prod,  # 계좌상품코드
            ord_dt="",  # 주문일자
            odno="",  # 주문번호
            ctx_area_fk200="",  # 연속조회검색조건200
            ctx_area_nk200="",  # 연속조회키200
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
        logger.info("=== 채권정정취소가능주문조회 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
