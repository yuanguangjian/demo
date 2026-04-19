"""设备网关调试 demo。

原 `ipc项目/设备网关.py` 是不完整代码片段（顶层缩进错误），这里补齐为可运行函数 + __main__。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import time
from typing import Dict

from common.http_client import HttpClient
from common.logger import get_logger
from common.signing.ecc_ugreen import sign as ecc_sign

_logger = get_logger(__name__)


def call_device_ts(
    *,
    sn: str,
    mac: str,
    product_model: str,
    version: str,
    private_key: str,
    endpoint: str = "http://localhost:9020/app/v1/software/ts",
) -> None:
    """模拟设备端请求 `/app/v1/software/ts`：构造 `x-ugreen-*` 签名头并 GET。"""
    headers: Dict[str, str] = {
        "x-ugreen-sn": sn,
        "x-ugreen-mac": mac,
        "x-ugreen-nonce": str(int(time.time())),
        "x-ugreen-version": version,
        "x-ugreen-model": product_model,
        "x-ugreen-timestamp": str(int(time.time())),
    }
    headers["x-ugreen-signature"] = ecc_sign(headers, private_key)
    with HttpClient() as client:
        resp = client.get(endpoint, headers=headers)
    _logger.info("%s -> %s %s", endpoint, resp.status_code, resp.text[:200])


if __name__ == "__main__":
    call_device_ts(
        sn="I50000U57Q200017",
        mac="I50000U57Q200017",
        product_model="Camera001",
        version="1.0.0",
        private_key="REPLACE_ME",
    )
