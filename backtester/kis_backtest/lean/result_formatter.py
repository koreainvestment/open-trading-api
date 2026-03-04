"""결과 포맷터

Lean 백테스트 결과를 API 응답 형식으로 변환.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .executor import LeanRun

logger = logging.getLogger(__name__)


def parse_lean_value(val: Any) -> float:
    """Lean 값 파싱 (%, $, , 제거 후 float 반환)"""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        val = val.replace("%", "").replace("$", "").replace(",", "").strip()
        try:
            return float(val)
        except ValueError:
            return 0.0
    return 0.0


class ResultFormatter:
    """Lean 결과 → API 응답 변환기"""
    
    @classmethod
    def to_api_response(
        cls,
        run: LeanRun,
        symbols: List[str],
        start_date: str,
        end_date: str,
        initial_capital: float,
        strategy_type: str,
        strategy_params: Dict[str, Any],
        currency: str = "KRW",
        strategy_name: Optional[str] = None,
    ) -> Dict:
        """Lean 결과를 API 응답 형식으로 변환
        
        Args:
            run: Lean 실행 결과
            symbols: 종목 코드 리스트
            start_date: 시작일
            end_date: 종료일
            initial_capital: 초기 자본
            strategy_type: 전략 타입
            strategy_params: 전략 파라미터
            currency: 통화 코드 ("KRW" 또는 "USD")
            strategy_name: 커스텀 전략 이름 (커스텀 전략일 경우)
        """
        if not run.success:
            return cls._error_response(run.error, symbols, start_date, end_date, initial_capital, currency)
        
        # Lean 결과 로드
        result = run.load_result()
        stats = run.get_statistics()
        
        # 통계 변환
        statistics = cls._convert_statistics(stats, initial_capital)
        
        # 자산 곡선 변환
        equity_data = cls._convert_equity_curve(result, initial_capital)
        
        # 거래 내역 변환
        trades = cls._convert_trades(result)
        
        # 낙폭 곡선
        drawdown_data = cls._convert_drawdown_curve(result)
        
        # 종목별 결과
        symbol_results = cls._calculate_symbol_results(trades, symbols)
        
        return {
            "currency": currency,
            "result": {
                "id": f"bt_{run.project.run_id}",
                "ran_at": run.started_at.isoformat(),
                "duration_seconds": run.duration_seconds,
                "statistics": statistics,
                "equity_curve": equity_data["values"],
                "equity_dates": equity_data["dates"],
                "drawdown_curve": drawdown_data["values"],
                "trades": trades,
                "symbol_results": symbol_results,
                "charts": {
                    "equity": {
                        "type": "equity",
                        "title": "자산 추이",
                        "labels": equity_data["dates"],
                        "datasets": [
                            {
                                "label": "자산",
                                "data": equity_data["values"],
                                "color": "#00d4aa",
                                "type": "line",
                            }
                        ],
                    },
                    "drawdown": {
                        "type": "drawdown",
                        "title": "낙폭",
                        "labels": drawdown_data["dates"],
                        "datasets": [
                            {
                                "label": "낙폭",
                                "data": drawdown_data["values"],
                                "color": "#ef4444",
                                "type": "line",
                            }
                        ],
                    },
                },
            },
            "data_range": {
                "start": start_date,
                "end": end_date,
                "symbols_used": len(symbols),
            },
            "cost_analysis": {
                "total_trades": statistics.get("num_trades", 0),
                "total_commission": statistics.get("total_commission", 0),
                "total_slippage": statistics.get("total_slippage", 0),
                "total_cost": statistics.get("total_cost", 0),
            },
            "lean": {
                "run_id": run.project.run_id,
                "output_dir": str(run.output_dir),
                "raw_statistics": stats,
            },
            # 커스텀 전략일 경우 이름 포함
            "strategy_name": strategy_name,
        }
    
    @classmethod
    def _parse_value(cls, val: Any) -> float:
        """Lean 값 파싱 (%, $ 제거)"""
        return parse_lean_value(val)
    
    @classmethod
    def _convert_statistics(cls, stats: Dict, initial_capital: float) -> Dict:
        """Lean 통계를 API 형식으로 변환"""
        # Lean 키 → 값 추출
        total_orders = int(cls._parse_value(stats.get("Total Orders", 0)))
        net_profit_pct = cls._parse_value(stats.get("Net Profit", 0))
        cagr = cls._parse_value(stats.get("Compounding Annual Return", 0))
        sharpe = cls._parse_value(stats.get("Sharpe Ratio", 0))
        sortino = cls._parse_value(stats.get("Sortino Ratio", 0))
        max_dd = cls._parse_value(stats.get("Drawdown", 0))
        win_rate = cls._parse_value(stats.get("Win Rate", 0))
        profit_loss_ratio = cls._parse_value(stats.get("Profit-Loss Ratio", 0))
        total_fees = cls._parse_value(stats.get("Total Fees", 0))
        
        start_equity = cls._parse_value(stats.get("Start Equity", initial_capital))
        end_equity = cls._parse_value(stats.get("End Equity", initial_capital))
        
        total_return = end_equity - start_equity
        
        # 퍼센트 값 정규화 (0.0~1.0 범위, Python % 포매터 호환)
        total_return_pct_normalized = net_profit_pct / 100  # 16.985 → 0.16985
        cagr_normalized = cagr / 100
        max_drawdown_normalized = abs(max_dd) / 100
        win_rate_normalized = win_rate / 100

        return {
            "total_return": total_return,
            "total_return_pct": total_return_pct_normalized,
            "cagr": cagr_normalized,
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "max_drawdown": initial_capital * max_drawdown_normalized if max_dd else 0,
            "max_drawdown_pct": max_drawdown_normalized,
            "num_trades": total_orders,
            "win_rate": win_rate_normalized,
            "profit_factor": profit_loss_ratio,
            "avg_trade_return": total_return_pct_normalized / total_orders if total_orders > 0 else 0,
            "total_commission": total_fees,
            "total_slippage": 0,
            "total_cost": total_fees,
        }
    
    @classmethod
    def _convert_equity_curve(cls, result: Dict, initial_capital: float) -> Dict:
        """자산 곡선 변환"""
        charts = result.get("charts", {})
        strategy_equity = charts.get("Strategy Equity", {})
        series = strategy_equity.get("series", {})
        equity_series = series.get("Equity", {})
        values = equity_series.get("values", [])
        
        if not values:
            return {"dates": [], "values": []}
        
        dates = []
        equity_values = []
        
        for point in values:
            # Lean format: [timestamp, open, high, low, close] or [timestamp, value]
            if not isinstance(point, list) or len(point) < 2:
                continue
            
            timestamp = point[0]
            # 마지막 값(close) 사용
            value = point[4] if len(point) > 4 else point[1]
            
            try:
                dt = datetime.fromtimestamp(timestamp)
                dates.append(dt.strftime("%Y-%m-%d"))
            except (ValueError, OSError, TypeError):
                dates.append(str(timestamp))
            
            equity_values.append(float(value))
        
        return {"dates": dates, "values": equity_values}
    
    @classmethod
    def _convert_drawdown_curve(cls, result: Dict) -> Dict:
        """낙폭 곡선 변환"""
        charts = result.get("charts", {})
        drawdown_chart = charts.get("Drawdown", {})
        series = drawdown_chart.get("series", {})
        
        # Lean의 Drawdown 차트에서 직접 가져옴
        dd_series = series.get("Equity Drawdown", {})
        values = dd_series.get("values", [])
        
        if not values:
            return {"dates": [], "values": []}
        
        dates = []
        dd_values = []
        
        for point in values:
            if not isinstance(point, list) or len(point) < 2:
                continue
            
            timestamp = point[0]
            value = point[1]
            
            try:
                dt = datetime.fromtimestamp(timestamp)
                dates.append(dt.strftime("%Y-%m-%d"))
            except (ValueError, OSError, TypeError):
                dates.append(str(timestamp))
            
            dd_values.append(float(value))
        
        return {"dates": dates, "values": dd_values}
    
    @classmethod
    def _convert_trades(cls, result: Dict) -> List[Dict]:
        """거래 내역 변환"""
        orders = result.get("orders", {})
        
        if isinstance(orders, dict):
            orders = list(orders.values())
        
        trades = []
        for order in orders:
            # status 3 = Filled
            if order.get("status") != 3:
                continue
            
            symbol_data = order.get("symbol", {})
            symbol_code = symbol_data.get("value", "") if isinstance(symbol_data, dict) else str(symbol_data)
            
            direction = order.get("direction", 0)  # 0=Buy, 1=Sell
            quantity = abs(order.get("quantity", 0))
            price = order.get("price", 0)
            value = order.get("value", quantity * price)
            
            # 수수료 추출 (Lean은 orderFee가 없을 수 있음)
            order_fee = 0
            
            trades.append({
                "datetime": order.get("time", ""),
                "symbol": symbol_code.upper(),
                "symbol_name": symbol_code.upper(),
                "side": "buy" if direction == 0 else "sell",
                "price": price,
                "quantity": int(quantity),
                "value": abs(value),
                "commission": order_fee,
                "slippage": 0,
                "pnl": None,
            })
        
        return trades
    
    @classmethod
    def _calculate_symbol_results(cls, trades: List[Dict], symbols: List[str]) -> List[Dict]:
        """종목별 결과 계산
        
        win_rate 계산 방식:
        1. 매수-매도 쌍을 매칭하여 라운드트립 생성
        2. 각 라운드트립의 수익 여부 판단
        3. 수익 라운드트립 / 전체 라운드트립 * 100
        """
        symbol_data = {}
        
        for symbol in symbols:
            symbol_data[symbol.upper()] = {
                "symbol": symbol.upper(),
                "symbol_name": symbol.upper(),
                "sector": "",
                "buy_amount": 0,
                "sell_amount": 0,
                "num_trades": 0,
                "round_trips": [],  # [(buy_value, sell_value), ...]
                "pending_buys": [],  # 아직 매도되지 않은 매수
            }
        
        # 거래를 시간순으로 정렬
        sorted_trades = sorted(trades, key=lambda x: x.get("datetime", ""))
        
        for trade in sorted_trades:
            symbol = trade.get("symbol", "").upper()
            if symbol not in symbol_data:
                symbol_data[symbol] = {
                    "symbol": symbol,
                    "symbol_name": symbol,
                    "sector": "",
                    "buy_amount": 0,
                    "sell_amount": 0,
                    "num_trades": 0,
                    "round_trips": [],
                    "pending_buys": [],
                }
            
            symbol_data[symbol]["num_trades"] += 1
            value = trade.get("value", 0)
            
            if trade.get("side") == "buy":
                symbol_data[symbol]["buy_amount"] += value
                symbol_data[symbol]["pending_buys"].append(value)
            else:  # sell
                symbol_data[symbol]["sell_amount"] += value
                # FIFO 방식으로 매수와 매칭
                if symbol_data[symbol]["pending_buys"]:
                    buy_value = symbol_data[symbol]["pending_buys"].pop(0)
                    symbol_data[symbol]["round_trips"].append((buy_value, value))
        
        results = []
        for data in symbol_data.values():
            buy = data["buy_amount"]
            sell = data["sell_amount"]
            
            if buy > 0:
                return_pct = (sell - buy) / buy * 100
            else:
                return_pct = 0
            
            # win_rate: 라운드트립 기반 정확한 계산
            round_trips = data["round_trips"]
            if round_trips:
                winning_trips = sum(1 for buy_val, sell_val in round_trips if sell_val > buy_val)
                win_rate = (winning_trips / len(round_trips)) * 100
            else:
                # 라운드트립이 없으면 전체 수익률 기반 추정
                win_rate = 100.0 if return_pct > 0 else 0.0 if return_pct < 0 else 0.0
            
            results.append({
                "symbol": data["symbol"],
                "symbol_name": data["symbol_name"],
                "sector": data["sector"],
                "total_return_pct": round(return_pct, 2),
                "num_trades": data["num_trades"],
                "win_rate": round(win_rate, 1),
            })
        
        return results
    
    @classmethod
    def _error_response(
        cls,
        error: Optional[str],
        symbols: List[str],
        start_date: str,
        end_date: str,
        initial_capital: float,
        currency: str = "KRW",
    ) -> Dict:
        """에러 응답 생성"""
        return {
            "error": True,
            "message": error or "백테스트 실행 실패",
            "currency": currency,
            "result": {
                "id": f"bt_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "ran_at": datetime.now().isoformat(),
                "duration_seconds": 0,
                "statistics": {
                    "total_return": 0,
                    "total_return_pct": 0,
                    "cagr": 0,
                    "sharpe_ratio": 0,
                    "sortino_ratio": 0,
                    "max_drawdown": 0,
                    "max_drawdown_pct": 0,
                    "num_trades": 0,
                    "win_rate": 0,
                    "profit_factor": 0,
                    "avg_trade_return": 0,
                    "total_commission": 0,
                    "total_slippage": 0,
                    "total_cost": 0,
                },
                "equity_curve": [],
                "equity_dates": [],
                "drawdown_curve": [],
                "trades": [],
                "symbol_results": [
                    {
                        "symbol": symbol.upper(),
                        "symbol_name": symbol.upper(),
                        "sector": "",
                        "total_return_pct": 0,
                        "num_trades": 0,
                        "win_rate": 0,
                    }
                    for symbol in symbols
                ],
                "charts": {},
            },
            "data_range": {
                "start": start_date,
                "end": end_date,
                "symbols_used": len(symbols),
            },
        }
