"""이슈 #6: kis_devlp.yaml 덮어쓰기 방지·백업·0600 회귀 테스트 (오프라인)."""
import importlib.util
import os
import stat
import sys
from pathlib import Path
from types import ModuleType

import pytest
import yaml

KIS_PATH = Path(__file__).resolve().parents[1] / "module" / "plugin" / "kis.py"

TEMPLATE = 'my_app: "앱키"\nmy_sec: "앱키 시크릿"\nmy_htsid: "사용자 HTS ID"\n'


@pytest.fixture()
def kmod(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    for var in ("KIS_APP_KEY", "KIS_APP_SECRET", "KIS_PAPER_APP_KEY",
                "KIS_PAPER_APP_SECRET", "KIS_HTS_ID", "KIS_ACCT_STOCK",
                "KIS_ACCT_FUTURE", "KIS_PAPER_STOCK", "KIS_PAPER_FUTURE",
                "KIS_PROD_TYPE", "KIS_URL_REST", "KIS_URL_REST_PAPER",
                "KIS_URL_WS", "KIS_URL_WS_PAPER", "MCP_KIS_CONFIG_OVERWRITE"):
        monkeypatch.delenv(var, raising=False)
    spec = importlib.util.spec_from_file_location("mcp_kis_issue06", KIS_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mcp_kis_issue06"] = mod
    spec.loader.exec_module(mod)
    return mod, home / "KIS" / "config" / "kis_devlp.yaml"


class _FakeResp:
    def __init__(self, text=TEMPLATE):
        self.text = text

    def raise_for_status(self):
        pass


def _seed(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("OLD CONTENT", encoding="utf-8")


def test_existing_file_preserved_by_default(kmod, monkeypatch):
    mod, cfg = kmod
    _seed(cfg)

    def _no_network(*a, **k):
        raise AssertionError("network used")

    monkeypatch.setattr(mod.requests, "get", _no_network)
    assert mod.setup_kis_config() is True
    assert cfg.read_text(encoding="utf-8") == "OLD CONTENT"


def test_force_without_optin_preserves(kmod, monkeypatch):
    mod, cfg = kmod
    _seed(cfg)

    def _no_network(*a, **k):
        raise AssertionError("network used")

    monkeypatch.setattr(mod.requests, "get", _no_network)
    assert mod.setup_kis_config(force_update=True) is True
    assert cfg.read_text(encoding="utf-8") == "OLD CONTENT"


def test_optin_with_full_env_overwrites_with_backup_0600(kmod, monkeypatch):
    mod, cfg = kmod
    _seed(cfg)
    monkeypatch.setenv("MCP_KIS_CONFIG_OVERWRITE", "1")
    monkeypatch.setenv("KIS_APP_KEY", "AK123")
    monkeypatch.setenv("KIS_APP_SECRET", "AS456")
    monkeypatch.setattr(mod.requests, "get", lambda *a, **k: _FakeResp())
    assert mod.setup_kis_config(force_update=True) is True
    assert Path(str(cfg) + ".bak").read_text(encoding="utf-8") == "OLD CONTENT"
    assert stat.S_IMODE(os.stat(cfg).st_mode) == 0o600
    body = cfg.read_text(encoding="utf-8")
    assert "AK123" in body and "AS456" in body
    assert "OLD CONTENT" not in body
    leftovers = [f for f in os.listdir(cfg.parent) if f.startswith(".kis_devlp_")]
    assert leftovers == []


def test_optin_without_env_preserves(kmod, monkeypatch):
    mod, cfg = kmod
    _seed(cfg)
    monkeypatch.setenv("MCP_KIS_CONFIG_OVERWRITE", "1")
    monkeypatch.setattr(mod.requests, "get", lambda *a, **k: _FakeResp())
    assert mod.setup_kis_config(force_update=True) is False
    assert cfg.read_text(encoding="utf-8") == "OLD CONTENT"
    assert not Path(str(cfg) + ".bak").exists()


def test_first_run_without_env_bootstraps_0600(kmod, monkeypatch):
    mod, cfg = kmod
    monkeypatch.setattr(mod.requests, "get", lambda *a, **k: _FakeResp())
    assert mod.setup_kis_config() is True
    assert cfg.is_file()
    assert stat.S_IMODE(os.stat(cfg).st_mode) == 0o600


def test_download_failure_creates_nothing(kmod, monkeypatch):
    mod, cfg = kmod

    def _boom(*a, **k):
        raise ConnectionError("down")

    monkeypatch.setattr(mod.requests, "get", _boom)
    assert mod.setup_kis_config() is False
    assert not cfg.exists()


def test_fallback_escapes_quotes(kmod, monkeypatch):
    mod, cfg = kmod
    monkeypatch.setenv("MCP_KIS_CONFIG_OVERWRITE", "1")
    monkeypatch.setenv("KIS_APP_KEY", 'a"b\\c')
    monkeypatch.setenv("KIS_APP_SECRET", "s")
    monkeypatch.setattr(mod.requests, "get", lambda *a, **k: _FakeResp())

    def _parse_fail(*a, **k):
        raise yaml.YAMLError("bad yaml")

    monkeypatch.setattr(mod.yaml, "safe_load", _parse_fail)
    assert mod.setup_kis_config(force_update=True) is True
    body = cfg.read_text(encoding="utf-8")
    assert 'my_app: "a\\"b\\\\c"' in body


def test_yaml_dq_escapes(kmod):
    mod, _ = kmod
    assert mod._yaml_dq('a"b\\c') == 'a\\"b\\\\c'
