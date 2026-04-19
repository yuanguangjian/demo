"""工厂上报客户端：设备签名 + 工厂签名，调 `/metadata/v1/factory/*`。

取自 `utils/ipc_factory.py`。
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

_JSON_HEADERS = {"Content-Type": "application/json"}


class Factory:
    def __init__(self, env: str) -> None:
        self.env = env
        self.client = HttpClient(env_base_url(env))

    def get_sn(self, mac: str, product_model: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "GET",
            f"/metadata/v1/factory/getSn?mac={mac}&productModel={product_model}",
            headers=_JSON_HEADERS,
        )

    def _factory_sign(self, data: Dict[str, Any]) -> None:
        secret = load_json("factory.json").get(self.env, {})
        data["clientId"] = secret.get("AppId", "")
        data["timestamp"] = str(int(time.time() * 1000))
        data["clientSign"] = ecc_sign(data, secret.get("AppSecret", ""))

    def _build_sn_submit_data(self, sn: str, product_model: str) -> Dict[str, Any]:
        private_key, public_key = gen_key()
        data = {
            "mac": sn,
            "nonce": str(int(time.time() * 1000)),
            "productModel": product_model,
            "publicKey": public_key,
            "sn": sn,
            "version": "1.0.0",
        }
        data["sign"] = ecc_sign(data, private_key)
        self._factory_sign(data)
        data["_private_key"] = private_key
        return data

    def submit_sn(self, sn: str, product_model: str, *, test: bool = False) -> Optional[Any]:
        data = self._build_sn_submit_data(sn, product_model)
        private_key = data.pop("_private_key")
        path = "/metadata/v1/factory/snSubmitTest" if test else "/metadata/v1/factory/snSubmit"
        result = self.client.request_json("POST", path, headers=_JSON_HEADERS, json_body=data)
        if result and result.get("code") == 100000:
            save_sn_secret(
                f"{product_model}_{sn}",
                {
                    "privateKey": private_key,
                    "publicKey": data["publicKey"],
                    "version": data["version"],
                },
                self.env,
            )
            return result["data"]
        return result

    def switch_state(self, sn: str, product_model: str) -> Optional[Dict[str, Any]]:
        sn_info = get_sn_secret(product_model, sn, self.env)
        if not sn_info:
            _logger.warning("switch_state: 密钥不存在 %s/%s", product_model, sn)
            return None
        data = {
            "mac": sn,
            "nonce": str(int(time.time() * 1000)),
            "productModel": product_model,
            "sn": sn,
            "version": sn_info["version"],
        }
        data["sign"] = ecc_sign(data, sn_info["privateKey"])
        self._factory_sign(data)
        return self.client.request_json(
            "POST", "/metadata/v1/factory/switchState", headers=_JSON_HEADERS, json_body=data
        )


if __name__ == "__main__":
    factory = Factory("device")
