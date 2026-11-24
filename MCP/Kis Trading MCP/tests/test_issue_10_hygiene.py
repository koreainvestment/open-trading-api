"""이슈 #10: 재현성·위생 모음 회귀 테스트 (오프라인)."""
import ast
import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

MCP_DIR = Path(__file__).resolve().parents[1]
TOOLS_DIR = MCP_DIR / "tools"
PLUGIN_DIR = MCP_DIR / "module" / "plugin"
AUTH_PATH = MCP_DIR / "module" / "mcp_auth.py"


def _stub_fastmcp():
    mapping = {
        "fastmcp": ["FastMCP"],
        "fastmcp.exceptions": ["ToolError"],
        "fastmcp.server": [],
        "fastmcp.server.middleware": ["Middleware", "MiddlewareContext"],
        "fastmcp.server.dependencies": ["get_http_headers"],
    }
    saved = {}
    for mod_name, attrs in mapping.items():
        saved[mod_name] = sys.modules.get(mod_name)
        mod = ModuleType(mod_name)
        for attr in attrs:
            if attr == "ToolError":
                setattr(mod, attr, type(attr, (Exception,), {}))
            else:
                setattr(mod, attr, type(attr, (), {}))
        sys.modules[mod_name] = mod
    return saved


def _unstub_fastmcp(saved):
    for mod_name, mod in saved.items():
        if mod is None:
            sys.modules.pop(mod_name, None)
        else:
            sys.modules[mod_name] = mod


@pytest.fixture()
def authmod(tmp_path):
    saved = _stub_fastmcp()
    sys.modules["fastmcp.server.dependencies"].get_http_headers = None
    spec = importlib.util.spec_from_file_location(
        "mcp_auth_issue10", AUTH_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mcp_auth_issue10"] = mod
    spec.loader.exec_module(mod)
    yield mod
    _unstub_fastmcp(saved)


def _load_master_file():
    for mod_name in ("module", "module.plugin", "module.plugin.database"):
        if mod_name not in sys.modules:
            stub = ModuleType(mod_name)
            if mod_name == "module.plugin.database":
                stub.Database = type("Database", (), {})
            sys.modules[mod_name] = stub
    sys.path.insert(0, str(MCP_DIR))
    spec = importlib.util.spec_from_file_location(
        "mcp_master_issue10", PLUGIN_DIR / "master_file.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mcp_master_issue10"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_lock_files_declared():
    import json
    assert (MCP_DIR / "uv.lock").stat().st_size > 0
    assert (MCP_DIR / ".python-version").exists()
    files = json.loads((MCP_DIR / "package.json").read_text(encoding="utf-8"))["files"]
    assert "uv.lock" in files
    assert ".python-version" in files


def test_token_compare_is_constant_time(authmod):
    src = AUTH_PATH.read_text(encoding="utf-8")
    assert "compare_digest" in src
    assert '== f"Bearer' not in src
    assert "api_key == self.access_token" not in src


def test_token_auth_accepts_and_rejects(authmod):
    import asyncio

    async def go(headers):
        authmod.get_http_headers = lambda **k: headers

        async def call_next(ctx):
            return "OK"

        mw = authmod.McpAuthMiddleware("sse", "tok")
        return await mw.on_request(SimpleNamespace(), call_next)

    assert asyncio.run(go({"authorization": "Bearer tok"})) == "OK"
    assert asyncio.run(go({"x-api-key": "tok"})) == "OK"
    with pytest.raises(authmod.ToolError):
        asyncio.run(go({"authorization": "Bearer wrong"}))


def test_no_global_tls_override():
    src = (PLUGIN_DIR / "master_file.py").read_text(encoding="utf-8")
    assert "ssl._create_default_https_context" not in src
    assert "import ssl" not in src


def test_no_upfront_clear():
    src = (PLUGIN_DIR / "master_file.py").read_text(encoding="utf-8")
    assert "__clear_category_tables" not in src
    assert "__clear_category_csv_files" not in src


def _engine(dbmod, tmp_path, name="t.db"):
    from model.base import Base as ProjectBase
    from sqlalchemy import Column, Integer, String

    class Row(ProjectBase):
        __tablename__ = "rows"
        __table_args__ = {"extend_existing": True}
        id = Column(Integer, primary_key=True)
        name = Column(String)

    eng = dbmod.DatabaseEngine(str(tmp_path / name), [Row])
    return eng, Row


def test_bulk_replace_is_atomic(tmp_path):
    sys.path.insert(0, str(MCP_DIR))
    spec = importlib.util.spec_from_file_location(
        "mcp_db_issue10", PLUGIN_DIR / "database.py")
    dbmod = importlib.util.module_from_spec(spec)
    sys.modules["mcp_db_issue10"] = dbmod
    spec.loader.exec_module(dbmod)
    eng, Row = _engine(dbmod, tmp_path)
    eng.bulk_replace_master_data(Row, [{"name": "a"}, {"name": "b"}], "m")
    assert sorted(r.name for r in eng.list(Row, {})) == ["a", "b"]
    eng.bulk_replace_master_data(Row, [{"name": "c"}], "m")
    assert [r.name for r in eng.list(Row, {})] == ["c"]
    with pytest.raises(ValueError):
        eng.bulk_replace_master_data(Row, [], "m")
    assert [r.name for r in eng.list(Row, {})] == ["c"]


def test_empty_process_result_raises_and_keeps_data(tmp_path):
    import asyncio

    import pandas as pd

    mod = _load_master_file()

    async def fake_proc(self, temp_file, ctx):
        return pd.DataFrame()

    async def _dl(u, p):
        return True

    async def _info(*a, **k):
        pass

    async def _warning(*a, **k):
        pass

    async def _error(*a, **k):
        pass

    ctx = SimpleNamespace(info=_info, warning=_warning, error=_error)
    fake = SimpleNamespace(
        MASTER_FILE_PROCESS={"m": {"file": "http://example.invalid/x",
                                   "process": "fake_proc"}},
        master_dir=str(tmp_path),
        _MasterFileManager__download_file=_dl,
        _log=lambda *a: None,
        _MasterFileManager__convert_to_model_data=lambda df, m: [],
        _MasterFileManager__get_model_class=lambda m: None,
        db_engine=SimpleNamespace(
            bulk_replace_master_data=lambda **k: (_ for _ in ()).throw(
                AssertionError("must not write on empty result"))),
    )
    fake.fake_proc = fake_proc.__get__(fake, SimpleNamespace)
    meth = getattr(mod.MasterFileManager,
                   "_MasterFileManager__ensure_single_master_updated")
    with pytest.raises(Exception, match="비어있음"):
        asyncio.run(meth(fake, ctx, "m", False))
