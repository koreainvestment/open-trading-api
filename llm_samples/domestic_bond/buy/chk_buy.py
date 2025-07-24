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
from buy import buy

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [장내채권] 주문/계좌 > 장내채권 매수주문 [국내주식-124]
##############################################################################################

COLUMN_MAPPING = {
    'KRX_FWDG_ORD_ORGNO': '한국거래소전송주문조직번호',
    'ODNO': '주문번호',
    'ORD_TMD': '주문시각'
}

NUMERIC_COLUMNS = []

def main():
    """
    [장내채권] 주문/계좌`
    장내채권 매수주문[국내주식-124]

    장내채권 매수주문 테스트 함수
    
    Parameters:
        cano (str): 종합계좌번호 (8자리)
        acnt_prdt_cd (str): 계좌상품코드 (2자리)
        pdno (str): 상품번호 (12자리)
        ord_qty2 (str): 주문수량2 (19자리)
        bond_ord_unpr (str): 채권주문단가 (182자리)
        samt_mket_ptci_yn (str): 소액시장참여여부 ('Y' or 'N')
        bond_rtl_mket_yn (str): 채권소매시장여부 ('Y' or 'N')
        idcr_stfno (str, optional): 유치자직원번호 (6자리). Defaults to "".
        mgco_aptm_odno (str, optional): 운용사지정주문번호 (12자리). Defaults to "".
    
    Returns:
        - DataFrame: 장내채권 매수주문 결과
    
    Example:
        >>> df = main()
        >>> print(df)
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
        logger.info("API 호출 시작: 장내채권 매수주문")
        result = buy(
            cano=trenv.my_acct,  # 종합계좌번호
            acnt_prdt_cd=trenv.my_prod,  # 계좌상품코드
            pdno="KR6095572D81",  # 상품번호
            ord_qty2="10",  # 주문수량
            bond_ord_unpr="9900",  # 채권주문단가
            samt_mket_ptci_yn="N",  # 소액시장참여여부
            bond_rtl_mket_yn="N",  # 채권소매시장여부
            idcr_stfno="",  # 유치자직원번호
            mgco_aptm_odno="",  # 운용사지정주문번호
            ord_svr_dvsn_cd="0",  # 주문서버구분코드
            ctac_tlno="",  # 연락전화번호
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
        logger.info("=== 장내채권 매수주문 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)

    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise


if __name__ == "__main__":
    main()
