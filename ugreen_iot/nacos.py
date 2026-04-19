"""Nacos 登录 / 实例查询 / 权重调整（替代 `utils/ipc_nacos.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import json
from typing import Any, Dict, List, Optional

from common.http_client import HttpClient
from common.logger import get_logger
from common.signing.ecc_ugreen import ascii_sort

_logger = get_logger(__name__)

_DEFAULT_NACOS = {
    "url": "http://47.113.118.66:8848",
    "username": "nacos",
    "password": "wz944308K2i41",
    "service_name": "ugreen-dpt-metadata-consumer",
    "group_name": "DPT_GROUP_dev",
}


class NacosClient:
    def __init__(
        self,
        *,
        base_url: str = _DEFAULT_NACOS["url"],
        username: str = _DEFAULT_NACOS["username"],
        password: str = _DEFAULT_NACOS["password"],
        service_name: str = _DEFAULT_NACOS["service_name"],
        group_name: str = _DEFAULT_NACOS["group_name"],
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.service_name = service_name
        self.group_name = group_name
        self.client = HttpClient(self.base_url)
        self.form_headers = {"Content-Type": "application/x-www-form-urlencoded"}

    def login(self) -> str:
        resp = self.client.post(
            "/nacos/v1/auth/users/login",
            headers=self.form_headers,
            data={"username": self.username, "password": self.password},
        )
        return resp.json()["accessToken"]

    def get_instances(self, *, page_size: int = 10, page_no: int = 1) -> List[Dict[str, Any]]:
        data = {
            "accessToken": self.login(),
            "serviceName": self.service_name,
            "pageSize": page_size,
            "pageNo": page_no,
            "clusterName": "DEFAULT",
            "groupName": self.group_name,
        }
        path = "/nacos/v1/ns/catalog/instances?" + ascii_sort(data)
        resp = self.client.get(path, headers=self.form_headers)
        if resp.status_code != 200:
            _logger.warning("Nacos 请求失败: %s", resp.status_code)
            return []
        payload = resp.json()
        return payload.get("list", []) if payload.get("count", 0) > 0 else []

    def set_weight(self, weight: int = 10) -> None:
        access_token = self.login()
        for data in self.get_instances():
            info = {
                "weight": weight,
                "groupName": self.group_name,
                "ip": data["ip"],
                "port": data["port"],
                "serviceName": self.service_name,
                "clusterName": data["clusterName"],
                "ephemeral": data["ephemeral"],
                "enabled": data["enabled"],
                "metadata": json.dumps(data["metadata"], separators=(",", ":")),
            }
            resp = self.client.put(
                f"/nacos/v1/ns/instance?&accessToken={access_token}",
                headers=self.form_headers,
                data=info,
            )
            _logger.info("setWeight: %s", resp.text)


if __name__ == "__main__":
    NacosClient()
