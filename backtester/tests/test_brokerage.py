"""KISBrokerageProvider.get_orders() 단위 테스트"""

from unittest.mock import MagicMock, patch

import pytest

from kis_backtest.models import OrderStatus, OrderSide, OrderType
from kis_backtest.providers.kis.brokerage import KISBrokerageProvider


@pytest.fixture
def provider():
    with patch("kis_backtest.providers.kis.brokerage.KISAuth") as MockAuth:
        mock_auth = MockAuth.return_value
        mock_auth.account_no = "12345678"
        mock_auth.account_prod = "01"
        mock_auth.is_paper = True
        p = KISBrokerageProvider.__new__(KISBrokerageProvider)
        p._auth = mock_auth
        p._ws_client = None
        yield p


def _make_resp(output1):
    resp = MagicMock()
    resp.is_ok.return_value = True
    resp.get_output1.return_value = output1
    return resp


def test_get_orders_empty(provider):
    provider._auth.get.return_value = _make_resp([])
    orders = provider.get_orders()
    assert orders == []


def test_get_orders_parses_buy_order(provider):
    provider._auth.get.return_value = _make_resp(
        [
            {
                "odno": "0001",
                "pdno": "005930",
                "sll_buy_dvsn_cd": "02",
                "ord_qty": "10",
                "ord_unpr": "70000",
                "tot_ccld_qty": "10",
                "avg_prvs": "69500",
                "rmn_qty": "0",
            }
        ]
    )
    orders = provider.get_orders()
    assert len(orders) == 1
    o = orders[0]
    assert o.id == "0001"
    assert o.symbol == "005930"
    assert o.side == OrderSide.BUY
    assert o.order_type == OrderType.LIMIT
    assert o.quantity == 10
    assert o.filled_quantity == 10
    assert o.status == OrderStatus.FILLED


def test_get_orders_parses_sell_unfilled(provider):
    provider._auth.get.return_value = _make_resp(
        [
            {
                "odno": "0002",
                "pdno": "035720",
                "sll_buy_dvsn_cd": "01",
                "ord_qty": "5",
                "ord_unpr": "50000",
                "tot_ccld_qty": "0",
                "avg_prvs": "0",
                "rmn_qty": "5",
            }
        ]
    )
    orders = provider.get_orders()
    assert len(orders) == 1
    o = orders[0]
    assert o.side == OrderSide.SELL
    assert o.status == OrderStatus.SUBMITTED
    assert o.filled_quantity == 0


def test_get_orders_partially_filled(provider):
    provider._auth.get.return_value = _make_resp(
        [
            {
                "odno": "0003",
                "pdno": "005930",
                "sll_buy_dvsn_cd": "02",
                "ord_qty": "10",
                "ord_unpr": "70000",
                "tot_ccld_qty": "3",
                "avg_prvs": "69800",
                "rmn_qty": "7",
            }
        ]
    )
    orders = provider.get_orders()
    assert orders[0].status == OrderStatus.PARTIALLY_FILLED


def test_get_orders_market_order(provider):
    provider._auth.get.return_value = _make_resp(
        [
            {
                "odno": "0004",
                "pdno": "005930",
                "sll_buy_dvsn_cd": "02",
                "ord_qty": "1",
                "ord_unpr": "0",
                "tot_ccld_qty": "1",
                "avg_prvs": "70000",
                "rmn_qty": "0",
            }
        ]
    )
    orders = provider.get_orders()
    assert orders[0].order_type == OrderType.MARKET
    assert orders[0].price is None


def test_get_orders_status_filter_passes_ccld_dvsn(provider):
    provider._auth.get.return_value = _make_resp([])
    provider.get_orders(status=OrderStatus.FILLED)
    call_args = provider._auth.get.call_args
    params = call_args[0][1]
    assert params["CCLD_DVSN"] == "01"


def test_get_orders_unfilled_filter(provider):
    provider._auth.get.return_value = _make_resp([])
    provider.get_orders(status=OrderStatus.SUBMITTED)
    call_args = provider._auth.get.call_args
    params = call_args[0][1]
    assert params["CCLD_DVSN"] == "02"
