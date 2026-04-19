"""绿联 WMS 入库接口 MD5 签名头。

原实现见 `utils/ipc_snIT_sync.py` 与 `ipc项目/sn扫码.py`。
"""
from __future__ import annotations

import hashlib
import time
from typing import Dict

__all__ = ["build_wms_headers", "md5_sign"]


def md5_sign(app_id: str, app_key: str, timestamp_ms: int) -> str:
    raw = f"{app_id}{app_key}{timestamp_ms}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def build_wms_headers(app_id: str, app_key: str) -> Dict[str, str]:
    ts = int(time.time() * 1000)
    return {
        "u-appid": app_id,
        "u-timestamp": str(ts),
        "u-sign": md5_sign(app_id, app_key, ts),
        "Content-Type": "application/json",
    }
