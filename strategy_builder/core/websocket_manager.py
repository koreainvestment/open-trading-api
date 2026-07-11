"""
실시간 호가 웹소켓 관리 모듈

Note: 현재 KIS WebSocket 완전 연동은 추가 구현 필요
      REST API 호가 조회는 정상 작동
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Set

from core import data_fetcher

logging.basicConfig(level=logging.INFO)


class OrderbookWebSocketManager:
    """
    실시간 호가 웹소켓 관리자

    현재는 폴링(polling) 방식으로 REST API를 주기적으로 호출하여
    실시간 호가를 시뮬레이션합니다.

    TODO: KIS WebSocket (H0UNASP0) 완전 연동
    """

    def __init__(self):
        self.subscriptions: Dict[str, Set] = {}  # {stock_code: {client_websockets}}
        self.running = False
        self.polling_tasks: Dict[str, asyncio.Task] = {}  # {stock_code: polling_task}

    async def start(self):
        """웹소켓 매니저 시작"""
        if self.running:
            return

        self.running = True
        logging.info("Orderbook WebSocket Manager 시작 (polling mode)")

    async def stop(self):
        """웹소켓 매니저 종료"""
        self.running = False

        # 모든 폴링 태스크 취소
        for task in self.polling_tasks.values():
            task.cancel()

        self.polling_tasks.clear()
        self.subscriptions.clear()
        logging.info("Orderbook WebSocket Manager 종료")

    async def subscribe_orderbook(self, stock_code: str, client_ws):
        """
        실시간 호가 구독

        Args:
            stock_code: 종목코드
            client_ws: 클라이언트 웹소켓
        """
        if stock_code not in self.subscriptions:
            self.subscriptions[stock_code] = set()

            # 폴링 태스크 시작 (1초마다 호가 조회)
            task = asyncio.create_task(
                self._polling_loop(stock_code)
            )
            self.polling_tasks[stock_code] = task
            logging.info(f"호가 구독 시작 (polling): {stock_code}")

        # 클라이언트 추가
        self.subscriptions[stock_code].add(client_ws)
        logging.info(f"클라이언트 추가: {stock_code} (총 {len(self.subscriptions[stock_code])}명)")

    async def unsubscribe_orderbook(self, stock_code: str, client_ws):
        """
        구독 해제

        Args:
            stock_code: 종목코드
            client_ws: 클라이언트 웹소켓
        """
        if stock_code not in self.subscriptions:
            return

        # 클라이언트 제거
        self.subscriptions[stock_code].discard(client_ws)
        logging.info(f"클라이언트 제거: {stock_code} (남은 {len(self.subscriptions[stock_code])}명)")

        # 구독자가 없으면 폴링 중단
        if len(self.subscriptions[stock_code]) == 0:
            if stock_code in self.polling_tasks:
                self.polling_tasks[stock_code].cancel()
                del self.polling_tasks[stock_code]
                logging.info(f"호가 구독 해제: {stock_code}")

            del self.subscriptions[stock_code]

    async def _polling_loop(self, stock_code: str):
        """
        호가 폴링 루프 (REST API 주기 호출)

        Args:
            stock_code: 종목코드
        """
        while self.running and stock_code in self.subscriptions:
            try:
                # REST API로 호가 조회
                orderbook = data_fetcher.get_orderbook(stock_code, env_dv="vps")

                if orderbook:
                    # 클라이언트에게 전달
                    orderbook_data = {
                        "type": "orderbook",
                        "stock_code": stock_code,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "data": {
                            "current_price": orderbook.get("current_price"),
                            "ask_prices": orderbook["ask_prices"],
                            "ask_volumes": orderbook["ask_volumes"],
                            "bid_prices": orderbook["bid_prices"],
                            "bid_volumes": orderbook["bid_volumes"],
                            "total_ask_volume": orderbook["total_ask_volume"],
                            "total_bid_volume": orderbook["total_bid_volume"],
                        }
                    }

                    # 모든 구독 클라이언트에게 전달
                    clients = list(self.subscriptions.get(stock_code, []))
                    for client_ws in clients:
                        try:
                            await client_ws.send_json(orderbook_data)
                        except Exception as e:
                            logging.error(f"클라이언트 전송 실패: {e}")
                            # 연결이 끊긴 클라이언트 제거
                            await self.unsubscribe_orderbook(stock_code, client_ws)

                # 1초 대기
                await asyncio.sleep(1)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"폴링 에러 ({stock_code}): {e}")
                await asyncio.sleep(1)


# 글로벌 웹소켓 매니저 인스턴스
_ws_manager = None


def get_ws_manager() -> OrderbookWebSocketManager:
    """웹소켓 매니저 싱글톤 인스턴스 반환"""
    global _ws_manager

    if _ws_manager is None:
        _ws_manager = OrderbookWebSocketManager()

    return _ws_manager
