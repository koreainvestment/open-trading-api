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
        - ctx_area_fk200 (str): 연속조회검색조건200 ()
        - ctx_area_nk200 (str): 연속조회키200 ()

    Returns:
        - DataFrame: 해외주식 기간손익 결과
    
    Example:
        >>> df1, df2 = inquire_period_profit(cano=trenv.my_acct, acnt_prdt_cd="01", ovrs_excg_cd="", natn_cd="", crcy_cd="", pdno="", inqr_strt_dt="20250101", inqr_end_dt="20250131", wcrc_frcr_dvsn_cd="01", ctx_area_fk200="", ctx_area_nk200="")
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

        # 해외주식 기간손익 파라미터 설정
        logger.info("API 파라미터 설정 중...")
        cano = trenv.my_acct  # 계좌번호 (자동 설정)
        acnt_prdt_cd = "01"  # 계좌상품코드
        ovrs_excg_cd = "NASD"  # 해외거래소코드
        natn_cd = ""  # 국가코드
        crcy_cd = "USD"  # 통화코드
        pdno = ""  # 상품번호
        inqr_strt_dt = "20250501"  # 조회시작일자
        inqr_end_dt = "20250708"  # 조회종료일자
        wcrc_frcr_dvsn_cd = "01"  # 원화외화구분코드
        ctx_area_fk200 = ""  # 연속조회검색조건200
        ctx_area_nk200 = ""  # 연속조회키200

        
        # API 호출
        logger.info("API 호출 시작: 해외주식 기간손익")
        result1, result2 = inquire_period_profit(
            cano=cano,  # 종합계좌번호
            acnt_prdt_cd=acnt_prdt_cd,  # 계좌상품코드
            ovrs_excg_cd=ovrs_excg_cd,  # 해외거래소코드
            natn_cd=natn_cd,  # 국가코드
            crcy_cd=crcy_cd,  # 통화코드
            pdno=pdno,  # 상품번호
            inqr_strt_dt=inqr_strt_dt,  # 조회시작일자
            inqr_end_dt=inqr_end_dt,  # 조회종료일자
            wcrc_frcr_dvsn_cd=wcrc_frcr_dvsn_cd,  # 원화외화구분코드
            ctx_area_fk200=ctx_area_fk200,  # 연속조회검색조건200
            ctx_area_nk200=ctx_area_nk200,  # 연속조회키200
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
