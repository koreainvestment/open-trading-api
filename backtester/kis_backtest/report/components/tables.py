"""테이블 컴포넌트

거래 내역 테이블. Order 객체 및 Dict 입력 지원.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Union

if TYPE_CHECKING:
    from ...models import Order
    from ..themes import KISTheme


class TradesTable:
    """거래 내역 테이블"""

    def __init__(self, theme: "KISTheme" = None):
        from ..themes import KISTheme
        self.theme = theme or KISTheme()

    def render(self, trades: Union[List["Order"], List[Dict[str, Any]]], limit: int = 20) -> str:
        """HTML 테이블 렌더링 (Order 객체 또는 Dict 리스트 지원)"""
        if not trades:
            return """
            <div class="card">
                <div class="table-header">
                    <h3>거래 내역</h3>
                </div>
                <div class="empty-state">
                    <p>거래 내역이 없습니다.</p>
                </div>
            </div>
            """

        # Dict인지 Order인지 감지
        is_dict = isinstance(trades[0], dict)

        if is_dict:
            return self._render_dict_trades(trades, limit)
        return self._render_order_trades(trades, limit)

    def _render_order_trades(self, orders: List["Order"], limit: int) -> str:
        """Order 객체 리스트 렌더링"""
        pnl_map = self._calculate_pnl_orders(orders)
        total_pnl = sum(v for v in pnl_map.values() if v is not None)

        rows = []
        for order in orders[:limit]:
            direction_class = "buy" if order.side.value == "buy" else "sell"
            direction_text = "매수" if order.side.value == "buy" else "매도"

            pnl = pnl_map.get(order.id)
            if pnl is not None:
                pnl_class = "positive" if pnl > 0 else "negative" if pnl < 0 else ""
                pnl_text = f"{pnl:+,.0f}원"
            else:
                pnl_class = ""
                pnl_text = "-"

            rows.append(f"""
                <tr>
                    <td>{order.created_at.strftime('%Y-%m-%d')}</td>
                    <td>{order.symbol}</td>
                    <td class="{direction_class}">{direction_text}</td>
                    <td class="number">{order.quantity:,}</td>
                    <td class="number">{order.average_price:,.0f}원</td>
                    <td class="number {pnl_class}">{pnl_text}</td>
                </tr>""")

        return self._wrap_table(rows, len(orders), limit, total_pnl)

    def _render_dict_trades(self, trades: List[Dict[str, Any]], limit: int) -> str:
        """Dict 리스트 렌더링"""
        pnl_map = self._calculate_pnl_dicts(trades)
        total_pnl = sum(v for v in pnl_map.values() if v is not None)

        rows = []
        for i, trade in enumerate(trades[:limit]):
            # 키 매핑
            trade_date = trade.get("datetime") or trade.get("time") or trade.get("date") or ""
            if isinstance(trade_date, datetime):
                trade_date = trade_date.strftime('%Y-%m-%d')
            elif isinstance(trade_date, str) and len(trade_date) > 10:
                trade_date = trade_date[:10]

            # symbol: nested dict {'value': '005930'} 또는 문자열
            raw_symbol = trade.get("symbol", "")
            symbol = raw_symbol.get("value", str(raw_symbol)) if isinstance(raw_symbol, dict) else str(raw_symbol)

            # direction: Lean int (0=buy, 1=sell) 또는 문자열
            raw_dir = trade.get("direction") if trade.get("direction") is not None else trade.get("side", "")
            if isinstance(raw_dir, int):
                is_buy = raw_dir == 0
            else:
                is_buy = str(raw_dir).lower() in ("buy", "매수", "long")

            direction_class = "buy" if is_buy else "sell"
            direction_text = "매수" if is_buy else "매도"

            qty = int(float(trade.get("quantity", 0)))
            price = float(trade.get("price", 0))

            pnl = pnl_map.get(i)
            if pnl is not None:
                pnl_class = "positive" if pnl > 0 else "negative" if pnl < 0 else ""
                pnl_text = f"{pnl:+,.0f}원"
            else:
                pnl_class = ""
                pnl_text = "-"

            rows.append(f"""
                <tr>
                    <td>{trade_date}</td>
                    <td>{symbol}</td>
                    <td class="{direction_class}">{direction_text}</td>
                    <td class="number">{qty:,}</td>
                    <td class="number">{price:,.0f}원</td>
                    <td class="number {pnl_class}">{pnl_text}</td>
                </tr>""")

        return self._wrap_table(rows, len(trades), limit, total_pnl)

    def _wrap_table(self, rows: List[str], total_count: int, limit: int, total_pnl: float) -> str:
        """테이블 HTML 래퍼"""
        more_text = ""
        if total_count > limit:
            more_text = f'<p style="text-align:center; color:var(--slate-400); font-size:0.75rem; margin-top:0.5rem;">외 {total_count - limit}건</p>'

        total_class = "text-profit" if total_pnl > 0 else "text-loss" if total_pnl < 0 else ""

        return f"""
        <div class="card">
            <div class="table-header">
                <h3>거래 내역</h3>
                <div style="display:flex; gap:0.75rem; align-items:center;">
                    <span class="{total_class}" style="font-weight:600; font-size:0.8125rem;">총 손익: {total_pnl:+,.0f}원</span>
                    <span class="badge">{total_count}건</span>
                </div>
            </div>
            <table class="kis-table">
                <thead>
                    <tr>
                        <th>일자</th>
                        <th>종목</th>
                        <th>구분</th>
                        <th style="text-align:right">수량</th>
                        <th style="text-align:right">체결가</th>
                        <th style="text-align:right">손익</th>
                    </tr>
                </thead>
                <tbody>
{''.join(rows)}
                </tbody>
            </table>
            {more_text}
        </div>
        """

    def _calculate_pnl_orders(self, orders: List["Order"]) -> Dict[str, float]:
        """Order 객체 기반 FIFO PnL 계산"""
        pnl_map: Dict[str, float] = {}
        pending_buys: Dict[str, list] = {}

        for order in orders:
            sym = order.symbol
            if sym not in pending_buys:
                pending_buys[sym] = []

            if order.side.value == "buy":
                pending_buys[sym].append({
                    'id': order.id,
                    'qty': order.quantity,
                    'price': order.average_price,
                })
                pnl_map[order.id] = None
            else:
                sell_qty = order.quantity
                sell_price = order.average_price
                total_pnl = 0.0

                while sell_qty > 0 and pending_buys[sym]:
                    buy = pending_buys[sym][0]
                    match_qty = min(sell_qty, buy['qty'])
                    total_pnl += (sell_price - buy['price']) * match_qty
                    buy['qty'] -= match_qty
                    sell_qty -= match_qty
                    if buy['qty'] <= 0:
                        pending_buys[sym].pop(0)

                pnl_map[order.id] = total_pnl

        return pnl_map

    def _calculate_pnl_dicts(self, trades: List[Dict[str, Any]]) -> Dict[int, float]:
        """Dict 기반 FIFO PnL 계산 (인덱스 -> PnL)

        Note: Lean 원시 데이터에서 매도 수량이 음수(-1624)로 올 수 있으므로
              abs()로 절대값 사용.
        """
        pnl_map: Dict[int, float] = {}
        pending_buys: Dict[str, list] = {}

        for i, trade in enumerate(trades):
            raw_symbol = trade.get("symbol", "")
            sym = raw_symbol.get("value", str(raw_symbol)) if isinstance(raw_symbol, dict) else str(raw_symbol)

            raw_dir = trade.get("direction") if trade.get("direction") is not None else trade.get("side", "")
            if isinstance(raw_dir, int):
                is_buy = raw_dir == 0
            else:
                is_buy = str(raw_dir).lower() in ("buy", "매수", "long")

            price = float(trade.get("price", 0))
            qty = abs(int(float(trade.get("quantity", 0))))

            if sym not in pending_buys:
                pending_buys[sym] = []

            if is_buy:
                pending_buys[sym].append({'qty': qty, 'price': price})
                pnl_map[i] = None
            else:
                sell_qty = qty
                total_pnl = 0.0

                while sell_qty > 0 and pending_buys.get(sym):
                    buy = pending_buys[sym][0]
                    match_qty = min(sell_qty, buy['qty'])
                    total_pnl += (price - buy['price']) * match_qty
                    buy['qty'] -= match_qty
                    sell_qty -= match_qty
                    if buy['qty'] <= 0:
                        pending_buys[sym].pop(0)

                pnl_map[i] = total_pnl

        return pnl_map
