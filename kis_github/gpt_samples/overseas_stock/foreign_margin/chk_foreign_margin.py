"""
Created on 2025-06-26

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from foreign_margin import foreign_margin

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 주문/계좌 - 해외증거금 통화별조회 [해외주식-035]
##############################################################################################

# 컬럼명 매핑 (한글 변환용)
COLUMN_MAPPING = {
    'natn_name': '국가명',
    'frcr_dncl_amt1': '외화예수금액',
    'ustl_buy_amt': '미결제매수금액',
    'ustl_sll_amt': '미결제매도금액',
    'frcr_rcvb_amt': '외화미수금액',
    'frcr_mgn_amt': '외화증거금액',
    'frcr_gnrl_ord_psbl_amt': '외화일반주문가능금액',
    'frcr_ord_psbl_amt1': '외화주문가능금액',
    'itgr_ord_psbl_amt': '통합주문가능금액',
    'bass_exrt': '기준환율'
}

# 숫자형 컬럼 정의 (소수점 처리용)
NUMERIC_COLUMNS = [
    '외화예수금액', '미결제매수금액', '미결제매도금액', '외화미수금액', '외화증거금액',
    '외화일반주문가능금액', '외화주문가능금액', '통합주문가능금액', '기준환율'
]

def main():
    """
    [해외주식] 주문/계좌
    해외증거금 통화별조회[해외주식-035]

    해외증거금 통화별조회 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 ()
        - acnt_prdt_cd (str): 계좌상품코드 ()

    Returns:
        - DataFrame: 해외증거금 통화별조회 결과
    
    Example:
        >>> df = foreign_margin(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod)
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
        result = foreign_margin(
            cano=trenv.my_acct,  # 종합계좌번호
            acnt_prdt_cd=trenv.my_prod,  # 계좌상품코드
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
        logger.info("=== 해외증거금 통화별조회 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
