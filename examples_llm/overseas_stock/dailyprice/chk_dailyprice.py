"""
Created on 2025-06-26

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from dailyprice import dailyprice

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 기본시세 > 해외주식 기간별시세[v1_해외주식-010]
##############################################################################################

COLUMN_MAPPING = {
    'rsym': '실시간조회종목코드',
    'zdiv': '소수점자리수',
    'nrec': '전일종가',
    'xymd': '일자(YYYYMMDD)',
    'clos': '종가',
    'sign': '대비기호',
    'diff': '대비',
    'rate': '등락율',
    'open': '시가',
    'high': '고가',
    'low': '저가',
    'tvol': '거래량',
    'tamt': '거래대금',
    'pbid': '매수호가',
    'vbid': '매수호가잔량',
    'pask': '매도호가',
    'vask': '매도호가잔량'
}
NUMERIC_COLUMNS = ['대비', '등락율', '시가', '고가', '저가', '거래량', '거래대금', '매수호가', '매도호가', '매수호가잔량', '매도호가잔량']

def main():
    """
    [해외주식] 기본시세
    해외주식 기간별시세[v1_해외주식-010]

    해외주식 기간별시세 테스트 함수
    
    Parameters:
        - auth (str): 사용자권한정보 ("" (Null 값 설정))
        - excd (str): 거래소코드 (HKS : 홍콩 NYS : 뉴욕 NAS : 나스닥 AMS : 아멕스 TSE : 도쿄 SHS : 상해 SZS : 심천 SHI : 상해지수 SZI : 심천지수 HSX : 호치민 HNX : 하노이)
        - symb (str): 종목코드 (종목코드 (ex. TSLA))
        - gubn (str): 일/주/월구분 (0 : 일 1 : 주 2 : 월)
        - bymd (str): 조회기준일자 (조회기준일자(YYYYMMDD) ※ 공란 설정 시, 기준일 오늘 날짜로 설정)
        - modp (str): 수정주가반영여부 (0 : 미반영 1 : 반영)
        - env_dv (str): 실전모의구분 (real:실전, demo:모의)

    Returns:
        - DataFrame: 해외주식 기간별시세 결과
    
    Example:
        >>> df1, df2 = dailyprice(auth="", excd="NAS", symb="TSLA", gubn="0", bymd="", modp="1", env_dv="real")  # 실전투자
        >>> df1, df2 = dailyprice(auth="", excd="NAS", symb="TSLA", gubn="0", bymd="", modp="1", env_dv="demo")  # 모의투자
    """
    try:
        # pandas 출력 옵션 설정
        pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
        pd.set_option('display.width', None)  # 출력 너비 제한 해제
        pd.set_option('display.max_rows', None)  # 모든 행 표시

        # 실전/모의투자 선택 (모의투자 지원 로직)
        env_dv = "real"  # "real": 실전투자, "demo": 모의투자
        logger.info("투자 환경: %s", "실전투자" if env_dv == "real" else "모의투자")

        # 토큰 발급 (모의투자 지원 로직)
        logger.info("토큰 발급 중...")
        if env_dv == "real":
            ka.auth(svr='prod')  # 실전투자용 토큰
        elif env_dv == "demo":
            ka.auth(svr='vps')   # 모의투자용 토큰
        logger.info("토큰 발급 완료")
        
        # API 호출
        logger.info("API 호출 시작: 해외주식 기간별시세 (%s)", "실전투자" if env_dv == "real" else "모의투자")
        result1, result2 = dailyprice(
            auth="",
            excd="NAS",
            symb="TSLA",
            gubn="2",
            bymd="",
            modp="1",
            env_dv=env_dv,
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
