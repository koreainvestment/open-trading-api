"""
시장 정보 API 라우터
"""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from core import data_fetcher
from core.websocket_manager import get_ws_manager
from backend import authenticate, is_authenticated

logging.basicConfig(level=logging.INFO)

router = APIRouter()


def ensure_authenticated(env_dv: str = "vps") -> bool:
    """인증 상태 확인 후 필요시 인증 시도"""
    if is_authenticated():
        return True
    # 인증되지 않았으면 인증 시도
    return authenticate(env_dv)


@router.get("/orderbook/{stock_code}")
async def get_orderbook(
    stock_code: str,
    env_dv: str = Query("demo", description="환경 구분 (real/demo/prod/vps)")
):
    """
    호가 조회 REST API

    Args:
        stock_code: 종목코드 (6자리)
        env_dv: 환경 구분

    Returns:
        {
            "status": "success" | "error",
            "data": {
                "stock_code": str,
                "stock_name": str,
                "current_price": int,
                "ask_prices": list[int],
                "ask_volumes": list[int],
                "bid_prices": list[int],
                "bid_volumes": list[int],
                "total_ask_volume": int,
                "total_bid_volume": int,
                "expected_price": int,
                "expected_volume": int
            }
        }
    """
    try:
        # 인증 확인/시도
        if not ensure_authenticated(env_dv):
            return {
                "status": "error",
                "message": "KIS API 인증 필요"
            }
        
        orderbook = data_fetcher.get_orderbook(stock_code, env_dv)

        if not orderbook:
            return {
                "status": "error",
                "message": f"호가 조회 실패: {stock_code}"
            }

        return {
            "status": "success",
            "data": orderbook
        }

    except Exception as e:
        logging.error(f"호가 조회 에러: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/price/{stock_code}")
async def get_current_price(
    stock_code: str,
    env_dv: str = Query("demo", description="환경 구분 (real/demo/prod/vps)")
):
    """
    현재가 조회 REST API (등락 정보 포함)

    Args:
        stock_code: 종목코드 (6자리)
        env_dv: 환경 구분

    Returns:
        {
            "status": "success" | "error",
            "data": {
                "price": int,        # 현재가
                "change": int,       # 전일대비
                "change_rate": float, # 전일대비율(%)
                "high": int,         # 고가
                "low": int,          # 저가
                "volume": int,       # 거래량
                "w52_high": int,     # 52주 최고가
                "w52_low": int       # 52주 최저가
            }
        }
    """
    try:
        # 인증 확인/시도
        if not ensure_authenticated(env_dv):
            return {
                "status": "error",
                "message": "KIS API 인증 필요"
            }

        price_data = data_fetcher.get_current_price(stock_code, env_dv)

        if not price_data:
            return {
                "status": "error",
                "message": f"현재가 조회 실패: {stock_code}"
            }

        return {
            "status": "success",
            "data": price_data
        }

    except Exception as e:
        logging.error(f"현재가 조회 에러: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@router.websocket("/ws/{stock_code}")
async def websocket_orderbook(websocket: WebSocket, stock_code: str):
    """
    실시간 호가 웹소켓

    Args:
        websocket: WebSocket 연결
        stock_code: 종목코드

    Message Format (Server → Client):
        {
            "type": "orderbook",
            "stock_code": str,
            "timestamp": str,
            "data": {
                "ask_prices": list[int],
                "ask_volumes": list[int],
                "bid_prices": list[int],
                "bid_volumes": list[int],
                "total_ask_volume": int,
                "total_bid_volume": int
            }
        }
    """
    await websocket.accept()
    logging.info(f"WebSocket 연결: {stock_code}")

    ws_manager = get_ws_manager()

    # 웹소켓 매니저 시작 (처음 연결 시)
    if not ws_manager.running:
        try:
            await ws_manager.start()
        except Exception as e:
            logging.error(f"WebSocket 매니저 시작 실패: {e}")
            await websocket.close(code=1011, reason="Internal error")
            return

    # 호가 구독
    try:
        await ws_manager.subscribe_orderbook(stock_code, websocket)
    except Exception as e:
        logging.error(f"호가 구독 실패: {e}")
        await websocket.close(code=1011, reason="Subscription failed")
        return

    try:
        # 연결 유지 (클라이언트 메시지 수신)
        while True:
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break

    except Exception as e:
        logging.error(f"WebSocket 에러: {e}")

    finally:
        # 구독 해제
        await ws_manager.unsubscribe_orderbook(stock_code, websocket)
        logging.info(f"WebSocket 연결 종료: {stock_code}")
