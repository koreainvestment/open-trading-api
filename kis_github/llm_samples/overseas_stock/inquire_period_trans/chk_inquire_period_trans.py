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

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 일별거래내역 [해외주식-063]
##############################################################################################

# 컬럼명 매핑 (한글 변환용)
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

# 숫자형 컬럼 정의 (소수점 처리용)
NUMERIC_COLUMNS = [
    'ccld_qty', 'amt_unit_ccld_qty', 'ft_ccld_unpr2', 'ovrs_stck_ccld_unpr', 'tr_frcr_amt2',
    'tr_amt', 'frcr_excc_amt_1', 'wcrc_excc_amt', 'dmst_frcr_fee1', 'frcr_fee1',
    'dmst_wcrc_fee', 'ovrs_wcrc_fee', 'erlm_exrt', 'frcr_buy_amt_smtl', 'frcr_sll_amt_smtl',
    'dmst_fee_smtl', 'ovrs_fee_smtl'
]

def main():
    """
    [해외주식] 주문/계좌
    해외주식 일별거래내역[해외주식-063]

    해외주식 일별거래내역 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        - erlm_strt_dt (str): 등록시작일자 (예: 20240420)
        - erlm_end_dt (str): 등록종료일자 (예: 20240520)
        - ovrs_excg_cd (str): 해외거래소코드
        - pdno (str): 상품번호
        - sll_buy_dvsn_cd (str): 매도매수구분코드 (00: 전체, 01: 매도, 02: 매수)
        - loan_dvsn_cd (str): 대출구분코드
        - FK100 (str): 연속조회검색조건100 (공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100값 : 다음페이지 조회시(2번째부터))
        - NK100 (str): 연속조회키100 (공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100값 : 다음페이지 조회시(2번째부터))

    Returns:
        - DataFrame: 해외주식 일별거래내역 결과 (output1: 거래내역 목록, output2: 거래내역 요약)
    
    Example:
        >>> df1, df2 = inquire_period_trans(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, erlm_strt_dt="20240420", erlm_end_dt="20240520", ovrs_excg_cd="NAS", pdno="", sll_buy_dvsn_cd="00", loan_dvsn_cd="", FK100="", NK100="")
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
        logger.info("API 호출")
        result1, result2 = inquire_period_trans(
            cano=trenv.my_acct,  # 종합계좌번호
            acnt_prdt_cd=trenv.my_prod,  # 계좌상품코드
            erlm_strt_dt="20240601",  # 등록시작일자
            erlm_end_dt="20240630",  # 등록종료일자
            ovrs_excg_cd="NASD",  # 해외거래소코드
            pdno="",  # 상품번호
            sll_buy_dvsn_cd="00",  # 매도매수구분코드
            loan_dvsn_cd="",  # 대출구분코드
            FK100="",  # 연속조회검색조건100
            NK100=""   # 연속조회키100
        )
        
        if result1 is None or result1.empty:
            logger.warning("조회된 거래내역 목록 데이터가 없습니다.")
        else:
            # 컬럼명 출력
            logger.info("사용 가능한 컬럼 목록 (output1):")
            logger.info(result1.columns.tolist())

            # 한글 컬럼명으로 변환
            result1 = result1.rename(columns=COLUMN_MAPPING)
            
            # 숫자형 컬럼 처리
            for col in NUMERIC_COLUMNS:
                if col in result1.columns:
                    result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)
            
            # 결과 출력
            logger.info("=== 해외주식 일별거래내역 목록 (output1) ===")
            logger.info("조회된 데이터 건수: %d", len(result1))
            print(result1)

        if result2 is None or result2.empty:
            logger.warning("조회된 거래내역 요약 데이터가 없습니다.")
        else:
            # 컬럼명 출력
            logger.info("사용 가능한 컬럼 목록 (output2):")
            logger.info(result2.columns.tolist())

            # 한글 컬럼명으로 변환
            result2 = result2.rename(columns=COLUMN_MAPPING)
            
            # 숫자형 컬럼 처리
            for col in NUMERIC_COLUMNS:
                if col in result2.columns:
                    result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

            # 결과 출력
            logger.info("=== 해외주식 일별거래내역 요약 (output2) ===")
            logger.info("조회된 데이터 건수: %d", len(result2))
            print(result2)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
