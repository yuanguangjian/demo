"""Consumer 侧客户端：App 校验 SN / 获取元数据 / 更新密钥 / 切换状态。

取自 `utils/ipc_consumer_api.py`（裸 requests 统一走 HttpClient）。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import time
from typing import Any, Dict, Optional

from common.config import env_base_url, load_json
from common.crypto.ecc import gen_key
from common.http_client import HttpClient
from common.logger import get_logger
from common.signing.ecc_ugreen import ascii_sort, sign as ecc_sign
from common.utils.json_store import get_sn_secret, save_sn_secret

_logger = get_logger(__name__)


class Consumer:
    def __init__(self, env: str) -> None:
        self.env = env
        self.client = HttpClient(env_base_url(env))
        self.headers: Dict[str, str] = {
            "x-ugreen-app-system": "ios",
            "content-type": "application/json",
            "countryCode": "CN",
            "language": "zh-Hans",
        }

    def _read_sn(self, sn: str, product_model: str) -> Optional[Dict[str, Any]]:
        info = get_sn_secret(product_model, sn, self.env)
        if not info:
            _logger.warning("密钥不存在：%s/%s", product_model, sn)
        return info

    def check_sn(self, sn: str, product_model: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "POST",
            "/app/v1/variety/checkSn",
            headers=self.headers,
            json_body={"sn": sn, "productSerialNo": product_model},
        )

    def _build_signed(self, sn: str, product_model: str, *, use_serial_no: bool = False) -> Optional[Dict[str, Any]]:
        info = self._read_sn(sn, product_model)
        if not info:
            return None
        key = "productSerialNo" if use_serial_no else "productModel"
        data: Dict[str, Any] = {
            "mac": sn,
            "nonce": int(time.time() * 1000),
            key: product_model,
            "sn": sn,
            "version": info["version"],
        }
        if use_serial_no:
            data["deviceType"] = "card"
        data["sign"] = ecc_sign(data, info["privateKey"])
        return data

    def get_meta(self, sn: str, product_model: str) -> Optional[Dict[str, Any]]:
        data = self._build_signed(sn, product_model, use_serial_no=True)
        if not data:
            return None
        return self.client.request_json("POST", "/app/v1/variety/getMeta", headers=self.headers, json_body=data)

    def check_sign(self, sn: str, product_model: str) -> Optional[Dict[str, Any]]:
        data = self._build_signed(sn, product_model)
        if not data:
            return None
        return self.client.request_json("POST", "/app/v1/variety/checkSign", headers=self.headers, json_body=data)

    def get_sn_secret(self, sn: str, product_model: str) -> Optional[Dict[str, Any]]:
        data = self._build_signed(sn, product_model)
        if not data:
            return None
        return self.client.request_json("POST", "/app/v1/variety/getSnSecret", headers=self.headers, json_body=data)

    def update_sn_secret(self, sn: str, product_model: str, new_version: str = "1.0.1") -> Optional[Dict[str, Any]]:
        info = self._read_sn(sn, product_model)
        if not info:
            return None
        new_private, new_public = gen_key()
        data = {
            "mac": sn,
            "nonce": int(time.time() * 1000),
            "productModel": product_model,
            "sn": sn,
            "oldVersion": info["version"],
            "publicKey": new_public,
            "version": new_version,
        }
        data["sign"] = ecc_sign(data, info["privateKey"])
        result = self.client.request_json(
            "POST", "/app/v1/variety/updateSnSecret", headers=self.headers, json_body=data
        )
        if result and result.get("code") == 100000:
            save_sn_secret(
                f"{product_model}_{sn}",
                {"privateKey": new_private, "publicKey": new_public, "version": new_version},
                self.env,
            )
        return result

    def switch_state(self, sn: str, product_model: str, *, factory_url: str) -> Optional[Dict[str, Any]]:
        """原实现直接裸 `requests.post`，这里改用独立 HttpClient。"""
        info = self._read_sn(sn, product_model)
        if not info:
            return None
        data = {
            "mac": sn,
            "nonce": int(time.time() * 1000),
            "productModel": product_model,
            "sn": sn,
            "version": info["version"],
        }
        data["sign"] = ecc_sign(data, info["privateKey"])

        secret = load_json("factory.json").get("dev", {})
        data["clientId"] = secret.get("AppId", "")
        data["timestamp"] = str(int(time.time() * 1000))
        data["clientSign"] = ecc_sign(data, secret.get("AppSecret", ""))

        with HttpClient() as factory_client:
            return factory_client.request_json(
                "POST", factory_url, headers=self.headers, json_body=data
            )


if __name__ == "__main__":
    c = Consumer("device")
    c.update_sn_secret("I50000U57Q200017", "00000")
