"""이슈 #14: TradingState가 인증 실패를 조용히 넘기지 않고 모드를 대조한다.

실제 kis_auth 대신 가짜 모듈을 주입한다. KIS API 호출 없음.
"""

import os
import sys
import types
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent


def _install_ka_stub(monkeypatch, tmp_path, *, paper, url):
    ka = types.ModuleType("kis_auth")
    ka._cfg = {"vps": "https://openapivts.koreainvestment.com:29443",
               "prod": "https://openapi.koreainvestment.com:9443"}
    ka._calls = []
    ka.auth = lambda svr: ka._calls.append(svr)
    ka.isPaperTrading = lambda: paper
    ka.getTREnv = lambda: types.SimpleNamespace(my_url=url)
    ka.read_token = lambda *a: None
    ka.clear_saved_tokens = lambda: 1
    monkeypatch.setitem(sys.modules, "kis_auth", ka)
    monkeypatch.setenv("HOME", str(tmp_path))
    return ka


def _load_state(monkeypatch, tmp_path, *, paper, url):
    ka = _install_ka_stub(monkeypatch, tmp_path, paper=paper, url=url)
    monkeypatch.syspath_prepend(str(HERE))
    for m in ("backend.state", "backend"):
        sys.modules.pop(m, None)
    import backend.state as st  # noqa: E402
    return ka, st


@pytest.fixture()
def mods(tmp_path, monkeypatch):
    ka, st = _load_state(monkeypatch, tmp_path, paper=True,
                         url="https://openapivts.koreainvestment.com:29443")
    return ka, st


def test_authenticate_verifies_mode_match(mods):
    ka, st = mods
    ts = st.TradingState()
    assert ts.authenticate("vps") is True
    assert ts.is_authenticated is True


def test_authenticate_rejects_mode_mismatch(mods):
    ka, st = mods
    ts = st.TradingState()
    ka.isPaperTrading = lambda: False  # 실전 토큰인데 vps 요청
    with pytest.raises(RuntimeError):
        ts.authenticate("vps")
    assert ts.is_authenticated is False


def test_authenticate_rejects_url_mismatch(mods):
    ka, st = mods
    ts = st.TradingState()
    ka.getTREnv = lambda: types.SimpleNamespace(
        my_url="https://openapi.koreainvestment.com:9443")  # 실전 도메인
    with pytest.raises(RuntimeError):
        ts.authenticate("vps")
    assert ts.is_authenticated is False


def test_clear_token_file_uses_ka_helper(mods):
    ka, st = mods
    removed = []
    ka.clear_saved_tokens = lambda: removed.append(1) or 1
    ts = st.TradingState()
    ts._clear_token_file()
    assert removed == [1]


def test_restore_skips_live_session(mods, tmp_path, monkeypatch):
    """실전 토큰이 캐시돼 있어도 재시작 때 자동 복원하지 않는다."""
    ka, st = mods
    ka.read_token = lambda *a: "DUMMY.LIVE.TOKEN"
    monkeypatch.setattr(st.TradingState, "_detect_mode_from_token", lambda self: "prod")
    monkeypatch.setattr(st.TradingState, "_save_mode_file", lambda self, m: None)
    ts = st.TradingState()
    assert ts.is_authenticated is False


def test_restore_restores_paper_session(mods, tmp_path, monkeypatch):
    ka, st = mods
    ka.read_token = lambda *a: "DUMMY.PAPER.TOKEN"
    monkeypatch.setattr(st.TradingState, "_detect_mode_from_token", lambda self: "vps")
    monkeypatch.setattr(st.TradingState, "_save_mode_file", lambda self, m: None)
    monkeypatch.setattr(ka, "auth", lambda svr: None)
    monkeypatch.setattr(ka, "isPaperTrading", lambda: True)
    monkeypatch.setattr(ka, "getTREnv", lambda: types.SimpleNamespace(my_url="https://openapivts.koreainvestment.com:29443"))
    ts = st.TradingState()
    assert ts.is_authenticated is True
