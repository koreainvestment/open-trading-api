"""websocket_manager 단위 테스트 - env_dv 버그 수정 검증"""

import pytest

from core.websocket_manager import OrderbookWebSocketManager


@pytest.fixture
def manager():
    return OrderbookWebSocketManager()


class FakeWebSocket:
    def __init__(self):
        self.sent = []

    async def send_json(self, data):
        self.sent.append(data)


@pytest.mark.asyncio
async def test_subscribe_stores_env_mode(manager):
    ws = FakeWebSocket()
    await manager.subscribe_orderbook("005930", ws, env_dv="prod")
    assert manager.env_modes["005930"] == "prod"


@pytest.mark.asyncio
async def test_subscribe_default_env_is_vps(manager):
    ws = FakeWebSocket()
    await manager.subscribe_orderbook("005930", ws)
    assert manager.env_modes["005930"] == "vps"


@pytest.mark.asyncio
async def test_unsubscribe_cleans_env_mode(manager):
    ws = FakeWebSocket()
    manager.running = True
    await manager.subscribe_orderbook("005930", ws, env_dv="prod")
    await manager.unsubscribe_orderbook("005930", ws)
    assert "005930" not in manager.env_modes


@pytest.mark.asyncio
async def test_multiple_clients_share_env_mode(manager):
    ws1, ws2 = FakeWebSocket(), FakeWebSocket()
    manager.running = True
    await manager.subscribe_orderbook("005930", ws1, env_dv="prod")
    await manager.subscribe_orderbook("005930", ws2, env_dv="vps")
    # env_dv is set by the first subscriber
    assert manager.env_modes["005930"] == "prod"
    assert len(manager.subscriptions["005930"]) == 2
