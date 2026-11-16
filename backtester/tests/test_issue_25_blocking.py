"""이슈 #25: async 블로킹 호출·컨테이너 정리·임시파일·폴링 모드 회귀 테스트 (오프라인)."""
import asyncio
import ast
import importlib.util
import subprocess
import sys
import time
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

HERE = Path(__file__).resolve().parent.parent
REPO_ROOT = HERE.parent
STRAT_DIR = REPO_ROOT / "strategy_builder"


def _stub_kis_auth(monkeypatch, tmp_path):
    ka = ModuleType("kis_auth")
    ka._cfg = {}
    ka.auth = lambda *a, **k: None
    ka.is_paper_trading = lambda: True
    ka.getTREnv = lambda: SimpleNamespace(my_url="https://x")
    ka.read_token = lambda *a: None
    monkeypatch.setitem(sys.modules, "kis_auth", ka)
    monkeypatch.setenv("HOME", str(tmp_path))
    return ka


@pytest.fixture()
def rt(monkeypatch, tmp_path):
    _stub_kis_auth(monkeypatch, tmp_path)
    monkeypatch.syspath_prepend(str(HERE))
    monkeypatch.delitem(sys.modules, "backend.routes.backtest", raising=False)
    import backend.routes.backtest as rt
    return rt


def _patch_providers(monkeypatch, get_history):
    import kis_backtest.providers.kis.auth as auth_mod
    import kis_backtest.providers.kis.data as data_mod
    monkeypatch.setattr(auth_mod.KISAuth, "from_env",
                        staticmethod(lambda *a, **k: object()))
    monkeypatch.setattr(data_mod.KISDataProvider, "get_history", get_history)
    return auth_mod, data_mod


def test_prepare_market_data_does_not_block_loop(rt, monkeypatch, tmp_path):
    def blocking_get_history(self, symbol, s, e):
        time.sleep(2)
        return []

    _patch_providers(monkeypatch, blocking_get_history)

    async def main():
        task = asyncio.create_task(rt.prepare_market_data(
            symbols=["005930"], start_date="2024-01-01",
            end_date="2024-01-31", workspace=tmp_path / "ws"))
        t0 = time.monotonic()
        await asyncio.sleep(0.2)
        tick = time.monotonic() - t0
        out = await task
        return tick, out

    tick, out = asyncio.run(main())
    assert tick < 1.0
    assert out["downloaded"] == [] and len(out["errors"]) == 1


def test_sync_bodies_have_no_await():
    src = (HERE / "backend" / "routes" / "backtest.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in (
                "_prepare_market_data_sync", "_prepare_benchmark_data_sync"):
            assert not any(isinstance(n, ast.Await) for n in ast.walk(node))
            assert isinstance(node, ast.FunctionDef)
    wrappers = {n.name for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)}
    assert "prepare_market_data" in wrappers
    assert "prepare_benchmark_data" in wrappers
    assert "to_thread" in src


def _load_executor(monkeypatch):
    monkeypatch.syspath_prepend(str(HERE))
    sys.modules.pop("kis_backtest.lean.executor", None)
    import kis_backtest.lean.executor as mod
    return mod


@pytest.fixture()
def execmod(monkeypatch, tmp_path):
    _stub_kis_auth(monkeypatch, tmp_path)
    return _load_executor(monkeypatch)


def _project(tmp_path):
    proj_dir = tmp_path / "ws" / "runs" / "proj"
    proj_dir.mkdir(parents=True)
    data_dir = tmp_path / "ws" / "data" / "symbol-properties"
    data_dir.mkdir(parents=True)
    (data_dir / "symbol-properties-database.csv").write_text("x\n", encoding="utf-8")
    out_dir = tmp_path / "ws" / "out"
    return SimpleNamespace(run_id="bt_abc123", project_dir=proj_dir,
                           output_dir=out_dir), out_dir


