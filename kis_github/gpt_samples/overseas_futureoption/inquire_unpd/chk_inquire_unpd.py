# -*- coding: utf-8 -*-
"""
Created on 2025-07-02

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from inquire_unpd import inquire_unpd

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

COLUMN_MAPPING = {
    'cano': '종합계좌번호',
    'acnt_prdt_cd': '계좌상품코드',
    'ovrs_futr_fx_pdno': '해외선물FX상품번호',
    'prdt_type_cd': '상품유형코드',
    'crcy_cd': '통화코드',
    'sll_buy_dvsn_cd': '매도매수구분코드',
    'fm_ustl_qty': 'FM미결제수량',
    'fm_ccld_avg_pric': 'FM체결평균가격',
    'fm_now_pric': 'FM현재가격',
    'fm_evlu_pfls_amt': 'FM평가손익금액',
    'fm_opt_evlu_amt': 'FM옵션평가금액',
    'fm_otp_evlu_pfls_amt': 'FM옵션평가손익금액',
    'fuop_dvsn': '선물옵션구분',
    'ecis_rsvn_ord_yn': '행사예약주문여부',
    'fm_lqd_psbl_qty': 'FM청산가능수량'
}

def main():
    """
    [해외선물옵션] 주문/계좌
    해외선물옵션 미결제내역조회(잔고)[v1_해외선물-005]

    해외선물옵션 미결제내역조회(잔고) 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        - fuop_dvsn (str): 선물옵션구분 (00: 전체 / 01:선물 / 02: 옵션)
        - ctx_area_fk100 (str): 연속조회검색조건100 ()
        - ctx_area_nk100 (str): 연속조회키100 ()

    Returns:
        - DataFrame: 해외선물옵션 미결제내역조회(잔고) 결과
    
    Example:
        >>> df = inquire_unpd(cano=trenv.my_acct, acnt_prdt_cd="08", fuop_dvsn="00", ctx_area_fk100="", ctx_area_nk100="")
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
        trenv = ka.getTREnv()

        # 해외선물옵션 미결제내역조회(잔고) 파라미터 설정
        logger.info("API 파라미터 설정 중...")
        cano = trenv.my_acct  # 계좌번호 (자동 설정)
        acnt_prdt_cd = "08"  # 계좌상품코드
        fuop_dvsn = "00"  # 선물옵션구분
        ctx_area_fk100 = ""  # 연속조회검색조건100
        ctx_area_nk100 = ""  # 연속조회키100

        
        # API 호출
        logger.info("API 호출 시작: 해외선물옵션 미결제내역조회(잔고)")
        result = inquire_unpd(
            cano=cano,  # 종합계좌번호
            acnt_prdt_cd=acnt_prdt_cd,  # 계좌상품코드
            fuop_dvsn=fuop_dvsn,  # 선물옵션구분
            ctx_area_fk100=ctx_area_fk100,  # 연속조회검색조건100
            ctx_area_nk100=ctx_area_nk100,  # 연속조회키100
        )
        
        if result is None or result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return
        
        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())

        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)
        
        # 결과 출력
        logger.info("=== 해외선물옵션 미결제내역조회(잔고) 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
