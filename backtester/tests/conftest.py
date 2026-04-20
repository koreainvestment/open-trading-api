"""backtester 테스트 설정

kis_auth 모듈은 pycryptodome과 KIS 설정 파일에 의존하므로,
테스트 환경에서는 mock으로 대체합니다.
"""

import os
import sys
from unittest.mock import MagicMock

# backtester 루트를 sys.path에 추가
_bt_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _bt_root not in sys.path:
    sys.path.insert(0, _bt_root)

# kis_auth mock 주입
_mock_ka = MagicMock()
_mock_ka.auth.return_value = None
_mock_ka.read_token.return_value = None
_mock_ka.getTREnv.return_value = MagicMock(my_url="", my_app="", my_sec="")
_mock_ka._cfg = {"my_app": "test_app", "paper_app": "test_paper"}
sys.modules["kis_auth"] = _mock_ka

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)
