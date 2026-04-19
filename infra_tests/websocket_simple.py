"""简易 WebSocket 多连接 demo（原 `websocket_demo1.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import asyncio
import signal
from typing import Set

import websockets

from common.logger import get_logger

_logger = get_logger(__name__)

_active: Set = set()
_close_event = asyncio.Event()


async def _hold_connection(uri: str, connection_id: int) -> None:
    try:
        async with websockets.connect(uri) as ws:
            _logger.info("connection %s established", connection_id)
            _active.add(ws)
            await _close_event.wait()
            _active.discard(ws)
    except Exception as e:
        _logger.error("connection %s failed: %s", connection_id, e)


async def run(uri: str, total: int) -> None:
    def handle_signal(signum, frame):  # type: ignore[no-untyped-def]
        _logger.info("received %s, closing...", signum)
        _close_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, handle_signal)

    tasks = [_hold_connection(uri, i) for i in range(total)]
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(run("ws://localhost:8080/ws/xx", total=1000))
