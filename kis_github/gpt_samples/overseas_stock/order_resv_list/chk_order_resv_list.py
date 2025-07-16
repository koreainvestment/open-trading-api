"""
Created on 20250601
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from order_resv_list import order_resv_list

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 예약주문조회[v1_해외주식-013]
##############################################################################################

def main():
    """
    해외주식 예약주문조회 테스트 함수
    
    이 함수는 해외주식 예약주문조회 API를 호출하여 결과를 출력합니다.
    
    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시
    
    # 인증 토큰 발급
    ka.auth()
    
    # case1 조회
    logging.info("=== case1 조회 ===")
    try:
        result = order_resv_list(nat_dv="us", cano="81180744", acnt_prdt_cd="01", inqr_strt_dt="20220809", inqr_end_dt="20220830", inqr_dvsn_cd="00", ovrs_excg_cd="NASD")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return
    
    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())
    
    # 컬럼명 한글 변환
    column_mapping = {
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
    
    result = result.rename(columns=column_mapping)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시
    numeric_columns = []
    
    for col in numeric_columns:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result)

if __name__ == "__main__":
    main() 