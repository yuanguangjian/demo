"""App 侧联系人/标签接口（取自 `utils/ipc_contact.py`）。

- 普通标签接口：HTTP + Bearer。
- getOpenIdByLabel / getDeviceAllOpenId：需要 ECC 业务签名。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import time
from typing import Any, Dict, Optional

from common.config import env_base_url
from common.http_client import HttpClient
from common.logger import get_logger
from common.signing.ecc_ugreen import sign as ecc_sign
from common.utils.json_store import get_sn_secret

_logger = get_logger(__name__)

_DEFAULT_BEARER = (
    "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"
    ".eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIxMzAyMDAwIiwiVVNFUl9DT1VOVFJZX0NPREUiOiJDTiIsImp0aSI6IjEzMDIwMDAiLCJpYXQiOjE3NjUzMzA2NjIsImV4cCI6MTc2NTQ1MDY2Mn0"
    ".5tC1LXWw7lhYXm2Duf5k9Nyv7gqrFbr4skQkryedizM"
)


class Contact:
    def __init__(self, env: str, *, bearer: str = _DEFAULT_BEARER) -> None:
        self.env = env
        self.client = HttpClient(env_base_url(env))
        self.headers: Dict[str, str] = {
            "content-type": "application/json",
            "x-ugreen-app-system": "ios",
            "language": "zh-Hans",
            "Authorization": bearer,
        }

    def get_all_labels(self) -> Optional[Dict[str, Any]]:
        return self.client.request_json("GET", "/app/v1/variety/contact/getAllLabels", headers=self.headers)

    def get_user_labels(self, sn: str, model: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "GET",
            f"/app/v1/variety/contact/getUserLabels?productSerialNo={model}&deviceUniqueCode={sn}",
            headers=self.headers,
        )

    def set_label(self, sn: str, model: str, code: str, user_id: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "POST",
            "/app/v1/variety/contact/setLabel",
            headers=self.headers,
            json_body={"productSerialNo": model, "deviceUniqueCode": sn, "code": code, "userId": user_id},
        )

    def del_label(self, sn: str, model: str, code: str, user_id: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "POST",
            "/app/v1/variety/contact/delLabel",
            headers=self.headers,
            json_body={"productSerialNo": model, "deviceUniqueCode": sn, "code": code, "userId": user_id},
        )

    def _build_signed(self, sn: str, model: str) -> Optional[Dict[str, Any]]:
        info = get_sn_secret(model, sn, self.env)
        if not info:
            _logger.warning("密钥不存在：%s/%s", model, sn)
            return None
        data = {
            "productModel": model,
            "sn": sn,
            "mac": sn,
            "nonce": int(time.time() * 1000),
            "version": info["version"],
        }
        data["sign"] = ecc_sign(data, info["privateKey"])
        return data

    def get_open_id_by_label(self, sn: str, model: str, label: str) -> Optional[Dict[str, Any]]:
        data = self._build_signed(sn, model)
        if not data:
            return None
        data["label"] = label
        return self.client.request_json(
            "POST", "/app/v1/variety/contact/getOpenIdByLabel", headers=self.headers, json_body=data
        )

    def get_device_all_open_id(self, sn: str, model: str) -> Optional[Dict[str, Any]]:
        data = self._build_signed(sn, model)
        if not data:
            return None
        return self.client.request_json(
            "POST", "/app/v1/variety/contact/getDeviceAllOpenId", headers=self.headers, json_body=data
        )


if __name__ == "__main__":
    Contact("dvt").get_all_labels()
