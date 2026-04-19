"""RTCX/阿里云 API 网关风格 HMAC 签名（`x-ca-*` 头）。

取自 `utils/rtcxUtil.py`；`app_key`/`app_secret`/`base_url` 仍由调用方传入，
不在本文件硬编码。
"""
from __future__ import annotations

import base64
import hashlib
import hmac as _hmac
import json
import time
import uuid
from collections import OrderedDict
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

__all__ = [
    "get_gmt_date",
    "content_md5",
    "build_string_to_sign",
    "sign",
    "build_rtcx_headers",
    "default_app_credentials",
]

# 历史默认凭据（请尽快迁移到环境变量/配置中心）。
_DEFAULT_APP_KEY = "PdRWfv0XaeJulQLKPh9GXo4P1"
_DEFAULT_APP_SECRET = "xyJtvem4l1eaqh8Cy17i1AsGAEUaD6d"


def default_app_credentials() -> Tuple[str, str]:
    return _DEFAULT_APP_KEY, _DEFAULT_APP_SECRET


def get_gmt_date(timestamp_ms: int) -> str:
    dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")


def content_md5(body_bytes: bytes) -> str:
    md5_digest = hashlib.md5(body_bytes).digest()
    base64_md5 = base64.b64encode(md5_digest).decode("utf-8")
    return base64_md5[:23] if len(base64_md5) > 24 else base64_md5


def _headers_str(headers: Dict[str, str], signature_headers: str) -> str:
    sb = []
    sorted_headers: "OrderedDict[str, str]" = OrderedDict()
    if signature_headers:
        for key in signature_headers.split(","):
            sorted_headers[key] = headers.get(key, "")
    else:
        sorted_headers.update(headers)
    for k, v in sorted(sorted_headers.items()):
        if not k.lower().startswith("x-ca") or k.lower() in {
            "x-ca-signature-headers",
            "x-ca-signature",
        }:
            continue
        sb.append(f"{k.strip().lower()}:{v.strip() if v else ''}")
    return "\n".join(sb)


def build_string_to_sign(method: str, headers: Dict[str, str], uri: str, body_bytes: bytes) -> str:
    accept = headers.get("Accept", "\n")
    content_type = headers.get("Content-Type", "\n")
    date = headers.get("date") or headers.get("Date", "\n")
    signature_headers = headers.get("x-ca-signature-headers", "")
    parts = [
        method.upper(),
        accept,
        content_md5(body_bytes),
        content_type,
        date,
        _headers_str(headers, signature_headers),
        uri,
    ]
    return "\n".join(parts)


def sign(method: str, secret: str, headers: Dict[str, str], uri: str, body_bytes: bytes) -> str:
    string_to_sign = build_string_to_sign(method, headers, uri, body_bytes)
    mac = _hmac.new(secret.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode("utf-8")


def build_rtcx_headers(
    method: str,
    path: str,
    body_dict: Any,
    *,
    app_key: Optional[str] = None,
    app_secret: Optional[str] = None,
) -> Tuple[Dict[str, str], bytes]:
    """生成完整 `x-ca-*` 签名头 + 序列化后的 body。"""
    ak, sk = app_key or _DEFAULT_APP_KEY, app_secret or _DEFAULT_APP_SECRET
    timestamp = int(time.time() * 1000)
    headers: Dict[str, str] = {
        "x-ca-key": ak,
        "x-ca-timestamp": str(timestamp),
        "x-ca-nonce": str(uuid.uuid4()),
        "Date": get_gmt_date(timestamp),
        "Accept": "application/json; charset=utf-8",
        "Content-Type": "application/octet-stream; charset=utf-8",
        "x-ca-signature-headers": "x-ca-key,x-ca-nonce,x-ca-timestamp",
    }
    body_str = json.dumps(body_dict, separators=(",", ":"))
    body_bytes = body_str.encode("utf-8")
    headers["x-ca-signature"] = sign(method, sk, headers, path, body_bytes)
    return headers, body_bytes
