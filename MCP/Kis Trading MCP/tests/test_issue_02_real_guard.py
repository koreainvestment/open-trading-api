"""이슈 #2: 실전 주문 확인 게이트·읽기전용·허용목록·어노테이션 회귀 테스트 (오프라인)."""
import ast
import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

BASE_PATH = Path(__file__).resolve().parents[1] / "tools" / "base.py"


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
    for name, attrs in stub_attrs.items():
        mod = ModuleType(name)
        for attr in attrs:
            setattr(mod, attr, type(attr, (_AnyInit,), {}))
        sys.modules[name] = mod
    sys.modules["module.factory"].CONTEXT_REQUEST_ID = "req-id"
    spec = importlib.util.spec_from_file_location("mcp_base_issue02", BASE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mcp_base_issue02"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_order_classifier(base):
    is_order = base.BaseTool._is_order_api
    for t in ("order", "order_cash", "order_credit", "order_rvsecncl",
              "order_resv", "order_resv_ccnl", "order_resv_rvsecncl",
              "daytime_order", "daytime_order_rvsecncl", "buy", "sell"):
        assert is_order(t), t
    for t in ("inquire_price", "inquire_psbl_order", "inquire_daily_order",
              "order_resv_list", "algo_ordno", "foreign_margin",
              "find_stock_code", "find_api_detail"):
        assert not is_order(t), t


def test_real_order_blocked_without_optin(base):
    err = base.BaseTool._check_execution_policy(
        "order_cash", {"env_dv": "real"}, env={})
    assert err is not None and "REAL_ORDER_BLOCKED" in err


def test_real_order_allowed_with_optin(base):
    assert base.BaseTool._check_execution_policy(
        "order_cash", {"env_dv": "real"},
        env={"MCP_ALLOW_REAL_ORDERS": "1"}) is None


def test_demo_order_needs_no_optin(base):
    assert base.BaseTool._check_execution_policy(
        "order_cash", {"env_dv": "demo"}, env={}) is None
    assert base.BaseTool._check_execution_policy(
        "order_cash", {}, env={}) is None


def test_allowlist(base):
    env = {"MCP_ALLOWED_APIS": "inquire_price, order_cash"}
    assert base.BaseTool._check_execution_policy(
        "inquire_price", {}, env=env) is None
    err = base.BaseTool._check_execution_policy("order", {}, env=env)
    assert err is not None and "API_ALLOWLIST_BLOCKED" in err


def _fake_self(base, config):
    return SimpleNamespace(
        config=config, _is_order_api=base.BaseTool._is_order_api)


def test_annotations_mark_destructive_tools(base):
    destructive = base.BaseTool._tool_annotations(
        _fake_self(base, {"apis": {"order_cash": {}, "inquire_price": {}}}))
    assert destructive["destructiveHint"] is True
    assert destructive["readOnlyHint"] is False
    readonly = base.BaseTool._tool_annotations(
        _fake_self(base, {"apis": {"inquire_price": {}}}))
    assert readonly["destructiveHint"] is False
    assert readonly["readOnlyHint"] is True


def test_read_only_blocks_orders_but_not_quotes(base):
    assert "READ_ONLY_MODE" in base.BaseTool._check_execution_policy(
        "order_cash", {"env_dv": "demo"}, env={"MCP_READ_ONLY": "1"})
    assert base.BaseTool._check_execution_policy(
        "inquire_price", {}, env={"MCP_READ_ONLY": "1"}) is None


def _make_tool(base, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg_dir = tmp_path / "configs"
    cfg_dir.mkdir()
    (cfg_dir / "probe_tool.json").write_text(
        '{"tool_info": {"introduce": "probe", "examples": []}, '
        '"apis": {"order_cash": {"name": "o"}, "inquire_price": {"name": "q"}}}',
        encoding="utf-8",
    )

    class ProbeTool(base.BaseTool):
        @property
        def tool_name(self):
            return "probe_tool"

    return ProbeTool()


def test_register_passes_annotations(base, tmp_path, monkeypatch):
    tool = _make_tool(base, tmp_path, monkeypatch)
    captured = {}

    class FakeMCP:
        def tool(self, fn, **kwargs):
            captured.update(kwargs)
            return fn

    tool.register(FakeMCP())
    assert captured["name"] == "probe_tool"
    assert captured["annotations"]["destructiveHint"] is True
    assert "MCP_ALLOW_REAL_ORDERS" in captured["description"]


def test_run_calls_policy_gate(base):
    tree = ast.parse(BASE_PATH.read_text(encoding="utf-8"))
    run = next(n for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
               and n.name == "_run")
    names = set()
    for n in ast.walk(run):
        if isinstance(n, ast.Attribute):
            names.add(n.attr)
        elif isinstance(n, ast.Name):
            names.add(n.id)
    assert "_check_execution_policy" in names
