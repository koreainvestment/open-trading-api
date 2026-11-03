"""이슈 #3: main 추적 다운로드 고정 회귀 테스트 (오프라인).

네트워크를 호출하지 않는다. `tools/base.py`만 스텁 import로 읽는다.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
BASE_PATH = TOOLS_DIR / "base.py"
REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_base(name):
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
            setattr(mod, attr, type(attr, (object,), {"__init__": lambda self, *a, **k: None}))
        sys.modules[mod_name] = mod
    sys.modules["module.factory"].CONTEXT_REQUEST_ID = "req-id"
    spec = importlib.util.spec_from_file_location(name, BASE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def base():
    return _load_base("mcp_base_issue03")


def _expected_raw_url(github_url, api_type, ref):
    raw = github_url.replace("/tree/", "/").replace("github.com", "raw.githubusercontent.com")
    return raw.replace("/main/", f"/{ref}/", 1) + f"/{api_type}.py"


def test_bundled_kis_auth_matches_fork_copy(base):
    bundled = Path(base.BUNDLED_KIS_AUTH_FILE).read_bytes()
    fork_copy = (REPO_ROOT / "examples_llm" / "kis_auth.py").read_bytes()
    assert bundled == fork_copy


def test_default_ref_is_pinned_sha(base):
    assert base.PINNED_API_REF == "3a9be59a3ed8745720dc3aa9d584bdf3b7830362"
    assert base.ApiExecutor._api_code_ref() == base.PINNED_API_REF


def test_pinned_url_replaces_main(base):
    url = base.ApiExecutor._pinned_raw_url(
        "https://github.com/koreainvestment/open-trading-api/tree/main/examples_llm/domestic_stock/order_cash",
        "order_cash")
    assert url == ("https://raw.githubusercontent.com/koreainvestment/open-trading-api/"
                   "3a9be59a3ed8745720dc3aa9d584bdf3b7830362/"
                   "examples_llm/domestic_stock/order_cash/order_cash.py")
    assert "/main/" not in url


def test_manifest_covers_all_configured_apis(base):
    manifest = base.ApiExecutor._load_api_hashes()
    assert len(manifest) > 0
    missing = []
    for cfg_path in sorted((REPO_ROOT / "MCP" / "Kis Trading MCP" / "configs").glob("*.json")):
        for api, info in json.loads(cfg_path.read_text(encoding="utf-8"))["apis"].items():
            if info.get("github_url"):
                if _expected_raw_url(info["github_url"], api, base.PINNED_API_REF) not in manifest:
                    missing.append(f"{cfg_path.name}:{api}")
    assert missing == []


def _order_cash_source():
    cfg = json.loads((REPO_ROOT / "MCP" / "Kis Trading MCP" / "configs"
                      / "domestic_stock.json").read_text(encoding="utf-8"))
    return cfg["apis"]["order_cash"]["github_url"], "order_cash"


def test_tampered_body_rejected(base, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ex = base.ApiExecutor("probe")
    github_url, api_type = _order_cash_source()

    class FakeResp:
        status_code = 200
        content = b"tampered"
        text = "tampered"

        def raise_for_status(self):
            pass

    monkeypatch.setattr(base.requests, "get", lambda *a, **k: FakeResp())
    with pytest.raises(ValueError):
        ex._download_api_code(github_url, str(tmp_path), api_type)


def test_cache_hit_needs_no_network(base, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ex = base.ApiExecutor("probe")
    github_url, api_type = _order_cash_source()
    url = base.ApiExecutor._pinned_raw_url(github_url, api_type)
    body = b"# cached\n"
    monkeypatch.setitem(base.ApiExecutor._load_api_hashes(), url,
                        hashlib.sha256(body).hexdigest())

    class FakeResp:
        status_code = 200
        content = body
        text = "# cached"

        def raise_for_status(self):
            pass

    monkeypatch.setattr(base.requests, "get", lambda *a, **k: FakeResp())
    temp_dl = tmp_path / "dl"
    temp_dl.mkdir()
    p1 = ex._download_api_code(github_url, str(temp_dl), api_type)
    assert Path(p1).read_bytes() == body

    def _no_network(*a, **k):
        raise AssertionError("network used on cache hit")

    monkeypatch.setattr(base.requests, "get", _no_network)
    temp_hit = tmp_path / "hit"
    temp_hit.mkdir()
    p2 = ex._download_api_code(github_url, str(temp_hit), api_type)
    assert Path(p2).read_bytes() == body


def test_ensure_kis_auth_copies_bundle(base, tmp_path):
    ex = base.ApiExecutor("probe")
    assert ex._ensure_kis_auth(str(tmp_path)) is True
    assert (tmp_path / "kis_auth.py").read_bytes() == Path(base.BUNDLED_KIS_AUTH_FILE).read_bytes()
