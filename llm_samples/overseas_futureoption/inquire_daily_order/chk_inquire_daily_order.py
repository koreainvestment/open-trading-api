# -*- coding: utf-8 -*-
"""
Created on 2025-07-03

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_daily_order import inquire_daily_order

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 일별 주문내역 [해외선물-013]
##############################################################################################

COLUMN_MAPPING = {
    'cano': '종합계좌번호',
    'acnt_prdt_cd': '계좌상품코드',
    'dt': '일자',
    'ord_dt': '주문일자',
    'odno': '주문번호',
    'orgn_ord_dt': '원주문일자',
    'orgn_odno': '원주문번호',
    'ovrs_futr_fx_pdno': '해외선물FX상품번호',
    'rvse_cncl_dvsn_cd': '정정취소구분코드',
    'sll_buy_dvsn_cd': '매도매수구분코드',
    'cplx_ord_dvsn_cd': '복합주문구분코드',
    'pric_dvsn_cd': '가격구분코드',
    'rcit_dvsn_cd': '접수구분코드',
    'fm_ord_qty': 'FM주문수량',
    'fm_ord_pric': 'FM주문가격',
    'fm_stop_ord_pric': 'FMSTOP주문가격',
    'ecis_rsvn_ord_yn': '행사예약주문여부',
    'fm_ccld_qty': 'FM체결수량',
    'fm_ccld_pric': 'FM체결가격',
    'fm_ord_rmn_qty': 'FM주문잔여수량',
    'ord_grp_name': '주문그룹명',
    'rcit_dtl_dtime': '접수상세일시',
    'ccld_dtl_dtime': '체결상세일시',
    'ordr_emp_no': '주문자사원번호',
    'rjct_rson_name': '거부사유명',
    'ccld_cndt_cd': '체결조건코드',
    'trad_end_dt': '매매종료일자'
}

NUMERIC_COLUMNS = ['FM주문수량', 'FM주문가격', 'FMSTOP주문가격', 'FM체결수량', 'FM체결가격', 'FM주문잔여수량']
    
def main():
    """
    [해외선물옵션] 주문/계좌
    해외선물옵션 일별 주문내역[해외선물-013]

    해외선물옵션 일별 주문내역 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        - strt_dt (str): 시작일자 ()
        - end_dt (str): 종료일자 ()
        - fm_pdgr_cd (str): FM상품군코드 ()
        - ccld_nccs_dvsn (str): 체결미체결구분 (01:전체 / 02:체결 / 03:미체결)
        - sll_buy_dvsn_cd (str): 매도매수구분코드 (%%전체 / 01 : 매도 / 02 : 매수)
        - fuop_dvsn (str): 선물옵션구분 (00:전체 / 01:선물 / 02:옵션)
        - ctx_area_fk200 (str): 연속조회검색조건200 ()
        - ctx_area_nk200 (str): 연속조회키200 ()

    Returns:
        - DataFrame: 해외선물옵션 일별 주문내역 결과
    
    Example:
        >>> df = inquire_daily_order(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, strt_dt="20250601", end_dt="20250703", fm_pdgr_cd="", ccld_nccs_dvsn="01", sll_buy_dvsn_cd="%%", fuop_dvsn="00", ctx_area_fk200="", ctx_area_nk200="")
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
        logger.info("API 호출 시작: 해외선물옵션 일별 주문내역")
        result = inquire_daily_order(
            cano=trenv.my_acct,           # 종합계좌번호 (자동 설정)
            acnt_prdt_cd=trenv.my_prod,            # 계좌상품코드
            strt_dt="20250601",           # 시작일자
            end_dt="20250703",            # 종료일자
            fm_pdgr_cd="",                # FM상품군코드
            ccld_nccs_dvsn="01",          # 체결미체결구분
            sll_buy_dvsn_cd="%%",         # 매도매수구분코드
            fuop_dvsn="00",               # 선물옵션구분
            ctx_area_fk200="",            # 연속조회검색조건200
            ctx_area_nk200=""             # 연속조회키200
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
        logger.info("=== 해외선물옵션 일별 주문내역 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
