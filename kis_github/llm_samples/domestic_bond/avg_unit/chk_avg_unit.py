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
from avg_unit import avg_unit

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [장내채권] 기본시세 > 장내채권 평균단가조회 [국내채권-158]
##############################################################################################


# 통합 컬럼 매핑 (모든 output에서 공통 사용)
COLUMN_MAPPING = {
    'evlu_dt': '평가일자',
    'pdno': '상품번호',
    'prdt_type_cd': '상품유형코드',
    'kis_unpr': '한국신용평가단가',
    'kbp_unpr': '한국채권평가단가',
    'nice_evlu_unpr': '한국신용정보평가단가',
    'fnp_unpr': '에프앤자산평가단가',
    'avg_evlu_unpr': '평균평가단가',
    'kis_crdt_grad_text': '한국신용평가신용등급내용',
    'kbp_crdt_grad_text': '한국채권평가신용등급내용',
    'nice_crdt_grad_text': '한국신용정보신용등급내용',
    'fnp_crdt_grad_text': '에프앤자산평가신용등급내용',
    'chng_yn': '변경여부',
    'kis_erng_rt': '한국신용평가수익율',
    'kbp_erng_rt': '한국채권평가수익율',
    'nice_evlu_erng_rt': '한국신용정보평가수익율',
    'fnp_erng_rt': '에프앤자산평가수익율',
    'avg_evlu_erng_rt': '평균평가수익율',
    'kis_rf_unpr': '한국신용평가RF단가',
    'kbp_rf_unpr': '한국채권평가RF단가',
    'nice_evlu_rf_unpr': '한국신용정보평가RF단가',
    'avg_evlu_rf_unpr': '평균평가RF단가',
    'evlu_dt': '평가일자',
    'pdno': '상품번호',
    'prdt_type_cd': '상품유형코드',
    'kis_evlu_amt': '한국신용평가평가금액',
    'kbp_evlu_amt': '한국채권평가평가금액',
    'nice_evlu_amt': '한국신용정보평가금액',
    'fnp_evlu_amt': '에프앤자산평가평가금액',
    'avg_evlu_amt': '평균평가금액',
    'chng_yn': '변경여부',
    'output3': '응답상세',
    'evlu_dt': '평가일자',
    'pdno': '상품번호',
    'prdt_type_cd': '상품유형코드',
    'kis_crcy_cd': '한국신용평가통화코드',
    'kis_evlu_unit_pric': '한국신용평가평가단위가격',
    'kis_evlu_pric': '한국신용평가평가가격',
    'kbp_crcy_cd': '한국채권평가통화코드',
    'kbp_evlu_unit_pric': '한국채권평가평가단위가격',
    'kbp_evlu_pric': '한국채권평가평가가격',
    'nice_crcy_cd': '한국신용정보통화코드',
    'nice_evlu_unit_pric': '한국신용정보평가단위가격',
    'nice_evlu_pric': '한국신용정보평가가격',
    'avg_evlu_unit_pric': '평균평가단위가격',
    'avg_evlu_pric': '평균평가가격',
    'chng_yn': '변경여부'
}

NUMERIC_COLUMNS = []


def main():
    """
    [장내채권] 기본시세
    장내채권 평균단가조회[국내주식-158]

    장내채권 평균단가조회 테스트 함수`
    
    Parameters:
        - inqr_strt_dt (str): 조회시작일자 (일자 ~)
        - inqr_end_dt (str): 조회종료일자 (~ 일자)
        - pdno (str): 상품번호 (공백: 전체,  특정종목 조회시 : 종목코드)
        - prdt_type_cd (str): 상품유형코드 (Unique key(302))
        - vrfc_kind_cd (str): 검증종류코드 (Unique key(00))

    Returns:
        - Tuple[DataFrame, ...]: 장내채권 평균단가조회 결과
    
    Example:
        >>> df1, df2, df3 = avg_unit(inqr_strt_dt="20250101", inqr_end_dt="20250131", pdno="KR2033022D33", prdt_type_cd="302", vrfc_kind_cd="00")
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
        logger.info("API 호출 시작: 장내채권 평균단가조회")
        result1, result2, result3 = avg_unit(
            inqr_strt_dt="20240101",  # 조회시작일자
            inqr_end_dt="20250630",  # 조회종료일자
            pdno="KR103502GA34",  # 상품번호
            prdt_type_cd="302",  # 상품유형코드
            vrfc_kind_cd="00",  # 검증종류코드
        )

        # 결과 확인
        results = [result1, result2, result3]
        if all(result is None or result.empty for result in results):
            logger.warning("조회된 데이터가 없습니다.")
            return

        # output1 결과 처리
        logger.info("=== output1 조회 ===")
        if not result1.empty:
            logger.info("사용 가능한 컬럼: %s", result1.columns.tolist())

            # 통합 컬럼명 한글 변환 (필요한 컬럼만 자동 매핑됨)
            result1 = result1.rename(columns=COLUMN_MAPPING)

            for col in NUMERIC_COLUMNS:
                if col in result1.columns:
                    result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

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

            for col in NUMERIC_COLUMNS:
                if col in result2.columns:
                    result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

            logger.info("output2 결과:")
            print(result2)
        else:
            logger.info("output2 데이터가 없습니다.")

        # output3 결과 처리
        logger.info("=== output3 조회 ===")
        if not result3.empty:
            logger.info("사용 가능한 컬럼: %s", result3.columns.tolist())

            # 통합 컬럼명 한글 변환 (필요한 컬럼만 자동 매핑됨)
            result3 = result3.rename(columns=COLUMN_MAPPING)

            for col in NUMERIC_COLUMNS:
                if col in result3.columns:
                    result3[col] = pd.to_numeric(result3[col], errors='coerce').round(2)

            logger.info("output3 결과:")
            print(result3)
        else:
            logger.info("output3 데이터가 없습니다.")


    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise


if __name__ == "__main__":
    main()
