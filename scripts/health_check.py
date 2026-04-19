"""简易 HTTP 健康检查（原 `ipc项目/xxxaaaaa.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import argparse

from common.http_client import HttpClient
from common.logger import get_logger

_logger = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="单次请求健康检查")
    parser.add_argument("url", nargs="?", default="https://dev3.ugreeniot.com/metadata/v1/factory/getSn?mac=BC:AD:AE:C8:17:E7")
    args = parser.parse_args()

    client = HttpClient(timeout=10.0)
    resp = client.request("GET", args.url)
    _logger.info("status=%s body=%s", resp.status_code, resp.text)


if __name__ == "__main__":
    main()
