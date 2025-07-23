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
from search_info import search_info

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 시세분석 > 해외주식 상품기본정보[v1_해외주식-034]
##############################################################################################

COLUMN_MAPPING = {
    'std_pdno': '표준상품번호',
    'prdt_eng_name': '상품영문명',
    'natn_cd': '국가코드',
    'natn_name': '국가명',
    'tr_mket_cd': '거래시장코드',
    'tr_mket_name': '거래시장명',
    'ovrs_excg_cd': '해외거래소코드',
    'ovrs_excg_name': '해외거래소명',
    'tr_crcy_cd': '거래통화코드',
    'ovrs_papr': '해외액면가',
    'crcy_name': '통화명',
    'ovrs_stck_dvsn_cd': '해외주식구분코드',
    'prdt_clsf_cd': '상품분류코드',
    'prdt_clsf_name': '상품분류명',
    'sll_unit_qty': '매도단위수량',
    'buy_unit_qty': '매수단위수량',
    'tr_unit_amt': '거래단위금액',
    'lstg_stck_num': '상장주식수',
    'lstg_dt': '상장일자',
    'ovrs_stck_tr_stop_dvsn_cd': '해외주식거래정지구분코드',
    'lstg_abol_item_yn': '상장폐지종목여부',
    'ovrs_stck_prdt_grp_no': '해외주식상품그룹번호',
    'lstg_yn': '상장여부',
    'tax_levy_yn': '세금징수여부',
    'ovrs_stck_erlm_rosn_cd': '해외주식등록사유코드',
    'ovrs_stck_hist_rght_dvsn_cd': '해외주식이력권리구분코드',
    'chng_bf_pdno': '변경전상품번호',
    'prdt_type_cd_2': '상품유형코드2',
    'ovrs_item_name': '해외종목명',
    'sedol_no': 'SEDOL번호',
    'blbg_tckr_text': '블름버그티커내용',
    'ovrs_stck_etf_risk_drtp_cd': '해외주식ETF위험지표코드',
    'etp_chas_erng_rt_dbnb': 'ETP추적수익율배수',
    'istt_usge_isin_cd': '기관용도ISIN코드',
    'mint_svc_yn': 'MINT서비스여부',
    'mint_svc_yn_chng_dt': 'MINT서비스여부변경일자',
    'prdt_name': '상품명',
    'lei_cd': 'LEI코드',
    'ovrs_stck_stop_rson_cd': '해외주식정지사유코드',
    'lstg_abol_dt': '상장폐지일자',
    'mini_stk_tr_stat_dvsn_cd': '미니스탁거래상태구분코드',
    'mint_frst_svc_erlm_dt': 'MINT최초서비스등록일자',
    'mint_dcpt_trad_psbl_yn': 'MINT소수점매매가능여부',
    'mint_fnum_trad_psbl_yn': 'MINT정수매매가능여부',
    'mint_cblc_cvsn_ipsb_yn': 'MINT잔고전환불가여부',
    'ptp_item_yn': 'PTP종목여부',
    'ptp_item_trfx_exmt_yn': 'PTP종목양도세면제여부',
    'ptp_item_trfx_exmt_strt_dt': 'PTP종목양도세면제시작일자',
    'ptp_item_trfx_exmt_end_dt': 'PTP종목양도세면제종료일자',
    'dtm_tr_psbl_yn': '주간거래가능여부',
    'sdrf_stop_ecls_yn': '급등락정지제외여부',
    'sdrf_stop_ecls_erlm_dt': '급등락정지제외등록일자',
    'memo_text1': '메모내용1',
    'ovrs_now_pric1': '해외현재가격1',
    'last_rcvg_dtime': '최종수신일시'
}

NUMERIC_COLUMNS = ['해외액면가', '매도단위수량', '매수단위수량', '거래단위금액', '상장주식수', 'ETP추적수익율배수', '해외현재가격1']

def main():
    """
    [해외주식] 기본시세
    해외주식 상품기본정보[v1_해외주식-034]

    해외주식 상품기본정보 테스트 함수
    
    Parameters:
        - prdt_type_cd (str): 상품유형코드 (512  미국 나스닥 / 513  미국 뉴욕 / 529  미국 아멕스  515  일본 501  홍콩 / 543  홍콩CNY / 558  홍콩USD 507  베트남 하노이 / 508  베트남 호치민 551  중국 상해A / 552  중국 심천A)
        - pdno (str): 상품번호 (예) AAPL (애플))

    Returns:
        - DataFrame: 해외주식 상품기본정보 결과
    
    Example:
        >>> df = search_info(prdt_type_cd="512", pdno="AAPL")
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

        # 해외주식 상품기본정보 파라미터 설정
        logger.info("API 파라미터 설정 중...")
        prdt_type_cd = "512"  # 상품유형코드
        pdno = "AAPL"  # 상품번호

        
        # API 호출
        logger.info("API 호출 시작: 해외주식 상품기본정보")
        result = search_info(
            prdt_type_cd=prdt_type_cd,  # 상품유형코드
            pdno=pdno,  # 상품번호
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
                result[col] = pd.to_numeric(result[col], errors='coerce')
        
        # 결과 출력
        logger.info("=== 해외주식 상품기본정보 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
