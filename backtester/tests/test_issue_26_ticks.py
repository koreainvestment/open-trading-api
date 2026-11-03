"""Issue #26: 2023 틱 테이블·부분 데이터 실패 처리 회귀 테스트 (오프라인)."""
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

HERE = Path(__file__).resolve().parent.parent
GEN_PATH = HERE / "kis_backtest" / "codegen" / "generator.py"


def _stub_kis_auth(monkeypatch, tmp_path):
    ka = ModuleType("kis_auth")
    ka._cfg = {}
    ka.auth = lambda *a, **k: None
    ka.read_token = lambda *a: None
    monkeypatch.setitem(sys.modules, "kis_auth", ka)
    monkeypatch.setenv("HOME", str(tmp_path))


@pytest.fixture()
def kdata(monkeypatch, tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("kdata")
    _stub_kis_auth(monkeypatch, tmp_path)
    monkeypatch.syspath_prepend(str(HERE))
    monkeypatch.delitem(sys.modules, "kis_backtest.providers.kis.data", raising=False)
    import kis_backtest.providers.kis.data as d
    return d


def _row(dt):
    return {"stck_bsop_date": dt.strftime("%Y%m%d"), "stck_oprc": "100",
            "stck_hgpr": "101", "stck_lwpr": "99", "stck_clpr": "100",
            "acml_vol": "1000"}


def _page(rows, ok=True, code="0", msg="OK"):
    return SimpleNamespace(is_ok=lambda: ok, get_output2=lambda: rows,
                           error_code=code, error_message=msg,
                           header=SimpleNamespace(tr_cont=""))


class _FakeAuth:
    def __init__(self, fn):
        self._fn = fn

    def get(self, *a, **k):
        return self._fn(*a, **k)

    def smart_sleep(self):
        return None


def _dates_desc(end, n):
    return [end - timedelta(days=i) for i in range(n)]


def test_tick_table_matches_2023_revision():
    src = GEN_PATH.read_text(encoding="utf-8")
    for bound in ("price < 2000", "price < 5000", "price < 20000",
                  "price < 50000", "price < 200000", "price < 500000"):
        assert bound in src, bound


def test_tick_values_at_boundaries():
    import kis_backtest.codegen.generator as gen

    cfg = gen.CodeGenConfig(slippage=0.01)
    inst = gen.LeanCodeGenerator.__new__(gen.LeanCodeGenerator)
    inst.config = cfg
    ns = {}
    exec(inst._generate_slippage_model(), ns)
    tick = ns["KRXSlippageModel"]()._tick
    cases = [(0, 1), (1999, 1), (2000, 5), (4999, 5), (5000, 10),
             (19999, 10), (20000, 50), (49999, 50), (50000, 100),
             (199999, 100), (200000, 500), (499999, 500),
             (500000, 1000), (10_000_000, 1000)]
    for price, want in cases:
        assert tick(price) == want, (price, want)


def _provider(monkeypatch, kdata, tmp_path, fake_get):
    import kis_backtest.providers.kis.auth as auth_mod
    _stub_kis_auth(monkeypatch, tmp_path)
    monkeypatch.setattr(auth_mod.KISAuth, "from_env",
                        staticmethod(lambda *a, **k: object()))
    monkeypatch.setattr(time, "sleep", lambda s: None)
    prov = kdata.KISDataProvider(object())
    prov._auth = _FakeAuth(fake_get)
    return prov


def test_daily_exhausted_rate_limit_raises_with_partial(kdata, monkeypatch, tmp_path):
    from kis_backtest.exceptions import KISError
    end = date(2024, 6, 30)
    page1 = [_row(d) for d in _dates_desc(end, 100)]
    bad = _page([], ok=False, code="EGW00201", msg="limit")
    calls = {"n": 0}

    def fake_get(*a, **k):
        calls["n"] += 1
        return _page(page1) if calls["n"] == 1 else bad

    prov = _provider(monkeypatch, kdata, tmp_path, fake_get)
    with pytest.raises(KISError):
        prov._get_daily_bars("005930", date(2024, 1, 1), end)


def test_daily_mid_pagination_non_ok_raises_with_partial(kdata, monkeypatch, tmp_path):
    from kis_backtest.exceptions import KISError
    end = date(2024, 6, 30)
    page1 = [_row(d) for d in _dates_desc(end, 100)]
    bad = _page([], ok=False, code="123", msg="boom")
    calls = {"n": 0}

    def fake_get(*a, **k):
        calls["n"] += 1
        return _page(page1) if calls["n"] == 1 else bad

    prov = _provider(monkeypatch, kdata, tmp_path, fake_get)
    with pytest.raises(KISError):
        prov._get_daily_bars("005930", date(2024, 1, 1), end)


def test_daily_first_page_failure_returns_empty(kdata, monkeypatch, tmp_path):
    bad = _page([], ok=False, code="EGW00201", msg="limit")
    prov = _provider(monkeypatch, kdata, tmp_path,
                     lambda *a, **k: bad)
    assert prov._get_daily_bars("005930", date(2024, 1, 1), date(2024, 6, 30)) == []


def test_daily_all_ok_paginated_merges(kdata, monkeypatch, tmp_path):
    end = date(2024, 6, 30)
    page1 = [_row(d) for d in _dates_desc(end, 100)]
    page2 = [_row(date(2024, 1, 1) + timedelta(days=i)) for i in range(9, -1, -1)]
    calls = {"n": 0}

    def fake_get(*a, **k):
        calls["n"] += 1
        return _page(page1) if calls["n"] == 1 else _page(page2)

    prov = _provider(monkeypatch, kdata, tmp_path, fake_get)
    bars = prov._get_daily_bars("005930", date(2024, 1, 1), end)
    assert len(bars) == 110
    assert bars[0].time.date() <= bars[-1].time.date()
