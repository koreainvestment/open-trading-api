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
from inquire_ccld import inquire_ccld

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 당일주문내역조회 [v1_해외선물-004]
##############################################################################################

# 상수 정의
COLUMN_MAPPING = {
    'cano': '종합계좌번호',
    'acnt_prdt_cd': '계좌상품코드',
    'ord_dt': '주문일자',
    'odno': '주문번호',
    'orgn_ord_dt': '원주문일자',
    'orgn_odno': '원주문번호',
    'ovrs_futr_fx_pdno': '해외선물FX상품번호',
    'rcit_dvsn_cd': '접수구분코드',
    'sll_buy_dvsn_cd': '매도매수구분코드',
    'trad_stgy_dvsn_cd': '매매전략구분코드',
    'bass_pric_type_cd': '기준가격유형코드',
    'ord_stat_cd': '주문상태코드',
    'fm_ord_qty': 'FM주문수량',
    'fm_ord_pric': 'FM주문가격',
    'fm_stop_ord_pric': 'FMSTOP주문가격',
    'rsvn_dvsn': '예약구분',
    'fm_ccld_qty': 'FM체결수량',
    'fm_ccld_pric': 'FM체결가격',
    'fm_ord_rmn_qty': 'FM주문잔여수량',
    'ord_grp_name': '주문그룹명',
    'erlm_dtl_dtime': '등록상세일시',
    'ccld_dtl_dtime': '체결상세일시',
    'ord_stfno': '주문직원번호',
    'rmks1': '비고1',
    'new_lqd_dvsn_cd': '신규청산구분코드',
    'fm_lqd_lmt_ord_pric': 'FM청산LIMIT주문가격',
    'fm_lqd_stop_pric': 'FM청산STOP가격',
    'ccld_cndt_cd': '체결조건코드',
    'noti_vald_dt': '게시유효일자',
    'acnt_type_cd': '계좌유형코드',
    'fuop_dvsn': '선물옵션구분'
}

NUMERIC_COLUMNS = ['FM주문수량', 'FM주문가격', 'FMSTOP주문가격', 'FM체결수량', 'FM체결가격', 'FM주문잔여수량',
                   'FM청산LIMIT주문가격', 'FM청산STOP가격']

def main():
    """
    [해외선물옵션] 주문/계좌
    해외선물옵션 당일주문내역조회[v1_해외선물-004]

    해외선물옵션 당일주문내역조회 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        - ccld_nccs_dvsn (str): 체결미체결구분 (01:전체 / 02:체결 / 03:미체결)
        - sll_buy_dvsn_cd (str): 매도매수구분코드 (%%:전체 / 01:매도 / 02:매수)
        - fuop_dvsn (str): 선물옵션구분 (00:전체 / 01:선물 / 02:옵션)
        - ctx_area_fk200 (str): 연속조회검색조건200 ()
        - ctx_area_nk200 (str): 연속조회키200 ()

    Returns:
        - DataFrame: 해외선물옵션 당일주문내역조회 결과
    
    Example:
        >>> df = inquire_ccld(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, ccld_nccs_dvsn="01", sll_buy_dvsn_cd="%%", fuop_dvsn="00", ctx_area_fk200="", ctx_area_nk200="")
    """
    try:
        # pandas 출력 옵션 설정
        pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
        pd.set_option('display.width', None)  # 출력 너비 제한 해제
        pd.set_option('display.max_rows', None)  # 모든 행 표시

        # 토큰 발급
        ka.auth()
        trenv = ka.getTREnv()

        # API 호출
        logger.info("API 호출")
        result = inquire_ccld(
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            ccld_nccs_dvsn="01",
            sll_buy_dvsn_cd="%%",
            fuop_dvsn="00",
            ctx_area_fk200="",
            ctx_area_nk200=""
        )
        
        if result is None or result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return
        
        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())

        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)
        
        # 숫자형 컬럼 처리
        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
        
        # 결과 출력
        logger.info("=== 해외선물옵션 당일주문내역조회 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
