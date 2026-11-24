"""이슈 #24: 미체결 조회·get_orders 구현·취소/정정 정렬 회귀 테스트 (오프라인)."""
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest

HERE = Path(__file__).resolve().parent.parent


def _stub_ka(monkeypatch, tmp_path):
    ka = types.ModuleType("kis_auth")
    ka._cfg = {}
    ka.auth = lambda *a, **k: None
    ka.isPaperTrading = lambda: True
    ka.getTREnv = lambda: SimpleNamespace(my_url="https://x")
    ka.read_token = lambda *a: None
    monkeypatch.setitem(sys.modules, "kis_auth", ka)
    monkeypatch.setenv("HOME", str(tmp_path))
    return ka


@pytest.fixture()
def brok(monkeypatch, tmp_path):
    _stub_ka(monkeypatch, tmp_path)
    monkeypatch.syspath_prepend(str(HERE))
    for m in ("kis_backtest.providers.kis.brokerage",):
        sys.modules.pop(m, None)
    import kis_backtest.providers.kis.brokerage as brok
    return brok


def _resp(ok=True, output1=None, output=None, tr_cont="", err=""):
    return SimpleNamespace(
        is_ok=lambda: ok,
        get_output1=lambda: output1,
        get_output=lambda key="output": output,
        header=SimpleNamespace(tr_cont=tr_cont),
        error_message=err,
    )


def _provider(brok, calls, pages=None, post_ok=True, post_out=None):
    pages = list(pages or [])

    def fake_get(path, params, tr_id, tr_cont=""):
        calls.append(("get", path, dict(params), tr_id, tr_cont))
        return pages.pop(0)

    def fake_post(path, body, tr_id):
        calls.append(("post", path, dict(body), tr_id))
        return _resp(ok=post_ok, output=post_out)

    auth = SimpleNamespace(account_no="12345678", account_prod="01",
                           is_paper=True, get=fake_get, post=fake_post)
    return brok.KISBrokerageProvider.from_auth(auth)


def _order_row(odno="1", pdno="005930", sbs="02", qty="10", unpr="70000",
               filled="0", avg="0", rmn="10"):
    return {"odno": odno, "pdno": pdno, "sll_buy_dvsn_cd": sbs,
            "ord_qty": qty, "ord_unpr": unpr, "tot_ccld_qty": filled,
            "avg_prvs": avg, "rmn_qty": rmn}


def test_data_fetcher_uses_unfilled_dvsn():
    src = (HERE.parent / "strategy_builder" / "core" / "data_fetcher.py").read_text(
        encoding="utf-8")
    assert '"CCLD_DVSN": "02"' in src
    assert '"CCLD_DVSN": "01"' not in src


def test_cancel_tr_ids_aligned(brok):
    assert brok.TrId.ORDER_CANCEL_REAL == "TTTC0013U"
    assert brok.TrId.ORDER_CANCEL_PAPER == "VTTC0013U"


def test_get_orders_paginates_and_maps(brok):
    from kis_backtest.models import OrderSide, OrderStatus
    calls = []
    p1 = _resp(output1=[_order_row()], tr_cont="M",
               output={"ctx_area_fk100": "FK", "ctx_area_nk100": "NK"})
    p2 = _resp(output1=[_order_row(odno="2", sbs="01", filled="10", rmn="0")],
               tr_cont="")
    prov = _provider(brok, calls, pages=[p1, p2])
    orders = prov.get_orders()
    assert [o.id for o in orders] == ["1", "2"]
    assert orders[0].side == OrderSide.BUY
    assert orders[0].status == OrderStatus.SUBMITTED
    assert orders[1].side == OrderSide.SELL
    assert orders[1].status == OrderStatus.FILLED
    assert orders[1].symbol == "005930"
    first = calls[0]
    assert first[1].endswith("inquire-daily-ccld") and first[3] == "VTTC8001R"
    assert first[2]["CCLD_DVSN"] == "00"
    second = calls[1]
    assert second[2]["CTX_AREA_FK100"] == "FK"
    assert second[4] == "N"


def test_get_orders_submitted_uses_02(brok):
    from kis_backtest.models import OrderStatus
    calls = []
    prov = _provider(brok, calls, pages=[_resp(output1=[], tr_cont="")])
    assert prov.get_orders(status=OrderStatus.SUBMITTED) == []
    assert calls[0][2]["CCLD_DVSN"] == "02"


def test_cancel_uses_lookup_quantity(brok):
    calls = []
    prov = _provider(brok, calls, pages=[
        _resp(output1=[_order_row(qty="10", filled="3")], tr_cont="")])
    assert prov.cancel_order("1") is True
    post = [c for c in calls if c[0] == "post"][0]
    assert post[3] == "VTTC0013U"
    assert post[2]["ORD_QTY"] == "7"
    assert post[2]["ORGN_ODNO"] == "1"
    assert post[2]["EXCG_ID_DVSN_CD"] == "KRX"
    assert post[2]["QTY_ALL_ORD_YN"] == "Y"


def test_cancel_unknown_order_returns_false(brok):
    calls = []
    prov = _provider(brok, calls, pages=[_resp(output1=[], tr_cont="")])
    assert prov.cancel_order("nope") is False
    assert [c for c in calls if c[0] == "post"] == []


def test_modify_fills_from_lookup(brok):
    from kis_backtest.exceptions import KISOrderError
    calls = []
    prov = _provider(brok, calls, pages=[
        _resp(output1=[_order_row(qty="10", filled="2")], tr_cont="")],
        post_ok=True, post_out={"ODNO": "2"})
    order = prov.modify_order("1", quantity=5, price=71000.0)
    assert order.symbol == "005930"
    assert order.side.value == "buy"
    post = [c for c in calls if c[0] == "post"][0]
    assert post[2]["RVSE_CNCL_DVSN_CD"] == "01"
    assert post[2]["ORD_QTY"] == "5"
    assert order.id == "2"
    calls2 = []
    prov2 = _provider(brok, calls2, pages=[_resp(output1=[], tr_cont="")])
    with pytest.raises(KISOrderError):
        prov2.modify_order("nope", quantity=1)
