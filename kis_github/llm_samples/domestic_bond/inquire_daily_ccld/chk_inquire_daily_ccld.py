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
from inquire_daily_ccld import inquire_daily_ccld

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [장내채권] 주문/계좌 > 장내채권 일별체결조회 [국내주식-127]
##############################################################################################

# 통합 컬럼 매핑 (모든 output에서 공통 사용)
COLUMN_MAPPING = {
    'tot_ord_qty': '총주문수량',
    'tot_ccld_qty_smtl': '총체결수량합계',
    'tot_bond_ccld_avg_unpr': '총채권체결평균단가',
    'tot_ccld_amt_smtl': '총체결금액합계',
    'ord_dt': '주문일자',
    'odno': '주문번호',
    'orgn_odno': '원주문번호',
    'ord_dvsn_name': '주문구분명',
    'sll_buy_dvsn_cd_name': '매도매수구분코드명',
    'shtn_pdno': '단축상품번호',
    'prdt_abrv_name': '상품약어명',
    'ord_qty': '주문수량',
    'bond_ord_unpr': '채권주문단가',
    'ord_tmd': '주문시각',
    'tot_ccld_qty': '총체결수량',
    'bond_avg_unpr': '채권평균단가',
    'tot_ccld_amt': '총체결금액',
    'loan_dt': '대출일자',
    'buy_dt': '매수일자',
    'samt_mket_ptci_yn_name': '소액시장참여여부명',
    'sprx_psbl_yn_ifom': '분리과세가능여부알림',
    'ord_mdia_dvsn_name': '주문매체구분묭',
    'sll_buy_dvsn_cd': '매도매수구분코드',
    'nccs_qty': '미체결수량',
    'ord_gno_brno': '주문채번지점번호'
}

NUMERIC_COLUMNS = []

def main():
    """
    [장내채권] 주문/계좌
    장내채권 주문체결내역[국내주식-127]

    장내채권 주문체결내역 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 (종합계좌번호)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌상품코드)
        - inqr_strt_dt (str): 조회시작일자 (일자 ~ (1주일 이내))
        - inqr_end_dt (str): 조회종료일자 (~ 일자 (조회 당일))
        - sll_buy_dvsn_cd (str): 매도매수구분코드 (%(전체), 01(매도), 02(매수))
        - sort_sqn_dvsn (str): 정렬순서구분 (01(주문순서), 02(주문역순))
        - pdno (str): 상품번호 ()
        - nccs_yn (str): 미체결여부 (N(전체), C(체결), Y(미체결))

    Returns:
        - Tuple[DataFrame, ...]: 장내채권 주문체결내역 결과
    
    Example:
        >>> df1, df2 = inquire_daily_ccld(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, inqr_strt_dt="20250601", inqr_end_dt="20250630", sll_buy_dvsn_cd="%", sort_sqn_dvsn="01", pdno="", nccs_yn="N", ctx_area_nk200="", ctx_area_fk200="")
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
        logger.info("API 호출 시작: 장내채권 주문체결내역")
        result1, result2 = inquire_daily_ccld(
            cano=trenv.my_acct,  # 종합계좌번호
            acnt_prdt_cd=trenv.my_prod,  # 계좌상품코드
            inqr_strt_dt="20250601",  # 조회시작일자
            inqr_end_dt="20250630",  # 조회종료일자
            sll_buy_dvsn_cd="%",  # 매도매수구분코드
            sort_sqn_dvsn="01",  # 정렬순서구분
            pdno="",  # 상품번호
            nccs_yn="N",  # 미체결여부
            ctx_area_nk200="",  # 연속조회키200
            ctx_area_fk200="",  # 연속조회검색조건200
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

            # 숫자형 컬럼 변환s
            for col in NUMERIC_COLUMNS:
                if col in result1.columns:
                    result1[col] = pd.to_numeric(result1[col], errors='coerce')

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

            # 숫자형 컬럼 변환s
            for col in NUMERIC_COLUMNS:
                if col in result2.columns:
                    result2[col] = pd.to_numeric(result2[col], errors='coerce')

            logger.info("output2 결과:")
            print(result2)
        else:
            logger.info("output2 데이터가 없습니다.")


    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise


if __name__ == "__main__":
    main()
