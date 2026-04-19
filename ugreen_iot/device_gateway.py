"""设备网关客户端：用设备 SN 密钥做 ECC 签名，调 `/device/v1/variety/*` 接口。

取自 `utils/ipc_gateway_device.py`。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import time
from typing import Any, Dict, Optional

from common.config import env_base_url
from common.crypto.ecc import gen_key
from common.http_client import HttpClient
from common.logger import get_logger
from common.signing.ecc_ugreen import ascii_sort, sign as ecc_sign
from common.utils.json_store import get_sn_secret, save_sn_secret

_logger = get_logger(__name__)


class DeviceGateway:
    def __init__(self, env: str) -> None:
        self.env = env
        self.client = HttpClient(env_base_url(env))
        self.default_headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-ugreen-app-system": "ios",
            "app_user_id": "1326011",
        }

    def _device_request(
        self,
        sn: str,
        product_model: str,
        method: str,
        path: str,
        params: Any,
    ) -> Optional[Dict[str, Any]]:
        sn_info = get_sn_secret(product_model, sn, self.env)
        if not sn_info:
            _logger.warning("经过设备网关的接口，没有找到密钥：%s/%s", product_model, sn)
            return None

        private_key = sn_info["privateKey"]
        version = sn_info["version"]

        sign_header = {
            "x-ugreen-sn": sn,
            "x-ugreen-mac": sn,
            "x-ugreen-nonce": str(int(time.time())),
            "x-ugreen-version": version,
            "x-ugreen-model": product_model,
            "x-ugreen-algorithm": "01",
        }
        signature = ecc_sign(ascii_sort(sign_header), private_key)
        sign_header["x-ugreen-signature"] = signature

        headers = {**self.default_headers, **sign_header}
        return self.client.request_json(method, path, headers=headers, json_body=params)

    def bind_by_token(self, sn: str, product_model: str, token: str) -> Optional[Dict[str, Any]]:
        sn_info = get_sn_secret(product_model, sn, self.env) or {}
        params = {
            "bindToken": token,
            "sn": sn,
            "productModel": product_model,
            "version": sn_info.get("version"),
            "mac": sn,
            "algorithm": "01",
        }
        return self._device_request(sn, product_model, "POST", "/device/v1/variety/bindByToken", params)

    def get_open_id_by_label(self, sn: str, product_model: str, label: str) -> Optional[Dict[str, Any]]:
        return self._device_request(
            sn,
            product_model,
            "POST",
            "/device/v1/variety/contact/getOpenIdByLabel",
            {"label": label, "sn": sn, "productModel": product_model},
        )

    def get_device_all_open_id(self, sn: str, product_model: str) -> Optional[Dict[str, Any]]:
        return self._device_request(
            sn,
            product_model,
            "POST",
            "/device/v1/variety/contact/getDeviceAllOpenId",
            {"sn": sn, "productModel": product_model},
        )

    def update_sn_secret(self, sn: str, product_model: str, new_version: str) -> Optional[Dict[str, Any]]:
        sn_info = get_sn_secret(product_model, sn, self.env) or {}
        new_private, new_public = gen_key()
        params = {
            "newVersion": new_version,
            "newAlgorithm": "01",
            "publicKey": new_public,
            "sn": sn,
            "productModel": product_model,
            "version": sn_info.get("version"),
            "algorithm": "01",
        }
        result = self._device_request(sn, product_model, "POST", "/device/v1/variety/updateSnSecret", params)
        if result and result.get("code") == 100000:
            save_sn_secret(
                f"{product_model}_{sn}",
                {"privateKey": new_private, "publicKey": new_public, "version": new_version},
                self.env,
            )
        return result


if __name__ == "__main__":
    gw = DeviceGateway("device")
    gw.bind_by_token("I50000U57Q200017", "00000", "GP7hJQiTsUtfp/JvNd/SXQ==")