def test_docker_cmd_isolated_and_named(execmod, monkeypatch, tmp_path):
    calls = []

    def fake_run(cmd, **k):
        calls.append((cmd, k))
        return subprocess.CompletedProcess(cmd, 0, stdout="{}", stderr="")

    monkeypatch.setattr(execmod.subprocess, "run", fake_run)
    proj, out = _project(tmp_path)
    run = execmod.LeanExecutor.run(proj)
    assert run.success is True
    cmd = calls[0][0]
    for flag in ("--network", "none", "--cap-drop", "ALL",
                 "--pids-limit", "--memory", "--cpus", "--name"):
        assert flag in cmd
    assert f"lean-{proj.run_id}" in cmd
    assert execmod.LEAN_IMAGE.startswith("quantconnect/lean@sha256:")


def test_timeout_cleans_container(execmod, monkeypatch, tmp_path):
    calls = []

    def fake_run(cmd, **k):
        calls.append(cmd)
        if len(calls) == 1:
            raise subprocess.TimeoutExpired(cmd, 600)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(execmod.subprocess, "run", fake_run)
    proj, out = _project(tmp_path)
    run = execmod.LeanExecutor.run(proj)
    assert run.success is False
    assert "타임아웃" in run.error
    assert calls[1][:3] == ["docker", "rm", "-f"]
    assert f"lean-{proj.run_id}" in calls[1]


def test_failure_returns_instead_of_raising(execmod, monkeypatch, tmp_path):
    def fake_run(cmd, **k):
        return subprocess.CompletedProcess(cmd, 1, stdout="ERR", stderr="")

    monkeypatch.setattr(execmod.subprocess, "run", fake_run)
    proj, out = _project(tmp_path)
    run = execmod.LeanExecutor.run(proj)
    assert run.success is False
    assert "exit code" in run.error


def test_export_temp_file_cleaned_up(monkeypatch, tmp_path):
    _stub_kis_auth(monkeypatch, tmp_path)
    monkeypatch.syspath_prepend(str(HERE))
    import backend.routes.files as files
    p = tmp_path / "x.kis.yaml"
    p.write_text("a: 1", encoding="utf-8")
    files._remove_temp_file(str(p))
    assert not p.exists()
    files._remove_temp_file(str(p))
    src = (HERE / "backend" / "routes" / "files.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    bg = [n for n in ast.walk(tree)
          if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
          and n.func.id == "FileResponse"
          and any(k.arg == "background" for k in n.keywords)]
    assert len(bg) == 2


def _load_manager(monkeypatch, tmp_path):
    _stub_kis_auth(monkeypatch, tmp_path)
    monkeypatch.syspath_prepend(str(STRAT_DIR))
    for m in ("core", "core.data_fetcher", "core.errors",
              "core.log_sanitize", "core.websocket_manager"):
        sys.modules.pop(m, None)
    import core.websocket_manager as mgr
    return mgr


def test_polling_uses_configured_mode(monkeypatch, tmp_path):
    mgr = _load_manager(monkeypatch, tmp_path)
    seen = []

    def fake_get_orderbook(stock_code, env_dv="real"):
        seen.append(env_dv)
        return {}

    monkeypatch.setattr(mgr.data_fetcher, "get_orderbook", fake_get_orderbook)

    async def go():
        m = mgr.OrderbookWebSocketManager()
        await m.start()
        ws = object()
        await m.subscribe_orderbook("005930", ws, env_dv="real")
        assert m._env_dv["005930"] == "real"
        t = asyncio.ensure_future(m._polling_loop("005930"))
        await asyncio.sleep(0.15)
        t.cancel()
        try:
            await t
        except asyncio.CancelledError:
            pass
        await m.unsubscribe_orderbook("005930", ws)
        assert "005930" not in m._env_dv
        await m.stop()
        return seen

    seen_modes = asyncio.run(go())
    assert seen_modes and all(v == "real" for v in seen_modes)
