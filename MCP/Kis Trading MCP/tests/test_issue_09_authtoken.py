"""이슈 #9: auth 도구 토큰 노출·식별자 로그 제거 회귀 테스트 (오프라인)."""
import importlib.util
import logging
import sys
from pathlib import Path
from types import ModuleType

import pytest

MCP_DIR = Path(__file__).resolve().parents[1]
TOOLS_DIR = MCP_DIR / "tools"
BASE_PATH = TOOLS_DIR / "base.py"
KIS_PATH = MCP_DIR / "module" / "plugin" / "kis.py"
TEMPLATE = 'my_app: "앱키"\nmy_sec: "앱키 시크릿"\nmy_htsid: "사용자 HTS ID"\n'


class _AnyInit:
    def __init__(self, *a, **k):
        pass


@pytest.fixture(scope="module")
def base():
    stub_attrs = {
        "fastmcp": ["FastMCP", "Context"],
        "module": [],
        "module.plugin": ["MasterFileManager"],
        "module.plugin.database": ["Database"],
        "module.factory": [],
    }
    for mod_name, attrs in stub_attrs.items():
        mod = ModuleType(mod_name)
        for attr in attrs:
            setattr(mod, attr, type(attr, (_AnyInit,), {}))
        sys.modules[mod_name] = mod
    sys.modules["module.factory"].CONTEXT_REQUEST_ID = "req-id"
    spec = importlib.util.spec_from_file_location("mcp_base_issue09", BASE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mcp_base_issue09"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_auth_tool_surface_removed():
    assert not (TOOLS_DIR / "auth.py").exists()
    assert not (MCP_DIR / "configs" / "auth.json").exists()
    assert "AuthTool" not in (MCP_DIR / "server.py").read_text(encoding="utf-8")
    assert "auth" not in (TOOLS_DIR / "__init__.py").read_text(encoding="utf-8")
    assert '"auth"' not in (MCP_DIR / "module" / "plugin" / "master_file.py").read_text(
        encoding="utf-8")


def test_dynamic_mapping_excludes_secrets(base):
    code = ("appsecret=ka.my_sec\nappkey=ka.my_app\n"
            "cano=ka.my_acct\ntok=ka.my_token\n")
    out = base.ApiExecutor._extract_trenv_params_from_example(code)
    assert "appsecret" not in out
    assert "tok" not in out
    assert out["appkey"] == "ka._TRENV.my_app"
    assert out["cano"] == "ka._TRENV.my_acct"


def _load_kis():
    spec = importlib.util.spec_from_file_location("mcp_kis_issue09", KIS_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mcp_kis_issue09"] = mod
    spec.loader.exec_module(mod)
    return mod


class _FakeResp:
    def __init__(self, text=TEMPLATE):
        self.text = text

    def raise_for_status(self):
        pass


def test_setup_logs_no_identifiers_or_secrets(tmp_path, monkeypatch, caplog):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("MCP_KIS_CONFIG_OVERWRITE", "1")
    monkeypatch.setenv("KIS_APP_KEY", "AK-SECRET-1")
    monkeypatch.setenv("KIS_APP_SECRET", "AS-SECRET-2")
    monkeypatch.setenv("KIS_HTS_ID", "HTS-SECRET-3")
    mod = _load_kis()
    monkeypatch.setattr(mod.requests, "get", lambda *a, **k: _FakeResp())
    with caplog.at_level(logging.INFO):
        assert mod.setup_kis_config(force_update=True) is True
    logs = "\n".join(r.getMessage() for r in caplog.records)
    assert "AK-SECRET-1" not in logs
    assert "AS-SECRET-2" not in logs
    assert "HTS-SECRET-3" not in logs
    body = (home / "KIS" / "config" / "kis_devlp.yaml").read_text(encoding="utf-8")
    assert "AK-SECRET-1" in body and "HTS-SECRET-3" in body
