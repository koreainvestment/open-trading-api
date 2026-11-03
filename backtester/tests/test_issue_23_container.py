"""Issue #23: container hardening / loader / report regression tests (offline, no docker)."""
import asyncio
import re
import sys
import types
from pathlib import Path

import pytest
from fastapi import HTTPException

HERE = Path(__file__).resolve().parent.parent
TEMPLATE = HERE / "kis_backtest" / "file" / "templates" / "sma_crossover.kis.yaml"


def _install_ka_stub(monkeypatch, tmp_path):
    ka = types.ModuleType("kis_auth")
    ka._cfg = {"vps": "https://openapivts.koreainvestment.com:29443",
               "prod": "https://openapi.koreainvestment.com:9443"}
    ka.auth = lambda svr: None
    ka.isPaperTrading = lambda: True
    ka.getTREnv = lambda: types.SimpleNamespace(my_url="https://x")
    ka.read_token = lambda *a: None
    ka.clear_saved_tokens = lambda: 1
    monkeypatch.setitem(sys.modules, "kis_auth", ka)
    monkeypatch.setenv("HOME", str(tmp_path))
    return ka


@pytest.fixture()
def rt(monkeypatch, tmp_path):
    _install_ka_stub(monkeypatch, tmp_path)
    monkeypatch.syspath_prepend(str(HERE))
    monkeypatch.delitem(sys.modules, "backend.routes.backtest", raising=False)
    import backend.routes.backtest as rt
    return rt


@pytest.fixture()
def loader(monkeypatch, tmp_path):
    _install_ka_stub(monkeypatch, tmp_path)
    monkeypatch.syspath_prepend(str(HERE))
    from kis_backtest.file.loader import StrategyFileLoader
    return StrategyFileLoader


def test_lean_image_pinned(monkeypatch, tmp_path):
    _install_ka_stub(monkeypatch, tmp_path)
    monkeypatch.syspath_prepend(str(HERE))
    from kis_backtest.lean.executor import LEAN_IMAGE
    assert re.match(r"^quantconnect/lean@sha256:[0-9a-f]{64}$", LEAN_IMAGE), LEAN_IMAGE


def test_docker_cmd_hardening_flags():
    src = (HERE / "kis_backtest" / "lean" / "executor.py").read_text(encoding="utf-8")
    for flag in ["--network", "none", "--memory", "4g", "--memory-swap",
                 "--cpus", "2.0", "--pids-limit", "512", "--cap-drop", "ALL",
                 "--user", "getuid"]:
        assert flag in src, f"missing docker flag: {flag}"
    # /Results stays rw (Lean needs it); mounts unchanged
    assert "/Results" in src


def _run_custom(rt, yaml_content):
    req = rt.CustomBacktestRequest(
        yaml_content=yaml_content,
        symbols=["005930"],
        start_date="2024-01-01",
        end_date="2024-02-01",
    )
    return asyncio.run(rt.run_custom_backtest(req))


def test_custom_backtest_local_path_no_echo(rt):
    # An existing local path must never be read or echoed back: it is treated
    # as YAML content and rejected with a generic 400.
    for bad in ("/etc/hostname", str(Path(__file__).resolve())):
        with pytest.raises(HTTPException) as e:
            _run_custom(rt, bad)
        assert e.value.status_code == 400
        assert bad not in str(e.value.detail)
def test_custom_backtest_invalid_yaml_no_echo(rt):
    bad = ":\n: bad: [unclosed"
    with pytest.raises(HTTPException) as e:
        _run_custom(rt, bad)
    assert e.value.status_code == 400
    assert bad not in str(e.value.detail)
    assert e.value.detail == "Invalid YAML"


def test_load_schema_from_string_applies_overrides(loader):
    if TEMPLATE.exists():
        content = TEMPLATE.read_text(encoding="utf-8")
        try:
            schema = loader.load_schema_from_string(content, param_overrides={"fast_period": 10})
        except ValueError:
            pytest.fail("minimal template from backtester examples failed to parse")
        fast = next(i for i in schema.indicators if (getattr(i, "alias", None) or getattr(i, "id", None)) == "fast")
        params = fast.params if isinstance(fast.params, dict) else fast.params.model_dump()
        assert params.get("period") == 10
    else:
        with pytest.raises(ValueError):
            loader.load_schema_from_string("not: [valid strategy")
