# -*- coding: utf-8 -*-
"""
Created on 2025-06-19

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from issue_info import issue_info

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [장내채권] 기본시세 > 장내채권 발행정보 [국내주식-156]
##############################################################################################

COLUMN_MAPPING = {
    'pdno': '상품번호',
    'prdt_type_cd': '상품유형코드',
    'prdt_name': '상품명',
    'prdt_eng_name': '상품영문명',
    'ivst_heed_prdt_yn': '투자유의상품여부',
    'exts_yn': '연장여부',
    'bond_clsf_cd': '채권분류코드',
    'bond_clsf_kor_name': '채권분류한글명',
    'papr': '액면가',
    'int_mned_dvsn_cd': '이자월말구분코드',
    'rvnu_shap_cd': '매출형태코드',
    'issu_amt': '발행금액',
    'lstg_rmnd': '상장잔액',
    'int_dfrm_mcnt': '이자지급개월수',
    'bond_int_dfrm_mthd_cd': '채권이자지급방법코드',
    'splt_rdpt_rcnt': '분할상환횟수',
    'prca_dfmt_term_mcnt': '원금거치기간개월수',
    'int_anap_dvsn_cd': '이자선후급구분코드',
    'bond_rght_dvsn_cd': '채권권리구분코드',
    'prdt_pclc_text': '상품특성내용',
    'prdt_abrv_name': '상품약어명',
    'prdt_eng_abrv_name': '상품영문약어명',
    'sprx_psbl_yn': '분리과세가능여부',
    'pbff_pplc_ofrg_mthd_cd': '공모사모모집방법코드',
    'cmco_cd': '주간사코드',
    'issu_istt_cd': '발행기관코드',
    'issu_istt_name': '발행기관명',
    'pnia_dfrm_agcy_istt_cd': '원리금지급대행기관코드',
    'dsct_ec_rt': '할인할증율',
    'srfc_inrt': '표면이율',
    'expd_rdpt_rt': '만기상환율',
    'expd_asrc_erng_rt': '만기보장수익율',
    'bond_grte_istt_name': '채권보증기관명',
    'int_dfrm_day_type_cd': '이자지급일유형코드',
    'ksd_int_calc_unit_cd': '증권예탁결제원이자계산단위코드',
    'int_wunt_uder_prcs_dvsn_cd': '이자원화단위미만처리구분코드',
    'rvnu_dt': '매출일자',
    'issu_dt': '발행일자',
    'lstg_dt': '상장일자',
    'expd_dt': '만기일자',
    'rdpt_dt': '상환일자',
    'sbst_pric': '대용가격',
    'rgbf_int_dfrm_dt': '직전이자지급일자',
    'nxtm_int_dfrm_dt': '차기이자지급일자',
    'frst_int_dfrm_dt': '최초이자지급일자',
    'ecis_pric': '행사가격',
    'rght_stck_std_pdno': '권리주식표준상품번호',
    'ecis_opng_dt': '행사개시일자',
    'ecis_end_dt': '행사종료일자',
    'bond_rvnu_mthd_cd': '채권매출방법코드',
    'oprt_stfno': '조작직원번호',
    'oprt_stff_name': '조작직원명',
    'rgbf_int_dfrm_wday': '직전이자지급요일',
    'nxtm_int_dfrm_wday': '차기이자지급요일',
    'kis_crdt_grad_text': '한국신용평가신용등급내용',
    'kbp_crdt_grad_text': '한국채권평가신용등급내용',
    'nice_crdt_grad_text': '한국신용정보신용등급내용',
    'fnp_crdt_grad_text': '에프앤자산평가신용등급내용',
    'dpsi_psbl_yn': '예탁가능여부',
    'pnia_int_calc_unpr': '원리금이자계산단가',
    'prcm_idx_bond_yn': '물가지수채권여부',
    'expd_exts_srdp_rcnt': '만기연장분할상환횟수',
    'expd_exts_srdp_rt': '만기연장분할상환율',
    'loan_psbl_yn': '대출가능여부',
    'grte_dvsn_cd': '보증구분코드',
    'fnrr_rank_dvsn_cd': '선후순위구분코드',
    'krx_lstg_abol_dvsn_cd': '한국거래소상장폐지구분코드',
    'asst_rqdi_dvsn_cd': '자산유동화구분코드',
    'opcb_dvsn_cd': '옵션부사채구분코드',
    'crfd_item_yn': '크라우드펀딩종목여부',
    'crfd_item_rstc_cclc_dt': '크라우드펀딩종목제한해지일자',
    'bond_nmpr_unit_pric': '채권호가단위가격',
    'ivst_heed_bond_dvsn_name': '투자유의채권구분명',
    'add_erng_rt': '추가수익율',
    'add_erng_rt_aply_dt': '추가수익율적용일자',
    'bond_tr_stop_dvsn_cd': '채권거래정지구분코드',
    'ivst_heed_bond_dvsn_cd': '투자유의채권구분코드',
    'pclr_cndt_text': '특이조건내용',
    'hbbd_yn': '하이브리드채권여부',
    'cdtl_cptl_scty_type_cd': '조건부자본증권유형코드',
    'elec_scty_yn': '전자증권여부',
    'sq1_clop_ecis_opng_dt': '1차콜옵션행사개시일자',
    'frst_erlm_stfno': '최초등록직원번호',
    'frst_erlm_dt': '최초등록일자',
    'frst_erlm_tmd': '최초등록시각',
    'tlg_rcvg_dtl_dtime': '전문수신상세일시'
}

NUMERIC_COLUMNS = []

def main():
    """
    [장내채권] 기본시세
    장내채권 발행정보[국내주식-156]

    장내채권 발행정보 테스트 함수
    
    Parameters:
        - pdno (str): 사용자권한정보 (채권 종목번호(ex. KR6449111CB8))
        - prdt_type_cd (str): 거래소코드 (Unique key(302))
    Returns:
        - DataFrame: 장내채권 발행정보 결과
    
    Example:
        >>> df = issue_info(pdno="KR6449111CB8", prdt_type_cd="302")
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

        # API 호출
        logger.info("API 호출 시작: 장내채권 발행정보")
        result = issue_info(
            pdno="KR6449111CB8",  # 사용자권한정보
            prdt_type_cd="302",  # 거래소코드
        )

        if result is None or result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return

        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())

        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)

        # 숫자형 컬럼 변환
        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce')

        # 결과 출력
        logger.info("=== 장내채권 발행정보 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)

    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise


if __name__ == "__main__":
    main()
