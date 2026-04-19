"""WMS 入库 SN 查询接口（MD5 签名）。

合并 `utils/ipc_snIT_sync.py` 与 `ipc项目/sn扫码.py`。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from typing import Any, Dict, Optional

from common.http_client import HttpClient
from common.logger import get_logger
from common.signing.md5_wms import md5_sign
import time

_logger = get_logger(__name__)

_CONFIG: Dict[str, Dict[str, str]] = {
    "dev": {
        "url": "https://test.ugreensmart.com/backend/d-wms/Api/OpenInbound/GetSNInboundRecordList",
        "appId": "UGTest001",
        "appKey": "dgugreenTest001",
    },
    "pro": {
        "url": "https://www.ugreensmart.com/backend/d-wms/Api/OpenInbound/GetSNInboundRecordList",
        "appId": "UG_pro_inner_001",
        "appKey": "dw#9DF4d2do&idwk24oaRTjdfEoijDeaw00I",
    },
}


class WmsSn:
    def __init__(self, env: str) -> None:
        if env not in _CONFIG:
            raise KeyError(f"wms 环境 '{env}' 未定义，可选：{list(_CONFIG)}")
        cfg = _CONFIG[env]
        self.env = env
        self.url = cfg["url"]
        self.app_id = cfg["appId"]
        self.app_key = cfg["appKey"]
        self.client = HttpClient()

    def _build_headers(self) -> Dict[str, str]:
        """原脚本用 `u-stamp`（秒）+ `u-secret`，与通用 `build_wms_headers` 略有差别。"""
        ts = int(time.time())
        return {
            "Content-Type": "application/json",
            "u-appid": self.app_id,
            "u-stamp": str(ts),
            "u-secret": md5_sign(self.app_id, self.app_key, ts),
        }

    def query(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        _logger.info("WMS 请求：%s %s", self.url, data)
        return self.client.request_json("POST", self.url, headers=self._build_headers(), json_body=data)


if __name__ == "__main__":
    WmsSn("pro").query(
        {
            "ProductNos": ["ID500 Pro"],
            "LastDateStart": "2025-11-19 00:00:00",
            "LastDateEnd": "2025-11-26 00:00:00",
            "PageSize": "100",
            "Page": "1",
        }
    )
