"""이슈 #26: 거래 비용 검증 회귀 테스트 (오프라인, KIS 호출 없음)."""
import sys
import types
from pathlib import Path

import pytest

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


@pytest.fixture()
def cfg(monkeypatch, tmp_path):
    _install_ka_stub(monkeypatch, tmp_path)
    monkeypatch.syspath_prepend(str(HERE))
    from kis_backtest.codegen.generator import CodeGenConfig
    return CodeGenConfig


def test_resolve_cost_none_returns_default(rt):
    assert rt._resolve_cost(None, 0.00015, "commission_rate") == 0.00015
    assert rt._resolve_cost(None, 0.002, "tax_rate") == 0.002
    assert rt._resolve_cost(None, 0.0, "slippage") == 0.0


def test_resolve_cost_zero_stays_zero(rt):
    assert rt._resolve_cost(0, 0.00015, "commission_rate") == 0.0
    assert rt._resolve_cost(0.0, 0.002, "tax_rate") == 0.0


def test_resolve_cost_rejects_bad_values(rt):
    for bad in (-1, -0.1, 1.5, float("nan"), float("inf"),
                float("-inf"), "x", True, False):
        with pytest.raises(ValueError):
            rt._resolve_cost(bad, 0.00015, "commission_rate")


def test_resolve_cost_route_valueerror_path(rt):
    # 라우트는 ValueError를 HTTP 400으로 변환한다: 헬퍼가 ValueError를
    # 발생시키는지, 소스가 400으로 매핑하는지 확인.
    with pytest.raises(ValueError):
        rt._resolve_cost(-1, 0.00015, "commission_rate")
    src = Path(rt.__file__).read_text(encoding="utf-8")
    assert "except ValueError" in src
    assert "status_code=400" in src


def test_codegen_config_zero_ok(cfg):
    c = cfg(commission_rate=0)
    assert c.commission_rate == 0


def test_codegen_config_negative_raises(cfg):
    with pytest.raises(ValueError):
        cfg(tax_rate=-0.1)
    for bad in (float("nan"), float("inf"), "x", True, 2.0):
        with pytest.raises(ValueError):
            cfg(commission_rate=bad)


def test_routes_use_resolve_cost_at_both_sites(rt):
    src = Path(rt.__file__).read_text(encoding="utf-8")
    assert "request.commission_rate or 0.00015" not in src
    assert "request.tax_rate or 0.002" not in src
    assert "request.slippage or 0.0" not in src
    assert src.count("_resolve_cost(request.commission_rate") == 2
    assert src.count("_resolve_cost(request.tax_rate") == 2
    assert src.count("_resolve_cost(request.slippage") == 2
