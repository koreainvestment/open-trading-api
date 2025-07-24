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
from inquire_period_profit import inquire_period_profit

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 기간손익 [v1_해외주식-032]
##############################################################################################

# 컬럼명 매핑 (한글 변환용)
COLUMN_MAPPING = {
    'trad_day': '매매일',
    'ovrs_pdno': '해외상품번호',
    'slcl_qty': '매도청산수량',
    'pchs_avg_pric': '매입평균가격',
    'frcr_pchs_amt1': '외화매입금액1',
    'avg_sll_unpr': '평균매도단가',
    'frcr_sll_amt_smtl1': '외화매도금액합계1',
    'stck_sll_tlex': '주식매도제비용',
    'ovrs_rlzt_pfls_amt': '해외실현손익금액',
    'pftrt': '수익률',
    'exrt': '환율',
    'ovrs_excg_cd': '해외거래소코드',
    'frst_bltn_exrt': '최초고시환율',
    'stck_sll_amt_smtl': '주식매도금액합계',
    'stck_buy_amt_smtl': '주식매수금액합계',
    'smtl_fee1': '합계수수료1',
    'excc_dfrm_amt': '정산지급금액',
    'ovrs_rlzt_pfls_tot_amt': '해외실현손익총금액',
    'tot_pftrt': '총수익률',
    'bass_dt': '기준일자',
    'exrt': '환율'
}

# 숫자형 컬럼 정의 (소수점 처리용)
NUMERIC_COLUMNS = [
    'slcl_qty', 'pchs_avg_pric', 'frcr_pchs_amt1', 'avg_sll_unpr', 'frcr_sll_amt_smtl1',
    'stck_sll_tlex', 'ovrs_rlzt_pfls_amt', 'pftrt', 'exrt', 'frst_bltn_exrt',
    'stck_sll_amt_smtl', 'stck_buy_amt_smtl', 'smtl_fee1', 'excc_dfrm_amt',
    'ovrs_rlzt_pfls_tot_amt', 'tot_pftrt'
]

def main():
    """
    [해외주식] 주문/계좌
    해외주식 기간손익[v1_해외주식-032]

    해외주식 기간손익 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        - ovrs_excg_cd (str): 해외거래소코드 (공란 : 전체,  NASD : 미국, SEHK : 홍콩, SHAA : 중국, TKSE : 일본, HASE : 베트남)
        - natn_cd (str): 국가코드 (공란(Default))
        - crcy_cd (str): 통화코드 (공란 : 전체 USD : 미국달러, HKD : 홍콩달러, CNY : 중국위안화,  JPY : 일본엔화, VND : 베트남동)
        - pdno (str): 상품번호 (공란 : 전체)
        - inqr_strt_dt (str): 조회시작일자 (YYYYMMDD)
        - inqr_end_dt (str): 조회종료일자 (YYYYMMDD)
        - wcrc_frcr_dvsn_cd (str): 원화외화구분코드 (01 : 외화, 02 : 원화)
        - FK200 (str): 연속조회검색조건200 (공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK200값 : 다음페이지 조회시(2번째부터))
        - NK200 (str): 연속조회키200 (공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK200값 : 다음페이지 조회시(2번째부터))

    Returns:
        - DataFrame: 해외주식 기간손익 결과 (output1: 기간손익 목록, output2: 기간손익 요약)
    
    Example:
        >>> df1, df2 = inquire_period_profit(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, ovrs_excg_cd="NASD", natn_cd="", crcy_cd="USD", pdno="", inqr_strt_dt="20230101", inqr_end_dt="20231231", wcrc_frcr_dvsn_cd="01", FK200="", NK200="")
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
        result1, result2 = inquire_period_profit(
            cano=trenv.my_acct,  # 종합계좌번호
            acnt_prdt_cd=trenv.my_prod,  # 계좌상품코드
            ovrs_excg_cd="NASD",  # 해외거래소코드
            natn_cd="",  # 국가코드
            crcy_cd="USD",  # 통화코드
            pdno="",  # 상품번호
            inqr_strt_dt="20240601",  # 조회시작일자
            inqr_end_dt="20240630",  # 조회종료일자
            wcrc_frcr_dvsn_cd="01",  # 원화외화구분코드
            FK200="",  # 연속조회검색조건200
            NK200=""   # 연속조회키200
        )
        
        if result1 is None or result1.empty:
            logger.warning("조회된 기간손익 목록 데이터가 없습니다.")
        else:
            # 컬럼명 출력
            logger.info("사용 가능한 컬럼 목록 (output1):")
            logger.info(result1.columns.tolist())

            # 한글 컬럼명으로 변환
            result1 = result1.rename(columns=COLUMN_MAPPING)
            
            # 숫자형 컬럼 처리
            for col in NUMERIC_COLUMNS:
                if col in result1.columns:
                    result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)
            
            # 결과 출력
            logger.info("=== 해외주식 기간손익 목록 (output1) ===")
            logger.info("조회된 데이터 건수: %d", len(result1))
            print(result1)

        if result2 is None or result2.empty:
            logger.warning("조회된 기간손익 요약 데이터가 없습니다.")
        else:
            # 컬럼명 출력
            logger.info("사용 가능한 컬럼 목록 (output2):")
            logger.info(result2.columns.tolist())

            # 한글 컬럼명으로 변환
            result2 = result2.rename(columns=COLUMN_MAPPING)
            
            # 숫자형 컬럼 처리
            for col in NUMERIC_COLUMNS:
                if col in result2.columns:
                    result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

            # 결과 출력
            logger.info("=== 해외주식 기간손익 요약 (output2) ===")
            logger.info("조회된 데이터 건수: %d", len(result2))
            print(result2)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
