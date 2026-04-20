"""strategy_builder 테스트 설정

kis_auth 모듈은 import 시 KIS API 설정 파일을 읽으므로,
테스트 환경에서는 mock으로 대체해야 합니다.
이 파일은 pytest가 테스트 수집 전에 실행하므로
모든 app 모듈 import보다 먼저 mock이 주입됩니다.
"""

import os
import sys
from unittest.mock import MagicMock

# strategy_builder 루트를 sys.path에 추가 (core, backend 등 import 가능)
_sb_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _sb_root not in sys.path:
    sys.path.insert(0, _sb_root)

# kis_auth mock 주입 (실제 KIS API 설정 파일 불필요)
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
