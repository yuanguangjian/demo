"""MySQL 客户端（合并 `utils/ipc_db.py` 与 `ipc项目/mysqlUtil.py`）。

- 优先从 `mysql.json` 读取配置（与历史实现一致）。
- 硬编码默认配置仍保留（后续迁 .env），但**仅作为 fallback**。
- 查询方法改为参数化：`execute(sql, params)`，消除 f-string 拼 SQL 的注入面。
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import mysql.connector

from ..config import load_json
from ..logger import get_logger

_logger = get_logger(__name__)

# 后备配置：mysql.json 缺失时使用。请尽快迁 .env。
_FALLBACK_CONFIG: Dict[str, Dict[str, Any]] = {
    "dev": {
        "host": "rm-wz9h6s898dole0ubjoo.mysql.rds.aliyuncs.com",
        "user": "ugreen_dev",
        "password": "AXwer!@#$!$@123",
        "port": 3306,
    },
    "test": {
        "host": "rm-wz9h6s898dole0ubjoo.mysql.rds.aliyuncs.com",
        "user": "ugreen_test",
        "password": "AXwer!@#$!$@123",
        "port": 3306,
    },
    "dvt": {
        "host": "rm-wz9h6s898dole0ubjoo.mysql.rds.aliyuncs.com",
        "user": "ugreen_dvt",
        "password": "VuX771t!iNniH9DB",
        "port": 3306,
    },
}


def get_env_config(env: str) -> Dict[str, Any]:
    """按环境名加载连接配置（不含 database，由调用方补上）。"""
    envs = load_json("mysql.json") or _FALLBACK_CONFIG
    if env not in envs:
        raise KeyError(f"mysql 环境 '{env}' 未定义，可选：{list(envs)}")
    return dict(envs[env])


class MySQLClient:
    """参数化 SQL 封装。不要再用 f-string 拼 SQL。"""

    def __init__(self, env: str, database: str, **overrides: Any) -> None:
        cfg = get_env_config(env)
        cfg["database"] = database
        cfg.update(overrides)
        self.env = env
        self.database = database
        self.conn = mysql.connector.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            port=cfg.get("port", 3306),
        )
        self.cursor = self.conn.cursor()

    def close(self) -> None:
        try:
            self.cursor.close()
        finally:
            self.conn.close()

    def __enter__(self) -> "MySQLClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def select(self, sql: str, params: Optional[Sequence[Any]] = None) -> List[Dict[str, Any]]:
        """返回 [dict(col=val), ...]，SQL 必须使用 `%s` 占位。"""
        self.cursor.execute(sql, params or ())
        if self.cursor.description is None:
            return []
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def execute(self, sql: str, params: Optional[Sequence[Any]] = None) -> int:
        """执行 INSERT/UPDATE/DELETE，返回受影响行数；失败回滚。"""
        try:
            self.conn.start_transaction()
            self.cursor.execute(sql, params or ())
            affected = self.cursor.rowcount
            self.conn.commit()
            return affected
        except Exception as exc:
            self.conn.rollback()
            _logger.error("SQL 执行失败，已回滚: %s", exc)
            raise

    def executemany(self, sql: str, seq_params: Iterable[Sequence[Any]]) -> int:
        try:
            self.conn.start_transaction()
            self.cursor.executemany(sql, list(seq_params))
            affected = self.cursor.rowcount
            self.conn.commit()
            return affected
        except Exception as exc:
            self.conn.rollback()
            _logger.error("SQL 批量执行失败: %s", exc)
            raise


@contextmanager
def connect(env: str, database: str, **overrides: Any):
    client = MySQLClient(env, database, **overrides)
    try:
        yield client
    finally:
        client.close()


def fetch(env: str, database: str, sql: str, params: Optional[Sequence[Any]] = None) -> List[Dict[str, Any]]:
    with connect(env, database) as client:
        return client.select(sql, params)
