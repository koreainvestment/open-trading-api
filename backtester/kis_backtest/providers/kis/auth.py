"""한국투자증권 인증 모듈 - kis_auth.py wrapper

backtester/kis_auth.py를 내부적으로 사용하여 기존 인터페이스 유지.
"""

import base64
import json as _json
import logging
import sys
from pathlib import Path
from typing import Dict, Optional

# backtester 루트를 sys.path에 추가하여 kis_auth import 가능하게
_root = Path(__file__).resolve().parents[3]  # kis_backtest/providers/kis/ → backtester/
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import kis_auth as ka

logger = logging.getLogger(__name__)


_SENSITIVE_PATTERNS = ("appkey", "appsecret", "app_key", "app_secret", "access_token")


def _sanitize_error(msg: str) -> str:
    """민감 패턴 포함 에러 메시지를 제네릭 메시지로 치환."""
    lower = msg.lower()
    if any(s in lower for s in _SENSITIVE_PATTERNS):
        return "API 호출 실패 (인증 오류)"
    return msg


# kis_auth의 APIResp wrapper (메서드명 호환성 제공)
class APIResp:
    """kis_auth.APIResp wrapper - 메서드명 호환성 제공
    
    kis_auth: isOK(), getOutput(), getOutput1(), getOutput2(), getErrorCode(), getErrorMessage()
    kis_backtest: is_ok(), get_output(), get_output1(), get_output2(), error_code, error_message
    """
    
    def __init__(self, ka_resp):
        """kis_auth.APIResp를 래핑"""
        self._ka_resp = ka_resp
    
    # kis_backtest 스타일 메서드 (snake_case)
    def is_ok(self) -> bool:
        """kis_auth.isOK() 호출"""
        return self._ka_resp.isOK()
    
    def get_output(self, key: str = "output"):
        """output 필드 가져오기 - kis_auth는 getBody()로 직접 접근"""
        body = self._ka_resp.getBody()
        if hasattr(body, key):
            return getattr(body, key)
        return None
    
    def get_output1(self):
        """output1 필드 가져오기"""
        body = self._ka_resp.getBody()
        if hasattr(body, 'output1'):
            return body.output1
        return None
    
    def get_output2(self):
        """output2 필드 가져오기"""
        body = self._ka_resp.getBody()
        if hasattr(body, 'output2'):
            return body.output2
        return None
    
    @property
    def error_code(self) -> str:
        """kis_auth.getErrorCode() 호출"""
        return self._ka_resp.getErrorCode()
    
    @property
    def error_message(self) -> str:
        """kis_auth.getErrorMessage() 호출 (민감 정보 필터링)"""
        return _sanitize_error(self._ka_resp.getErrorMessage())
    
    @property
    def status_code(self) -> int:
        """HTTP 상태 코드"""
        return getattr(self._ka_resp, '_rescode', 0)
    
    @property
    def header(self):
        """응답 헤더"""
        return self._ka_resp.getHeader()
    
    @property
    def body(self):
        """응답 본문"""
        return self._ka_resp.getBody()
    
    # kis_auth 스타일 메서드도 유지 (하위 호환)
    def isOK(self) -> bool:
        return self._ka_resp.isOK()
    
    def getOutput(self, key: str = "output"):
        return self.get_output(key)
    
    def getOutput1(self):
        return self.get_output1()
    
    def getOutput2(self):
        return self.get_output2()
    
    def getErrorCode(self) -> str:
        return self._ka_resp.getErrorCode()
    
    def getErrorMessage(self) -> str:
        return _sanitize_error(self._ka_resp.getErrorMessage())
    
    def getHeader(self):
        return self._ka_resp.getHeader()
    
    def getBody(self):
        return self._ka_resp.getBody()


