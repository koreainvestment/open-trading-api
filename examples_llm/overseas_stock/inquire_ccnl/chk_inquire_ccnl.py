"""
Created on 2025-06-30

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from inquire_ccnl import inquire_ccnl

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 주문체결내역 [v1_해외주식-007]
##############################################################################################

# 컬럼명 매핑 (한글 변환용)
COLUMN_MAPPING = {
    'ord_dt': '주문일자',
    'ord_gno_brno': '주문채번지점번호',
    'odno': '주문번호',
    'orgn_odno': '원주문번호',
    'sll_buy_dvsn_cd': '매도매수구분코드',
    'sll_buy_dvsn_cd_name': '매도매수구분코드명',
    'rvse_cncl_dvsn': '정정취소구분',
    'rvse_cncl_dvsn_name': '정정취소구분명',
    'pdno': '상품번호',
    'prdt_name': '상품명',
    'ft_ord_qty': 'FT주문수량',
    'ft_ord_unpr3': 'FT주문단가3',
    'ft_ccld_qty': 'FT체결수량',
    'ft_ccld_unpr3': 'FT체결단가3',
    'ft_ccld_amt3': 'FT체결금액3',
    'nccs_qty': '미체결수량',
    'prcs_stat_name': '처리상태명',
    'rjct_rson': '거부사유',
    'rjct_rson_name': '거부사유명',
    'ord_tmd': '주문시각',
    'tr_mket_name': '거래시장명',
    'tr_crcy_cd': '거래통화코드',
    'tr_natn': '거래국가',
    'ovrs_excg_cd': '해외거래소코드',
    'tr_natn_name': '거래국가명',
    'dmst_ord_dt': '국내주문일자',
    'thco_ord_tmd': '당사주문시각',
    'loan_type_cd': '대출유형코드',
    'loan_dt': '대출일자',
    'mdia_dvsn_name': '매체구분명',
    'usa_amk_exts_rqst_yn': '미국애프터마켓연장신청여부',
    'splt_buy_attr_name': '분할매수/매도속성명'
}

# 숫자형 컬럼 정의 (소수점 처리용)
NUMERIC_COLUMNS = []


def main():
    """
    [해외주식] 주문/계좌
    해외주식 주문체결내역[v1_해외주식-007]

    해외주식 주문체결내역 테스트 함수
    
    Parameters:
        - cano (str): 종합계좌번호 (계좌번호 체계(8-2)의 앞 8자리)
        - acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계(8-2)의 뒤 2자리)
        - pdno (str): 상품번호 (전종목일 경우 "%" 입력 ※ 모의투자계좌의 경우 ""(전체 조회)만 가능)
        - ord_strt_dt (str): 주문시작일자 (YYYYMMDD 형식 (현지시각 기준))
        - ord_end_dt (str): 주문종료일자 (YYYYMMDD 형식 (현지시각 기준))
        - sll_buy_dvsn (str): 매도매수구분 (00 : 전체  01 : 매도  02 : 매수 ※ 모의투자계좌의 경우 "00"(전체 조회)만 가능)
        - ccld_nccs_dvsn (str): 체결미체결구분 (00 : 전체  01 : 체결  02 : 미체결 ※ 모의투자계좌의 경우 "00"(전체 조회)만 가능)
        - ovrs_excg_cd (str): 해외거래소코드 (전종목일 경우 "%" 입력 NASD : 미국시장 전체(나스닥, 뉴욕, 아멕스) NYSE : 뉴욕 AMEX : 아멕스 SEHK : 홍콩  SHAA : 중국상해 SZAA : 중국심천 TKSE : 일본 HASE : 베트남 하노이 VNSE : 베트남 호치민 ※ 모의투자계좌의 경우 ""(전체 조회)만 가능)
        - sort_sqn (str): 정렬순서 (DS : 정순 AS : 역순  ※ 모의투자계좌의 경우 정렬순서 사용불가(Default : DS(정순)))
        - ord_dt (str): 주문일자 ("" (Null 값 설정))
        - ord_gno_brno (str): 주문채번지점번호 ("" (Null 값 설정))
        - odno (str): 주문번호 ("" (Null 값 설정) ※ 주문번호로 검색 불가능합니다. 반드시 ""(Null 값 설정) 바랍니다.)
        - NK200 (str): 연속조회키200 (공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK200값 : 다음페이지 조회시(2번째부터))
        - FK200 (str): 연속조회검색조건200 (공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK200값 : 다음페이지 조회시(2번째부터))
        - env_dv (str): 실전모의구분 (real:실전, demo:모의)

    Returns:
        - DataFrame: 해외주식 주문체결내역 결과
    
    Example:
        >>> df = inquire_ccnl(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, pdno="%", ord_strt_dt="20250101", ord_end_dt="20250131", sll_buy_dvsn="00", ccld_nccs_dvsn="00", ovrs_excg_cd="NASD", sort_sqn="DS", ord_dt="", ord_gno_brno="", odno="", env_dv="real")  # 실전투자
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
            ka.auth(svr='vps')  # 모의투자용 토큰
        logger.info("토큰 발급 완료")

        trenv = ka.getTREnv()

        # API 호출
        logger.info("API 호출")
        result = inquire_ccnl(
            cano=trenv.my_acct,  # 종합계좌번호
            acnt_prdt_cd=trenv.my_prod,  # 계좌상품코드
            pdno="",  # 상품번호
            ord_strt_dt="20250601",  # 주문시작일자
            ord_end_dt="20250630",  # 주문종료일자
            sll_buy_dvsn="00",  # 매도매수구분
            ccld_nccs_dvsn="00",  # 체결미체결구분
            ovrs_excg_cd="NASD",  # 해외거래소코드
            sort_sqn="DS",  # 정렬순서
            env_dv="real",  # 실전모의구분
            ord_dt="",
            ord_gno_brno="",
            odno="",
        )

        if result is None:
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
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

        # 결과 출력
        logger.info("=== 해외주식 주문체결내역 결과 (%s) ===", "실전투자" if env_dv == "real" else "모의투자")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)

    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise


if __name__ == "__main__":
    main()
