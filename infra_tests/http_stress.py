"""HTTP 并发压测（合并 `utils/threadxx.py` + `utils/threadxx2.py`）。

两种模式：
- `run_fixed_count(url, total)` - 固定总请求数；原 `threadxx.py` 的流程。
- `run_duration(url, concurrency, duration)` - 持续时间 + 最大并发；原 `threadxx2.py` 的流程。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import asyncio
import sys
import time

import aiohttp

from common.logger import get_logger

_logger = get_logger(__name__)


async def _call(session: aiohttp.ClientSession, url: str, task_id: int) -> int:
    try:
        async with session.get(url) as resp:
            return resp.status
    except Exception as e:
        _logger.error("task %s error: %s", task_id, e)
        return -1


async def run_fixed_count(url: str, *, total: int = 1000) -> None:
    start = time.time()
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[_call(session, url, i) for i in range(total)])
    _logger.info("前 10 结果: %s", results[:10])
    _logger.info("总耗时：%.2fs", time.time() - start)


async def run_duration(url: str, *, concurrency: int = 2000, duration: float = 30.0) -> None:
    start = time.time()
    counter = {"id": 0, "done": 0}
    semaphore = asyncio.Semaphore(concurrency)

    async def limited(session: aiohttp.ClientSession) -> None:
        async with semaphore:
            tid = counter["id"]
            counter["id"] += 1
            await _call(session, url, tid)
            counter["done"] += 1

    async with aiohttp.ClientSession() as session:
        pending: set = set()
        while time.time() - start < duration:
            pending.add(asyncio.create_task(limited(session)))
            await asyncio.sleep(0)
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)

    _logger.info("总耗时：%.2fs, 已完成：%s / %s", time.time() - start, counter["done"], counter["id"])


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "fixed"
    target = "http://192.168.75.132:8080/getKey?key=name&value=hello"
    if mode == "fixed":
        asyncio.run(run_fixed_count(target, total=1000))
    else:
        asyncio.run(run_duration(target, concurrency=2000, duration=30.0))
