# -*- coding: utf-8 -*-
"""
Created on 20250601

@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from order_resv_list import order_resv_list

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 예약주문조회[v1_해외주식-013]
##############################################################################################
# 컬럼명 매핑 (한글 변환용)
COLUMN_MAPPING = {
    'cncl_yn': '취소여부',
    'rsvn_ord_rcit_dt': '예약주문접수일자',
    'ovrs_rsvn_odno': '해외예약주문번호',
    'ord_dt': '주문일자',
    'ord_gno_brno': '주문채번지점번호',
    'odno': '주문번호',
    'sll_buy_dvsn_cd': '매도매수구분코드',
    'sll_buy_dvsn_name': '매도매수구분명',
    'ovrs_rsvn_ord_stat_cd': '해외예약주문상태코드',
    'ovrs_rsvn_ord_stat_cd_name': '해외예약주문상태코드명',
    'pdno': '상품번호',
    'prdt_type_cd': '상품유형코드',
    'prdt_name': '상품명',
    'ord_rcit_tmd': '주문접수시각',
    'ord_fwdg_tmd': '주문전송시각',
    'tr_dvsn_name': '거래구분명',
    'ovrs_excg_cd': '해외거래소코드',
    'tr_mket_name': '거래시장명',
    'ord_stfno': '주문직원번호',
    'ft_ord_qty': 'FT주문수량',
    'ft_ord_unpr3': 'FT주문단가3',
    'ft_ccld_qty': 'FT체결수량',
    'nprc_rson_text': '미처리사유내용',
    'splt_buy_attr_name': '분할매수속성명'
}

# 숫자형 컬럼 정의 (소수점 처리용)
NUMERIC_COLUMNS = [
    'FT주문수량', 'FT주문단가', 'FT체결수량'
]

def main():
    """
    [해외주식] 주문/계좌
    해외주식 예약주문조회[v1_해외주식-013]

    해외주식 예약주문조회 테스트 함수
    
    Parameters:
        - nat_dv (str): 국가구분 (us: 미국)
        - cano (str): 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        - inqr_strt_dt (str): 조회시작일자 (YYYYMMDD)
        - inqr_end_dt (str): 조회종료일자 (YYYYMMDD)
        - inqr_dvsn_cd (str): 조회구분코드 (00: 전체, 01: 예약, 02: 체결, 03: 거부)
        - ovrs_excg_cd (str): 해외거래소코드 (NASD: 나스닥, NYSE: 뉴욕, AMEX: 아멕스, SEHK: 홍콩, SHAA: 중국상해, SZAA: 중국심천, TKSE: 일본, HASE: 베트남 하노이, VNSE: 베트남 호치민)
        - env_dv (str): 실전모의구분 (real:실전, demo:모의)

    Returns:
        - DataFrame: 해외주식 예약주문조회 결과
    
    Example:
        >>> df = order_resv_list(nat_dv="us", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, inqr_strt_dt="20220809", inqr_end_dt="20220830", inqr_dvsn_cd="00", ovrs_excg_cd="NASD")  # 실전투자
    """
    try:
        # pandas 출력 옵션 설정
        pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
        pd.set_option('display.width', None)  # 출력 너비 제한 해제
        pd.set_option('display.max_rows', None)  # 모든 행 표시

        # 토큰 발급 (모의투자 지원 로직)
        logger.info("토큰 발급 중...")
        ka.auth()
        logger.info("토큰 발급 완료")
        

        trenv = ka.getTREnv()
        
        # API 호출
        logger.info("API 호출")
        result = order_resv_list(
            nat_dv="us",  # 국가구분
            cano=trenv.my_acct,  # 종합계좌번호
            acnt_prdt_cd=trenv.my_prod,  # 계좌상품코드
            inqr_strt_dt="20220809",  # 조회시작일자
            inqr_end_dt="20220830",  # 조회종료일자
            inqr_dvsn_cd="00",  # 조회구분코드
            ovrs_excg_cd="NASD",  # 해외거래소코드
        )
        
        if result is None or result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return
        
        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())

        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)
        
        # 숫자형 처리
        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce')
        
        # 결과 출력
        logger.info("=== 해외주식 예약주문조회 결과 (실전투자) ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main() 