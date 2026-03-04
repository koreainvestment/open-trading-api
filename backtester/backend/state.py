"""트레이딩 상태 관리 모듈

Mode Switching Feature 구현:
- 모의(vps) / 실전(prod) 모드 전환
- 1분 쿨다운 제한
- 재시작 시 유효 토큰 자동 복원 (토큰 파일 보존)
"""
import base64
import json
import logging
import os
from datetime import datetime
from typing import Optional

import kis_auth as ka

logger = logging.getLogger(__name__)


class TradingState:
    """트레이딩 상태를 관리하는 싱글톤 클래스

    Attributes:
        MODE_SWITCH_COOLDOWN: 모드 전환 쿨다운 시간 (초)

    Properties:
        is_authenticated: 인증 상태 (_TRENV 실제 초기화 여부 포함)
        current_mode: 현재 모드 ("vps" 또는 "prod")
        cooldown_remaining: 모드 전환까지 남은 시간 (초)
    """

    MODE_SWITCH_COOLDOWN = 60  # 1분 쿨다운

    def __init__(self):
        self._authenticated = False
        self._current_mode = self._load_mode_file()  # 파일에서 복원 (기본값 "vps")
        self._last_mode_switch: Optional[datetime] = None

        # 재시작 시 유효 토큰이 있으면 자동 복원
        self._try_restore_auth()

    # ------------------------------------------------------------------
    # 모드 파일 헬퍼 (~KIS/config/KIS_MODE)
    # ------------------------------------------------------------------

    def _get_mode_file_path(self) -> str:
        """KIS_MODE 파일 경로 (~KIS/config/KIS_MODE)"""
        return os.path.join(os.path.expanduser("~"), "KIS", "config", "KIS_MODE")

    def _load_mode_file(self) -> str:
        """저장된 모드 파일 읽기. 없거나 잘못된 경우 기본값 'vps' 반환."""
        path = self._get_mode_file_path()
        try:
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    mode = f.read().strip()
                if mode in ("vps", "prod"):
                    return mode
        except OSError:
            pass
        return "vps"

    def _save_mode_file(self, mode: str) -> None:
        """인증 성공 후 현재 모드를 파일에 저장."""
        path = self._get_mode_file_path()
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(mode)
        except OSError as e:
            logger.warning(f"모드 파일 저장 실패: {e}")

    def _delete_mode_file(self) -> None:
        """로그아웃 시 모드 파일 삭제."""
        path = self._get_mode_file_path()
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError as e:
            logger.warning(f"모드 파일 삭제 실패: {e}")

    # ------------------------------------------------------------------
    # 재시작 시 자동 인증 복원
    # ------------------------------------------------------------------

    def _detect_mode_from_token(self) -> Optional[str]:
        """JWT jti와 config의 my_app/paper_app 대조로 실제 모드 감지.

        auth.py의 detect_mode()와 동일한 방식. 토큰 원본은 보관하지 않음.
        감지 실패 시 None 반환.
        """
        try:
            token = ka.read_token()
            if token is None:
                return None
            payload_b64 = token.split(".")[1]
            payload_b64 += "=" * (4 - len(payload_b64) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
            jti = payload.get("jti", "")
            if not jti:
                return None
            if jti == ka._cfg.get("my_app"):
                return "prod"
            if jti == ka._cfg.get("paper_app"):
                return "vps"
            return None
        except Exception:
            return None

    def _try_restore_auth(self) -> None:
        """유효한 토큰 파일이 있으면 ka.auth()로 _TRENV를 재설정한다.

        JWT jti로 실제 모드를 감지하여 KIS_MODE 파일 부재 시 모드 불일치 방지.
        실패해도 예외를 전파하지 않는다 — 복원 실패는 미인증 상태로 처리.
        """
        try:
            if ka.read_token() is None:
                return
            detected = self._detect_mode_from_token()
            mode = detected if detected else self._current_mode
            ka.auth(svr=mode)
            self._authenticated = True
            self._current_mode = mode
            self._save_mode_file(mode)
            logger.info(f"인증 자동 복원 완료 (mode={mode})")
        except Exception as e:
            logger.info(f"인증 자동 복원 실패 (미인증 상태로 시작): {e}")
            self._authenticated = False

    # ------------------------------------------------------------------
    # 토큰 파일 (모드 전환 시에만 삭제)
    # ------------------------------------------------------------------

    def _get_token_file_path(self) -> str:
        """오늘 날짜의 토큰 파일 경로"""
        return os.path.join(
            os.path.expanduser("~"), "KIS", "config",
            f"KIS{datetime.today().strftime('%Y%m%d')}"
        )

    def _clear_token_file(self):
        """오늘 날짜의 토큰 파일 삭제"""
        token_file = self._get_token_file_path()
        if os.path.exists(token_file):
            try:
                os.remove(token_file)
                logger.info(f"토큰 삭제: {token_file}")
            except OSError as e:
                logger.warning(f"토큰 삭제 실패: {e}")

    def _reload_config(self) -> None:
        """kis_devlp.yaml 변경사항을 ka._cfg에 반영한다.

        ka._cfg는 모듈 임포트 시 한 번만 로드되므로,
        yaml을 수정한 뒤 인증 시도 시 이 메서드로 재로드해야 반영된다.
        """
        import yaml as _yaml
        config_path = os.path.join(
            os.path.expanduser("~"), "KIS", "config", "kis_devlp.yaml"
        )
        try:
            with open(config_path, encoding="UTF-8") as f:
                new_cfg = _yaml.load(f, Loader=_yaml.FullLoader)
            ka._cfg.clear()
            ka._cfg.update(new_cfg)
        except Exception as e:
            logger.warning(f"설정 파일 재로드 실패: {e}")

    def authenticate(self, mode: str = "vps") -> bool:
        """KIS API 인증

        Args:
            mode: 트레이딩 모드 ("vps" 모의투자, "prod" 실전투자)

        Returns:
            인증 성공 여부

        Raises:
            Exception: 쿨다운 중 모드 전환 시도 시
        """
        switching_mode = self._authenticated and self._current_mode != mode

        if switching_mode:
            can_switch, remaining = self.can_switch_mode()
            if not can_switch:
                raise Exception(
                    f"모드 전환은 1분에 1회만 가능합니다. {remaining}초 후 다시 시도하세요."
                )
            self._clear_token_file()
            self._authenticated = False

        try:
            self._reload_config()
            ka.auth(svr=mode)
            self._authenticated = True
            self._current_mode = mode
            if switching_mode:
                self._last_mode_switch = datetime.now()  # 성공 시에만 쿨다운 적용
            self._save_mode_file(mode)
            return True
        except Exception as e:
            self._authenticated = False
            raise e

    def can_switch_mode(self) -> tuple[bool, int]:
        """모드 전환 가능 여부 및 남은 쿨다운 시간

        Returns:
            (전환 가능 여부, 남은 쿨다운 시간 초)
        """
        if self._last_mode_switch is None:
            return True, 0
        elapsed = (datetime.now() - self._last_mode_switch).total_seconds()
        remaining = max(0, int(self.MODE_SWITCH_COOLDOWN - elapsed))
        return remaining == 0, remaining

    def logout(self):
        """로그아웃 (토큰 삭제 및 상태 초기화)"""
        self._clear_token_file()
        self._delete_mode_file()
        self._authenticated = False

    @property
    def is_authenticated(self) -> bool:
        """인증 상태 — 메모리 플래그와 _TRENV 실제 초기화 여부를 함께 검증."""
        if not self._authenticated:
            return False
        trenv = ka.getTREnv()
        return hasattr(trenv, "my_url") and bool(trenv.my_url)

    @property
    def current_mode(self) -> str:
        """현재 트레이딩 모드"""
        return self._current_mode

    @property
    def mode_display(self) -> str:
        """모드 표시명"""
        return "모의투자" if self._current_mode == "vps" else "실전투자"

    @property
    def cooldown_remaining(self) -> int:
        """모드 전환까지 남은 쿨다운 시간 (초)"""
        _, remaining = self.can_switch_mode()
        return remaining

    def get_status(self) -> dict:
        """현재 상태 딕셔너리 반환

        다른 프로세스(strategy_builder 등)에서 KIS_MODE 파일이 변경된 경우
        자동으로 감지하여 인증 상태를 초기화한다 (재인증 필요).
        """
        file_mode = self._load_mode_file()
        if file_mode != self._current_mode:
            self._current_mode = file_mode
            self._authenticated = False  # 다른 프로세스가 모드 변경 → 재인증 필요

        can_switch, remaining = self.can_switch_mode()
        return {
            "authenticated": self.is_authenticated,
            "mode": self._current_mode,
            "mode_display": self.mode_display,
            "can_switch_mode": can_switch,
            "cooldown_remaining": remaining,
        }


# 싱글톤 인스턴스
trading_state = TradingState()
