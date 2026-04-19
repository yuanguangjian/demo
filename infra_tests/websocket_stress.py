"""WebSocket 负载测试工具（原 `websocket.py`）。

仅做了：日志切换到 `common.logger`，删除了冗长的 emoji 和重复注释，保持原算法不变。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import argparse
import asyncio
import random
import signal
import sys
import time
from typing import List

import websockets

from common.logger import get_logger

_logger = get_logger(__name__, log_file="websocket_test.log")


_state = {
    "active_connections": 0,
    "failed_connections": 0,
    "connection_times": [],  # type: List[float]
    "message_latencies": [],  # type: List[float]
}


async def connect_websocket(url: str, connection_id: int, message_interval: float, test_duration: float) -> None:
    start_time = time.time()
    try:
        async with websockets.connect(url, ping_interval=20, ping_timeout=60, close_timeout=10) as websocket:
            conn_time = time.time() - start_time
            _state["connection_times"].append(conn_time)
            _state["active_connections"] += 1
            _logger.debug("连接 #%s 已建立，耗时 %.4fs", connection_id, conn_time)

            end_time = start_time + test_duration
            while time.time() < end_time:
                try:
                    msg_send_time = time.time()
                    payload = f"msg-#{connection_id}-{random.randint(1, 10000)}"
                    await websocket.send(payload)
                    await asyncio.wait_for(websocket.recv(), timeout=5)
                    _state["message_latencies"].append(time.time() - msg_send_time)
                    await asyncio.sleep(message_interval * (0.8 + 0.4 * random.random()))
                except asyncio.TimeoutError:
                    _logger.warning("连接 #%s 消息超时", connection_id)
                except websockets.exceptions.ConnectionClosed:
                    _logger.warning("连接 #%s 被服务器关闭", connection_id)
                    _state["active_connections"] -= 1
                    _state["failed_connections"] += 1
                    return
    except (websockets.exceptions.WebSocketException, ConnectionRefusedError, OSError) as e:
        _state["failed_connections"] += 1
        _logger.error("连接 #%s 建立失败: %s", connection_id, e)


async def connection_monitor() -> None:
    last = 0
    while True:
        await asyncio.sleep(1)
        current = _state["active_connections"]
        if current != last:
            _logger.info(
                "当前活跃连接 %s, 失败连接 %s",
                current,
                _state["failed_connections"],
            )
            last = current


async def _delayed_connect(url: str, idx: int, delay: float, message_interval: float, duration: float) -> None:
    await asyncio.sleep(delay)
    await connect_websocket(url, idx, message_interval, duration)


async def create_connections(url: str, num: int, ramp_up: float, interval: float, duration: float) -> None:
    _logger.info("开始测试: 目标 %s 连接, 每个持续 %ss", num, duration)
    asyncio.create_task(connection_monitor())
    per_conn_delay = ramp_up / num if num > 0 else 0
    tasks = [
        asyncio.create_task(
            _delayed_connect(url, i + 1, per_conn_delay * i * (0.9 + 0.2 * random.random()), interval, duration)
        )
        for i in range(num)
    ]
    await asyncio.gather(*tasks)
    _print_results(num, duration)


def _print_results(num: int, duration: float) -> None:
    _logger.info("=" * 50)
    _logger.info("WebSocket 压测结果：目标=%s 失败=%s 持续=%ss", num, _state["failed_connections"], duration)
    times = _state["connection_times"]
    if times:
        _logger.info(
            "连接耗时 avg/max/min = %.4f / %.4f / %.4f s",
            sum(times) / len(times), max(times), min(times),
        )
    latencies = _state["message_latencies"]
    if latencies:
        _logger.info(
            "消息延迟 avg/max/min = %.4f / %.4f / %.4f s",
            sum(latencies) / len(latencies), max(latencies), min(latencies),
        )


def _handle_signal(sig, frame):  # type: ignore[no-untyped-def]
    _logger.info("收到中断信号 %s，停止测试", sig)
    _print_results(0, 0)
    sys.exit(0)


async def main() -> None:
    parser = argparse.ArgumentParser(description="WebSocket 连接负载测试")
    parser.add_argument("url", help="WebSocket URL (ws://... 或 wss://...)")
    parser.add_argument("-n", "--connections", type=int, default=2000)
    parser.add_argument("-r", "--ramp-up", type=float, default=30.0)
    parser.add_argument("-d", "--duration", type=float, default=60.0)
    parser.add_argument("-i", "--interval", type=float, default=5.0)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        _logger.setLevel("DEBUG")

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    await create_connections(args.url, args.connections, args.ramp_up, args.interval, args.duration)


if __name__ == "__main__":
    asyncio.run(main(), debug=False)
