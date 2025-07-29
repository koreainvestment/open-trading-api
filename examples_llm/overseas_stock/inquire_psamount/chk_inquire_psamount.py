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
from inquire_psamount import inquire_psamount

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 매수가능금액조회 [v1_해외주식-014]
##############################################################################################

# 컬럼명 매핑 (한글 변환용)
COLUMN_MAPPING = {
    'tr_crcy_cd': '거래통화코드',
    'ord_psbl_frcr_amt': '주문가능외화금액',
    'sll_ruse_psbl_amt': '매도재사용가능금액',
    'ovrs_ord_psbl_amt': '해외주문가능금액',
    'max_ord_psbl_qty': '최대주문가능수량',
    'echm_af_ord_psbl_amt': '환전이후주문가능금액',
    'echm_af_ord_psbl_qty': '환전이후주문가능수량',
    'ord_psbl_qty': '주문가능수량',
    'exrt': '환율',
    'frcr_ord_psbl_amt1': '외화주문가능금액1',
    'ovrs_max_ord_psbl_qty': '해외최대주문가능수량'
}

# 숫자형 컬럼 정의 (소수점 처리용)
NUMERIC_COLUMNS = []

def main():
    """
    [해외주식] 주문/계좌
    해외주식 매수가능금액조회[v1_해외주식-014]

    해외주식 매수가능금액조회 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        - ovrs_excg_cd (str): 해외거래소코드 (NASD : 나스닥 / NYSE : 뉴욕 / AMEX : 아멕스 SEHK : 홍콩 / SHAA : 중국상해 / SZAA : 중국심천 TKSE : 일본 / HASE : 하노이거래소 / VNSE : 호치민거래소)
        - ovrs_ord_unpr (str): 해외주문단가 (해외주문단가 (23.8) 정수부분 23자리, 소수부분 8자리)
        - item_cd (str): 종목코드 (종목코드)
        - env_dv (str): 실전모의구분 (real:실전, demo:모의)

    Returns:
        - DataFrame: 해외주식 매수가능금액조회 결과
    
    Example:
        >>> df = inquire_psamount(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, ovrs_excg_cd="NASD", ovrs_ord_unpr="1.4", item_cd="QQQ", env_dv="real")  # 실전투자
    """
    try:
        # pandas 출력 옵션 설정
        pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
        pd.set_option('display.width', None)  # 출력 너비 제한 해제
        pd.set_option('display.max_rows', None)  # 모든 행 표시

        # 실전/모의투자 선택 (모의투자 지원 로직)
        env_dv = "real"  # "real": 실전투자, "demo": 모의투자
        logger.info("투자 환경: %s", "실전투자" if env_dv == "real" else "모의투자")

        # 토큰 발급 (모의투자 지원 로직)
        logger.info("토큰 발급 중...")
        if env_dv == "real":
            ka.auth(svr='prod')  # 실전투자용 토큰
        elif env_dv == "demo":
            ka.auth(svr='vps')   # 모의투자용 토큰
        logger.info("토큰 발급 완료")
        trenv = ka.getTREnv()

        # API 호출
        logger.info("API 호출")
        result = inquire_psamount(
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            ovrs_excg_cd="NASD",
            ovrs_ord_unpr="1.4",
            item_cd="QQQ",
            env_dv="real", 
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
        logger.info("=== 해외주식 매수가능금액조회 결과 (%s) ===", "실전투자" if env_dv == "real" else "모의투자")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
