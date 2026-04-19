"""绿联设备侧业务签名：ASCII 排序 + ECC 签名，写入 `x-ugreen-*` 请求头。

历史实现分散在 `ipc_gateway_device.py`、`ipc_bind.py` 等多处，这里做一次抽取。
"""
from __future__ import annotations

import time
import uuid
from typing import Any, Dict

from ..crypto.ecc import sign as ecdsa_sign

__all__ = ["ascii_sort", "sign", "build_ugreen_headers"]


def ascii_sort(params: Dict[str, Any]) -> str:
    """按 key 的 ASCII 升序拼接 `k=v&...`，跳过"空"值（保持与 Java 侧一致的 `if v` 语义）。"""
    items = sorted((k, v) for k, v in params.items() if v and str(v).strip() != "")
    return "&".join(f"{k}={v}" for k, v in items)


def sign(params: Dict[str, Any], private_key_b64: str) -> str:
    """对请求参数做 ASCII 排序后 ECDSA(SHA-256) 签名。"""
    return ecdsa_sign(ascii_sort(params), private_key_b64)


def build_ugreen_headers(
    params: Dict[str, Any],
    private_key_b64: str,
    *,
    app_id: str = "",
    nonce: str = "",
    timestamp_ms: int = 0,
    extra: Dict[str, str] | None = None,
) -> Dict[str, str]:
    """根据参数与私钥，生成带 `x-ugreen-*` 签名的标准请求头。"""
    ts = str(timestamp_ms or int(time.time() * 1000))
    nonce_val = nonce or uuid.uuid4().hex
    enriched = {**params, "nonce": nonce_val, "timestamp": ts}
    signature = sign(enriched, private_key_b64)
    headers = {
        "Content-Type": "application/json",
        "x-ugreen-nonce": nonce_val,
        "x-ugreen-timestamp": ts,
        "x-ugreen-sign": signature,
    }
    if app_id:
        headers["x-ugreen-appid"] = app_id
    if extra:
        headers.update(extra)
    return headers
