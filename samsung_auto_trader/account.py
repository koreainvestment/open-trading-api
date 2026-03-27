"""
계좌 정보 조회 - 잔액 및 보유 주식 정보를 가져옵니다.
"""

from typing import Dict, Optional
from logger import logger
from api_client import api_client
from auth import get_auth_token
import config
import os


class AccountInfo:
    """계좌 정보를 담는 클래스."""

    def __init__(self):
        self.cash_balance: Optional[int] = None
        self.holdings: Dict[str, int] = {}  # {주식코드: 수량}
        self.account_number: str = ""

    def __repr__(self) -> str:
        return f"AccountInfo(cash={self.cash_balance}, holdings={self.holdings})"


def get_account_info() -> Optional[AccountInfo]:
    """
    계좌 정보를 조회합니다 (잔액 및 보유 주식).
    
    Returns:
        AccountInfo 객체, 실패 시 None
    """
    try:
        token = get_auth_token()
        account_number = os.getenv('GH_ACCOUNT')

        if not account_number:
            logger.error("환경변수 GH_ACCOUNT를 설정해야 합니다")
            return None

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        params = {
            "CANO": account_number,  # 계좌번호
            "ACNT_PRDT_CD": "01",    # 계좌상품코드 (기본값)
            "INQR_DVSN_1": "0",
            "INQR_DVSN_2": "0",
            "CMA_EVLU_AMT_ICLD_YN": "Y",
            "OVRS_INCL_YN": "N",
            "EVAL_AMT_DVSN_CD": "01",
            "SORT_SQN": "D",
            "QUERY_STR": "0",
            "REAL_CPRI_DVSN_CD": "01",
            "TR_CRCY_CODE": "USD",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }

        logger.debug(f"계좌정보 조회: {account_number}")
        response = api_client.get(
            config.HOLDINGS_ENDPOINT,
            headers=headers,
            params=params
        )

        account_info = AccountInfo()
        account_info.account_number = account_number

        # 응답에서 현금 잔액 추출
        # NOTE: 정확한 필드명은 API 응답 구조에 따라 조정 필요
        output = response.get('output1', {})
        cash = output.get('scts_evlu_amt')
        if cash:
            account_info.cash_balance = int(cash)

        # 응답에서 보유 주식 정보 추출
        # NOTE: 정확한 필드명은 API 응답 구조에 따라 조정 필요
        holdings_list = response.get('output2', [])
        for holding in holdings_list:
            stock_code = holding.get('pdno')  # 상품번호 (주식코드)
            quantity = holding.get('hldg_qty')  # 보유 수량
            
            if stock_code and quantity:
                account_info.holdings[stock_code] = int(quantity)

        logger.info(f"계좌 정보 조회 완료: {account_info}")
        return account_info

    except Exception as e:
        logger.error(f"계좌 정보 조회 실패: {e}")
        return None
