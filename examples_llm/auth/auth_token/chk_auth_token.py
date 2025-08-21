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
from auth_token import auth_token

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [인증] OAuth 접근토큰 발급 테스트
##############################################################################################

# 통합 컬럼 매핑
COLUMN_MAPPING = {
    'access_token': '접근토큰',
    'token_type': '접근토큰유형',
    'expires_in': '접근토큰유효기간_초',
    'access_token_token_expired': '접근토큰유효기간_일시표시'
}

def main():
    """
    OAuth 접근토큰 발급 테스트 함수
    
    Parameters:
        - grant_type (str): 권한부여 Type (client_credentials)
        - appkey (str): 앱키 (한국투자증권 홈페이지에서 발급받은 appkey)
        - appsecret (str): 앱시크릿키 (한국투자증권 홈페이지에서 발급받은 appsecret)
        - env_dv (str): 환경구분 (real: 실전, demo: 모의)

    Returns:
        - pd.DataFrame: OAuth 토큰 발급 결과
        
    Response Fields:
        - access_token: 접근토큰 (OAuth 토큰이 필요한 API 경우 발급한 Access token)
        - token_type: 접근토큰유형 ("Bearer")
        - expires_in: 접근토큰 유효기간(초)
        - access_token_token_expired: 접근토큰 유효기간(일시표시)
    
    Example:
        >>> df = auth_token(grant_type="client_credentials", appkey=trenv.my_app, appsecret=trenv.my_sec, env_dv="real")
    """
    try:
        # pandas 출력 옵션 설정
        pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
        pd.set_option('display.width', None)  # 출력 너비 제한 해제
        pd.set_option('display.max_rows', None)  # 모든 행 표시

        # 환경 설정에서 앱키와 앱시크릿 가져오기
        config = ka.getEnv()
        
        # 실전투자용 앱키/앱시크릿 사용 (모의투자의 경우 paper_app, paper_sec 사용)
        appkey = config.get("my_app", "")
        appsecret = config.get("my_sec", "")
        
        # 앱키와 앱시크릿이 설정되어 있는지 확인
        if not appkey or not appsecret:
            logger.error("앱키 또는 앱시크릿이 설정되지 않았습니다. kis_devlp.yaml 파일을 확인해주세요.")
            logger.info("필요한 설정: my_app (앱키), my_sec (앱시크릿)")
            return

        # API 호출
        logger.info("OAuth 접근토큰 발급 API 호출 시작")
        result = auth_token(
            grant_type="client_credentials",
            appkey=appkey,
            appsecret=appsecret,
            env_dv="real"  # 실전 환경으로 설정 (필요시 "demo"로 변경)
        )

        # 결과 확인
        if result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return

        # 결과 처리
        logger.info("=== OAuth 접근토큰 발급 결과 ===")
        logger.info("사용 가능한 컬럼: %s", result.columns.tolist())

        # 통합 컬럼명 한글 변환 (필요한 컬럼만 자동 매핑됨)
        result = result.rename(columns=COLUMN_MAPPING)


        logger.info("결과:")
        print(result)

    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise


if __name__ == "__main__":
    main()
