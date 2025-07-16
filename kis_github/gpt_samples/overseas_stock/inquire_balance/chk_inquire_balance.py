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
from inquire_balance import inquire_balance

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

COLUMN_MAPPING = {
    'cano': '종합계좌번호',
    'acnt_prdt_cd': '계좌상품코드',
    'prdt_type_cd': '상품유형코드',
    'ovrs_pdno': '해외상품번호',
    'frcr_evlu_pfls_amt': '외화평가손익금액',
    'evlu_pfls_rt': '평가손익율',
    'pchs_avg_pric': '매입평균가격',
    'ovrs_cblc_qty': '해외잔고수량',
    'ord_psbl_qty': '주문가능수량',
    'frcr_pchs_amt1': '외화매입금액1',
    'ovrs_stck_evlu_amt': '해외주식평가금액',
    'now_pric2': '현재가격2',
    'tr_crcy_cd': '거래통화코드',
    'ovrs_excg_cd': '해외거래소코드',
    'loan_type_cd': '대출유형코드',
    'loan_dt': '대출일자',
    'expd_dt': '만기일자',
    'frcr_pchs_amt1': '외화매입금액1',
    'ovrs_rlzt_pfls_amt': '해외실현손익금액',
    'ovrs_tot_pfls': '해외총손익',
    'rlzt_erng_rt': '실현수익율',
    'tot_evlu_pfls_amt': '총평가손익금액',
    'tot_pftrt': '총수익률',
    'frcr_buy_amt_smtl1': '외화매수금액합계1',
    'ovrs_rlzt_pfls_amt2': '해외실현손익금액2',
    'frcr_buy_amt_smtl2': '외화매수금액합계2'
}

def main():
    """
    [해외주식] 주문/계좌
    해외주식 잔고[v1_해외주식-006]

    해외주식 잔고 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        - ovrs_excg_cd (str): 해외거래소코드 ([모의] NASD : 나스닥 NYSE : 뉴욕  AMEX : 아멕스  [실전] NASD : 미국전체 NAS : 나스닥 NYSE : 뉴욕  AMEX : 아멕스  [모의/실전 공통] SEHK : 홍콩 SHAA : 중국상해 SZAA : 중국심천 TKSE : 일본 HASE : 베트남 하노이 VNSE : 베트남 호치민)
        - tr_crcy_cd (str): 거래통화코드 (USD : 미국달러 HKD : 홍콩달러 CNY : 중국위안화 JPY : 일본엔화 VND : 베트남동)
        - ctx_area_fk200 (str): 연속조회검색조건200 (공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK200값 : 다음페이지 조회시(2번째부터))
        - ctx_area_nk200 (str): 연속조회키200 (공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK200값 : 다음페이지 조회시(2번째부터))
        - env_dv (str): 실전모의구분 (real:실전, demo:모의)

    Returns:
        - DataFrame: 해외주식 잔고 결과
    
    Example:
        >>> df1, df2 = inquire_balance(cano=trenv.my_acct, acnt_prdt_cd="01", ovrs_excg_cd="NASD", tr_crcy_cd="USD", ctx_area_fk200="", ctx_area_nk200="", env_dv="real")  # 실전투자
        >>> df1, df2 = inquire_balance(cano=trenv.my_acct, acnt_prdt_cd="01", ovrs_excg_cd="NASD", tr_crcy_cd="USD", ctx_area_fk200="", ctx_area_nk200="", env_dv="demo")  # 모의투자
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

        # 해외주식 잔고 파라미터 설정
        logger.info("API 파라미터 설정 중...")
        cano = trenv.my_acct  # 계좌번호 (자동 설정)
        acnt_prdt_cd = "01"  # 계좌상품코드
        ovrs_excg_cd = "NASD"  # 해외거래소코드
        tr_crcy_cd = "USD"  # 거래통화코드
        ctx_area_fk200 = ""  # 연속조회검색조건200
        ctx_area_nk200 = ""  # 연속조회키200

        
        # API 호출
        logger.info("API 호출 시작: 해외주식 잔고 (%s)", "실전투자" if env_dv == "real" else "모의투자")
        result1, result2 = inquire_balance(
            cano=cano,  # 종합계좌번호
            acnt_prdt_cd=acnt_prdt_cd,  # 계좌상품코드
            ovrs_excg_cd=ovrs_excg_cd,  # 해외거래소코드
            tr_crcy_cd=tr_crcy_cd,  # 거래통화코드
            ctx_area_fk200=ctx_area_fk200,  # 연속조회검색조건200
            ctx_area_nk200=ctx_area_nk200,  # 연속조회키200
            env_dv=env_dv,  # 실전모의구분
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
            logger.info("output2 결과:")
            print(result2)
        else:
            logger.info("output2 데이터가 없습니다.")

        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
