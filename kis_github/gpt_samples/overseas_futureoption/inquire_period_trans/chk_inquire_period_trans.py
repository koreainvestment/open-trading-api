# -*- coding: utf-8 -*-
"""
Created on 2025-07-02

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_period_trans import inquire_period_trans

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 기간계좌거래내역 [해외선물-014]
##############################################################################################

# 상수 정의
COLUMN_MAPPING = {
    'bass_dt': '기준일자',
    'cano': '종합계좌번호',
    'acnt_prdt_cd': '계좌상품코드',
    'fm_ldgr_inog_seq': 'FM원장출납순번',
    'crcy_cd': '통화코드',
    'fm_iofw_amt': 'FM입출금액',
    'fm_fee': 'FM수수료',
    'fm_tax_amt': 'FM세금금액',
    'fm_sttl_amt': 'FM결제금액',
    'fm_bf_dncl_amt': 'FM이전예수금액',
    'fm_dncl_amt': 'FM예수금액',
    'fm_rcvb_occr_amt': 'FM미수발생금액',
    'fm_rcvb_pybk_amt': 'FM미수변제금액',
    'ovdu_int_pybk_amt': '연체이자변제금액',
    'rmks_text': '비고내용'
}
NUMERIC_COLUMNS = ['FM입출금액', 'FM수수료', 'FM세금금액', 'FM결제금액', 'FM이전예수금액', 'FM예수금액', 'FM미수발생금액', 'FM미수변제금액', '연체이자변제금액']

def main():
    """
    [해외선물옵션] 주문/계좌
    해외선물옵션 기간계좌거래내역[해외선물-014]

    해외선물옵션 기간계좌거래내역 테스트 함수
    
    Parameters:
        - inqr_term_from_dt (str): 조회기간FROM일자 ()
        - inqr_term_to_dt (str): 조회기간TO일자 ()
        - cano (str): 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        - acnt_tr_type_cd (str): 계좌거래유형코드 (1: 전체, 2:입출금 , 3: 결제)
        - crcy_cd (str): 통화코드 ('%%% : 전체 TUS: TOT_USD  / TKR: TOT_KRW KRW: 한국  / USD: 미국 EUR: EUR   / HKD: 홍콩 CNY: 중국  / JPY: 일본 VND: 베트남  ')
        - ctx_area_fk100 (str): 연속조회검색조건100 (공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100값 : 다음페이지 조회시(2번째부터))
        - ctx_area_nk100 (str): 연속조회키100 (공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100값 : 다음페이지 조회시(2번째부터))
        - pwd_chk_yn (str): 비밀번호체크여부 (공란(Default))

    Returns:
        - DataFrame: 해외선물옵션 기간계좌거래내역 결과
    
    Example:
        >>> df = inquire_period_trans(inqr_term_from_dt="20250101", inqr_term_to_dt="20250131", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, acnt_tr_type_cd="1", crcy_cd="%%%", ctx_area_fk100="", ctx_area_nk100="", pwd_chk_yn="")
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
        
        # API 호출
        logger.info("API 호출 시작: 해외선물옵션 기간계좌거래내역")
        result = inquire_period_trans(
            inqr_term_from_dt="20250601",  # 조회기간FROM일자
            inqr_term_to_dt="20250630",  # 조회기간TO일자
            cano=trenv.my_acct,  # 종합계좌번호
            acnt_prdt_cd=trenv.my_prod,  # 계좌상품코드
            acnt_tr_type_cd="1",  # 계좌거래유형코드
            crcy_cd="%%%",  # 통화코드
            ctx_area_fk100="",  # 연속조회검색조건100
            ctx_area_nk100="",  # 연속조회키100
            pwd_chk_yn="N",  # 비밀번호체크여부
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
        logger.info("=== 해외선물옵션 기간계좌거래내역 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
