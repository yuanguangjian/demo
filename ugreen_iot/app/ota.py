"""OTA 检测升级（合并 `utils/ipc_ota.py` 与 `utils/ugreen_software.py`）。"""
from __future__ import annotations

import _demo_syspath  # noqa: F401

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from typing import Any, Dict, Optional

from common.config import env_base_url
from common.http_client import HttpClient

class Ota:
    def __init__(self, env: str) -> None:
        self.env = env
        self.client = HttpClient(env_base_url(env))
        self.headers: Dict[str, str] = {
            "content-type": "application/json",
            "x-ugreen-app-system": "ios",
            "language": "zh-Hans",
        }

    def check(
        self,
        serial_no: str,
        *,
        version_code: int = 0,
        version_name: str = "",
    ) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "POST",
            "/app/v1/software/version/check_upgrade",
            headers=self.headers,
            json_body={
                "serialNo": serial_no,
                "versionCode": version_code,
                "versionName": version_name or serial_no,
            },
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="OTA 检测升级")
    parser.add_argument(
        "--env",
        default="test",
        help="env.json 中的环境名（如 dev/test/ces）",
    )
    parser.add_argument(
        "serial",
        nargs="?",
        default="010001",
        help="设备序列号",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只校验 env.json 并打印 base URL，不发起 HTTP",
    )
    args = parser.parse_args()
    ota = Ota(args.env)
    if args.dry_run:
        print("env OK:", args.env, "base_url =", ota.client.base_url)
    else:
        print(ota.check(args.serial))