class KISAuth:
    """한국투자증권 OAuth 인증 관리 - kis_auth.py wrapper
    
    기존 인터페이스를 유지하면서 내부적으로 kis_auth.py를 사용합니다.
    
    사용법:
        # 방법 1: 환경변수 대신 ~/KIS/config/kis_devlp.yaml 사용
        auth = KISAuth.from_env()
        
        # 방법 2: 직접 지정
        auth = KISAuth(
            app_key="...",
            app_secret="...",
            account_no="12345678",  # example
            is_paper=True
        )
    """
    
    def __init__(
        self,
        app_key: str,
        app_secret: str,
        account_no: str,
        is_paper: bool = True,
        prod_code: str = "01"
    ):
        """
        Args:
            app_key: 앱키 (ka.auth()가 config에서 직접 관리하므로 저장하지 않음)
            app_secret: 앱시크리트 (ka.auth()가 config에서 직접 관리하므로 저장하지 않음)
            account_no: 계좌번호 (8자리)
            is_paper: 모의투자 여부 (True: 모의, False: 실전)
            prod_code: 상품코드 (기본 "01")
        """
        # kis_auth 초기화
        svr = "vps" if is_paper else "prod"
        ka.auth(svr=svr, product=prod_code)

        # 기존 속성 유지 (호환성)
        # app_key, app_secret는 ka.auth()가 config에서 직접 관리하므로 저장하지 않음
        self.is_paper = is_paper
        self.account_no = account_no[:8]
        self.account_prod = prod_code

        # kis_auth에서 base_url 가져오기
        tr_env = ka.getTREnv()
        self.base_url = tr_env.my_url

        mode_str = "모의투자" if is_paper else "실전투자"
        logger.info(f"KIS Backtest 인증 초기화: {mode_str}, 계좌: {self.acct_masked}")

    @property
    def acct_masked(self) -> str:
        """계좌번호 마스킹 (앞 4자리만 표시)"""
        if len(self.account_no) >= 4:
            return self.account_no[:4] + "****"
        return "****"
    
    @classmethod
    def _detect_mode_from_token(cls) -> Optional[str]:
        """JWT jti와 config의 my_app/paper_app 대조로 실제 모드 감지.

        토큰 원본은 보관하지 않음. 감지 실패 시 None 반환.
        """
        try:
            token = ka.read_token()
            if token is None:
                return None
            parts = token.split(".")
            if len(parts) != 3:
                return None
            payload_b64 = parts[1]
            payload_b64 += "=" * (4 - len(payload_b64) % 4)
            payload = _json.loads(base64.urlsafe_b64decode(payload_b64))
            jti = payload.get("jti", "")
            if not jti:
                return None
            cfg = ka.getEnv()
            if jti == cfg.get("my_app"):
                return "live"
            if jti == cfg.get("paper_app"):
                return "paper"
            return None
        except Exception:
            return None

    @classmethod
    def from_env(cls, mode: Optional[str] = None) -> "KISAuth":
        """~/KIS/config/kis_devlp.yaml 기반 초기화

        Args:
            mode: "live" 또는 "paper". None이면 JWT jti로 자동 감지, 실패 시 "paper" fallback

        설정 파일:
            ~/KIS/config/kis_devlp.yaml
            - my_app, my_sec, my_acct_stock (실전)
            - paper_app, paper_sec, my_paper_stock (모의)

        Returns:
            KISAuth 인스턴스
        """
        # mode 미지정 시 JWT jti로 자동 감지, 실패 시 "paper" fallback
        if mode is None:
            mode = cls._detect_mode_from_token() or "paper"

        # kis_auth 설정 읽기
        env = ka.getEnv()
        
        is_paper = mode != "live"
        
        # 실전/모의에 따라 설정 읽기
        if is_paper:
            app_key = env.get("paper_app", "")
            app_secret = env.get("paper_sec", "")
            account_no = env.get("my_paper_stock", "")
        else:
            app_key = env.get("my_app", "")
            app_secret = env.get("my_sec", "")
            account_no = env.get("my_acct_stock", "")
        
        prod_code = env.get("my_prod", "01")
        
        # 필수값 검증
        if not app_key or not app_secret or not account_no:
            raise ValueError(
                f"~/KIS/config/kis_devlp.yaml에 필수 설정이 없습니다.\n"
                f"모의투자: paper_app, paper_sec, my_paper_stock\n"
                f"실전투자: my_app, my_sec, my_acct_stock"
            )
        
        return cls(
            app_key=app_key,
            app_secret=app_secret,
            account_no=account_no,
            is_paper=is_paper,
            prod_code=prod_code
        )
    
    @property
    def is_authenticated(self) -> bool:
        """인증 상태 (kis_auth.auth() 성공 시 항상 True)"""
        return True
    
    def get(
        self,
        endpoint: str,
        params: Dict,
        tr_id: str,
        tr_cont: str = ""
    ) -> APIResp:
        """GET 요청 - kis_auth._url_fetch() 경유
        
        Args:
            endpoint: API 경로
            params: 쿼리 파라미터
            tr_id: 트랜잭션 ID
            tr_cont: 연속조회 키
        
        Returns:
            APIResp wrapper 객체
        """
        ka_resp = ka._url_fetch(endpoint, tr_id, tr_cont, params, postFlag=False)
        return APIResp(ka_resp)  # kis_auth.APIResp를 wrapper로 감싸기
    
    def post(
        self,
        endpoint: str,
        body: Dict,
        tr_id: str,
        tr_cont: str = ""
    ) -> APIResp:
        """POST 요청 - kis_auth._url_fetch() 경유
        
        Args:
            endpoint: API 경로
            body: 요청 본문
            tr_id: 트랜잭션 ID
            tr_cont: 연속조회 키
        
        Returns:
            APIResp wrapper 객체
        """
        ka_resp = ka._url_fetch(endpoint, tr_id, tr_cont, body, postFlag=True)
        return APIResp(ka_resp)  # kis_auth.APIResp를 wrapper로 감싸기
    
    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        body: Optional[Dict] = None,
        tr_id: str = "",
        tr_cont: str = ""
    ) -> APIResp:
        """인증된 API 요청 (범용 메서드)
        
        Args:
            method: HTTP 메서드 ("GET" or "POST")
            endpoint: API 경로
            params: 쿼리 파라미터 (GET용)
            body: 요청 본문 (POST용)
            tr_id: 트랜잭션 ID
            tr_cont: 연속조회 키
        
        Returns:
            kis_auth의 APIResp 객체
        """
        if method.upper() == "GET":
            return self.get(endpoint, params or {}, tr_id, tr_cont)
        elif method.upper() == "POST":
            return self.post(endpoint, body or {}, tr_id, tr_cont)
        else:
            raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
    
    def get_access_token(self) -> str:
        """액세스 토큰 반환
        
        Returns:
            kis_auth의 현재 토큰
        """
        tr_env = ka.getTREnv()
        return tr_env.my_token
    
    @staticmethod
    def smart_sleep(seconds: float = 0.1) -> None:
        """레이트 리밋 대응 슬립 - kis_auth.smart_sleep() 호출"""
        ka.smart_sleep()
