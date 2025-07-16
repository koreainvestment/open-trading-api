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
from order_rvsecncl import order_rvsecncl

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

COLUMN_MAPPING = {
    'KRX_FWDG_ORD_ORGNO': '한국거래소전송주문조직번호',
    'ODNO': '주문번호',
    'ORD_TMD': '주문시각'
}

def main():
    """
    [장내채권] 주문/계좌
    장내채권 정정취소주문[국내주식-125]

    장내채권 정정취소주문 테스트 함수
    
    Parameters:
        cano (str): 종합계좌번호
        acnt_prdt_cd (str): 계좌상품코드
        pdno (str): 상품번호
        orgn_odno (str): 원주문번호
        ord_qty2 (str): 주문수량2
        bond_ord_unpr (str): 채권주문단가
        qty_all_ord_yn (str): 잔량전부주문여부
        rvse_cncl_dvsn_cd (str): 정정취소구분코드
        mgco_aptm_odno (str): 운용사지정주문번호
        ord_svr_dvsn_cd (str): 주문서버구분코드
        ctac_tlno (str): 연락전화번호

    Returns:
        - DataFrame: 장내채권 정정취소주문 결과
    
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

        # 장내채권 정정취소주문 파라미터 설정
        logger.info("API 파라미터 설정 중...")

        cano = trenv.my_acct
        acnt_prdt_cd = "01"
        pdno = "KR6095572D81"
        orgn_odno = "0004357900"  # 실제 테스트 시 유효한 원주문번호로 변경해야 합니다.
        ord_qty2 = "1"  # 정정/취소 수량
        bond_ord_unpr = "10470"  # 정정 단가
        qty_all_ord_yn = "Y"  # 잔량 전부 주문 여부
        rvse_cncl_dvsn_cd = "01"  # 01: 정정, 02: 취소
        mgco_aptm_odno = ""
        ord_svr_dvsn_cd = "0"
        ctac_tlno = ""

        # API 호출
        logger.info("API 호출 시작: 장내채권 정정취소주문")
        result = order_rvsecncl(
            cano=cano,
            acnt_prdt_cd=acnt_prdt_cd,
            pdno=pdno,
            orgn_odno=orgn_odno,
            ord_qty2=ord_qty2,
            bond_ord_unpr=bond_ord_unpr,
            qty_all_ord_yn=qty_all_ord_yn,
            rvse_cncl_dvsn_cd=rvse_cncl_dvsn_cd,
            mgco_aptm_odno=mgco_aptm_odno,
            ord_svr_dvsn_cd=ord_svr_dvsn_cd,
            ctac_tlno=ctac_tlno,
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
        logger.info("=== 장내채권 정정취소주문 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
