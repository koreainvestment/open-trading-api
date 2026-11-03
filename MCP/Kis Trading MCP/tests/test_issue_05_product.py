"""이슈 #5: 도구별 계좌상품코드(product) 전달 회귀 테스트 (오프라인)."""
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
BASE_PATH = TOOLS_DIR / "base.py"


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
    spec = importlib.util.spec_from_file_location("mcp_base_issue05", BASE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mcp_base_issue05"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_product_per_tool(base):
    assert base._resolve_product("domestic_stock") == "01"
    assert base._resolve_product("overseas_stock") == "01"
    assert base._resolve_product("domestic_bond") == "01"
    assert base._resolve_product("elw") == "01"
    assert base._resolve_product("etfetn") == "01"
    assert base._resolve_product("auth") == "01"
    assert base._resolve_product("domestic_futureoption") == "03"
    assert base._resolve_product("overseas_futureoption") == "08"
    assert base._resolve_product("unknown_tool") == "01"
    assert base._resolve_product("") == "01"


def _fake_api_file(tmp_path):
    src = ('def order(env_dv, cano, acnt_prdt_cd, pdno):\n'
           '    """docstring"""\n'
           '    pass\n')
    p = tmp_path / "api_code.py"
    p.write_text(src, encoding="utf-8")
    return str(p)


def test_modify_embeds_futures_product(base, tmp_path):
    out = base.ApiExecutor._modify_api_code(
        _fake_api_file(tmp_path), {"env_dv": "demo", "pdno": "1"},
        "order", "domestic_futureoption")
    payload = json.loads((tmp_path / "params.json").read_text(encoding="utf-8"))
    assert payload["product"] == "03"
    assert "__FUNCTION_NAME__" not in Path(out).read_text(encoding="utf-8")


def test_modify_embeds_stock_product(base, tmp_path):
    base.ApiExecutor._modify_api_code(
        _fake_api_file(tmp_path), {"env_dv": "demo", "pdno": "1"},
        "inquire_price", "domestic_stock")
    payload = json.loads((tmp_path / "params.json").read_text(encoding="utf-8"))
    assert payload["product"] == "01"


def _run_auth_block(base, env_dv, product):
    src = base.API_RUNNER_TEMPLATE
    start = src.index("    _env_dv = ")
    end = src.index("    _kwargs = {}")
    lines = src[start:end].splitlines()
    snippet = "\n".join(line[4:] if line.startswith("    ") else line for line in lines)
    calls = []
    ka = SimpleNamespace(auth=lambda *a: calls.append(a))
    ns = {"ka": ka, "_mcp_cfg": {"env_dv": env_dv, "product": product}}
    exec(compile(snippet, "<runner-auth>", "exec"), ns)  # noqa: S102
    return calls


def test_runner_auth_demo_futures(base):
    assert _run_auth_block(base, "demo", "03") == [("vps", "03")]


def test_runner_auth_real_overseas_futures(base):
    assert _run_auth_block(base, "real", "08") == [("prod", "08")]


def test_runner_auth_without_product(base):
    assert _run_auth_block(base, "demo", None) == [("vps",)]
    assert _run_auth_block(base, "real", None) == [()]
