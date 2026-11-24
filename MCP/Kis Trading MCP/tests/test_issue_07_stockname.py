"""이슈 #7: stock_name 오염·pdno 덮어쓰기·LIKE·KRX 따옴표 회귀 테스트 (오프라인)."""
import asyncio
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
BASE_PATH = TOOLS_DIR / "base.py"
DB_PATH = TOOLS_DIR.parent / "module" / "plugin" / "database.py"
BASE_SRC = BASE_PATH.read_text(encoding="utf-8")


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
    spec = importlib.util.spec_from_file_location("mcp_base_issue07", BASE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mcp_base_issue07"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def dbmod():
    sys.path.insert(0, str(TOOLS_DIR.parent))
    spec = importlib.util.spec_from_file_location("mcp_db_issue07", DB_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mcp_db_issue07"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_krx_default_has_no_quotes():
    assert "'\"KRX\"'" not in BASE_SRC
    assert "adjusted_params['excg_id_dvsn_cd'] = 'KRX'" in BASE_SRC


def _fake_api_file(tmp_path, sig):
    p = tmp_path / "api_code.py"
    p.write_text(f"def {sig}:\n    \"\"\"docstring\"\"\"\n    pass\n", encoding="utf-8")
    return str(p)


def test_modify_strips_internal_keys(base, tmp_path):
    out = base.ApiExecutor._modify_api_code(
        _fake_api_file(tmp_path, "inquire_price(env_dv, pdno)"),
        {"env_dv": "demo", "pdno": "1", "stock_name": "삼성전자",
         "_original_search_value": "삼성전자", "_resolved_stock_code": "005930"},
        "inquire_price", "domestic_stock")
    payload = json.loads((tmp_path / "params.json").read_text(encoding="utf-8"))
    assert payload["has_stock_name"] is True
    assert payload["params"]["pdno"] == "1"
    for k in payload["params"]:
        assert not k.startswith("_"), k
        assert k not in ("stock_name", "stock_name_kr", "korean_name", "company_name")


def test_modify_keeps_signature_stock_name(base, tmp_path):
    out = base.ApiExecutor._modify_api_code(
        _fake_api_file(tmp_path, "search(env_dv, stock_name)"),
        {"env_dv": "demo", "stock_name": "삼성전자"},
        "search", "domestic_stock")
    assert Path(out).read_text(encoding="utf-8")
    payload = json.loads((tmp_path / "params.json").read_text(encoding="utf-8"))
    assert payload["params"]["stock_name"] == "삼성전자"


def _fake_ctx():
    rec = {"info": [], "warning": []}

    async def _info(msg):
        rec["info"].append(msg)

    async def _warning(msg):
        rec["warning"].append(msg)

    async def _error(msg):
        rec["error"] = msg

    return SimpleNamespace(info=_info, warning=_warning, error=_error), rec


def _run_process(base, params, code):
    import types

    async def _find(self, ctx, value):
        return {"found": True, "code": code}

    async def go():
        ctx, rec = _fake_ctx()
        fake_self = SimpleNamespace()
        fake_self._find_stock_by_name_or_code = types.MethodType(_find, fake_self)
        out = await base.BaseTool._process_stock_name(fake_self, ctx, dict(params))
        return out, rec

    return asyncio.run(go())


def test_pdno_conflict_keeps_explicit_and_warns(base):
    out, rec = _run_process(base, {"stock_name": "삼성전자", "pdno": "000660"}, "005930")
    assert out["pdno"] == "000660"
    assert any("충돌" in w for w in rec["warning"])


def test_pdno_set_when_absent(base):
    out, rec = _run_process(base, {"stock_name": "삼성전자"}, "005930")
    assert out["pdno"] == "005930"


def test_list_supports_like(dbmod, tmp_path):
    from sqlalchemy import Column, Integer, String
    from model.base import Base as ProjectBase

    class Stock(ProjectBase):
        __tablename__ = "stocks"
        __table_args__ = {"extend_existing": True}
        id = Column(Integer, primary_key=True)
        name = Column(String)
        code = Column(String)

    eng = dbmod.DatabaseEngine(str(tmp_path / "t.db"), [Stock])
    eng.insert(Stock(name="삼성전자", code="005930"))
    eng.insert(Stock(name="SK하이닉스", code="000660"))
    assert [r.code for r in eng.list(Stock, {"name": "삼성전자"})] == ["005930"]
    assert [r.code for r in eng.list(Stock, {"name": "삼성%"})] == ["005930"]
    assert [r.code for r in eng.list(Stock, {"name": "%전자"})] == ["005930"]
    assert [r.code for r in eng.list(Stock, {"name": "%하이%"})] == ["000660"]
    assert eng.list(Stock, {"name": "X%"}) == []
