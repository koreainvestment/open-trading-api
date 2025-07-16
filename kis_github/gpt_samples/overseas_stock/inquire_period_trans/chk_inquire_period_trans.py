# -*- coding: utf-8 -*-
"""
Created on 2025-06-30

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from inquire_period_trans import inquire_period_trans

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

COLUMN_MAPPING = {
    'trad_dt': '매매일자',
    'sttl_dt': '결제일자',
    'sll_buy_dvsn_cd': '매도매수구분코드',
    'sll_buy_dvsn_name': '',
    'pdno': '상품번호',
    'ovrs_item_name': '',
    'ccld_qty': '체결수량',
    'amt_unit_ccld_qty': '금액단위체결수량',
    'ft_ccld_unpr2': 'FT체결단가2',
    'ovrs_stck_ccld_unpr': '해외주식체결단가',
    'tr_frcr_amt2': '거래외화금액2',
    'tr_amt': '거래금액',
    'frcr_excc_amt_1': '외화정산금액1',
    'wcrc_excc_amt': '원화정산금액',
    'dmst_frcr_fee1': '국내외화수수료1',
    'frcr_fee1': '외화수수료1',
    'dmst_wcrc_fee': '국내원화수수료',
    'ovrs_wcrc_fee': '해외원화수수료',
    'crcy_cd': '통화코드',
    'std_pdno': '표준상품번호',
    'erlm_exrt': '등록환율',
    'loan_dvsn_cd': '대출구분코드',
    'loan_dvsn_name': '',
    'frcr_buy_amt_smtl': '외화매수금액합계',
    'frcr_sll_amt_smtl': '외화매도금액합계',
    'dmst_fee_smtl': '국내수수료합계',
    'ovrs_fee_smtl': '해외수수료합계'
}

def main():
    """
    [해외주식] 주문/계좌
    해외주식 일별거래내역[해외주식-063]

    해외주식 일별거래내역 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 ()
        - acnt_prdt_cd (str): 계좌상품코드 ()
        - erlm_strt_dt (str): 등록시작일자 (입력날짜 ~ (ex) 20240420))
        - erlm_end_dt (str): 등록종료일자 (~입력날짜 (ex) 20240520))
        - ovrs_excg_cd (str): 해외거래소코드 (공백)
        - pdno (str): 상품번호 (공백 (전체조회), 개별종목 조회는 상품번호입력)
        - sll_buy_dvsn_cd (str): 매도매수구분코드 (00(전체), 01(매도), 02(매수))
        - loan_dvsn_cd (str): 대출구분코드 (공백)
        - ctx_area_fk100 (str): 연속조회검색조건100 (공백)
        - ctx_area_nk100 (str): 연속조회키100 (공백)

    Returns:
        - DataFrame: 해외주식 일별거래내역 결과
    
    Example:
        >>> df1, df2 = inquire_period_trans(cano=trenv.my_acct, acnt_prdt_cd="", erlm_strt_dt="20240420", erlm_end_dt="20240520", ovrs_excg_cd="", pdno="", sll_buy_dvsn_cd="00", loan_dvsn_cd="", ctx_area_fk100="", ctx_area_nk100="")
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

        # 해외주식 일별거래내역 파라미터 설정
        logger.info("API 파라미터 설정 중...")
        cano = trenv.my_acct  # 계좌번호 (자동 설정)
        acnt_prdt_cd = "01"  # 계좌상품코드
        erlm_strt_dt = "20250601"  # 등록시작일자
        erlm_end_dt = "20250630"  # 등록종료일자
        ovrs_excg_cd = "NASD"  # 해외거래소코드
        pdno = ""  # 상품번호
        sll_buy_dvsn_cd = "00"  # 매도매수구분코드
        loan_dvsn_cd = ""  # 대출구분코드
        ctx_area_fk100 = ""  # 연속조회검색조건100
        ctx_area_nk100 = ""  # 연속조회키100

        
        # API 호출
        logger.info("API 호출 시작: 해외주식 일별거래내역")
        result1, result2 = inquire_period_trans(
            cano=cano,  # 종합계좌번호
            acnt_prdt_cd=acnt_prdt_cd,  # 계좌상품코드
            erlm_strt_dt=erlm_strt_dt,  # 등록시작일자
            erlm_end_dt=erlm_end_dt,  # 등록종료일자
            ovrs_excg_cd=ovrs_excg_cd,  # 해외거래소코드
            pdno=pdno,  # 상품번호
            sll_buy_dvsn_cd=sll_buy_dvsn_cd,  # 매도매수구분코드
            loan_dvsn_cd=loan_dvsn_cd,  # 대출구분코드
            ctx_area_fk100=ctx_area_fk100,  # 연속조회검색조건100
            ctx_area_nk100=ctx_area_nk100,  # 연속조회키100
        )
        
        # 결과 확인
        results = [result1, result2]
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

        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
