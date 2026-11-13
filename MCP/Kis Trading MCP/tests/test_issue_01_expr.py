"""이슈 #1: `__expr__` dict 주입 → eval 임의 코드 실행 회귀 테스트 (오프라인).

KIS API·네트워크를 호출하지 않는다. `tools/base.py`만 스텁 import로 읽는다.
"""
import ast
import importlib.util
import sys
import textwrap
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

BASE_PATH = Path(__file__).resolve().parents[1] / "tools" / "base.py"


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
            setattr(mod, attr, type(attr, (), {}))
        sys.modules[name] = mod
    sys.modules["module.factory"].CONTEXT_REQUEST_ID = "req-id"
    spec = importlib.util.spec_from_file_location("mcp_base_issue01", BASE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mcp_base_issue01"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_serialize_accepts_scalars_and_valid_trenv(base):
    out = base.ApiExecutor._serialize_params_for_runner(
        {"a": "x", "b": 3, "c": 1.5, "d": True, "e": None,
         "cano": "ka._TRENV.my_acct"}
    )
    assert out["a"] == "x"
    assert out["cano"] == {"__expr__": "ka._TRENV.my_acct"}


def test_serialize_rejects_expr_injection_str(base):
    with pytest.raises(ValueError):
        base.ApiExecutor._serialize_params_for_runner(
            {"x": "ka._TRENV.my_app or 1"})
    with pytest.raises(ValueError):
        base.ApiExecutor._serialize_params_for_runner(
            {"x": "ka._TRENV.my_app or __import__('os').system('pwned')"})


def test_serialize_rejects_dict_expr(base):
    with pytest.raises(ValueError):
        base.ApiExecutor._serialize_params_for_runner(
            {"x": {"__expr__": "ka._TRENV.my_app or 1"}})


def test_serialize_rejects_nonscalar(base):
    for bad in (["a"], {"a": 1}, ("a",),  b"raw"):
        with pytest.raises(ValueError):
            base.ApiExecutor._serialize_params_for_runner({"x": bad})


def test_runner_template_removes_eval(base):
    src = base.API_RUNNER_TEMPLATE.replace("__FUNCTION_NAME__", "dummy_fn")
    tree = ast.parse(src)
    banned = {"eval", "exec", "compile", "__import__"}
    called = {n.func.id for n in ast.walk(tree)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert not (called & banned), called & banned
    assert "getattr(ka._TRENV" in src


def _run_template_loop(base, params):
    import re
    src = base.API_RUNNER_TEMPLATE
    start = src.index("_kwargs = {}")
    end = src.index("\n    try:", start)
    lines = src[start:end].splitlines()
    snippet = "\n".join(
        line[4:] if line.startswith("    ") else line for line in lines)
    ka = SimpleNamespace(
        _TRENV=SimpleNamespace(my_acct="ACCT123", my_app="APP123"))
    ns = {"re": re, "_mcp_cfg": {"env_dv": "demo", "params": params}, "ka": ka}
    exec(compile(snippet, "<runner>", "exec"), ns)  # noqa: S102 (테스트 대상 코드 실행)
    return ns["_kwargs"]


def test_runner_loop_rejects_injection(base):
    with pytest.raises(ValueError):
        _run_template_loop(
            base, {"x": {"__expr__": "ka._TRENV.my_app or 1"}})


def test_runner_loop_resolves_allowlisted_attr(base):
    kwargs = _run_template_loop(
        base, {"cano": {"__expr__": "ka._TRENV.my_acct"}, "n": "005930"})
    assert kwargs == {"cano": "ACCT123", "n": "005930"}


def test_child_env_drops_secrets(base, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MCP_ISSUE01_SENTINEL", "1")
    ex = base.ApiExecutor("probe")
    ex.venv_python = sys.executable
    temp_dir = tmp_path / "child"
    temp_dir.mkdir()
    (temp_dir / "api_code.py").write_text(
        "import os\n"
        "print('LEAKED' if 'MCP_ISSUE01_SENTINEL' in os.environ else 'MISSING')\n",
        encoding="utf-8",
    )
    assert "MCP_ISSUE01_SENTINEL" not in ex._minimal_child_env()
    result = ex._execute_code(str(temp_dir))
    assert result["success"] is True
    assert "MISSING" in result["output"]
    assert "LEAKED" not in result["output"]
