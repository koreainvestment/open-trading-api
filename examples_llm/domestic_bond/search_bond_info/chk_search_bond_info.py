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
from search_bond_info import search_bond_info

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [장내채권] 기본시세 > 장내채권 기본조회 [국내주식-129]
##############################################################################################

COLUMN_MAPPING = {
    'pdno': '상품번호',
    'prdt_type_cd': '상품유형코드',
    'ksd_bond_item_name': '증권예탁결제원채권종목명',
    'ksd_bond_item_eng_name': '증권예탁결제원채권종목영문명',
    'ksd_bond_lstg_type_cd': '증권예탁결제원채권상장유형코드',
    'ksd_ofrg_dvsn_cd': '증권예탁결제원모집구분코드',
    'ksd_bond_int_dfrm_dvsn_cd': '증권예탁결제원채권이자지급구분',
    'issu_dt': '발행일자',
    'rdpt_dt': '상환일자',
    'rvnu_dt': '매출일자',
    'iso_crcy_cd': '통화코드',
    'mdwy_rdpt_dt': '중도상환일자',
    'ksd_rcvg_bond_dsct_rt': '증권예탁결제원수신채권할인율',
    'ksd_rcvg_bond_srfc_inrt': '증권예탁결제원수신채권표면이율',
    'bond_expd_rdpt_rt': '채권만기상환율',
    'ksd_prca_rdpt_mthd_cd': '증권예탁결제원원금상환방법코드',
    'int_caltm_mcnt': '이자계산기간개월수',
    'ksd_int_calc_unit_cd': '증권예탁결제원이자계산단위코드',
    'uval_cut_dvsn_cd': '절상절사구분코드',
    'uval_cut_dcpt_dgit': '절상절사소수점자릿수',
    'ksd_dydv_caltm_aply_dvsn_cd': '증권예탁결제원일할계산기간적용',
    'dydv_calc_dcnt': '일할계산일수',
    'bond_expd_asrc_erng_rt': '채권만기보장수익율',
    'padf_plac_hdof_name': '원리금지급장소본점명',
    'lstg_dt': '상장일자',
    'lstg_abol_dt': '상장폐지일자',
    'ksd_bond_issu_mthd_cd': '증권예탁결제원채권발행방법코드',
    'laps_indf_yn': '경과이자지급여부',
    'ksd_lhdy_pnia_dfrm_mthd_cd': '증권예탁결제원공휴일원리금지급',
    'frst_int_dfrm_dt': '최초이자지급일자',
    'ksd_prcm_lnkg_gvbd_yn': '증권예탁결제원물가연동국고채여',
    'dpsi_end_dt': '예탁종료일자',
    'dpsi_strt_dt': '예탁시작일자',
    'dpsi_psbl_yn': '예탁가능여부',
    'atyp_rdpt_bond_erlm_yn': '비정형상환채권등록여부',
    'dshn_occr_yn': '부도발생여부',
    'expd_exts_yn': '만기연장여부',
    'pclr_ptcr_text': '특이사항내용',
    'dpsi_psbl_excp_stat_cd': '예탁가능예외상태코드',
    'expd_exts_srdp_rcnt': '만기연장분할상환횟수',
    'expd_exts_srdp_rt': '만기연장분할상환율',
    'expd_rdpt_rt': '만기상환율',
    'expd_asrc_erng_rt': '만기보장수익율',
    'bond_int_dfrm_mthd_cd': '채권이자지급방법코드',
    'int_dfrm_day_type_cd': '이자지급일유형코드',
    'prca_dfmt_term_mcnt': '원금거치기간개월수',
    'splt_rdpt_rcnt': '분할상환횟수',
    'rgbf_int_dfrm_dt': '직전이자지급일자',
    'nxtm_int_dfrm_dt': '차기이자지급일자',
    'sprx_psbl_yn': '분리과세가능여부',
    'ictx_rt_dvsn_cd': '소득세율구분코드',
    'bond_clsf_cd': '채권분류코드',
    'bond_clsf_kor_name': '채권분류한글명',
    'int_mned_dvsn_cd': '이자월말구분코드',
    'pnia_int_calc_unpr': '원리금이자계산단가',
    'frn_intr': 'FRN금리',
    'aply_day_prcm_idx_lnkg_cefc': '적용일물가지수연동계수',
    'ksd_expd_dydv_calc_bass_cd': '증권예탁결제원만기일할계산기준',
    'expd_dydv_calc_dcnt': '만기일할계산일수',
    'ksd_cbbw_dvsn_cd': '증권예탁결제원신종사채구분코드',
    'crfd_item_yn': '크라우드펀딩종목여부',
    'pnia_bank_ofdy_dfrm_mthd_cd': '원리금은행휴무일지급방법코드',
    'qib_yn': 'QIB여부',
    'qib_cclc_dt': 'QIB해지일자',
    'csbd_yn': '영구채여부',
    'csbd_cclc_dt': '영구채해지일자',
    'ksd_opcb_yn': '증권예탁결제원옵션부사채여부',
    'ksd_sodn_yn': '증권예탁결제원후순위채권여부',
    'ksd_rqdi_scty_yn': '증권예탁결제원유동화증권여부',
    'elec_scty_yn': '전자증권여부',
    'rght_ecis_mbdy_dvsn_cd': '권리행사주체구분코드',
    'int_rkng_mthd_dvsn_cd': '이자산정방법구분코드',
    'ofrg_dvsn_cd': '모집구분코드',
    'ksd_tot_issu_amt': '증권예탁결제원총발행금액',
    'next_indf_chk_ecls_yn': '다음이자지급체크제외여부',
    'ksd_bond_intr_dvsn_cd': '증권예탁결제원채권금리구분코드',
    'ksd_inrt_aply_dvsn_cd': '증권예탁결제원이율적용구분코드',
    'krx_issu_istt_cd': 'KRX발행기관코드',
    'ksd_indf_frqc_uder_calc_cd': '증권예탁결제원이자지급주기미만',
    'ksd_indf_frqc_uder_calc_dcnt': '증권예탁결제원이자지급주기미만',
    'tlg_rcvg_dtl_dtime': '전문수신상세일시'
}

NUMERIC_COLUMNS = []

def main():
    """
    [장내채권] 기본시세
    장내채권 기본조회[국내주식-129]

    장내채권 기본조회 테스트 함수
    
    Parameters:
        - pdno (str): 상품번호 (상품번호)
        - prdt_type_cd (str): 상품유형코드 (Unique key(302))
    Returns:
        - DataFrame: 장내채권 기본조회 결과
    
    Example:
        >>> df = search_bond_info(pdno="", prdt_type_cd="302")
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
        logger.info("API 호출 시작: 장내채권 기본조회")
        result = search_bond_info(
            pdno="KR103502GA34",  # 상품번호
            prdt_type_cd="302",  # 상품유형코드
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
        logger.info("=== 장내채권 기본조회 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)

    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise


if __name__ == "__main__":
    main()
