"""이슈 #26: UTC/KST 경계·워크스페이스 회귀 테스트 (오프라인, KIS 호출 없음)."""
import os
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # backtester/
SB = HERE.parent / "strategy_builder"

_KST = timezone(timedelta(hours=9))


def _write_dummy_yaml(tmp_path, monkeypatch):
    cfg = tmp_path / "KIS" / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "kis_devlp.yaml").write_text("my_app: DUMMY\nmy_sec: DUMMY\n", encoding="utf-8")
    monkeypatch.setenv("HOME", str(tmp_path))


class _FakeRes:
    def __init__(self, body):
        self._body = body

    def isOK(self):
        return True

    def getBody(self):
        return self._body


def _install_ka_stub(monkeypatch, tmp_path, captured):
    ka = types.ModuleType("kis_auth")
    ka._cfg = {"vps": "https://openapivts.koreainvestment.com:29443",
               "prod": "https://openapi.koreainvestment.com:9443"}
    ka.auth = lambda svr: None
    ka.isPaperTrading = lambda: True
    ka.getTREnv = lambda: types.SimpleNamespace(
        my_url="https://x", my_acct="00000000", my_prod="01")
    ka.read_token = lambda *a: None
    ka.clear_saved_tokens = lambda: 1

    def _url_fetch(url, tr_id, tr_cont, params, postFlag=False):
        captured.append({"url": url, "tr_id": tr_id, "params": dict(params)})
        if "inquire-daily-ccld" in url:
            body = types.SimpleNamespace(output1=[{
                "odno": "0000001", "ord_orgno": "", "pdno": "005930",
                "prdt_name": "삼성전자", "sll_buy_dvsn_cd_name": "매수",
                "ord_qty": "10", "ord_unpr": "70000", "tot_ccld_qty": "0",
                "rmn_qty": "10", "ord_tmd": "093000",
            }])
        else:
            body = types.SimpleNamespace(output2=[{
                "stck_bsop_date": "20240102", "stck_oprc": "100",
                "stck_hgpr": "110", "stck_lwpr": "90",
                "stck_clpr": "105", "acml_vol": "1000",
            }])
        return _FakeRes(body)

    ka._url_fetch = _url_fetch
    monkeypatch.setitem(sys.modules, "kis_auth", ka)
    return ka


def _load_formatter(monkeypatch):
    monkeypatch.syspath_prepend(str(HERE))
    from kis_backtest.lean.result_formatter import ResultFormatter
    return ResultFormatter


def _load_fetcher(monkeypatch, tmp_path, captured):
    _write_dummy_yaml(tmp_path, monkeypatch)
    _install_ka_stub(monkeypatch, tmp_path, captured)
    monkeypatch.syspath_prepend(str(SB))
    sys.modules.pop("core.data_fetcher", None)
    import core.data_fetcher as df
    return df


def test_equity_curve_uses_utc_date_at_kst_boundary(monkeypatch):
    """KST 자정+30분 epoch은 UTC 날짜(전날)로 변환된다."""
    fmt = _load_formatter(monkeypatch)
    ts = int(datetime(2024, 1, 1, 0, 30, tzinfo=_KST).timestamp())
    result = {"charts": {"Strategy Equity": {"series": {"Equity": {"values": [[ts, 100.0]]}}}}}
    out = fmt._convert_equity_curve(result, 100.0)
    assert out["dates"] == ["2023-12-31"]


def test_drawdown_curve_uses_utc_date_at_kst_boundary(monkeypatch):
    fmt = _load_formatter(monkeypatch)
    ts = int(datetime(2024, 1, 1, 0, 30, tzinfo=_KST).timestamp())
    result = {"charts": {"Drawdown": {"series": {"Equity Drawdown": {"values": [[ts, 1.5]]}}}}}
    out = fmt._convert_drawdown_curve(result)
    assert out["dates"] == ["2023-12-31"]


def test_daily_klines_query_dates_use_kst(monkeypatch, tmp_path):
    captured = []
    df = _load_fetcher(monkeypatch, tmp_path, captured)
    assert df._KST == _KST
    df.get_daily_prices("005930", days=5)
    assert captured, "KIS API가 호출되지 않았다"
    params = captured[0]["params"]
    today = datetime.now(_KST).strftime("%Y%m%d")
    assert params["FID_INPUT_DATE_2"] == today
    assert params["FID_INPUT_DATE_1"] == (
        datetime.now(_KST) - timedelta(days=5 + 50)).strftime("%Y%m%d")


def test_pending_orders_inqr_dates_use_kst(monkeypatch, tmp_path):
    captured = []
    df = _load_fetcher(monkeypatch, tmp_path, captured)
    _, ok = df.get_pending_orders()
    assert ok is True
    assert captured, "KIS API가 호출되지 않았다"
    params = captured[0]["params"]
    today = datetime.now(_KST).strftime("%Y%m%d")
    assert params["INQR_STRT_DT"] == today
    assert params["INQR_END_DT"] == today


def test_workspace_resolves_absolute_with_env(monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(HERE))
    monkeypatch.setenv("LEAN_WORKSPACE", str(tmp_path / "custom-ws"))
    from kis_backtest.lean.project_manager import LeanProjectManager
    prev = LeanProjectManager.workspace
    try:
        LeanProjectManager.set_workspace(
            os.environ.get("LEAN_WORKSPACE") or str(HERE / ".lean-workspace"))
        assert LeanProjectManager.workspace == tmp_path / "custom-ws"
        assert LeanProjectManager.workspace.is_absolute()
    finally:
        LeanProjectManager.workspace = prev


def test_workspace_resolves_absolute_without_env(monkeypatch):
    monkeypatch.syspath_prepend(str(HERE))
    monkeypatch.delenv("LEAN_WORKSPACE", raising=False)
    from kis_backtest.lean.project_manager import LeanProjectManager
    prev = LeanProjectManager.workspace
    try:
        LeanProjectManager.set_workspace(
            os.environ.get("LEAN_WORKSPACE") or str(HERE / ".lean-workspace"))
        assert LeanProjectManager.workspace == HERE / ".lean-workspace"
        assert LeanProjectManager.workspace.is_absolute()
    finally:
        LeanProjectManager.workspace = prev


def test_startup_files_honor_lean_workspace_env():
    """MCP 서버·백엔드 진입점이 LEAN_WORKSPACE를 우선한다."""
    server_src = (HERE / "kis_mcp" / "server.py").read_text(encoding="utf-8")
    assert 'os.environ.get("LEAN_WORKSPACE")' in server_src
    assert "set_workspace" in server_src
    assert '.lean-workspace' in server_src
    main_src = (HERE / "backend" / "main.py").read_text(encoding="utf-8")
    assert 'os.environ.get("LEAN_WORKSPACE")' in main_src
    assert "set_workspace" in main_src
