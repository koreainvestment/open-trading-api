# -*- coding: utf-8 -*-
"""
Created on 2025-07-10

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from frgnmem_trade_trend import frgnmem_trade_trend

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 기본시세 > 회원사 실 시간 매매동향(틱)[국내주식-163]
##############################################################################################

# 통합 컬럼 매핑
COLUMN_MAPPING = {
    'total_seln_qty': '총매도수량',
    'total_shnu_qty': '총매수2수량',
    'bsop_hour': '영업시간',
    'hts_kor_isnm': 'HTS한글종목명',
    'stck_prpr': '주식현재가',
    'prdy_vrss': '전일대비',
    'prdy_vrss_sign': '전일대비부호',
    'cntg_vol': '체결거래량',
    'acml_ntby_qty': '누적순매수수량',
    'glob_ntby_qty': '외국계순매수수량',
    'frgn_ntby_qty_icdc': '외국인순매수수량증감'
}

NUMERIC_COLUMNS = []


def main():
    """
    [국내주식] 시세분석
    회원사 실 시간 매매동향(틱)[국내주식-163]

    회원사 실 시간 매매동향(틱) 테스트 함수
    
    Parameters:
        - fid_cond_scr_div_code (str): 화면분류코드 (20432(primary key))
        - fid_cond_mrkt_div_code (str): 조건시장구분코드 (J 고정입력)
        - fid_input_iscd (str): 종목코드 (ex. 005930(삼성전자)   ※ FID_INPUT_ISCD(종목코드) 혹은 FID_MRKT_CLS_CODE(시장구분코드) 둘 중 하나만 입력)
        - fid_input_iscd_2 (str): 회원사코드 (ex. 99999(전체)  ※ 회원사코드 (kis developers 포탈 사이트 포럼-> FAQ -> 종목정보 다운로드(국내) 참조))
        - fid_mrkt_cls_code (str): 시장구분코드 (A(전체),K(코스피), Q(코스닥), K2(코스피200), W(ELW)  ※ FID_INPUT_ISCD(종목코드) 혹은 FID_MRKT_CLS_CODE(시장구분코드) 둘 중 하나만 입력)
        - fid_vol_cnt (str): 거래량 (거래량 ~)

    Returns:
        - DataFrame: 회원사 실 시간 매매동향(틱) 결과
    
    Example:
        >>> df1, df2 = frgnmem_trade_trend(fid_cond_mrkt_div_code="J", fid_cond_scr_div_code="20432", fid_input_iscd="005930", fid_input_iscd_2="99999", fid_mrkt_cls_code="A", fid_vol_cnt="1000")
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
        result1, result2 = frgnmem_trade_trend(
            fid_cond_scr_div_code="20432",  # 화면분류코드
            fid_cond_mrkt_div_code="J",  # 조건시장구분코드
            fid_input_iscd="005930",  # 종목코드
            fid_input_iscd_2="99999",  # 회원사코드
            fid_mrkt_cls_code="A",  # 시장구분코드
            fid_vol_cnt="",  # 거래량
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


    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise


if __name__ == "__main__":
    main()
