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
from order import order

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 주문 [v1_해외주식-001]
##############################################################################################

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
    해외주식 주문[v1_해외주식-001]

    해외주식 주문 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        - ovrs_excg_cd (str): 해외거래소코드 (NASD : 나스닥 NYSE : 뉴욕 AMEX : 아멕스 SEHK : 홍콩 SHAA : 중국상해 SZAA : 중국심천 TKSE : 일본 HASE : 베트남 하노이 VNSE : 베트남 호치민)
        - pdno (str): 상품번호 (종목코드)
        - ord_qty (str): 주문수량 (주문수량 (해외거래소 별 최소 주문수량 및 주문단위 확인 필요))
        - ovrs_ord_unpr (str): 해외주문단가 (1주당 가격 * 시장가의 경우 1주당 가격을 공란으로 비우지 않음 "0"으로 입력)
        - ord_dv (str): 주문구분 (buy: 매수, sell: 매도)
        - ctac_tlno (str): 연락전화번호 ()
        - mgco_aptm_odno (str): 운용사지정주문번호 ()
        - ord_svr_dvsn_cd (str): 주문서버구분코드 ("0"(Default))
        - ord_dvsn (str): 주문구분 ([Header tr_id TTTT1002U(미국 매수 주문)] 00 : 지정가 32 : LOO(장개시지정가) 34 : LOC(장마감지정가) * 모의투자 VTTT1002U(미국 매수 주문)로는 00:지정가만 가능  [Header tr_id TTTT1006U(미국 매도 주문)] 00 : 지정가 31 : MOO(장개시시장가) 32 : LOO(장개시지정가) 33 : MOC(장마감시장가) 34 : LOC(장마감지정가) * 모의투자 VTTT1006U(미국 매도 주문)로는 00:지정가만 가능  [Header tr_id TTTS1001U(홍콩 매도 주문)] 00 : 지정가 50 : 단주지정가 * 모의투자 VTTS1001U(홍콩 매도 주문)로는 00:지정가만 가능  [그외 tr_id] 제거)
        - env_dv (str): 실전모의구분 (real:실전, demo:모의)

    Returns:
        - DataFrame: 해외주식 주문 결과
    
    Example:
        >>> df = order(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, ovrs_excg_cd="NASD", pdno="AAPL", ord_qty="10", ovrs_ord_unpr="150.00", ord_dv="sell", ctac_tlno="", mgco_aptm_odno="", ord_svr_dvsn_cd="0", ord_dvsn="00", env_dv="real")  # 실전투자
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
        result = order(
            cano=trenv.my_acct,  # 종합계좌번호
            acnt_prdt_cd=trenv.my_prod,  # 계좌상품코드
            ovrs_excg_cd="NASD",  # 해외거래소코드
            pdno="AAPL",  # 상품번호
            ord_qty="10",  # 주문수량
            ovrs_ord_unpr="200",  # 해외주문단가
            ord_dv="sell",  # 주문구분
            ctac_tlno="",  # 연락전화번호
            mgco_aptm_odno="",  # 운용사지정주문번호
            ord_svr_dvsn_cd="0",  # 주문서버구분코드
            ord_dvsn="00",  # 주문구분
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
        
        # 숫자형 컬럼 소수점 둘째자리까지 표시
        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
        
        # 결과 출력
        logger.info("=== 해외주식 주문 결과 (%s) ===", "실전투자" if env_dv == "real" else "모의투자")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
