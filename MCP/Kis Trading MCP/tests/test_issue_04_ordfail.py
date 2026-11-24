"""이슈 #4: 주문 거절 success:true·15초 타임아웃·동기 블로킹 회귀 테스트 (오프라인)."""
import asyncio
import ast
import importlib.util
import json
import subprocess
import sys
import textwrap
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
BASE_PATH = TOOLS_DIR / "base.py"
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
    spec = importlib.util.spec_from_file_location("mcp_base_issue04", BASE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mcp_base_issue04"] = mod
    spec.loader.exec_module(mod)
    return mod


def _classify_snippet(base):
    src = base.API_RUNNER_TEMPLATE
    start = src.index("        _parts = ")
    end = src.index("        if isinstance(result, tuple):")
    lines = src[start:end].splitlines()
    return "\n".join(line[8:] if line.startswith(" " * 8) else line for line in lines)


def _run_snippet(base, result, is_order):
    import io
    from contextlib import redirect_stdout
    ns = {"result": result, "_mcp_cfg": {"params": {}, "is_order": is_order},
          "_json": json, "sys": sys}
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            exec(compile(_classify_snippet(base), "<runner>", "exec"), ns)  # noqa: S102
    except SystemExit as e:
        return e.code, buf.getvalue()
    return None, buf.getvalue()


class _FakeDF:
    empty = True

    def __init__(self, n):
        self._n = n

    def __len__(self):
        return self._n


def test_runner_rejects_bad_rt_cd(base):
    code, out = _run_snippet(base, {"rt_cd": "1", "msg1": "거절"}, False)
    assert code == 2
    assert json.loads(out)["ok"] is False


def test_runner_rejects_empty_order_result(base):
    code, out = _run_snippet(base, _FakeDF(0), True)
    assert code == 2
    assert "empty order result" in out


def test_runner_keeps_empty_inquiry_result(base):
    code, out = _run_snippet(base, _FakeDF(0), False)
    assert code is None


def test_runner_accepts_ok_result(base):
    code, _ = _run_snippet(base, {"rt_cd": "0", "output": {"a": 1}}, True)
    assert code is None


def test_order_timeout_is_unknown_not_retryable(base, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ex = base.ApiExecutor("probe")

    def _boom(*a, **k):
        raise subprocess.TimeoutExpired(cmd="x", timeout=120)

    monkeypatch.setattr(base.subprocess, "run", _boom)
    out = ex._execute_code(str(tmp_path), "order_cash")
    assert out["success"] is False
    assert out["order_state"] == "unknown"
    assert "ORDER_STATE_UNKNOWN" in out["error"]
    assert "재주문하지 말고" in out["error"]


def test_inquiry_timeout_keeps_old_message(base, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ex = base.ApiExecutor("probe")

    def _boom(*a, **k):
        raise subprocess.TimeoutExpired(cmd="x", timeout=15)

    monkeypatch.setattr(base.subprocess, "run", _boom)
    out = ex._execute_code(str(tmp_path), "inquire_price")
    assert out["success"] is False
    assert "order_state" not in out
    assert "실행 시간 초과" in out["error"]


def test_order_uses_longer_timeout(base, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ex = base.ApiExecutor("probe")
    seen = {}

    def _cap(*a, **k):
        seen.update(k)
        return subprocess.CompletedProcess(args=a, returncode=0, stdout="{}", stderr="")

    monkeypatch.setattr(base.subprocess, "run", _cap)
    ex._execute_code(str(tmp_path), "order_cash")
    assert seen["timeout"] == base.ORDER_TIMEOUT == 120
    ex._execute_code(str(tmp_path), "inquire_price")
    assert seen["timeout"] == base.DEFAULT_TIMEOUT == 15


def _fake_ctx():
    async def _info(*a, **k):
        pass

    async def _error(*a, **k):
        pass

    async def _get_state(*a, **k):
        return "t"

    return SimpleNamespace(info=_info, error=_error, get_state=_get_state)


def _make_tool(base, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg_dir = tmp_path / "configs"
    cfg_dir.mkdir(exist_ok=True)
    (cfg_dir / "probe_tool.json").write_text(
        '{"tool_info": {"introduce": "probe", "examples": []}, '
        '"apis": {"order_cash": {"name": "o"}}}',
        encoding="utf-8",
    )

    class ProbeTool(base.BaseTool):
        @property
        def tool_name(self):
            return "probe_tool"

    return ProbeTool()


def test_run_reports_execution_failure(base, tmp_path, monkeypatch):
    tool = _make_tool(base, tmp_path, monkeypatch)

    async def fake_run_api(self, ctx, api_type, params):
        return {"success": False, "error": "boom"}

    tool._run_api = fake_run_api.__get__(tool, type(tool))
    out = asyncio.run(tool._run(_fake_ctx(), "order_cash", {"pdno": "1"}))
    assert out["ok"] is False
    assert out["error"] == "boom"


def test_run_keeps_success(base, tmp_path, monkeypatch):
    tool = _make_tool(base, tmp_path, monkeypatch)

    async def fake_run_api(self, ctx, api_type, params):
        return {"success": True, "data": "x"}

    tool._run_api = fake_run_api.__get__(tool, type(tool))
    out = asyncio.run(tool._run(_fake_ctx(), "order_cash", {"pdno": "1"}))
    assert out == {"ok": True, "data": {"success": True, "data": "x"}}


def test_execute_api_uses_threads_and_real_cleanup(base, tmp_path, monkeypatch):
    assert "to_thread" in BASE_SRC
    monkeypatch.chdir(tmp_path)
    ex = base.ApiExecutor("probe")
    ex._download_api_code = lambda *a: str(tmp_path / "api_code.py")
    ex._modify_api_code = lambda *a: None
    ex._execute_code = lambda *a: {"success": False, "error": "runner boom"}
    out = asyncio.run(ex.execute_api(
        _fake_ctx(), "order_cash", {}, "https://example.invalid/x"))
    assert out["success"] is False
    assert out["cleanup_success"] is True
    assert list(tmp_path.glob("tmp/*")) == []


def test_modify_api_code_embeds_is_order(base, tmp_path):
    src = ('def order_cash(env_dv, cano, acnt_prdt_cd, pdno):\n'
           '    """docstring"""\n'
           '    pass\n')
    api_file = tmp_path / "api_code.py"
    api_file.write_text(src, encoding="utf-8")
    out = base.ApiExecutor._modify_api_code(
        str(api_file), {"env_dv": "demo", "pdno": "1"}, "order_cash")
    payload = json.loads((tmp_path / "params.json").read_text(encoding="utf-8"))
    assert payload["is_order"] is True
    assert payload["env_dv"] == "demo"
    body = Path(out).read_text(encoding="utf-8")
    assert "__FUNCTION_NAME__" not in body
    assert "def order_cash" in body
