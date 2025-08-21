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
from auth_ws_token import auth_ws_token

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [인증] WebSocket 웹소켓 접속키 발급 테스트
##############################################################################################

# 통합 컬럼 매핑
COLUMN_MAPPING = {
    'code': '응답코드',
    'message': '응답메세지',
    'approval_key': '웹소켓접속키'
}

def main():
    """
    WebSocket 웹소켓 접속키 발급 테스트 함수
    
    Parameters:
        - grant_type (str): 권한부여 Type (client_credentials)
        - appkey (str): 고객 앱Key (한국투자증권 홈페이지에서 발급받은 appkey)
        - appsecret (str): 고객 앱Secret (한국투자증권 홈페이지에서 발급받은 appsecret)
        - env_dv (str): 환경구분 (real: 실전, demo: 모의)
        - token (str): 접근토큰 (OAuth 토큰이 필요한 API 경우 발급한 Access token)

    Returns:
        - pd.DataFrame: WebSocket 접속키 발급 결과
        
    Response Fields:
        - code: 응답코드 (HTTP 응답코드)
        - message: 응답메세지
    
    Example:
        >>> df = auth_ws_token(grant_type="client_credentials", appkey=trenv.my_app, appsecret=trenv.my_sec, env_dv="real")
    """
    try:
        # pandas 출력 옵션 설정
        pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
        pd.set_option('display.width', None)  # 출력 너비 제한 해제
        pd.set_option('display.max_rows', None)  # 모든 행 표시

        # OAuth 토큰 발급 (WebSocket 접속키 발급에 필요)
        logger.info("OAuth 토큰 발급 중...")
        ka.auth()  # 토큰 발급
        logger.info("OAuth 토큰 발급 완료")

        # 환경 설정에서 토큰, 앱키, 앱시크릿 가져오기
        trenv = ka.getTREnv()
        appkey = trenv.my_app
        appsecret = trenv.my_sec
        
        # 토큰 및 앱키가 설정되어 있는지 확인
        if not appkey or not appsecret:
            logger.error("앱키 또는 앱시크릿이 설정되지 않았습니다.")
            return

        # API 호출
        logger.info("WebSocket 웹소켓 접속키 발급 API 호출 시작")
        result = auth_ws_token(
            grant_type="client_credentials",
            appkey=appkey,
            appsecret=appsecret,
            env_dv="real",  # 실전 환경으로 설정 (필요시 "demo"로 변경)
        )

        # 결과 확인
        if result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return

        # 결과 처리
        logger.info("=== WebSocket 웹소켓 접속키 발급 결과 ===")
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
