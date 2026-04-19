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
    # 需要试跑时改下面两行，再执行本文件。
    env = "test"
    serial_no = "010001"

    ota = Ota(env)
    print(ota.check(serial_no))
