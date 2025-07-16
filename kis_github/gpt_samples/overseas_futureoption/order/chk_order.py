# -*- coding: utf-8 -*-
"""
Created on 2025-07-01

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from order import order

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

COLUMN_MAPPING = {
    'ORD_DT': '주문일자',
    'ODNO': '주문번호'
}

def main():
    """
    [해외선물옵션] 주문/계좌
    해외선물옵션 주문[v1_해외선물-001]

    해외선물옵션 주문 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        - ovrs_futr_fx_pdno (str): 해외선물FX상품번호 ()
        - sll_buy_dvsn_cd (str): 매도매수구분코드 (01 : 매도 02 : 매수)
        - fm_lqd_ustl_ccld_dt (str): FM청산미결제체결일자 (빈칸 (hedge청산만 이용))
        - fm_lqd_ustl_ccno (str): FM청산미결제체결번호 (빈칸 (hedge청산만 이용))
        - pric_dvsn_cd (str): 가격구분코드 (1.지정, 2. 시장, 3. STOP, 4 S/L)
        - fm_limit_ord_pric (str): FMLIMIT주문가격 (지정가인 경우 가격 입력 * 시장가, STOP주문인 경우, 빈칸("") 입력)
        - fm_stop_ord_pric (str): FMSTOP주문가격 (STOP 주문 가격 입력 * 시장가, 지정가인 경우, 빈칸("") 입력)
        - fm_ord_qty (str): FM주문수량 ()
        - fm_lqd_lmt_ord_pric (str): FM청산LIMIT주문가격 (빈칸 (hedge청산만 이용))
        - fm_lqd_stop_ord_pric (str): FM청산STOP주문가격 (빈칸 (hedge청산만 이용))
        - ccld_cndt_cd (str): 체결조건코드 (일반적으로 6 (EOD, 지정가)  GTD인 경우 5, 시장가인 경우만 2)
        - cplx_ord_dvsn_cd (str): 복합주문구분코드 (0 (hedge청산만 이용))
        - ecis_rsvn_ord_yn (str): 행사예약주문여부 (N)
        - fm_hdge_ord_scrn_yn (str): FM_HEDGE주문화면여부 (N)

    Returns:
        - DataFrame: 해외선물옵션 주문 결과
    
    Example:
        >>> df = order(cano=trenv.my_acct, acnt_prdt_cd="08", ovrs_futr_fx_pdno="1AALN25 C10.0", sll_buy_dvsn_cd="02", fm_lqd_ustl_ccld_dt="", fm_lqd_ustl_ccno="", pric_dvsn_cd="1", fm_limit_ord_pric="1.17", fm_stop_ord_pric="", fm_ord_qty="1", fm_lqd_lmt_ord_pric="", fm_lqd_stop_ord_pric="", ccld_cndt_cd="6", cplx_ord_dvsn_cd="0", ecis_rsvn_ord_yn="N", fm_hdge_ord_scrn_yn="N")
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

        # 해외선물옵션 주문 파라미터 설정
        logger.info("API 파라미터 설정 중...")
        cano = trenv.my_acct  # 계좌번호 (자동 설정)
        acnt_prdt_cd = "08"  # 계좌상품코드
        ovrs_futr_fx_pdno = "6NU25"  # 해외선물FX상품번호
        sll_buy_dvsn_cd = "02"  # 매도매수구분코드
        fm_lqd_ustl_ccld_dt = ""  # FM청산미결제체결일자
        fm_lqd_ustl_ccno = ""  # FM청산미결제체결번호
        pric_dvsn_cd = "1"  # 가격구분코드
        fm_limit_ord_pric = "100"  # FMLIMIT주문가격
        fm_stop_ord_pric = ""  # FMSTOP주문가격
        fm_ord_qty = "1"  # FM주문수량
        fm_lqd_lmt_ord_pric = ""  # FM청산LIMIT주문가격
        fm_lqd_stop_ord_pric = ""  # FM청산STOP주문가격
        ccld_cndt_cd = "6"  # 체결조건코드
        cplx_ord_dvsn_cd = "0"  # 복합주문구분코드
        ecis_rsvn_ord_yn = "N"  # 행사예약주문여부
        fm_hdge_ord_scrn_yn = "N"  # FM_HEDGE주문화면여부

        
        # API 호출
        logger.info("API 호출 시작: 해외선물옵션 주문")
        result = order(
            cano=cano,  # 종합계좌번호
            acnt_prdt_cd=acnt_prdt_cd,  # 계좌상품코드
            ovrs_futr_fx_pdno=ovrs_futr_fx_pdno,  # 해외선물FX상품번호
            sll_buy_dvsn_cd=sll_buy_dvsn_cd,  # 매도매수구분코드
            fm_lqd_ustl_ccld_dt=fm_lqd_ustl_ccld_dt,  # FM청산미결제체결일자
            fm_lqd_ustl_ccno=fm_lqd_ustl_ccno,  # FM청산미결제체결번호
            pric_dvsn_cd=pric_dvsn_cd,  # 가격구분코드
            fm_limit_ord_pric=fm_limit_ord_pric,  # FMLIMIT주문가격
            fm_stop_ord_pric=fm_stop_ord_pric,  # FMSTOP주문가격
            fm_ord_qty=fm_ord_qty,  # FM주문수량
            fm_lqd_lmt_ord_pric=fm_lqd_lmt_ord_pric,  # FM청산LIMIT주문가격
            fm_lqd_stop_ord_pric=fm_lqd_stop_ord_pric,  # FM청산STOP주문가격
            ccld_cndt_cd=ccld_cndt_cd,  # 체결조건코드
            cplx_ord_dvsn_cd=cplx_ord_dvsn_cd,  # 복합주문구분코드
            ecis_rsvn_ord_yn=ecis_rsvn_ord_yn,  # 행사예약주문여부
            fm_hdge_ord_scrn_yn=fm_hdge_ord_scrn_yn,  # FM_HEDGE주문화면여부
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
        logger.info("=== 해외선물옵션 주문 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
