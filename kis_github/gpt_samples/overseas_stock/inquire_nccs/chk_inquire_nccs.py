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
from inquire_nccs import inquire_nccs

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

COLUMN_MAPPING = {
    'ord_dt': '주문일자',
    'ord_gno_brno': '주문채번지점번호',
    'odno': '주문번호',
    'orgn_odno': '원주문번호',
    'pdno': '상품번호',
    'sll_buy_dvsn_cd': '매도매수구분코드',
    'rvse_cncl_dvsn_cd': '정정취소구분코드',
    'rjct_rson': '거부사유',
    'ord_tmd': '주문시각',
    'tr_crcy_cd': '거래통화코드',
    'natn_cd': '국가코드',
    'ft_ord_qty': 'FT주문수량',
    'ft_ccld_qty': 'FT체결수량',
    'nccs_qty': '미체결수량',
    'ft_ord_unpr3': 'FT주문단가3',
    'ft_ccld_unpr3': 'FT체결단가3',
    'ft_ccld_amt3': 'FT체결금액3',
    'ovrs_excg_cd': '해외거래소코드',
    'loan_type_cd': '대출유형코드',
    'loan_dt': '대출일자',
    '-usa_amk_exts_rqst_yn': '미국애프터마켓연장신청여부',
    'ctx_area_fk200': '연속조회검색조건200',
    'ctx_area_nk200': '연속조회키200'
}

def main():
    """
    [해외주식] 주문/계좌
    해외주식 미체결내역[v1_해외주식-005]

    해외주식 미체결내역 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        - ovrs_excg_cd (str): 해외거래소코드 (NASD : 나스닥 NYSE : 뉴욕  AMEX : 아멕스 SEHK : 홍콩 SHAA : 중국상해 SZAA : 중국심천 TKSE : 일본 HASE : 베트남 하노이 VNSE : 베트남 호치민  * NASD 인 경우만 미국전체로 조회되며 나머지 거래소 코드는 해당 거래소만 조회됨 * 공백 입력 시 다음조회가 불가능하므로, 반드시 거래소코드 입력해야 함)
        - sort_sqn (str): 정렬순서 (DS : 정순 그외 : 역순  [header tr_id: TTTS3018R] ""(공란))
        - ctx_area_fk200 (str): 연속조회검색조건200 (공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK200값 : 다음페이지 조회시(2번째부터))
        - ctx_area_nk200 (str): 연속조회키200 (공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK200값 : 다음페이지 조회시(2번째부터))

    Returns:
        - DataFrame: 해외주식 미체결내역 결과
    
    Example:
        >>> df = inquire_nccs(cano=trenv.my_acct, acnt_prdt_cd="01", ovrs_excg_cd="", sort_sqn="DS", ctx_area_fk200="", ctx_area_nk200="")
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

        # 해외주식 미체결내역 파라미터 설정
        logger.info("API 파라미터 설정 중...")
        cano = trenv.my_acct  # 계좌번호 (자동 설정)
        acnt_prdt_cd = "01"  # 계좌상품코드
        ovrs_excg_cd = "NASD"  # 해외거래소코드
        sort_sqn = "DS"  # 정렬순서
        ctx_area_fk200 = ""  # 연속조회검색조건200
        ctx_area_nk200 = ""  # 연속조회키200

        
        # API 호출
        logger.info("API 호출 시작: 해외주식 미체결내역")
        result = inquire_nccs(
            cano=cano,  # 종합계좌번호
            acnt_prdt_cd=acnt_prdt_cd,  # 계좌상품코드
            ovrs_excg_cd=ovrs_excg_cd,  # 해외거래소코드
            sort_sqn=sort_sqn,  # 정렬순서
            ctx_area_fk200=ctx_area_fk200,  # 연속조회검색조건200
            ctx_area_nk200=ctx_area_nk200,  # 연속조회키200
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
        logger.info("=== 해외주식 미체결내역 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
