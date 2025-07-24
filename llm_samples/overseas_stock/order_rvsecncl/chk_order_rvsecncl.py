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
from order_rvsecncl import order_rvsecncl

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

################################################################################
# [해외주식] 주문/계좌 > 해외주식 정정취소주문[v1_해외주식-003]
################################################################################

# 컬럼명 매핑 (한글 변환용)
COLUMN_MAPPING = {
    'KRX_FWDG_ORD_ORGNO': '한국거래소전송주문조직번호',
    'ODNO': '주문번호',
    'ORD_TMD': '주문시각'
}

# 숫자형 컬럼 정의 (소수점 처리용)
NUMERIC_COLUMNS = []

def main():
    """
    [해외주식] 주문/계좌
    해외주식 정정취소주문[v1_해외주식-003]

    해외주식 정정취소주문 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        - ovrs_excg_cd (str): 해외거래소코드 (NASD : 나스닥  NYSE : 뉴욕  AMEX : 아멕스 SEHK : 홍콩 SHAA : 중국상해 SZAA : 중국심천 TKSE : 일본 HASE : 베트남 하노이 VNSE : 베트남 호치민)
        - pdno (str): 상품번호 ()
        - orgn_odno (str): 원주문번호 (정정 또는 취소할 원주문번호 (해외주식_주문 API ouput ODNO  or 해외주식 미체결내역 API output ODNO 참고))
        - rvse_cncl_dvsn_cd (str): 정정취소구분코드 (01 : 정정  02 : 취소)
        - ord_qty (str): 주문수량 ()
        - ovrs_ord_unpr (str): 해외주문단가 (취소주문 시, "0" 입력)
        - mgco_aptm_odno (str): 운용사지정주문번호 ()
        - ord_svr_dvsn_cd (str): 주문서버구분코드 ("0"(Default))
        - env_dv (str): 실전모의구분 (real:실전, demo:모의)

    Returns:
        - DataFrame: 해외주식 정정취소주문 결과
    
    Example:
        >>> df = order_rvsecncl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, ovrs_excg_cd="NYSE", pdno="BA", orgn_odno="1234567890", rvse_cncl_dvsn_cd="01", ord_qty="100", ovrs_ord_unpr="0", mgco_aptm_odno="", ord_svr_dvsn_cd="0", env_dv="real")  # 실전투자
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
        result = order_rvsecncl(
            cano=trenv.my_acct,  # 종합계좌번호
            acnt_prdt_cd=trenv.my_prod,  # 계좌상품코드
            ovrs_excg_cd="NASD",  # 해외거래소코드
            pdno="AMZN",  # 상품번호
            orgn_odno="0030132992",  # 원주문번호
            rvse_cncl_dvsn_cd="01",  # 정정취소구분코드
            ord_qty="100",  # 주문수량
            ovrs_ord_unpr="99",  # 해외주문단가
            mgco_aptm_odno="",  # 운용사지정주문번호
            ord_svr_dvsn_cd="0",  # 주문서버구분코드
            env_dv="real",  # 실전모의구분
        )
        
        if result is None or result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return
        
        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())

        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)
        
        # 숫자형 컬럼 변환 (object -> float64)
        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce')
        
        # 결과 출력
        logger.info("=== 해외주식 정정취소주문 결과 (%s) ===", "실전투자" if env_dv == "real" else "모의투자")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
