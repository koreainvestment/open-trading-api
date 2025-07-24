# -*- coding: utf-8 -*-
"""
Created on 2025-07-03

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

##############################################################################################
# [해외선물옵션] 주문/계좌 > 해외선물옵션 정정취소주문[v1_해외선물-002, 003]
##############################################################################################

# 컬럼명 매핑
COLUMN_MAPPING = {
    'ORD_DT': '주문일자',
    'ODNO': '주문번호'
}

# 숫자형 컬럼
NUMERIC_COLUMNS = []

def main():
    """
    [해외선물옵션] 주문/계좌
    해외선물옵션 정정취소주문[v1_해외선물-002, 003]

    해외선물옵션 정정취소주문 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        - ord_dv (str): 주문구분 (0:정정, 1:취소)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        - orgn_ord_dt (str): 원주문일자 (원 주문 시 출력되는 ORD_DT 값을 입력 (현지거래일))
        - orgn_odno (str): 원주문번호 (정정/취소시 주문번호(ODNO) 8자리를 문자열처럼 "0"을 포함해서 전송 (원 주문 시 출력된 ODNO 값 활용) (ex. ORGN_ODNO : 00360686))
        - fm_limit_ord_pric (str): FMLIMIT주문가격 (OTFM3002U(해외선물옵션주문정정)만 사용)
        - fm_stop_ord_pric (str): FMSTOP주문가격 (OTFM3002U(해외선물옵션주문정정)만 사용)
        - fm_lqd_lmt_ord_pric (str): FM청산LIMIT주문가격 (OTFM3002U(해외선물옵션주문정정)만 사용)
        - fm_lqd_stop_ord_pric (str): FM청산STOP주문가격 (OTFM3002U(해외선물옵션주문정정)만 사용)
        - fm_hdge_ord_scrn_yn (str): FM_HEDGE주문화면여부 (N)
        - fm_mkpr_cvsn_yn (str): FM시장가전환여부 (OTFM3003U(해외선물옵션주문취소)만 사용  ※ FM_MKPR_CVSN_YN 항목에 'Y'로 설정하여 취소주문을 접수할 경우, 주문 취소확인이 들어오면 원장에서 시장가주문을 하나 또 내줌)

    Returns:
        - DataFrame: 해외선물옵션 정정취소주문 결과
    
    Example:
        >>> df = order_rvsecncl(cano=trenv.my_acct, ord_dv="0", acnt_prdt_cd=trenv.my_prod, orgn_ord_dt="20250630", orgn_odno="00123456", fm_limit_ord_pric="10.0", fm_stop_ord_pric="", fm_lqd_lmt_ord_pric="", fm_lqd_stop_ord_pric="", fm_hdge_ord_scrn_yn="N", fm_mkpr_cvsn_yn="") # 정정
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
        result = order_rvsecncl(
            cano=trenv.my_acct,
            ord_dv="1",
            acnt_prdt_cd=trenv.my_prod,
            orgn_ord_dt="20250703",
            orgn_odno="00000398",
            fm_limit_ord_pric="",
            fm_stop_ord_pric="",
            fm_lqd_lmt_ord_pric="",
            fm_lqd_stop_ord_pric="",
            fm_hdge_ord_scrn_yn="N",
            fm_mkpr_cvsn_yn="N"
        )
        
        if result is None or result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return
        
        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())

        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)
        
        # 숫자형 컬럼 소수점 둘째자리까지 표시
        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
        
        # 결과 출력
        logger.info("=== 해외선물옵션 정정취소주문 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
