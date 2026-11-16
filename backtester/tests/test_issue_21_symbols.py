"""이슈 #21: symbols 경로 순회 방지 회귀 테스트 (오프라인, KIS 호출 없음)."""
import sys
import types
from datetime import datetime
from pathlib import Path

import pytest
from fastapi import HTTPException

HERE = Path(__file__).resolve().parent.parent


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


def _symbols(monkeypatch, tmp_path):
    _install_ka_stub(monkeypatch, tmp_path)
    monkeypatch.syspath_prepend(str(HERE))
    from kis_backtest.utils.symbols import invalid_symbols, is_valid_symbol
    return invalid_symbols, is_valid_symbol


def test_symbol_validation_rules(monkeypatch, tmp_path):
    invalid_symbols, is_valid_symbol = _symbols(monkeypatch, tmp_path)
    assert is_valid_symbol("005930")
    assert is_valid_symbol("AAPL")
    assert is_valid_symbol("000660")
    assert not is_valid_symbol("../x")
    assert not is_valid_symbol("a/b")
    assert not is_valid_symbol("")
    assert not is_valid_symbol("0123456789013")
    assert not is_valid_symbol("005930.csv")
    assert not is_valid_symbol("AB CD")
    assert not is_valid_symbol(None)
    assert invalid_symbols(["005930", "../x", ""]) == ["../x", ""]


def test_route_rejects_bad_symbols_400(rt):
    from backend.schemas.backtest import BacktestRequest
    req = BacktestRequest(strategy_id="rsi_oversold", symbols=["../x"],
                          start_date="2024-01-01", end_date="2024-01-31")
    with pytest.raises(HTTPException) as e:
        import asyncio
        asyncio.run(rt.run_backtest(req))
    assert e.value.status_code == 400
def test_custom_route_rejects_bad_symbols_400(rt):
    req = rt.CustomBacktestRequest(yaml_content="x: 1", symbols=["a/b"],
                                   start_date="2024-01-01", end_date="2024-01-31")
    with pytest.raises(HTTPException) as e:
        import asyncio
        asyncio.run(rt.run_custom_backtest(req))
    assert e.value.status_code == 400


def test_prepare_rejects_without_fs_or_network(rt, monkeypatch, tmp_path):
    import kis_backtest.providers.kis.auth as auth_mod

    def _boom(*a, **k):
        raise AssertionError("must not authenticate")

    monkeypatch.setattr(auth_mod.KISAuth, "from_env", staticmethod(_boom))
    out = asyncio_run(rt.prepare_market_data(
        symbols=["../x", "a/b", ""], start_date="2024-01-01",
        end_date="2024-01-31", workspace=tmp_path / "ws"))
    assert len(out["errors"]) == 3
    assert out["downloaded"] == [] and out["skipped"] == []
    assert list((tmp_path / "ws").rglob("*.csv")) == []


def asyncio_run(coro):
    import asyncio
    return asyncio.run(coro)


def test_prepare_downloads_only_valid(rt, monkeypatch, tmp_path):
    import kis_backtest.providers.kis.auth as auth_mod
    import kis_backtest.providers.kis.data as data_mod

    monkeypatch.setattr(auth_mod.KISAuth, "from_env",
                        staticmethod(lambda *a, **k: object()))

    class Bar:
        def __init__(self, t, o, h, l, c, v):
            self.time, self.open, self.high, self.low = t, o, h, l
            self.close, self.volume = c, v

    class FakeProvider:
        def __init__(self, auth):
            pass

        def get_history(self, symbol, s, e):
            assert symbol == "005930"
            return [Bar(datetime(2024, 1, 2), 1, 2, 1, 2, 100)]

    monkeypatch.setattr(data_mod, "KISDataProvider", FakeProvider)
    out = asyncio_run(rt.prepare_market_data(
        symbols=["005930", "../x"], start_date="2024-01-01",
        end_date="2024-01-31", workspace=tmp_path / "ws"))
    assert out["downloaded"] == ["005930"]
    assert [e["symbol"] for e in out["errors"]] == ["../x"]
    assert (tmp_path / "ws" / "data" / "equity" / "krx" / "daily" / "005930.csv").is_file()
    assert [p for p in (tmp_path / "ws").rglob("*.csv")
            if "005930" not in p.name] == []


def test_export_symbol_confines_path(monkeypatch, tmp_path):
    _install_ka_stub(monkeypatch, tmp_path)
    monkeypatch.syspath_prepend(str(HERE))
    import pandas as pd
    from kis_backtest.lean.data_converter import DataConverter
    df = pd.DataFrame([{"date": "2024-01-02", "open": 1, "high": 2,
                        "low": 1, "close": 2, "volume": 100}])
    with pytest.raises(ValueError):
        DataConverter._export_symbol("../x", df, tmp_path, "krx")
    p = DataConverter._export_symbol("005930", df, tmp_path, "krx")
    assert p.parent == tmp_path.resolve()
    assert p.is_file()
