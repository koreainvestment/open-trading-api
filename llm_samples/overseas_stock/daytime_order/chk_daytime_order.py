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
from daytime_order import daytime_order

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 미국주간주문 [v1_해외주식-026]
##############################################################################################

# 컬럼명 매핑 (한글 변환용)
COLUMN_MAPPING = {
    'KRX_FWDG_ORD_ORGNO': '한국거래소전송주문조직번호',
    'ODNO': '주문번호',
    'ORD_TMD': '주문시각'
}

# 숫자형 컬럼 정의
NUMERIC_COLUMNS = []

def main():
    """
    [해외주식] 주문/계좌
    해외주식 미국주간주문[v1_해외주식-026]

    해외주식 미국주간주문 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        - ovrs_excg_cd (str): 해외거래소코드 (NASD:나스닥 / NYSE:뉴욕 / AMEX:아멕스)
        - pdno (str): 상품번호 (종목코드)
        - ord_qty (str): 주문수량 (해외거래소 별 최소 주문수량 및 주문단위 확인 필요)
        - ovrs_ord_unpr (str): 해외주문단가 (소수점 포함, 1주당 가격 * 시장가의 경우 1주당 가격을 공란으로 비우지 않음 "0"으로 입력)
        - ctac_tlno (str): 연락전화번호 (" ")
        - mgco_aptm_odno (str): 운용사지정주문번호 (" ")
        - ord_svr_dvsn_cd (str): 주문서버구분코드 ("0")
        - ord_dvsn (str): 주문구분 ([미국 매수/매도 주문]  00 : 지정가  * 주간거래는 지정가만 가능)

    Returns:
        - DataFrame: 해외주식 미국주간주문 결과
    
    Example:
        >>> df = daytime_order(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, order_dv="buy", ovrs_excg_cd="NASD", pdno="AAPL", ord_qty="10", ovrs_ord_unpr="150.50", ctac_tlno="", mgco_aptm_odno="", ord_svr_dvsn_cd="0", ord_dvsn="00")
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
        result = daytime_order(
            order_dv="buy",  # 주문구분
            cano=trenv.my_acct,  # 종합계좌번호
            acnt_prdt_cd=trenv.my_prod,  # 계좌상품코드
            ovrs_excg_cd="NASD",  # 해외거래소코드
            pdno="AAPL",  # 상품번호
            ord_qty="10",  # 주문수량
            ovrs_ord_unpr="0.8",  # 해외주문단가
            ctac_tlno="",  # 연락전화번호
            mgco_aptm_odno="",  # 운용사지정주문번호
            ord_svr_dvsn_cd="0",  # 주문서버구분코드
            ord_dvsn="00",  # 주문구분
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
        logger.info("=== 해외주식 미국주간주문 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
