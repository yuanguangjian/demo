"""Elasticsearch 简单 `_bulk` 写入工具。"""
from __future__ import annotations

import json
import random
from typing import Any, Dict, Iterable, List

import requests

from ..logger import get_logger

_logger = get_logger(__name__)


def build_bulk_payload(actions: Iterable[Dict[str, Any]]) -> str:
    """把 `[{"_index":..,"_id":..,"_source":{...}}]` 打包成 NDJSON。"""
    lines: List[str] = []
    for action in actions:
        meta = {"index": {"_index": action["_index"], "_id": action["_id"]}}
        lines.append(json.dumps(meta))
        lines.append(json.dumps(action["_source"]))
    return "\n".join(lines) + "\n"


def bulk_index(es_host: str, actions: Iterable[Dict[str, Any]], *, timeout: float = 30.0) -> bool:
    payload = build_bulk_payload(actions)
    headers = {"Content-Type": "application/x-ndjson"}
    resp = requests.post(f"{es_host}/_bulk", headers=headers, data=payload, timeout=timeout)
    if resp.status_code < 300:
        return True
    _logger.error("_bulk 失败: %s %s", resp.status_code, resp.text[:200])
    return False


def random_choice(seq):
    return random.choice(seq)
