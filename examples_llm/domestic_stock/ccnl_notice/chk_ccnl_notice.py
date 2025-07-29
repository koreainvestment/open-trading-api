"""
Created on 2025-07-08
@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from ccnl_notice import ccnl_notice

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 주식체결통보 [실시간-005]
##############################################################################################

COLUMN_MAPPING = {
    "CUST_ID": "고객 ID",
    "ACNT_NO": "계좌번호",
    "ODER_NO": "주문번호",
    "ODER_QTY": "주문수량",
    "SELN_BYOV_CLS": "매도매수구분",
    "RCTF_CLS": "접수구분",
    "ODER_KIND": "주문종류",
    "ODER_COND": "주문조건",
    "STCK_SHRN_ISCD": "종목코드",
    "CNTG_QTY": "체결수량",
    "CNTG_UNPR": "체결단가",
    "STCK_CNTG_HOUR": "주식체결시간",
    "RFUS_YN": "거부여부",
    "CNTG_YN": "체결여부",
    "ACPT_YN": "접수여부",
    "BRNC_NO": "지점번호",
    "ACNT_NO2": "계좌번호2",
    "ACNT_NAME": "계좌명",
    "ORD_COND_PRC": "호가조건가격",
    "ORD_EXG_GB": "주문거래소 구분",
    "POPUP_YN": "체결정보 표시",
    "FILLER": "필러",
    "CRDT_CLS": "신용거래구분",
    "CRDT_LOAN_DATE": "신용대출일자",
    "CNTG_ISNM40": "체결일자",
    "ODER_PRC": "주문가격"
}
NUMERIC_COLUMNS = ["주문수량", "체결수량", "체결단가", "호가조건가격", "주문가격"]


def main():
    """
    국내주식 실시간체결통보
    
    국내주식 실시간 체결통보 수신 시에 (1) 주문·정정·취소·거부 접수 통보 와 (2) 체결 통보 가 모두 수신됩니다.
(14번째 값(CNTG_YN;체결여부)가 2이면 체결통보, 1이면 주문·정정·취소·거부 접수 통보입니다.)

※ 모의투자는 H0STCNI9 로 변경하여 사용합니다.

[호출 데이터]
헤더와 바디 값을 합쳐 JSON 형태로 전송합니다.

[응답 데이터]
1. 정상 등록 여부 (JSON)
- JSON["body"]["msg1"] - 정상 응답 시, SUBSCRIBE SUCCESS
- JSON["body"]["output"]["iv"] - 실시간 결과 복호화에 필요한 AES256 IV (Initialize Vector)
- JSON["body"]["output"]["key"] - 실시간 결과 복호화에 필요한 AES256 Key

2. 실시간 결과 응답 ( | 로 구분되는 값)
- 암호화 유무 : 0 암호화 되지 않은 데이터 / 1 암호화된 데이터
- TR_ID : 등록한 tr_id
- 데이터 건수 : (ex. 001 데이터 건수를 참조하여 활용)
- 응답 데이터 : 아래 response 데이터 참조 ( ^로 구분됨)

체결 통보 응답 결과는 암호화되어 출력됩니다. AES256 KEY IV를 활용해 복호화하여 활용하세요. 자세한 예제는 [도구&gt;wikidocs]에 준비되어 있습니다.
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 인증 토큰 발급
    ka.auth()
    ka.auth_ws()
    trenv = ka.getTREnv()

    # 인증(auth_ws()) 이후에 선언
    kws = ka.KISWebSocket(api_url="/tryitout")

    # 조회
    kws.subscribe(request=ccnl_notice, data=[trenv.my_htsid])

    # 결과 표시
    def on_result(ws, tr_id: str, result: pd.DataFrame, data_map: dict):
        try:
            # 컬럼 매핑
            result.rename(columns=COLUMN_MAPPING, inplace=True)

            # 숫자형 컬럼 변환
            for col in NUMERIC_COLUMNS:
                if col in result.columns:
                    result[col] = pd.to_numeric(result[col], errors='coerce')

            logging.info("결과:")
            print(result)
        except Exception as e:
            logging.error(f"결과 처리 중 오류: {e}")
            logging.error(f"받은 데이터: {result}")

    kws.start(on_result=on_result)


if __name__ == "__main__":
    main()
