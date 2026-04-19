"""Redis 客户端小封装。"""
from __future__ import annotations

from typing import Any, Dict

import redis as _redis

from ..logger import get_logger

_logger = get_logger(__name__)


class RedisClient:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.conn = _redis.Redis(
            host=config["host"],
            port=config.get("port", 6379),
            db=config.get("db", 0),
            password=config.get("password"),
            decode_responses=True,
        )

    def __enter__(self) -> "RedisClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        self.conn.close()

    def scan_types(self) -> None:
        """打印所有 key 的类型。谨慎在生产环境使用。"""
        for key in self.conn.scan_iter():
            _logger.info("%s: %s", key, self.conn.type(key))
